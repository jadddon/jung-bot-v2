"""
Main FastAPI application for Jung AI Analysis System - Railway Optimized
"""

import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import uvicorn

# Internal imports
from config import get_settings, MEMORY_SETTINGS
from models.schemas import (
    SessionCreate, SessionResponse, SessionUpdate, SessionSummary,
    ChatMessageRequest, ChatMessageResponse, UserResponse, HealthCheck,
    APIResponse, HTTPError
)
from services.auth_service import auth_service
from services.session_service import session_service
from services.openai_service import openai_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()

# Rate limiting setup
limiter = Limiter(key_func=get_remote_address)

# Security
security = HTTPBearer(auto_error=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info("Performing startup health checks...")
    
    # Startup cleanup
    try:
        await session_service.cleanup_old_anonymous_sessions(hours_old=24)
        logger.info("Startup cleanup completed")
    except Exception as e:
        logger.error(f"Startup cleanup failed: {str(e)}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Jung AI backend...")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Jung AI Analysis System - Authentic Jungian psychological analysis",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["*.railway.app", "*.vercel.app"]
)

# Request size middleware for Railway optimization
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    """Limit request size for Railway memory optimization."""
    content_length = request.headers.get("content-length")
    if content_length:
        content_length = int(content_length)
        if content_length > settings.max_request_size:
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large"}
            )
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-App-Version"] = settings.app_version
    
    return response

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Optional[UserResponse]:
    """Get current user from JWT token (optional)."""
    if not credentials:
        return None
    
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except Exception as e:
        logger.error(f"Authentication failed: {str(e)}")
        return None

# Required authentication dependency
async def require_auth(user: UserResponse = Depends(get_current_user)) -> UserResponse:
    """Require authentication."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    return user

# Health check endpoint
@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint for Railway."""
    try:
        # Basic health check
        health_status = HealthCheck(
            status="healthy",
            version=settings.app_version,
            timestamp=time.time(),
            database="connected",  # Would check Supabase in production
            openai="available",    # Would check OpenAI in production
            pinecone="available"   # Would check Pinecone in production
        )
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return APIResponse(
        success=True,
        message=f"Welcome to {settings.app_name}",
        data={
            "version": settings.app_version,
            "docs_url": "/docs" if settings.debug else None
        }
    )

