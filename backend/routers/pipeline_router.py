"""
backend/routers/pipeline_router.py — Pipeline API endpoints
"""
import json
import logging
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.models import AdGenerationRequest, AdGenerationResponse
from backend.pipeline import AdGenerationPipeline
from backend.database import PredictionHistoryDB, get_db
from backend.auth import get_optional_user
from backend.database import UserDB

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def get_pipeline(request: Request) -> AdGenerationPipeline:
    return request.app.state.pipeline


@router.post("/generate", response_model=AdGenerationResponse, summary="Generate ad (blocking)")
async def generate_ad(
    body: AdGenerationRequest,
    api_key: Optional[str] = None,
    pipeline: AdGenerationPipeline = Depends(get_pipeline),
):
    """
    Run the full 6-step pipeline and return the complete result.
    Blocks until all steps are done (~15-30s depending on scraping).
    """
    try:
        result = await pipeline.run(body, api_key=api_key)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Pipeline failed")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.post("/generate/stream", summary="Generate ad with SSE streaming")
async def generate_ad_stream(
    body: AdGenerationRequest,
    api_key: Optional[str] = None,
    pipeline: AdGenerationPipeline = Depends(get_pipeline),
    current_user: Optional[UserDB] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Run the pipeline with real-time Server-Sent Events (SSE) streaming.
    Each pipeline step emits a status update as it completes.

    Connect with EventSource in the browser or any SSE client.

    Event format:
        data: {"type": "step", "step": 1, "status": "done", "message": "..."}
        data: {"type": "complete", "result": {...}}
    """
    async def event_generator():
        final_result = None
        try:
            async for event in pipeline.run_streaming(body, api_key=api_key):
                if event.get("type") == "complete" and event.get("result"):
                    final_result = event["result"]
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:
            logger.exception("Stream pipeline failed")
            error_event = {"type": "error", "message": str(e)}
            yield f"data: {json.dumps(error_event)}\n\n"
        finally:
            # Save to history if user is authenticated and pipeline succeeded
            if current_user and final_result:
                try:
                    entry = PredictionHistoryDB(
                        user_id=current_user.id,
                        product_description=body.product_description,
                        product_category=body.product_category,
                        target_audience=body.target_audience,
                        messaging_angle=body.messaging_angle,
                        result_json=json.dumps(final_result),
                        rag_patterns=final_result.get("rag_patterns_found", 0),
                        scraper_results=final_result.get("scraper_results_found", 0),
                    )
                    db.add(entry)
                    db.commit()
                    logger.info(f"Saved prediction to history for user {current_user.username}")
                except Exception as save_err:
                    logger.warning(f"Failed to save history: {save_err}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
