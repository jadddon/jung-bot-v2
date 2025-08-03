"""
Pydantic schemas for Jung AI Analysis System - Request/Response validation
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, EmailStr, validator
from enum import Enum
import uuid

# Enums for structured data
class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class SessionType(str, Enum):
    GENERAL = "general"
    DREAM_ANALYSIS = "dream_analysis"
    SHADOW_WORK = "shadow_work"
    ACTIVE_IMAGINATION = "active_imagination"
    INDIVIDUATION = "individuation"

class AnalysisType(str, Enum):
    DREAM_ANALYSIS = "dream_analysis"
    SHADOW_WORK = "shadow_work"
    ANIMA_ANIMUS = "anima_animus"
    ARCHETYPAL_ANALYSIS = "archetypal_analysis"
    THERAPEUTIC_DIALOGUE = "therapeutic_dialogue"

class ModelType(str, Enum):
    GPT_35_TURBO = "gpt-3.5-turbo"
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo-preview"

# Base schemas
class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

# User schemas
class UserBase(BaseSchema):
    email: EmailStr
    preferred_name: Optional[str] = None
    timezone: str = "UTC"

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    total_sessions: int = 0
    total_messages: int = 0

class UserUpdate(BaseSchema):
    preferred_name: Optional[str] = None
    timezone: Optional[str] = None

# Session schemas
class SessionBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    session_type: SessionType = SessionType.GENERAL
    therapeutic_goals: Optional[List[str]] = None

class SessionCreate(SessionBase):
    is_anonymous: bool = True

class SessionResponse(SessionBase):
    id: str
    user_id: Optional[int] = None
    is_anonymous: bool
    created_at: datetime
    updated_at: datetime
    last_activity: datetime
    is_active: bool
    context_summary: Optional[str] = None
    key_insights: Optional[List[str]] = None
    message_count: int = 0
    duration_minutes: int = 0

class SessionUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    session_type: Optional[SessionType] = None
    therapeutic_goals: Optional[List[str]] = None
    is_active: Optional[bool] = None

class SessionSummary(BaseSchema):
    """Lightweight session summary for lists."""
    id: str
    title: str
    session_type: SessionType
    created_at: datetime
    last_activity: datetime
    message_count: int
    is_anonymous: bool

# Message schemas
class MessageBase(BaseSchema):
    content: str = Field(..., min_length=1, max_length=10000)
    role: MessageRole

class MessageCreate(MessageBase):
    session_id: str

class MessageResponse(MessageBase):
    id: int
    session_id: str
    timestamp: datetime
    sources: Optional[List[Dict[str, Any]]] = None
    analysis_type: Optional[AnalysisType] = None
    therapeutic_techniques: Optional[List[str]] = None
    model_used: Optional[ModelType] = None
    tokens_used: Optional[int] = None
    response_time_ms: Optional[int] = None
    cost_usd: Optional[str] = None
    relevance_score: Optional[float] = None
    therapeutic_value: Optional[float] = None

class MessageWithSources(MessageResponse):
    """Extended message response with Jung sources."""
    jung_sources: Optional[List[Dict[str, Any]]] = Field(
        None, 
        description="Jung text sources used for this response"
    )

# Chat interaction schemas
class ChatMessageRequest(BaseSchema):
    content: str = Field(..., min_length=1, max_length=10000)
    session_id: str
    context_length: Optional[int] = Field(default=4000, ge=1000, le=8000)

class ChatMessageResponse(BaseSchema):
    user_message: MessageResponse
    assistant_message: MessageResponse
    session_updated: bool = False
    cost_info: Optional[Dict[str, Any]] = None

class StreamingChatResponse(BaseSchema):
    """For server-sent events streaming."""
    type: str = Field(..., description="Type of streaming event")
    data: Dict[str, Any] = Field(..., description="Event data")
    session_id: str

# Session context schemas
class SessionContextBase(BaseSchema):
    recurring_themes: Optional[List[str]] = None
    emotional_patterns: Optional[List[str]] = None
    therapeutic_progress: Optional[Dict[str, Any]] = None
    archetypal_patterns: Optional[List[str]] = None
    shadow_work_progress: Optional[Dict[str, Any]] = None
    individuation_stage: Optional[str] = None

class SessionContextResponse(SessionContextBase):
    id: int
    session_id: str
    related_sessions: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

# Jung-specific schemas
class JungSource(BaseSchema):
    """Jung text source reference."""
    chunk_id: str
    text: str
    source: str = Field(..., description="Jung work title")
    volume: Optional[str] = None
    page: Optional[int] = None
    concepts: List[str] = Field(default_factory=list)
    relevance_score: float = Field(..., ge=0.0, le=1.0)

class TherapeuticTechnique(BaseSchema):
    """Therapeutic technique used in analysis."""
    name: str
    description: str
    effectiveness: Optional[float] = Field(None, ge=0.0, le=1.0)

class AnalysisResult(BaseSchema):
    """Result of Jung analysis."""
    analysis_type: AnalysisType
    insights: List[str]
    techniques_used: List[TherapeuticTechnique]
    archetypal_patterns: List[str]
    therapeutic_value: float = Field(..., ge=0.0, le=1.0)
    sources: List[JungSource]

# Cost tracking schemas
class CostInfo(BaseSchema):
    """Cost information for API usage."""
    model_used: ModelType
    tokens_used: int
    cost_usd: str
    daily_spend: str
    monthly_spend: str
    budget_remaining: str

class UsageStats(BaseSchema):
    """Usage statistics."""
    total_sessions: int
    total_messages: int
    total_cost: str
    average_cost_per_session: str
    most_used_model: str
    daily_stats: Dict[str, Any]

# API Response schemas
class APIResponse(BaseSchema):
    """Standard API response wrapper."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    errors: Optional[List[str]] = None

class PaginatedResponse(BaseSchema):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool

# Authentication schemas
class TokenResponse(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class LoginRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)

class RegisterRequest(BaseSchema):
    email: EmailStr
    password: str = Field(..., min_length=8)
    preferred_name: Optional[str] = None

# Health check schema
class HealthCheck(BaseSchema):
    status: str = "healthy"
    version: str
    timestamp: datetime
    database: str = "connected"
    openai: str = "available"
    pinecone: str = "available"
    memory_usage: Optional[str] = None
    uptime: Optional[str] = None

# Error schemas
class ErrorDetail(BaseSchema):
    loc: List[Union[str, int]]
    msg: str
    type: str

class ValidationError(BaseSchema):
    detail: List[ErrorDetail]

class HTTPError(BaseSchema):
    detail: str
    status_code: int
    error_type: str

# Validators
class SessionValidators:
    @validator('title')
    def validate_title(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip()

class MessageValidators:
    @validator('content')
    def validate_content(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Message content cannot be empty")
        return v.strip()

# Export commonly used schemas
__all__ = [
    "MessageRole", "SessionType", "AnalysisType", "ModelType",
    "UserCreate", "UserResponse", "UserUpdate",
    "SessionCreate", "SessionResponse", "SessionUpdate", "SessionSummary",
    "MessageCreate", "MessageResponse", "MessageWithSources",
    "ChatMessageRequest", "ChatMessageResponse", "StreamingChatResponse",
    "SessionContextResponse", "JungSource", "AnalysisResult",
    "CostInfo", "UsageStats", "APIResponse", "PaginatedResponse",
    "TokenResponse", "LoginRequest", "RegisterRequest",
    "HealthCheck", "HTTPError", "ValidationError"
] 