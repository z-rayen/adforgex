"""
backend/routers/auth_router.py — Signup, Login, Profile, and History endpoints
"""
import json
import random
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import UserDB, PredictionHistoryDB, get_db
from backend.auth import hash_password, verify_password, create_access_token, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["auth"])

AVATAR_COLORS = [
    "#7c3aed", "#2563eb", "#db2777", "#16a34a",
    "#d97706", "#0891b2", "#7c3aed", "#be185d",
    "#4f46e5", "#0f766e",
]


# ─────────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────────

class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=32)
    email: str = Field(...)
    password: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class HistoryItem(BaseModel):
    id: int
    product_description: str
    product_category: str
    target_audience: Optional[str]
    messaging_angle: str
    result: dict
    created_at: str
    rag_patterns: int
    scraper_results: int


# ─────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────

@router.post("/signup", response_model=TokenResponse, status_code=201)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    # Check unique
    if db.query(UserDB).filter(UserDB.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(UserDB).filter(UserDB.username == body.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    user = UserDB(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
        avatar_color=random.choice(AVATAR_COLORS),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username)
    logger.info(f"New user registered: {user.username} ({user.email})")

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_color": user.avatar_color,
            "created_at": user.created_at.isoformat(),
        },
    }


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate and receive JWT."""
    user = db.query(UserDB).filter(UserDB.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id, user.username)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "avatar_color": user.avatar_color,
            "created_at": user.created_at.isoformat(),
        },
    }


@router.get("/me")
def me(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user profile + stats."""
    total = db.query(PredictionHistoryDB).filter(
        PredictionHistoryDB.user_id == current_user.id
    ).count()
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "avatar_color": current_user.avatar_color,
        "created_at": current_user.created_at.isoformat(),
        "total_predictions": total,
    }


@router.get("/history", response_model=List[HistoryItem])
def get_history(
    limit: int = 20,
    offset: int = 0,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the authenticated user's prediction history."""
    rows = (
        db.query(PredictionHistoryDB)
        .filter(PredictionHistoryDB.user_id == current_user.id)
        .order_by(PredictionHistoryDB.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [
        HistoryItem(
            id=r.id,
            product_description=r.product_description,
            product_category=r.product_category,
            target_audience=r.target_audience,
            messaging_angle=r.messaging_angle,
            result=json.loads(r.result_json),
            created_at=r.created_at.isoformat(),
            rag_patterns=r.rag_patterns,
            scraper_results=r.scraper_results,
        )
        for r in rows
    ]


@router.delete("/history/{history_id}", status_code=204)
def delete_history_item(
    history_id: int,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a specific history entry."""
    row = db.query(PredictionHistoryDB).filter(
        PredictionHistoryDB.id == history_id,
        PredictionHistoryDB.user_id == current_user.id,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="History item not found")
    db.delete(row)
    db.commit()
