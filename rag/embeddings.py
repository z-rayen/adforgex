"""
rag/embeddings.py — Sentence-transformer embedding wrapper

Wraps HuggingFace sentence-transformers for generating
embeddings used in ChromaDB vector similarity search.
"""
import logging
from typing import List, Union
import numpy as np

logger = logging.getLogger(__name__)

_model_instance = None


def get_embedding_model(model_name: str = "all-MiniLM-L6-v2"):
    """
    Lazy singleton for the embedding model.
    Downloads on first call (~80MB for all-MiniLM-L6-v2).
    """
    global _model_instance
    if _model_instance is None:
        logger.info(f"Loading embedding model: {model_name}")
        from sentence_transformers import SentenceTransformer
        _model_instance = SentenceTransformer(model_name)
        logger.info("Embedding model loaded")
    return _model_instance


def embed_texts(texts: Union[str, List[str]], model_name: str = "all-MiniLM-L6-v2") -> List[List[float]]:
    """
    Embed one or more texts.

    Args:
        texts: Single string or list of strings
        model_name: Sentence transformer model to use

    Returns:
        List of embedding vectors (list of floats)
    """
    if isinstance(texts, str):
        texts = [texts]

    model = get_embedding_model(model_name)
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

    return embeddings.tolist()


def embed_query(query: str, model_name: str = "all-MiniLM-L6-v2") -> List[float]:
    """Embed a single query string. Returns a flat vector."""
    return embed_texts([query], model_name)[0]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))
