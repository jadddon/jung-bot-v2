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
        self.supabase: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_service_role_key  # Use service role for admin operations
        )
        
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
                "duration_minutes": 0
            }
            
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
            
            # Delete session (cascades to messages)
            response = self.supabase.table("sessions").delete().eq("id", session_id).execute()
            
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
            response = self.supabase.table("sessions").select(
                "id, title, session_type, created_at, last_activity, message_count, is_anonymous"
            ).eq("user_id", user_id).order("last_activity", desc=True).range(offset, offset + limit - 1).execute()
            
            sessions = []
            for session_data in response.data:
                sessions.append(SessionSummary(**session_data))
            
            return sessions
            
        except Exception as e:
            logger.error(f"Failed to get user sessions for user {user_id}: {str(e)}")
            return []
    
    async def save_anonymous_session(self, session_id: str, user_id: int) -> bool:
        """Convert anonymous session to authenticated user session."""
        try:
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
            
            # Update user stats
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
            
            response = self.supabase.table("messages").select("*").eq("session_id", session_id).order("timestamp", desc=False).limit(limit).execute()
            
            messages = []
            for message_data in response.data:
                messages.append(MessageResponse(**message_data))
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to get messages for session {session_id}: {str(e)}")
            return []
    
    async def update_session_activity(self, session_id: str) -> None:
        """Update session last activity timestamp."""
        try:
            self.supabase.table("sessions").update({
                "last_activity": datetime.utcnow().isoformat()
            }).eq("id", session_id).execute()
            
        except Exception as e:
            logger.error(f"Failed to update session activity {session_id}: {str(e)}")
    
    async def increment_message_count(self, session_id: str) -> None:
        """Increment message count for session."""
        try:
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
                
                # Extract therapeutic goals
                if session_data.get("therapeutic_goals"):
                    context["therapeutic_goals"].extend(session_data["therapeutic_goals"])
                
                # Extract key insights
                if session_data.get("key_insights"):
                    context["recurring_themes"].extend(session_data["key_insights"])
            
            # Remove duplicates and limit
            context["therapeutic_goals"] = list(set(context["therapeutic_goals"]))[:10]
            context["recurring_themes"] = list(set(context["recurring_themes"]))[:10]
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get session context for user {user_id}: {str(e)}")
            return {}
    
    async def cleanup_old_anonymous_sessions(self, hours_old: int = 24) -> int:
        """Clean up old anonymous sessions to save space."""
        try:
            cutoff_time = (datetime.utcnow() - timedelta(hours=hours_old)).isoformat()
            
            # Get old anonymous sessions
            response = self.supabase.table("sessions").select("id").eq("is_anonymous", True).lt("last_activity", cutoff_time).execute()
            
            if not response.data:
                return 0
            
            session_ids = [session["id"] for session in response.data]
            
            # Delete sessions (cascades to messages)
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