"""
rag/seed_data.py — Seed the knowledge base with real social media ad patterns

Run once to populate ChromaDB before using the pipeline:
    python rag/seed_data.py

Loads data from training_dataset_with_sentiment.csv containing real Instagram posts.
"""
import sys
import os
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rag.rag_engine import RAGEngine

# ─────────────────────────────────────────────────────────────────────────────
# CSV DATA LOADING AND TRANSFORMATION
# ─────────────────────────────────────────────────────────────────────────────

def extract_hook_from_caption(caption: str, max_length: int = 80) -> str:
    """Extract the first compelling line from the caption as the hook."""
    if pd.isna(caption) or not caption:
        return "Premium product"
    
    # Split by newline or period
    lines = caption.replace('\n', '. ').split('. ')
    first_line = lines[0].strip()
    
    # If too long, take first part
    if len(first_line) > max_length:
        first_line = first_line[:max_length].rsplit(' ', 1)[0] + '...'
    
    return first_line if first_line else "Check this out"


def load_patterns_from_csv(csv_path: str = "rag/training_dataset_with_sentiment.csv", limit: int = None) -> list:
    """
    Load ad patterns from the CSV dataset.
    
    Args:
        csv_path: Path to the CSV file
        limit: Optional limit on number of patterns to load
    
    Returns:
        List of pattern dictionaries ready for RAG ingestion
    """
    print(f"Loading patterns from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    if limit:
        df = df.head(limit)
    
    patterns = []
    
    for idx, row in df.iterrows():
        # Skip rows with missing essential data
        if pd.isna(row.get('clean_caption')) or not str(row.get('clean_caption')).strip():
            continue
        
        caption = str(row.get('clean_caption', '')).strip()
        hook = extract_hook_from_caption(caption)
        
        # Build visual description from available visual data
        visual_elements = []
        if not pd.isna(row.get('visual_tags')) and row.get('visual_tags'):
            visual_elements.append(f"Visual elements: {row['visual_tags']}")
        if not pd.isna(row.get('detected_objects')) and row.get('detected_objects'):
            visual_elements.append(f"Objects: {row['detected_objects']}")
        if not pd.isna(row.get('number_of_people')) and row.get('number_of_people'):
            visual_elements.append(f"People in image: {row['number_of_people']}")
        
        visual_description = " | ".join(visual_elements) if visual_elements else "Fashion/lifestyle imagery"
        
        # Extract pain points from comments (look for negative sentiment or common concerns)
        pain_points = []
        comments = str(row.get('user_comments', ''))
        if comments and len(comments) > 10:
            # Extract common concerns from comments
            if 'price' in comments.lower() or 'expensive' in comments.lower() or 'cost' in comments.lower():
                pain_points.append("pricing concerns")
            if 'quality' in comments.lower():
                pain_points.append("quality expectations")
            if 'restock' in comments.lower() or 'sold out' in comments.lower():
                pain_points.append("availability concerns")
            if 'size' in comments.lower() or 'fit' in comments.lower():
                pain_points.append("sizing concerns")
        
        # Default pain points if none detected
        if not pain_points:
            pain_points = ["style preference", "value for money"]
        
        # Build notes from metadata
        notes_parts = []
        if not pd.isna(row.get('media_type')):
            notes_parts.append(f"Media: {row['media_type']}")
        if not pd.isna(row.get('sentiment_label')):
            notes_parts.append(f"Sentiment: {row['sentiment_label']}")
        if not pd.isna(row.get('performance_label')):
            notes_parts.append(f"Performance: {row['performance_label']}")
        if not pd.isna(row.get('likes')):
            notes_parts.append(f"Likes: {row['likes']}")
        if not pd.isna(row.get('actual_comment_count')):
            notes_parts.append(f"Comments: {row['actual_comment_count']}")
        
        notes = " | ".join(notes_parts) if notes_parts else ""
        
        # Get engagement score (normalize to 0-10 scale if needed)
        engagement_score = float(row.get('engagement_score', 5.0))
        # Cap at 10 for consistency
        performance_score = min(engagement_score, 10.0)
        
        # Get category
        category = str(row.get('brand_category', 'Fashion & Lifestyle'))
        
        pattern = {
            "id": str(row.get('post_id', f"post_{idx}")),
            "category": category,
            "hook": hook,
            "caption": caption,
            "visual_description": visual_description,
            "pain_points": pain_points,
            "performance_score": performance_score,
            "notes": notes,
        }
        
        patterns.append(pattern)
    
    print(f"✓ Loaded {len(patterns)} valid patterns from CSV")
    return patterns


def seed_knowledge_base(db_path: str = "./chroma_db", csv_path: str = "rag/training_dataset_with_sentiment.csv", limit: int = None) -> int:
    """
    Seed the RAG knowledge base with patterns from CSV.

    Args:
        db_path: Path to ChromaDB database
        csv_path: Path to CSV file with training data
        limit: Optional limit on number of patterns to load

    Returns the number of documents added.
    """
    # Load patterns from CSV
    patterns = load_patterns_from_csv(csv_path, limit=limit)
    
    if not patterns:
        print("⚠ No valid patterns found in CSV")
        return 0
    
    # Initialize RAG engine
    engine = RAGEngine(db_path=db_path)
    engine.initialize()

    print(f"Current documents in DB: {engine.count()}")
    print(f"Seeding {len(patterns)} patterns from CSV...")

    # Bulk add to database
    ids = engine.bulk_add(patterns)

    print(f"✓ Seeded {len(ids)} ad patterns successfully")
    print(f"Total documents in DB: {engine.count()}")
    return len(ids)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed RAG database with ad patterns from CSV")
    parser.add_argument("--db-path", default="./chroma_db", help="Path to ChromaDB database")
    parser.add_argument("--csv-path", default="rag/training_dataset_with_sentiment.csv", help="Path to CSV file")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of patterns to load (for testing)")
    
    args = parser.parse_args()
    
    db_path = os.environ.get("CHROMA_DB_PATH", args.db_path)
    csv_path = args.csv_path
    
    print("=" * 60)
    print("AdForge RAG Database Seeding")
    print("=" * 60)
    print(f"Database: {db_path}")
    print(f"CSV Source: {csv_path}")
    if args.limit:
        print(f"Limit: {args.limit} patterns")
    print("=" * 60)
    print()
    
    count = seed_knowledge_base(db_path, csv_path, limit=args.limit)
    
    print()
    print("=" * 60)
    print(f"✓ Done! {count} patterns added to RAG knowledge base")
    print(f"Location: {db_path}")
    print("=" * 60)

