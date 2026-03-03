from sqlalchemy import (Column, String, Float, Integer, DateTime, func)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
import uuid

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/jodi")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ConversationStateDB(Base):
    __tablename__ = "conversation_state"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    session_id = Column(String, nullable=False, unique=True)
    state_json = Column(JSONB, nullable=False, default={})
    completion_map = Column(JSONB, nullable=False, default={})
    confidence_map = Column(JSONB, nullable=False, default={})
    progress_pct = Column(Float, nullable=False, default=0.0)
    priority_tier = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# helper functions
def get_state_by_session(db, session_id: str):
    return db.query(ConversationStateDB).filter(ConversationStateDB.session_id == session_id).first()

def create_or_update_state(db, user_id, session_id, state_json, confidence):
    obj = get_state_by_session(db, session_id)
    if not obj:
        obj = ConversationStateDB(user_id=user_id, session_id=session_id, state_json=state_json, confidence_map={"last": confidence})
        db.add(obj)
    else:
        obj.state_json = state_json
        obj.confidence_map = {**(obj.confidence_map or {}), "last": confidence}
    # naive progress calculation
    obj.progress_pct = float(confidence * 100)
    db.commit()
    db.refresh(obj)
    return obj

def advance_state(db, session_id: str):
    obj = get_state_by_session(db, session_id)
    if not obj:
        return None
    obj.progress_pct = min(100.0, (obj.progress_pct or 0.0) + 10.0)
    db.commit()
    db.refresh(obj)
    return obj
