"""
backend/database.py — SQLAlchemy SQLite setup for users & history
"""
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, ForeignKey, create_engine
)
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DB_PATH = Path(__file__).parent.parent / "adforge.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ─────────────────────────────────────────────────
# ORM Models
# ─────────────────────────────────────────────────

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    avatar_color = Column(String(16), default="#7c3aed")  # random accent per user


class PredictionHistoryDB(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Input snapshot
    product_description = Column(Text, nullable=False)
    product_category = Column(String(128), nullable=False)
    target_audience = Column(String(256), nullable=True)
    messaging_angle = Column(String(64), nullable=False)

    # Output snapshot (JSON string)
    result_json = Column(Text, nullable=False)

    # Meta
    created_at = Column(DateTime, default=datetime.utcnow)
    pipeline_steps = Column(Integer, default=6)
    rag_patterns = Column(Integer, default=0)
    scraper_results = Column(Integer, default=0)


# ─────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────

def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
