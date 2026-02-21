"""
rag/rag_engine.py — RAG (Retrieval-Augmented Generation) engine

Uses ChromaDB as the vector database to store and retrieve
historical ad patterns, best-performing captions, and user insights.

Collections:
  - "ad_patterns": Stores past ad data indexed by product category
"""
import uuid
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime

import chromadb
from chromadb.config import Settings as ChromaSettings

from rag.embeddings import embed_texts, embed_query

logger = logging.getLogger(__name__)

COLLECTION_NAME = "ad_patterns"


class RAGEngine:
    """
    ChromaDB-backed RAG engine for ad pattern retrieval.

    Usage:
        engine = RAGEngine(db_path="./chroma_db")
        await engine.initialize()

        # Ingest a past ad
        doc_id = engine.add_ad_pattern(
            category="Travel Gadgets",
            caption="Stop drinking sketchy water...",
            hook="Your water filter is lying to you.",
            visual_description="Lifestyle shot: hiker filling bottle from river",
            pain_points=["contaminated water", "heavy filters"],
            performance_score=8.5,
        )

        # Retrieve similar patterns
        results = engine.search(query="UV water purifier for travel", top_k=5)
    """

    def __init__(self, db_path: str = "./chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model = embedding_model
        self._client: Optional[chromadb.Client] = None
        self._collection = None

    # ─────────────────────────────────────────────────
    # Init
    # ─────────────────────────────────────────────────

    def initialize(self) -> None:
        """Initialize ChromaDB client and collection. Call once at startup."""
        logger.info(f"Initializing ChromaDB at: {self.db_path}")
        self._client = chromadb.PersistentClient(
            path=self.db_path,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        count = self._collection.count()
        logger.info(f"RAG engine initialized — {count} documents in collection")

    def _ensure_ready(self):
        if self._collection is None:
            raise RuntimeError("RAGEngine not initialized. Call .initialize() first.")

    # ─────────────────────────────────────────────────
    # Ingestion
    # ─────────────────────────────────────────────────

    def add_ad_pattern(
        self,
        category: str,
        caption: str,
        hook: str,
        visual_description: str,
        pain_points: List[str],
        performance_score: float = 5.0,
        notes: Optional[str] = None,
        doc_id: Optional[str] = None,
    ) -> str:
        """
        Add an ad pattern to the knowledge base.

        The document text is a rich combination of all fields to
        maximize semantic match quality.

        Returns:
            The document ID (use for updates/deletes)
        """
        self._ensure_ready()

        doc_id = doc_id or str(uuid.uuid4())

        # Build the semantic document from all fields
        document_text = f"""
Category: {category}
Hook: {hook}
Caption: {caption}
Visual: {visual_description}
Pain Points Addressed: {', '.join(pain_points)}
Notes: {notes or ''}
        """.strip()

        metadata = {
            "category": category.lower(),
            "hook": hook,
            "visual_description": visual_description,
            "pain_points": " | ".join(pain_points),
            "performance_score": float(performance_score),
            "created_at": datetime.utcnow().isoformat(),
            "notes": notes or "",
        }

        # Embed using sentence transformers
        embeddings = embed_texts([document_text], model_name=self.embedding_model)

        self._collection.upsert(
            ids=[doc_id],
            documents=[document_text],
            embeddings=embeddings,
            metadatas=[metadata],
        )

        logger.info(f"RAG: Added document {doc_id} for category '{category}'")
        return doc_id

    def bulk_add(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Add multiple patterns at once (more efficient than one-by-one)."""
        self._ensure_ready()

        ids, documents, metadatas_list, embeddings_list = [], [], [], []

        for p in patterns:
            doc_id = p.get("id") or str(uuid.uuid4())
            document_text = f"""
Category: {p['category']}
Hook: {p['hook']}
Caption: {p['caption']}
Visual: {p.get('visual_description', '')}
Pain Points: {', '.join(p.get('pain_points', []))}
Notes: {p.get('notes', '')}
            """.strip()

            ids.append(doc_id)
            documents.append(document_text)
            metadatas_list.append({
                "category": p["category"].lower(),
                "hook": p["hook"],
                "visual_description": p.get("visual_description", ""),
                "pain_points": " | ".join(p.get("pain_points", [])),
                "performance_score": float(p.get("performance_score", 5.0)),
                "created_at": datetime.utcnow().isoformat(),
                "notes": p.get("notes", ""),
            })

        if documents:
            all_embeddings = embed_texts(documents, model_name=self.embedding_model)
            self._collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=all_embeddings,
                metadatas=metadatas_list,
            )
            logger.info(f"RAG: Bulk added {len(ids)} documents")

        return ids

    # ─────────────────────────────────────────────────
    # Retrieval
    # ─────────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for similar ad patterns.

        Args:
            query: Natural language query (e.g. "UV water purifier travel")
            top_k: Number of results to return
            category_filter: Optional: filter to a specific category
            min_score: Minimum similarity score (0-1) to include

        Returns:
            List of matching patterns with similarity scores
        """
        self._ensure_ready()

        if self._collection.count() == 0:
            logger.warning("RAG: Knowledge base is empty, no patterns to retrieve")
            return []

        query_embedding = embed_query(query, model_name=self.embedding_model)

        where_filter = None
        if category_filter:
            where_filter = {"category": {"$eq": category_filter.lower()}}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self._collection.count()),
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )

        patterns = []
        for i, (doc, meta, dist) in enumerate(zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )):
            # ChromaDB cosine distance: 0 = identical, 2 = opposite
            # Convert to similarity score 0-1
            similarity = 1.0 - (dist / 2.0)

            if similarity < min_score:
                continue

            patterns.append({
                "rank": i + 1,
                "similarity_score": round(similarity, 4),
                "document": doc,
                "category": meta.get("category"),
                "hook": meta.get("hook"),
                "visual_description": meta.get("visual_description"),
                "pain_points": meta.get("pain_points", "").split(" | "),
                "performance_score": meta.get("performance_score"),
                "notes": meta.get("notes"),
            })

        logger.info(f"RAG: Found {len(patterns)} patterns for query: '{query[:60]}'")
        return patterns

    def search_by_category(self, category: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get top patterns for a specific product category."""
        return self.search(
            query=f"best performing ads for {category}",
            top_k=top_k,
            category_filter=category,
        )

    # ─────────────────────────────────────────────────
    # Management
    # ─────────────────────────────────────────────────

    def delete(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        self._ensure_ready()
        try:
            self._collection.delete(ids=[doc_id])
            return True
        except Exception as e:
            logger.error(f"RAG: Delete failed for {doc_id}: {e}")
            return False

    def count(self) -> int:
        """Return total number of documents in the collection."""
        self._ensure_ready()
        return self._collection.count()

    def get_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return all documents (for inspection/debugging)."""
        self._ensure_ready()
        results = self._collection.get(limit=limit, include=["documents", "metadatas"])
        return [
            {"document": doc, **meta}
            for doc, meta in zip(results["documents"], results["metadatas"])
        ]

    def reset_collection(self) -> None:
        """⚠️ Delete all documents in the collection."""
        self._ensure_ready()
        self._client.delete_collection(COLLECTION_NAME)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        logger.warning("RAG: Collection reset — all data deleted")
