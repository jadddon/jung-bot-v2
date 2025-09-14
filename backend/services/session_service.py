"""
Session service for Jung AI - Anonymous and Authenticated Session Management
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from supabase import create_client, Client
import uuid
from config import get_settings
from models.schemas import (
    SessionCreate, SessionResponse, SessionUpdate, SessionSummary,
    MessageResponse, SessionContextResponse
)

logger = logging.getLogger(__name__)

class SessionService:
    """Session management service for Jung AI."""
    
    def __init__(self):
        self.settings = get_settings()

        # Determine demo mode: when Supabase creds are missing or clearly placeholders
        demo_like_values = {None, "", "demo", "demo-key", "demo-service-key", "placeholder"}
        is_missing_creds = (
            getattr(self.settings, "supabase_url", None) in demo_like_values
            or getattr(self.settings, "supabase_service_role_key", None) in demo_like_values
        )
        self.demo_mode: bool = bool(is_missing_creds)

        # Initialize Supabase client only when not in demo mode
        self.supabase: Client | None = None
        if not self.demo_mode:
            self.supabase = create_client(
                self.settings.supabase_url,
                self.settings.supabase_service_role_key  # Use service role for admin operations
            )

        # In-memory stores used only in demo mode
        self._memory_sessions: Dict[str, Dict[str, Any]] = {}
        self._memory_messages: Dict[str, List[Dict[str, Any]]] = {}
        
    async def create_session(self, user_id: Optional[int] = None, title: Optional[str] = None) -> SessionResponse:
        """Create a new session (anonymous or authenticated)."""
        try:
            session_id = str(uuid.uuid4())
            is_anonymous = user_id is None

            session_data = {
                "id": session_id,
                "user_id": user_id,
                "title": title or "New Jung Analysis Session",
                "is_anonymous": is_anonymous,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat(),
                "is_active": True,
                "session_type": "general",
                "message_count": 0,
                "duration_minutes": 0,
            }

            if self.demo_mode or self.supabase is None:
                # Store session in memory for demo mode
                self._memory_sessions[session_id] = session_data
                self._memory_messages.setdefault(session_id, [])
                logger.info(f"[DEMO] Created {'anonymous' if is_anonymous else 'authenticated'} session: {session_id}")
                return SessionResponse(**session_data)
            else:
                response = self.supabase.table("sessions").insert(session_data).execute()

                if not response.data:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to create session"
                    )

                session = response.data[0]

                # Update user stats if authenticated
                if user_id:
                    await self._update_user_session_count(user_id, increment=True)

                logger.info(f"Created {'anonymous' if is_anonymous else 'authenticated'} session: {session_id}")
                return SessionResponse(**session)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to create session: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Session creation failed"
            )
    
    async def get_session(self, session_id: str, user_id: Optional[int] = None) -> Optional[SessionResponse]:
        """Get session by ID with access control."""
        try:
            if self.demo_mode or self.supabase is None:
                session_data = self._memory_sessions.get(session_id)
                if not session_data:
                    return None
            else:
                response = self.supabase.table("sessions").select("*").eq("id", session_id).execute()
                if not response.data:
                    return None
                session_data = response.data[0]
            
            # Check access permissions
            if not session_data["is_anonymous"] and session_data["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this session"
                )
            
            return SessionResponse(**session_data)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {str(e)}")
            return None
    
    async def update_session(self, session_id: str, updates: SessionUpdate, user_id: Optional[int] = None) -> Optional[SessionResponse]:
        """Update session with access control."""
        try:
            # First, verify access
            session = await self.get_session(session_id, user_id)
            if not session:
                return None
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow().isoformat(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            if updates.title is not None:
                update_data["title"] = updates.title
            if updates.session_type is not None:
                update_data["session_type"] = updates.session_type
            if updates.therapeutic_goals is not None:
                update_data["therapeutic_goals"] = updates.therapeutic_goals
            if updates.is_active is not None:
                update_data["is_active"] = updates.is_active

            if self.demo_mode or self.supabase is None:
                # Update in-memory
                if session_id in self._memory_sessions:
                    self._memory_sessions[session_id].update(update_data)
                    return SessionResponse(**self._memory_sessions[session_id])
                return None
            else:
                response = self.supabase.table("sessions").update(update_data).eq("id", session_id).execute()
                if not response.data:
                    return None
                return SessionResponse(**response.data[0])
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {str(e)}")
            return None
    
    async def delete_session(self, session_id: str, user_id: Optional[int] = None) -> bool:
        """Delete session with access control."""
        try:
            # First, verify access
            session = await self.get_session(session_id, user_id)
            if not session:
                return False
            
            if self.demo_mode or self.supabase is None:
                self._memory_sessions.pop(session_id, None)
                self._memory_messages.pop(session_id, None)
                return True
            
            # Delete session (cascades to messages) in Supabase
            self.supabase.table("sessions").delete().eq("id", session_id).execute()
            
            # Update user stats if authenticated
            if session.user_id:
                await self._update_user_session_count(session.user_id, increment=False)
            
            logger.info(f"Deleted session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {str(e)}")
            return False
    
    async def get_user_sessions(self, user_id: int, limit: int = 50, offset: int = 0) -> List[SessionSummary]:
        """Get user's session history with pagination."""
        try:
            if self.demo_mode or self.supabase is None:
                # Filter in-memory sessions for the user
                sessions: List[SessionSummary] = []
                for sess in self._memory_sessions.values():
                    if sess.get("user_id") == user_id:
                        sessions.append(SessionSummary(**sess))
                return sessions
            else:
                response = self.supabase.table("sessions").select(
                    "id, title, session_type, created_at, last_activity, message_count, is_anonymous"
                ).eq("user_id", user_id).order("last_activity", desc=True).range(offset, offset + limit - 1).execute()
                sessions: List[SessionSummary] = []
                for session_data in response.data:
                    sessions.append(SessionSummary(**session_data))
                return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions for user {user_id}: {str(e)}")
            return []
    
    async def save_anonymous_session(self, session_id: str, user_id: int) -> bool:
        """Convert anonymous session to authenticated user session."""
        try:
            if self.demo_mode or self.supabase is None:
                if session_id in self._memory_sessions and self._memory_sessions[session_id].get("is_anonymous"):
                    self._memory_sessions[session_id].update({
                        "user_id": user_id,
                        "is_anonymous": False,
                        "updated_at": datetime.utcnow().isoformat(),
                    })
                    return True
                return False
            else:
                # Get the anonymous session
                response = self.supabase.table("sessions").select("*").eq("id", session_id).eq("is_anonymous", True).execute()
                if not response.data:
                    return False
                # Update session to be owned by user
                update_data = {
                    "user_id": user_id,
                    "is_anonymous": False,
                    "updated_at": datetime.utcnow().isoformat()
                }
                self.supabase.table("sessions").update(update_data).eq("id", session_id).execute()
                await self._update_user_session_count(user_id, increment=True)
                logger.info(f"Converted anonymous session {session_id} to user {user_id}")
                return True
            
        except Exception as e:
            logger.error(f"Failed to save anonymous session {session_id}: {str(e)}")
            return False
    
    async def get_session_messages(self, session_id: str, user_id: Optional[int] = None, limit: int = 100) -> List[MessageResponse]:
        """Get messages for a session with access control."""
        try:
            # Verify access to session
            session = await self.get_session(session_id, user_id)
            if not session:
                return []

            if self.demo_mode or self.supabase is None:
                messages: List[MessageResponse] = []
                for msg in self._memory_messages.get(session_id, [])[:limit]:
                    messages.append(MessageResponse(**msg))
                return messages
            else:
                response = self.supabase.table("messages").select("*").eq("session_id", session_id).order("timestamp", desc=False).limit(limit).execute()
                messages: List[MessageResponse] = []
                for message_data in response.data:
                    messages.append(MessageResponse(**message_data))
                return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {str(e)}")
            return []
    
    async def update_session_activity(self, session_id: str) -> None:
        """Update session last activity timestamp."""
        try:
            if self.demo_mode or self.supabase is None:
                if session_id in self._memory_sessions:
                    self._memory_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
                return
            else:
                self.supabase.table("sessions").update({
                    "last_activity": datetime.utcnow().isoformat()
                }).eq("id", session_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to update session activity {session_id}: {str(e)}")
    
    async def increment_message_count(self, session_id: str) -> None:
        """Increment message count for session."""
        try:
            if self.demo_mode or self.supabase is None:
                if session_id in self._memory_sessions:
                    current = int(self._memory_sessions[session_id].get("message_count", 0))
                    self._memory_sessions[session_id]["message_count"] = current + 1
                    self._memory_sessions[session_id]["last_activity"] = datetime.utcnow().isoformat()
                return
            else:
                # Get current count
                response = self.supabase.table("sessions").select("message_count").eq("id", session_id).execute()
                if response.data:
                    current_count = response.data[0]["message_count"]
                    new_count = current_count + 1
                    self.supabase.table("sessions").update({
                        "message_count": new_count,
                        "last_activity": datetime.utcnow().isoformat()
                    }).eq("id", session_id).execute()
                
        except Exception as e:
            logger.error(f"Failed to increment message count for session {session_id}: {str(e)}")
    
    async def generate_session_summary(self, session_id: str) -> Optional[str]:
        """Generate AI summary of session (placeholder - would use OpenAI in production)."""
        try:
            # Get session messages
            messages = await self.get_session_messages(session_id)
            
            if not messages:
                return None
            
            # Simple summary generation (in production, this would use OpenAI)
            user_messages = [msg.content for msg in messages if msg.role == "user"]
            assistant_messages = [msg.content for msg in messages if msg.role == "assistant"]
            
            summary_data = {
                "total_messages": len(messages),
                "user_message_count": len(user_messages),
                "assistant_message_count": len(assistant_messages),
                "session_topics": user_messages[:3] if user_messages else [],
                "key_insights": assistant_messages[:2] if assistant_messages else [],
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Update session with summary
            if self.demo_mode or self.supabase is None:
                if session_id in self._memory_sessions:
                    self._memory_sessions[session_id]["context_summary"] = str(summary_data)
                    self._memory_sessions[session_id]["updated_at"] = datetime.utcnow().isoformat()
            else:
                self.supabase.table("sessions").update({
                    "context_summary": str(summary_data),
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", session_id).execute()
            
            return str(summary_data)
            
        except Exception as e:
            logger.error(f"Failed to generate session summary {session_id}: {str(e)}")
            return None
    
    async def get_session_context(self, user_id: int, current_session_id: str) -> Dict[str, Any]:
        """Build context from previous sessions for authenticated users."""
        try:
            if not user_id:
                return {}
            if self.demo_mode or self.supabase is None:
                return {}
            else:
                # Get recent sessions (excluding current)
                response = self.supabase.table("sessions").select(
                    "id, title, session_type, context_summary, therapeutic_goals, key_insights"
                ).eq("user_id", user_id).neq("id", current_session_id).order("last_activity", desc=True).limit(5).execute()
                if not response.data:
                    return {}
                context = {
                    "previous_sessions": [],
                    "recurring_themes": [],
                    "therapeutic_goals": [],
                    "session_count": len(response.data)
                }
                for session_data in response.data:
                    context["previous_sessions"].append({
                        "id": session_data["id"],
                        "title": session_data["title"],
                        "type": session_data["session_type"],
                        "summary": session_data.get("context_summary")
                    })
                    if session_data.get("therapeutic_goals"):
                        context["therapeutic_goals"].extend(session_data["therapeutic_goals"])
                    if session_data.get("key_insights"):
                        context["recurring_themes"].extend(session_data["key_insights"])
                context["therapeutic_goals"] = list(set(context["therapeutic_goals"]))[:10]
                context["recurring_themes"] = list(set(context["recurring_themes"]))[:10]
                return context
            
        except Exception as e:
            logger.error(f"Failed to get session context for user {user_id}: {str(e)}")
            return {}
    
    async def cleanup_old_anonymous_sessions(self, hours_old: int = 24) -> int:
        """Clean up old anonymous sessions to save space."""
        try:
            if self.demo_mode or self.supabase is None:
                # In demo mode, trim in-memory sessions older than cutoff
                cutoff_time = (datetime.utcnow() - timedelta(hours=hours_old)).isoformat()
                to_delete = [sid for sid, sess in self._memory_sessions.items() if sess.get("is_anonymous") and sess.get("last_activity", "") < cutoff_time]
                for sid in to_delete:
                    self._memory_sessions.pop(sid, None)
                    self._memory_messages.pop(sid, None)
                logger.info(f"[DEMO] Cleaned up {len(to_delete)} old anonymous sessions")
                return len(to_delete)
            else:
                cutoff_time = (datetime.utcnow() - timedelta(hours=hours_old)).isoformat()
                response = self.supabase.table("sessions").select("id").eq("is_anonymous", True).lt("last_activity", cutoff_time).execute()
                if not response.data:
                    return 0
                session_ids = [session["id"] for session in response.data]
                for session_id in session_ids:
                    self.supabase.table("sessions").delete().eq("id", session_id).execute()
                logger.info(f"Cleaned up {len(session_ids)} old anonymous sessions")
                return len(session_ids)
            
        except Exception as e:
            logger.error(f"Failed to cleanup anonymous sessions: {str(e)}")
            return 0
    
    async def _update_user_session_count(self, user_id: int, increment: bool = True) -> None:
        """Update user's total session count."""
        try:
            if self.demo_mode or self.supabase is None:
                # No-op in demo mode
                return
            else:
                # Get current count
                response = self.supabase.table("users").select("total_sessions").eq("id", user_id).execute()
                if response.data:
                    current_count = response.data[0]["total_sessions"]
                    new_count = current_count + 1 if increment else max(0, current_count - 1)
                    self.supabase.table("users").update({
                        "total_sessions": new_count,
                        "updated_at": datetime.utcnow().isoformat()
                    }).eq("id", user_id).execute()
                
        except Exception as e:
            logger.error(f"Failed to update user session count: {str(e)}")

# Global session service instance
session_service = SessionService() 