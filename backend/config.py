"""
backend/config.py — Centralized settings using pydantic-settings
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # API Keys
    groq_api_key: str = ""

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False

    # RAG
    chroma_db_path: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    rag_collection_name: str = "ad_patterns"
    rag_top_k: int = 5

    # Scraper
    scrape_timeout: int = 15
    max_images_per_product: int = 5
    headless: bool = True

    # Groq Models
    text_model: str = "llama-3.3-70b-versatile"
    vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    max_tokens_text: int = 2000
    max_tokens_vision: int = 1500

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
