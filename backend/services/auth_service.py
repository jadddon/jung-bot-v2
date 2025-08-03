"""
Authentication service for Jung AI - Supabase Integration
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from supabase import create_client, Client
from config import get_settings
from models.schemas import UserCreate, UserResponse, TokenResponse

logger = logging.getLogger(__name__)

class AuthService:
    """Supabase authentication service for Jung AI."""
    
    def __init__(self):
        self.settings = get_settings()
        self.supabase: Client = create_client(
            self.settings.supabase_url,
            self.settings.supabase_key
        )
        
    async def register_user(self, email: str, password: str, preferred_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user with Supabase Auth."""
        try:
            # Create user in Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": {
                        "preferred_name": preferred_name
                    }
                }
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User registration failed"
                )
            
            # Create user record in our database
            user_data = {
                "id": auth_response.user.id,
                "email": email,
                "full_name": preferred_name,
                "created_at": datetime.utcnow().isoformat()
            }
            
            db_response = self.supabase.table("users").insert(user_data).execute()
            
            logger.info(f"User registered successfully: {email}")
            return {
                "user": auth_response.user,
                "session": auth_response.session,
                "db_user": db_response.data[0] if db_response.data else None
            }
            
        except Exception as e:
            logger.error(f"Registration failed for {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Registration failed: {str(e)}"
            )
    
    async def login_user(self, email: str, password: str) -> TokenResponse:
        """Login user with Supabase Auth."""
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if auth_response.user is None or auth_response.session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials"
                )
            
            # Get user data from our database
            user_response = self.supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
            
            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database"
                )
            
            user_data = user_response.data[0]
            
            logger.info(f"User logged in successfully: {email}")
            return TokenResponse(
                access_token=auth_response.session.access_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in,
                user=UserResponse(
                    id=user_data["id"],
                    email=user_data["email"],
                    preferred_name=user_data.get("full_name"),
                    timezone=user_data.get("timezone", "UTC"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"],
                    total_sessions=user_data.get("total_sessions", 0),
                    total_messages=user_data.get("total_messages", 0)
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Login failed for {email}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
    
    async def logout_user(self, access_token: str) -> bool:
        """Logout user by invalidating session."""
        try:
            # Set the session token
            self.supabase.auth.set_session(access_token, None)
            
            # Sign out
            self.supabase.auth.sign_out()
            
            logger.info("User logged out successfully")
            return True
            
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False
    
    async def get_current_user(self, access_token: str) -> Optional[UserResponse]:
        """Get current user from access token."""
        try:
            # Set the session token
            self.supabase.auth.set_session(access_token, None)
            
            # Get user from Supabase
            user = self.supabase.auth.get_user()
            
            if user.user is None:
                return None
            
            # Get user data from our database
            user_response = self.supabase.table("users").select("*").eq("id", user.user.id).execute()
            
            if not user_response.data:
                # User doesn't exist in our database, create them (for OAuth users)
                await self.create_user_from_auth(user.user)
                # Try again to get user data
                user_response = self.supabase.table("users").select("*").eq("id", user.user.id).execute()
                if not user_response.data:
                    return None
            
            user_data = user_response.data[0]
            
            return UserResponse(
                id=user_data["id"],
                email=user_data["email"],
                preferred_name=user_data.get("full_name"),
                timezone=user_data.get("timezone", "UTC"),
                created_at=user_data["created_at"],
                updated_at=user_data["updated_at"],
                total_sessions=user_data.get("total_sessions", 0),
                total_messages=user_data.get("total_messages", 0)
            )
            
        except Exception as e:
            logger.error(f"Get current user failed: {str(e)}")
            return None
    
    async def create_user_from_auth(self, auth_user) -> None:
        """Create user record from Supabase auth user (for OAuth users)."""
        try:
            # Extract preferred name from user metadata (Google OAuth)
            preferred_name = (
                auth_user.user_metadata.get("preferred_name") or
                auth_user.user_metadata.get("full_name") or
                auth_user.user_metadata.get("name") or
                None
            )
            
            user_data = {
                "id": auth_user.id,
                "email": auth_user.email,
                "full_name": preferred_name,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("users").insert(user_data).execute()
            logger.info(f"Created user record for OAuth user: {auth_user.email}")
            
        except Exception as e:
            logger.error(f"Failed to create user from auth: {str(e)}")
            # Don't raise exception, as the auth user exists
    
    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token."""
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if auth_response.session is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid refresh token"
                )
            
            # Get user data
            user_response = self.supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
            
            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user_data = user_response.data[0]
            
            return TokenResponse(
                access_token=auth_response.session.access_token,
                token_type="bearer",
                expires_in=auth_response.session.expires_in,
                user=UserResponse(
                    id=user_data["id"],
                    email=user_data["email"],
                    preferred_name=user_data.get("full_name"),
                    timezone=user_data.get("timezone", "UTC"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"],
                    total_sessions=user_data.get("total_sessions", 0),
                    total_messages=user_data.get("total_messages", 0)
                )
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token refresh failed"
            )
    
    async def update_user_stats(self, user_id: int, new_session: bool = False, new_message: bool = False) -> None:
        """Update user statistics."""
        try:
            updates = {}
            
            if new_session:
                # Increment session count
                current_user = self.supabase.table("users").select("total_sessions").eq("id", user_id).execute()
                if current_user.data:
                    updates["total_sessions"] = current_user.data[0]["total_sessions"] + 1
            
            if new_message:
                # Increment message count
                current_user = self.supabase.table("users").select("total_messages").eq("id", user_id).execute()
                if current_user.data:
                    updates["total_messages"] = current_user.data[0]["total_messages"] + 1
            
            if updates:
                updates["updated_at"] = datetime.utcnow().isoformat()
                self.supabase.table("users").update(updates).eq("id", user_id).execute()
                
        except Exception as e:
            logger.error(f"Failed to update user stats: {str(e)}")
    
    async def verify_session_access(self, user_id: int, session_id: str) -> bool:
        """Verify user has access to session."""
        try:
            session_response = self.supabase.table("sessions").select("user_id, is_anonymous").eq("id", session_id).execute()
            
            if not session_response.data:
                return False
            
            session_data = session_response.data[0]
            
            # Anonymous sessions are accessible to anyone
            if session_data["is_anonymous"]:
                return True
            
            # User sessions are only accessible to the owner
            return session_data["user_id"] == user_id
            
        except Exception as e:
            logger.error(f"Session access verification failed: {str(e)}")
            return False

# Global auth service instance
auth_service = AuthService() 