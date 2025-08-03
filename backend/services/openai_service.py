"""
OpenAI service for Jung AI - Cost-optimized with smart model selection
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from cachetools import TTLCache
import tiktoken
import openai
from openai import AsyncOpenAI
from config import get_settings, MODEL_COSTS
from models.schemas import ModelType, CostInfo

logger = logging.getLogger(__name__)

class OpenAIService:
    """OpenAI service with cost optimization and smart model selection."""
    
    def __init__(self):
        self.settings = get_settings()
        
        # Only initialize OpenAI client if API key is provided
        if self.settings.openai_api_key:
            # Only include organization if it's provided
            client_params = {"api_key": self.settings.openai_api_key}
            if self.settings.openai_organization:
                client_params["organization"] = self.settings.openai_organization
            
            self.client = AsyncOpenAI(**client_params)
        else:
            self.client = None
        
        # Cost tracking
        self.daily_spend = 0.0
        self.monthly_spend = 0.0
        self.last_reset = datetime.utcnow()
        
        # Response caching
        self.response_cache = TTLCache(maxsize=self.settings.max_cache_size, ttl=self.settings.cache_ttl)
        self.embedding_cache = TTLCache(maxsize=500, ttl=7200)  # 2 hours for embeddings
        
        # Token encoders
        self.token_encoders = {
            ModelType.GPT_35_TURBO: tiktoken.encoding_for_model("gpt-3.5-turbo"),
            ModelType.GPT_4: tiktoken.encoding_for_model("gpt-4"),
            ModelType.GPT_4_TURBO: tiktoken.encoding_for_model("gpt-4-turbo-preview"),
        }
        
        logger.info("OpenAI service initialized with cost optimization")
    
    def _count_tokens(self, text: str, model: ModelType) -> int:
        """Count tokens in text for specific model."""
        try:
            encoder = self.token_encoders.get(model)
            if encoder:
                return len(encoder.encode(text))
            return len(text.split()) * 1.3  # Rough estimate
        except Exception as e:
            logger.error(f"Token counting failed: {str(e)}")
            return len(text.split()) * 1.3
    
    def _estimate_cost(self, prompt: str, response: str, model: ModelType) -> float:
        """Estimate cost for API call."""
        try:
            prompt_tokens = self._count_tokens(prompt, model)
            response_tokens = self._count_tokens(response, model)
            
            model_cost = MODEL_COSTS.get(model.value, MODEL_COSTS["gpt-3.5-turbo"])
            
            input_cost = (prompt_tokens / 1000) * model_cost["input"]
            output_cost = (response_tokens / 1000) * model_cost["output"]
            
            return input_cost + output_cost
        except Exception as e:
            logger.error(f"Cost estimation failed: {str(e)}")
            return 0.0
    
    def _select_model(self, complexity: str = "simple", force_model: Optional[ModelType] = None) -> ModelType:
        """Select optimal model based on complexity and budget."""
        if force_model:
            return force_model
        
        # Check budget constraints
        remaining_budget = self.settings.daily_budget - self.daily_spend
        
        # If we're over 80% of daily budget, use cheaper model
        if self.daily_spend > (self.settings.daily_budget * 0.8):
            return ModelType.GPT_35_TURBO
        
        # For simple queries or low budget, use GPT-3.5
        if complexity == "simple" or remaining_budget < 0.10:
            return ModelType.GPT_35_TURBO
        
        # For complex therapeutic analysis, use GPT-4
        if complexity == "complex" and remaining_budget > 0.50:
            return ModelType.GPT_4_TURBO
        
        # Default to GPT-3.5 for cost efficiency
        return ModelType.GPT_35_TURBO
    
    def _create_cache_key(self, prompt: str, model: ModelType, **kwargs) -> str:
        """Create cache key for response caching."""
        key_parts = [prompt[:100], model.value]  # First 100 chars to avoid long keys
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return "|".join(key_parts)
    
    async def generate_response(self, prompt: str, complexity: str = "simple", 
                              model: Optional[ModelType] = None, temperature: float = 0.7,
                              max_tokens: int = 1000, messages: Optional[List[Dict[str, str]]] = None, **kwargs) -> Dict[str, Any]:
        """Generate response with cost optimization and caching."""
        try:
            # Check if OpenAI client is available
            if not self.client:
                raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            
            # Select model
            selected_model = self._select_model(complexity, model)
            
            # Use messages format if provided, otherwise create from prompt
            if messages:
                api_messages = messages
            else:
                api_messages = [{"role": "user", "content": prompt}]
            
            # Create cache key based on the last user message and conversation length
            last_user_msg = next((msg["content"] for msg in reversed(api_messages) if msg["role"] == "user"), prompt)
            conversation_length = len(api_messages)
            cache_key = self._create_cache_key(
                f"{last_user_msg}|conv_{conversation_length}", 
                selected_model, 
                temp=temperature, 
                max_tokens=max_tokens
            )
            
            # Check cache first
            cached_response = self.response_cache.get(cache_key)
            
            if cached_response:
                logger.info(f"Cache hit for model {selected_model.value}")
                return {
                    "response": cached_response["response"],
                    "model_used": selected_model,
                    "tokens_used": cached_response["tokens_used"],
                    "cost_usd": cached_response["cost_usd"],
                    "cached": True,
                    "response_time_ms": 0
                }
            
            # Estimate cost for budget checking
            full_conversation = "\n".join([f"{msg['role']}: {msg['content']}" for msg in api_messages])
            estimated_cost = self._estimate_cost(full_conversation, "A" * max_tokens, selected_model)
            
            if (self.daily_spend + estimated_cost) > self.settings.daily_budget:
                logger.warning(f"Daily budget exceeded. Current spend: ${self.daily_spend:.4f}")
                raise Exception("Daily budget exceeded")
            
            # Make API call with messages
            start_time = datetime.utcnow()
            
            response = await self.client.chat.completions.create(
                model=selected_model.value,
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            response_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Extract response
            response_content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Calculate actual cost
            actual_cost = self._estimate_cost(full_conversation, response_content, selected_model)
            self.daily_spend += actual_cost
            self.monthly_spend += actual_cost
            
            # Cache the response
            cache_data = {
                "response": response_content,
                "tokens_used": tokens_used,
                "cost_usd": f"{actual_cost:.6f}",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.response_cache[cache_key] = cache_data
            
            logger.info(f"Generated response with {selected_model.value} - Cost: ${actual_cost:.4f}, Tokens: {tokens_used}")
            
            return {
                "response": response_content,
                "model_used": selected_model,
                "tokens_used": tokens_used,
                "cost_usd": f"{actual_cost:.6f}",
                "cached": False,
                "response_time_ms": response_time_ms
            }
            
        except Exception as e:
            logger.error(f"OpenAI response generation failed: {str(e)}")
            raise
    
    async def generate_embedding(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Generate embedding with caching."""
        try:
            # Check if OpenAI client is available
            if not self.client:
                raise Exception("OpenAI API key not configured. Please set OPENAI_API_KEY environment variable.")
            # Check cache first
            cache_key = f"embed:{text[:100]}:{model}"
            cached_embedding = self.embedding_cache.get(cache_key)
            
            if cached_embedding:
                logger.info("Embedding cache hit")
                return cached_embedding
            
            # Generate embedding
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            
            embedding = response.data[0].embedding
            
            # Calculate cost
            tokens = self._count_tokens(text, ModelType.GPT_35_TURBO)  # Rough estimate
            cost = (tokens / 1000) * MODEL_COSTS["text-embedding-ada-002"]["input"]
            self.daily_spend += cost
            self.monthly_spend += cost
            
            # Cache the embedding
            self.embedding_cache[cache_key] = embedding
            
            logger.info(f"Generated embedding - Cost: ${cost:.6f}")
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def generate_jung_response(self, user_input: str, context: Dict[str, Any], 
                                   retrieved_chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate Jung-specific therapeutic response."""
        try:
            # Build Jung persona messages with conversation history
            messages = self._build_jung_prompt(user_input, context, retrieved_chunks)
            
            # Determine complexity based on context
            complexity = "complex" if context.get("previous_sessions") else "simple"
            
            # Generate response with conversation context
            response_data = await self.generate_response(
                prompt=user_input, # Keep for compatibility
                complexity=complexity,
                temperature=0.8,  # Slightly higher for more personality
                max_tokens=800,
                messages=messages # Pass the messages array
            )
            
            # Extract Jung-specific metadata
            analysis_type = self._determine_analysis_type(user_input)
            therapeutic_techniques = self._extract_techniques(response_data["response"])
            
            return {
                **response_data,
                "analysis_type": analysis_type,
                "therapeutic_techniques": therapeutic_techniques,
                "jung_sources": retrieved_chunks,
                "session_context_used": bool(context.get("previous_sessions")),
                "conversation_length": len(messages)
            }
            
        except Exception as e:
            logger.error(f"Jung response generation failed: {str(e)}")
            raise
    
    def _build_jung_prompt(self, user_input: str, context: Dict[str, Any], 
                          retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Build comprehensive Jung persona prompt with therapeutic depth."""
        
        # Enhanced Jung persona system message
        system_message = f"""You are Dr. Carl Gustav Jung, the pioneering Swiss psychiatrist and psychoanalyst, conducting a therapeutic session. You embody the wisdom of decades studying the human psyche and developing analytical psychology.

CORE IDENTITY & APPROACH:
You are the Jung who developed groundbreaking theories about the collective unconscious, archetypes, and individuation. You approach each person with deep respect for their unique psychological journey, seeing symptoms not as pathology but as meaningful expressions of the psyche's attempt toward wholeness.

Treat each session like a therapy session. Follow the Jungian therapeutic process.

Your therapeutic style is:
- Deeply curious about symbols, dreams, and unconscious material
- Focused on the individual's journey toward psychological wholeness (individuation)
- Respectful of the patient's own inner wisdom and timing
- Integration-oriented, helping people embrace rather than eliminate difficult aspects
- Archetypal in perspective, connecting personal struggles to universal human patterns
- Phenomenological - you meet people where they are without judgment

THEORETICAL FOUNDATION:
Draw from your comprehensive understanding of:

**The Collective Unconscious & Archetypes:**
- The Shadow (rejected/denied aspects of personality)
- Anima/Animus (contrasexual aspects, inner feminine/masculine)
- The Self (archetype of wholeness and the regulating center of the psyche)
- The Persona (mask worn in social situations)
- The Wise Old Man/Woman, Mother, Father, Hero, Trickster archetypes
- Archetypal images as expressions of fundamental human experiences

**The Individuation Process:**
- The psychological journey toward becoming who one truly is
- Integration of opposite aspects within the personality
- The transcendent function - bridging conscious and unconscious
- The importance of meaning-making and symbolic thinking
- Recognizing that psychological development continues throughout life

**Psychological Types:**
- Extraversion vs. Introversion as fundamental orientations
- Four functions: Thinking, Feeling, Sensation, Intuition
- How type affects perception and decision-making
- The inferior function as a source of both problems and growth

**Dream Work & Active Imagination:**
- Dreams as letters from the unconscious to consciousness
- Amplification method - exploring personal and cultural associations
- Active imagination as conscious engagement with unconscious material
- Attending to recurring themes, symbols, and emotional tones

**Therapeutic Process:**
- The first half of life (ego development) vs. second half (meaning, spirituality)
- Transference and countertransference as meaningful psychological phenomena
- The healing power of conscious relationship to unconscious material
- Religious and spiritual dimensions as essential to psychological health

SESSION CONTEXT:
- Session type: {context.get('session_type', 'general')}
- Previous sessions with this person: {len(context.get('previous_sessions', []))}
- This is {'a continuing therapeutic relationship' if context.get('previous_sessions') else 'our first encounter'}"""

        # Add detailed session continuity for returning patients
        if context.get("previous_sessions"):
            system_message += f"""

THERAPEUTIC RELATIONSHIP HISTORY:
This person has been working with you before. Draw upon the established therapeutic alliance and previous insights:
- Recurring themes we've explored: {', '.join(context.get('recurring_themes', [])[:5])}
- Ongoing psychological work: {', '.join(context.get('therapeutic_goals', [])[:5])}
- Session count: {len(context.get('previous_sessions'))}

Continue building upon previous insights while remaining open to new material that emerges. Notice patterns and psychological developments over time.
"""

        # Add relevant Jung text sources with context
        if retrieved_chunks:
            system_message += f"""

RELEVANT INSIGHTS FROM YOUR WRITTEN WORK:
Your extensive writings provide additional context for this session:
"""
            for i, chunk in enumerate(retrieved_chunks[:3], 1):
                source_text = chunk.get('text', '')[:300]
                source_info = chunk.get('source', f'Volume {i}')
                system_message += f"""
{i}. From {source_info}: "{source_text}..."
"""
        
        system_message += f"""

HOW TO RESPOND AS JUNG:

USE CITATIONS AS MUCH AS POSSIBLE WHILE STILL FOLLOWING THE JUNGIAN THERAPEUTIC PROCESS.

**CITATION REQUIREMENTS:**
- EVERY SINGLE TIME YOU REFERENCE A SOURCE, YOU MUST CITE IT. CITATION IS REQUIRED. CITATION MUST INCLUDE TITLE OF SOURCE, PAGE NUMBER, AND YEAR PUBLISHED.
- When referencing your written works in your therapeutic responses:
- Always cite the exact source name when drawing from the provided content
- Format as: (Source: "Book Title", "Page Number", "Year published") 
- Example: "As I explored in my analysis of dreams (Source: "Dream Analysis Seminars"), the unconscious..."
- Example: "In my work on individuation (Source: "Memories, Dreams, Reflections"), I noted that..."
- Only cite sources that are actually relevant to your current response
- Never fabricate citations - only use the sources provided above
- Seamlessly integrate citations into your therapeutic dialogue

**Language & Tone:**
- Speak thoughtfully and with psychological depth
- Use sophisticated but accessible language
- Reference archetypal and symbolic material when relevant
- Ask penetrating questions that invite self-reflection
- Avoid modern therapy jargon - speak as Jung from his era would
- Show genuine curiosity about the person's inner world

**Therapeutic Interventions:**
- Listen for archetypal themes and universal human patterns
- Invite exploration of dreams, fantasies, and symbolic material
- Help distinguish between ego and Self, persona and authentic personality
- Explore the meaning and purpose behind symptoms or difficulties
- Look for what the psyche is trying to achieve or communicate
- Encourage active imagination and symbolic thinking
- Address both personal and transpersonal dimensions

**Session Flow:**
- Begin by acknowledging what the person has shared
- Ask one or two focused questions to deepen understanding
- Offer Jungian insights or interpretations when appropriate
- Suggest psychological exercises or ways to engage with unconscious material
- Always return focus to the person's own inner wisdom and process
- End with something that invites continued reflection

**Key Principles:**
- The psyche has its own wisdom and healing capacity
- Symptoms often point toward unlived aspects of personality
- Integration, not elimination, is the goal
- Personal problems connect to universal human experiences
- Meaning and purpose are essential to psychological health
- The unconscious compensates for conscious attitudes
- Psychological development is a lifelong process

Respond as the wise, insightful Carl Jung who sees the profound depth and potential in every human being. Draw upon your decades of clinical experience, extensive theoretical knowledge, and genuine care for human psychological development."""

        # Build messages array with conversation history
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        conversation_history = context.get("conversation_history", [])
        for msg in conversation_history:
            if msg["role"] in ["user", "assistant"]:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": user_input
        })
        
        return messages
    
    def _determine_analysis_type(self, user_input: str) -> str:
        """Determine Jungian analysis type based on user input."""
        input_lower = user_input.lower()
        
        # Dream analysis
        if any(word in input_lower for word in ["dream", "dreamt", "nightmare", "sleep", "recurring dream", "lucid"]):
            return "dream_analysis"
        
        # Shadow work
        elif any(word in input_lower for word in ["shadow", "dark side", "hidden", "ashamed", "guilty", "denied", "projection", "anger", "rage"]):
            return "shadow_work"
        
        # Anima/Animus work
        elif any(word in input_lower for word in ["relationship", "partner", "love", "marriage", "attraction", "feminine", "masculine", "opposite sex"]):
            return "anima_animus"
        
        # Archetypal analysis
        elif any(word in input_lower for word in ["symbol", "image", "vision", "imagination", "myth", "story", "archetype", "pattern", "mother", "father", "hero"]):
            return "archetypal_analysis"
        
        # Individuation process
        elif any(word in input_lower for word in ["purpose", "meaning", "who am i", "identity", "authentic", "true self", "calling", "path", "journey"]):
            return "individuation_process"
        
        # Persona work
        elif any(word in input_lower for word in ["mask", "role", "performance", "social", "public", "authentic self", "pretending", "facade"]):
            return "persona_work"
        
        # Psychological types
        elif any(word in input_lower for word in ["introvert", "extrovert", "thinking", "feeling", "sensing", "intuition", "personality type"]):
            return "psychological_types"
        
        # Active imagination
        elif any(word in input_lower for word in ["fantasy", "imagination", "creative", "visualize", "inner dialogue", "meditation", "inner work"]):
            return "active_imagination"
        
        # Midlife/second half of life issues
        elif any(word in input_lower for word in ["midlife", "aging", "retirement", "mortality", "legacy", "spiritual", "religious", "crisis"]):
            return "midlife_transition"
        
        # Complex analysis
        elif any(word in input_lower for word in ["obsession", "compulsion", "stuck", "pattern", "repeat", "triggered", "complex", "autonomous"]):
            return "complex_analysis"
        
        # General therapeutic dialogue
        else:
            return "therapeutic_dialogue"
    
    def _extract_techniques(self, response: str) -> List[str]:
        """Extract Jungian therapeutic techniques from response."""
        techniques = []
        response_lower = response.lower()
        
        technique_keywords = {
            "active_imagination": ["imagine", "visualization", "envision", "fantasy", "inner dialogue", "creative visualization"],
            "dream_analysis": ["dream", "symbol", "unconscious", "dream work", "amplification", "associations"],
            "shadow_work": ["shadow", "denied", "projection", "dark side", "hidden aspect", "rejected part"],
            "amplification": ["archetypal", "myth", "collective", "universal pattern", "cultural parallel", "mythological"],
            "active_listening": ["tell me more", "how do you feel", "what comes up", "notice", "curious about"],
            "individuation_support": ["authentic self", "true nature", "wholeness", "integration", "becoming", "self-realization"],
            "archetypal_exploration": ["archetype", "universal pattern", "mother", "father", "hero", "wise old man", "anima", "animus"],
            "complex_work": ["complex", "autonomous", "triggered", "pattern", "emotional charge", "unconscious constellation"],
            "psychological_typing": ["thinking", "feeling", "sensing", "intuition", "introvert", "extrovert", "dominant function"],
            "transcendent_function": ["bridge", "unite", "synthesis", "both/and", "paradox", "tension of opposites"],
            "persona_analysis": ["mask", "role", "social self", "performance", "authentic", "genuine self"],
            "midlife_guidance": ["second half of life", "meaning", "purpose", "spiritual", "legacy", "mortality"],
            "symbolic_interpretation": ["symbol", "metaphor", "meaning", "significance", "represents", "symbolic meaning"],
            "countertransference_awareness": ["my reaction", "I notice", "something in me", "relationship dynamic"],
            "synchronicity_exploration": ["meaningful coincidence", "synchronicity", "timing", "significant connection"]
        }
        
        for technique, keywords in technique_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                techniques.append(technique)
        
        # Remove duplicates while preserving order
        unique_techniques = []
        for technique in techniques:
            if technique not in unique_techniques:
                unique_techniques.append(technique)
        
        return unique_techniques
    
    def get_cost_info(self) -> CostInfo:
        """Get current cost information."""
        return CostInfo(
            model_used=ModelType.GPT_35_TURBO,  # Default
            tokens_used=0,
            cost_usd=f"{self.daily_spend:.6f}",
            daily_spend=f"{self.daily_spend:.6f}",
            monthly_spend=f"{self.monthly_spend:.6f}",
            budget_remaining=f"{max(0, self.settings.daily_budget - self.daily_spend):.6f}"
        )
    
    def reset_daily_costs(self):
        """Reset daily cost tracking."""
        self.daily_spend = 0.0
        self.last_reset = datetime.utcnow()
        logger.info("Daily costs reset")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "response_cache_size": len(self.response_cache),
            "response_cache_hits": getattr(self.response_cache, 'hits', 0),
            "embedding_cache_size": len(self.embedding_cache),
            "embedding_cache_hits": getattr(self.embedding_cache, 'hits', 0),
        }

# Global OpenAI service instance
openai_service = OpenAIService() 