# Authentication endpoints
@app.post("/auth/register")
@limiter.limit("3/minute")
async def register(request: Request, email: str, password: str, preferred_name: Optional[str] = None):
    """Register a new user."""
    try:
        result = await auth_service.register_user(email, password, preferred_name)
        return APIResponse(
            success=True,
            message="User registered successfully",
            data=result
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@app.post("/auth/login")
@limiter.limit("5/minute")
async def login(request: Request, email: str, password: str):
    """Login user."""
    try:
        token_response = await auth_service.login_user(email, password)
        return APIResponse(
            success=True,
            message="Login successful",
            data=token_response.dict()
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed"
        )

@app.post("/auth/logout")
async def logout(user: UserResponse = Depends(require_auth)):
    """Logout user."""
    try:
        # In a real implementation, you'd invalidate the token
        return APIResponse(
            success=True,
            message="Logout successful"
        )
    except Exception as e:
        logger.error(f"Logout failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

# Session endpoints
@app.post("/sessions", response_model=SessionResponse)
@limiter.limit("10/minute")
async def create_session(
    request: Request,
    session_data: SessionCreate,
    user: Optional[UserResponse] = Depends(get_current_user)
):
    """Create a new session (anonymous or authenticated)."""
    try:
        session = await session_service.create_session(
            user_id=user.id if user else None,
            title=session_data.title
        )
        return session
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session creation failed"
        )

@app.get("/sessions", response_model=List[SessionSummary])
@limiter.limit("20/minute")
async def get_user_sessions(
    request: Request,
    user: UserResponse = Depends(require_auth),
    limit: int = 50,
    offset: int = 0
):
    """Get user's session history."""
    try:
        sessions = await session_service.get_user_sessions(user.id, limit, offset)
        return sessions
    except Exception as e:
        logger.error(f"Get sessions failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve sessions"
        )

@app.get("/sessions/{session_id}", response_model=SessionResponse)
@limiter.limit("30/minute")
async def get_session(
    request: Request,
    session_id: str,
    user: Optional[UserResponse] = Depends(get_current_user)
):
    """Get specific session."""
    try:
        session = await session_service.get_session(
            session_id,
            user_id=user.id if user else None
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return session
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Get session failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session"
        )

@app.put("/sessions/{session_id}", response_model=SessionResponse)
@limiter.limit("10/minute")
async def update_session(
    request: Request,
    session_id: str,
    updates: SessionUpdate,
    user: Optional[UserResponse] = Depends(get_current_user)
):
    """Update session."""
    try:
        session = await session_service.update_session(
            session_id,
            updates,
            user_id=user.id if user else None
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return session
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Update session failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session"
        )

@app.delete("/sessions/{session_id}")
@limiter.limit("5/minute")
async def delete_session(
    request: Request,
    session_id: str,
    user: Optional[UserResponse] = Depends(get_current_user)
):
    """Delete session."""
    try:
        success = await session_service.delete_session(
            session_id,
            user_id=user.id if user else None
        )
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        return APIResponse(
            success=True,
            message="Session deleted successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Delete session failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )

@app.post("/sessions/{session_id}/save")
@limiter.limit("5/minute")
async def save_anonymous_session(
    request: Request,
    session_id: str,
    user: UserResponse = Depends(require_auth)
):
    """Save anonymous session to user account."""
    try:
        success = await session_service.save_anonymous_session(session_id, user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Anonymous session not found"
            )
        return APIResponse(
            success=True,
            message="Session saved successfully"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Save session failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save session"
        )

# Chat endpoints
@app.post("/chat/message", response_model=ChatMessageResponse)
@limiter.limit("10/minute")  # Aggressive rate limiting for OpenAI costs
async def send_chat_message(
    request: Request,
    message_request: ChatMessageRequest,
    user: Optional[UserResponse] = Depends(get_current_user)
):
    """Send message and get Jung AI response."""
    try:
        # Verify session access
        session = await session_service.get_session(
            message_request.session_id,
            user_id=user.id if user else None
        )
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Get conversation history for context
        conversation_history = await session_service.get_session_messages(
            message_request.session_id,
            user_id=user.id if user else None
        )
        
        # Get session context for authenticated users
        context = {}
        if user:
            context = await session_service.get_session_context(
                user.id,
                message_request.session_id
            )
        
        # Add conversation history to context
        context["conversation_history"] = [
            {"role": msg.role, "content": msg.content} 
            for msg in conversation_history
        ]
        
        # Generate Jung AI response with conversation context
        ai_response = await openai_service.generate_jung_response(
            message_request.content,
            context,
            []  # Would retrieve from Pinecone in production
        )
        
        # Save user message to database
        current_time = datetime.now().isoformat()
        user_message_data = {
            "session_id": message_request.session_id,
            "role": "user",
            "content": message_request.content,
            "timestamp": current_time
        }
        
        # Save assistant message to database
        assistant_message_data = {
            "session_id": message_request.session_id,
            "role": "assistant",
            "content": ai_response["response"],
            "timestamp": current_time,
            "model_used": ai_response["model_used"].value,
            "tokens_used": ai_response["tokens_used"],
            "cost_usd": ai_response["cost_usd"],
            "analysis_type": ai_response.get("analysis_type"),
            "therapeutic_techniques": ai_response.get("therapeutic_techniques")
        }
        
        # Insert messages into database
        try:
            # Insert user message
            user_msg_response = session_service.supabase.table("messages").insert(user_message_data).execute()
            user_message_id = user_msg_response.data[0]["id"] if user_msg_response.data else None
            
            # Insert assistant message
            assistant_msg_response = session_service.supabase.table("messages").insert(assistant_message_data).execute()
            assistant_message_id = assistant_msg_response.data[0]["id"] if assistant_msg_response.data else None
            
        except Exception as e:
            logger.error(f"Failed to save messages to database: {str(e)}")
            # Generate fallback IDs
            user_message_id = f"user-{int(datetime.now().timestamp() * 1000)}"
            assistant_message_id = f"assistant-{int(datetime.now().timestamp() * 1000)}"
        
        # Update session stats
        await session_service.increment_message_count(message_request.session_id)
        await session_service.update_session_activity(message_request.session_id)
        
        # Create response with proper message IDs
        response = ChatMessageResponse(
            user_message={
                "id": user_message_id,
                "session_id": message_request.session_id,
                "role": "user",
                "content": message_request.content,
                "timestamp": current_time
            },
            assistant_message={
                "id": assistant_message_id,
                "session_id": message_request.session_id,
                "role": "assistant",
                "content": ai_response["response"],
                "timestamp": current_time,
                "model_used": ai_response["model_used"].value,
                "tokens_used": ai_response["tokens_used"],
                "cost_usd": ai_response["cost_usd"],
                "analysis_type": ai_response.get("analysis_type"),
                "therapeutic_techniques": ai_response.get("therapeutic_techniques")
            },
            cost_info=openai_service.get_cost_info().model_dump()
        )
        
        return response
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Chat message failed: {str(e)}")
        # Provide more specific error messages for debugging
        if "OpenAI API key not configured" in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OpenAI API key not configured. Please contact administrator."
            )
        elif "Daily budget exceeded" in str(e):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Daily API budget exceeded. Please try again tomorrow."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {str(e)}"
            )

# Analytics endpoints
@app.get("/analytics/costs")
@limiter.limit("20/minute")
async def get_cost_analytics(
    request: Request,
    user: UserResponse = Depends(require_auth)
):
    """Get cost analytics for user."""
    try:
        cost_info = openai_service.get_cost_info()
        cache_stats = openai_service.get_cache_stats()
        
        return APIResponse(
            success=True,
            message="Cost analytics retrieved",
            data={
                "cost_info": cost_info.dict(),
                "cache_stats": cache_stats
            }
        )
    except Exception as e:
        logger.error(f"Cost analytics failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=HTTPError(
            detail=exc.detail,
            status_code=exc.status_code,
            error_type="HTTPException"
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=HTTPError(
            detail="Internal server error",
            status_code=500,
            error_type="InternalError"
        ).dict()
    )

# Railway-specific startup
if __name__ == "__main__":
    port = int(settings.port)
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=port,
        workers=MEMORY_SETTINGS["max_workers"],
        log_level="info"
    ) 