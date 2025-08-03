"""
Database models for Jung AI Analysis System - Supabase Optimized
"""

from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from uuid import uuid4
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session as SQLSession
from sqlalchemy.dialects.postgresql import UUID
import json

Base = declarative_base()

class User(Base):
    """User model for authenticated users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # User preferences and settings
    full_name = Column(String, nullable=True)
    timezone = Column(String, default="UTC")
    
    # Usage tracking
    total_sessions = Column(Integer, default=0)
    total_messages = Column(Integer, default=0)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"

class Session(Base):
    """Session model for both anonymous and authenticated sessions."""
    
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # NULL for anonymous
    
    # Session metadata
    title = Column(String, nullable=False, default="New Jung Analysis Session")
    is_anonymous = Column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Session state
    is_active = Column(Boolean, default=True, nullable=False)
    session_type = Column(String, default="general", nullable=False)  # general, dream_analysis, etc.
    
    # AI context and summary
    context_summary = Column(Text, nullable=True)  # AI-generated session summary
    therapeutic_goals = Column(JSON, nullable=True)  # List of therapeutic goals
    key_insights = Column(JSON, nullable=True)  # Key insights from the session
    
    # Session statistics
    message_count = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_session_user_created', 'user_id', 'created_at'),
        Index('idx_session_anonymous_created', 'is_anonymous', 'created_at'),
        Index('idx_session_active', 'is_active', 'last_activity'),
    )
    
    def __repr__(self):
        return f"<Session(id={self.id}, title={self.title}, anonymous={self.is_anonymous})>"

class Message(Base):
    """Message model for chat messages in sessions."""
    
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)
    
    # Message content
    role = Column(String, nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Jung analysis metadata
    sources = Column(JSON, nullable=True)  # Jung text sources used
    analysis_type = Column(String, nullable=True)  # dream_analysis, shadow_work, etc.
    therapeutic_techniques = Column(JSON, nullable=True)  # List of techniques used
    
    # Response metadata (for assistant messages)
    model_used = Column(String, nullable=True)  # OpenAI model used
    tokens_used = Column(Integer, nullable=True)  # Token count
    response_time_ms = Column(Integer, nullable=True)  # Response time
    cost_usd = Column(String, nullable=True)  # Cost in USD (stored as string for precision)
    
    # Quality metrics
    relevance_score = Column(String, nullable=True)  # Relevance score (0-1)
    therapeutic_value = Column(String, nullable=True)  # Therapeutic value score
    
    # Relationships
    session = relationship("Session", back_populates="messages")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_message_session_timestamp', 'session_id', 'timestamp'),
        Index('idx_message_role_timestamp', 'role', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<Message(id={self.id}, session_id={self.session_id}, role={self.role})>"

class SessionContext(Base):
    """Extended context for sessions to support therapeutic continuity."""
    
    __tablename__ = "session_contexts"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, unique=True, index=True)
    
    # Therapeutic context
    recurring_themes = Column(JSON, nullable=True)  # List of recurring themes
    emotional_patterns = Column(JSON, nullable=True)  # Emotional patterns observed
    therapeutic_progress = Column(JSON, nullable=True)  # Progress tracking
    
    # Jung-specific context
    archetypal_patterns = Column(JSON, nullable=True)  # Archetypal patterns identified
    shadow_work_progress = Column(JSON, nullable=True)  # Shadow work progress
    individuation_stage = Column(String, nullable=True)  # Current individuation stage
    
    # Session relationships (for cross-session context)
    related_sessions = Column(JSON, nullable=True)  # List of related session IDs
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<SessionContext(id={self.id}, session_id={self.session_id})>"

# Database utility functions for Railway optimization
def create_indexes(engine):
    """Create additional indexes for performance optimization."""
    with engine.connect() as conn:
        # Additional indexes for common queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_user_active 
            ON sessions(user_id, is_active, last_activity);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_messages_session_recent 
            ON messages(session_id, timestamp DESC);
        """)
        
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_sessions_cleanup 
            ON sessions(is_anonymous, last_activity) 
            WHERE is_anonymous = true;
        """)

def optimize_for_railway():
    """Database optimization settings for Railway's constraints."""
    return {
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "pool_recycle": 1800,  # 30 minutes
        "pool_pre_ping": True,
        "echo": False,  # Disable SQL logging in production
    }

# Supabase Row Level Security (RLS) policies
RLS_POLICIES = {
    "users": {
        "select": "auth.uid()::text = id::text",
        "insert": "auth.uid()::text = id::text",
        "update": "auth.uid()::text = id::text",
        "delete": "auth.uid()::text = id::text",
    },
    "sessions": {
        "select": "user_id IS NULL OR user_id = auth.uid()",
        "insert": "user_id IS NULL OR user_id = auth.uid()",
        "update": "user_id IS NULL OR user_id = auth.uid()",
        "delete": "user_id IS NULL OR user_id = auth.uid()",
    },
    "messages": {
        "select": "session_id IN (SELECT id FROM sessions WHERE user_id IS NULL OR user_id = auth.uid())",
        "insert": "session_id IN (SELECT id FROM sessions WHERE user_id IS NULL OR user_id = auth.uid())",
        "update": "session_id IN (SELECT id FROM sessions WHERE user_id IS NULL OR user_id = auth.uid())",
        "delete": "session_id IN (SELECT id FROM sessions WHERE user_id IS NULL OR user_id = auth.uid())",
    }
}

# Cleanup utilities for anonymous sessions
def cleanup_anonymous_sessions(db: SQLSession, hours_old: int = 24):
    """Clean up old anonymous sessions to save space."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_old)
    
    old_sessions = db.query(Session).filter(
        Session.is_anonymous == True,
        Session.last_activity < cutoff_time
    ).all()
    
    for session in old_sessions:
        db.delete(session)
    
    db.commit()
    return len(old_sessions)

def compress_old_sessions(db: SQLSession, days_old: int = 30):
    """Compress old session data to save space."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days_old)
    
    old_sessions = db.query(Session).filter(
        Session.created_at < cutoff_time,
        Session.context_summary.is_(None)
    ).all()
    
    compressed_count = 0
    for session in old_sessions:
        # Generate compressed summary of messages
        messages = db.query(Message).filter(Message.session_id == session.id).all()
        if messages:
            summary = generate_session_summary(messages)
            session.context_summary = summary
            compressed_count += 1
    
    db.commit()
    return compressed_count

def generate_session_summary(messages: List[Message]) -> str:
    """Generate a compressed summary of session messages."""
    # Simple summary generation - in production, this would use AI
    user_messages = [msg.content for msg in messages if msg.role == "user"]
    assistant_messages = [msg.content for msg in messages if msg.role == "assistant"]
    
    summary = {
        "message_count": len(messages),
        "user_topics": user_messages[:3],  # First 3 user messages
        "key_insights": assistant_messages[:2],  # First 2 assistant responses
        "session_type": "general",  # Would be determined by analysis
    }
    
    return json.dumps(summary, default=str) 