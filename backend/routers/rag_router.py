"""
backend/routers/rag_router.py — RAG knowledge base management endpoints
"""
import logging
from fastapi import APIRouter, Request, HTTPException, Depends
from typing import List, Optional

from backend.models import RAGIngestRequest, RAGIngestResponse
from rag.rag_engine import RAGEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["rag"])


def get_rag(request: Request) -> RAGEngine:
    return request.app.state.rag_engine


@router.post("/ingest", response_model=RAGIngestResponse)
async def ingest_ad_pattern(
    body: RAGIngestRequest,
    rag: RAGEngine = Depends(get_rag),
):
    """
    Add a new ad pattern to the RAG knowledge base.

    Use this to continuously improve the knowledge base with
    ad patterns that performed well in production.
    """
    try:
        doc_id = rag.add_ad_pattern(
            category=body.product_category,
            caption=body.caption,
            hook=body.hook,
            visual_description=body.visual_description,
            pain_points=body.pain_points,
            performance_score=body.performance_score,
            notes=body.notes,
        )
        return RAGIngestResponse(
            success=True,
            document_id=doc_id,
            message=f"Pattern added to knowledge base (ID: {doc_id})",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search")
async def search_patterns(
    query: str,
    top_k: int = 5,
    category: Optional[str] = None,
    rag: RAGEngine = Depends(get_rag),
):
    """Search the RAG knowledge base for similar ad patterns."""
    try:
        results = rag.search(query=query, top_k=top_k, category_filter=category)
        return {"query": query, "results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def rag_stats(rag: RAGEngine = Depends(get_rag)):
    """Return statistics about the RAG knowledge base."""
    count = rag.count()
    return {
        "total_documents": count,
        "status": "ready" if count > 0 else "empty — run seed_data.py",
    }


@router.post("/bulk-ingest")
async def bulk_ingest(
    patterns: List[RAGIngestRequest],
    rag: RAGEngine = Depends(get_rag),
):
    """Bulk ingest multiple ad patterns at once."""
    try:
        items = [p.model_dump() for p in patterns]
        ids = rag.bulk_add(items)
        return {"success": True, "inserted": len(ids), "ids": ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/document/{doc_id}")
async def delete_document(doc_id: str, rag: RAGEngine = Depends(get_rag)):
    """Delete a document from the knowledge base by ID."""
    success = rag.delete(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"success": True, "deleted": doc_id}


@router.get("/all")
async def list_all(limit: int = 50, rag: RAGEngine = Depends(get_rag)):
    """List all documents in the RAG knowledge base."""
    docs = rag.get_all(limit=limit)
    return {"documents": docs, "count": len(docs)}
