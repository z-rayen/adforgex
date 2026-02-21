"""
backend/models.py — All Pydantic request/response models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class MessagingAngle(str, Enum):
    AUTO = "auto"
    PROBLEM_SOLUTION = "problem-solution"
    LUXURY = "luxury"
    UGC = "ugc"
    FEAR = "fear"
    SOCIAL_PROOF = "social-proof"
    DISCOUNT = "discount"
    LIFESTYLE = "lifestyle"


# ──────────────────────────────────────────────
# REQUEST
# ──────────────────────────────────────────────

class AdGenerationRequest(BaseModel):
    product_description: str = Field(..., min_length=10, description="Full product description")
    product_category: str = Field(..., min_length=2, description="Product type/category")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    messaging_angle: MessagingAngle = Field(MessagingAngle.AUTO, description="Preferred ad angle")
    competitor_images_b64: Optional[List[str]] = Field(
        default=None,
        description="Base64-encoded competitor ad images"
    )
    image_mime_types: Optional[List[str]] = Field(
        default=None,
        description="MIME types for each image (image/jpeg, image/png, etc.)"
    )
    scrape_competitors: bool = Field(
        default=True,
        description="Whether to scrape competitor ads from the web"
    )
    use_rag: bool = Field(
        default=True,
        description="Whether to use RAG for knowledge retrieval"
    )


class RAGIngestRequest(BaseModel):
    product_category: str
    caption: str
    hook: str
    visual_description: str
    pain_points: List[str]
    performance_score: float = Field(ge=0.0, le=10.0, description="0-10 performance score")
    notes: Optional[str] = None


# ──────────────────────────────────────────────
# RESPONSE
# ──────────────────────────────────────────────

class UserInsights(BaseModel):
    pain_points: List[str]
    questions: List[str]
    desired_features: List[str]
    use_cases: List[str]


class AdGenerationResponse(BaseModel):
    hook: str
    caption: str
    cta: str
    visual_recommendations: List[str]
    user_insights: UserInsights
    strategy: str

    # Pipeline metadata
    rag_patterns_found: int = 0
    scraper_results_found: int = 0
    images_analyzed: int = 0
    pipeline_steps_completed: List[str] = []


class PipelineStatusUpdate(BaseModel):
    step: int
    step_name: str
    status: str  # "running" | "done" | "skipped" | "error"
    message: str


class RAGIngestResponse(BaseModel):
    success: bool
    document_id: str
    message: str


class HealthResponse(BaseModel):
    status: str
    rag_ready: bool
    groq_key_set: bool
