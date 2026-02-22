"""
llm/steps.py — Executes each of the 6 pipeline steps

Each step is an async function that takes the client + context
and returns a structured dict result.
"""
import logging
from typing import Optional, List, Dict, Any

from llm.groq_client import GroqClient
from llm import prompts

logger = logging.getLogger(__name__)


async def run_step1(
    client: GroqClient,
    description: str,
    category: str,
    audience: Optional[str],
    rag_patterns: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Step 1 — Product analysis + RAG pattern injection."""
    logger.info("Step 1: Running product analysis")
    prompt = prompts.step1_product_analysis(description, category, audience, rag_patterns)
    result = await client.complete_json(prompt)
    logger.info(f"Step 1 done: {len(result.get('key_selling_points', []))} USPs found")
    return result


async def run_step2(
    client: GroqClient,
    description: str,
    category: str,
    scraped_ads: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """Step 2 — Competitor intelligence (with or without scraped data)."""
    logger.info("Step 2: Running competitor intelligence")
    prompt = prompts.step2_competitor_intelligence(description, category, scraped_ads)
    result = await client.complete_json(prompt)
    logger.info(f"Step 2 done: {len(result.get('opportunity_gaps', []))} gaps found")
    return result


async def run_step3_with_images(
    client: GroqClient,
    description: str,
    category: str,
    images: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Step 3 — Image analysis using vision model."""
    logger.info(f"Step 3: Analyzing {len(images)} images with vision model")
    product_context = f"{category} — {description[:300]}"
    prompt = prompts.step3_image_analysis(product_context)

    try:
        result = await client.vision_json(prompt, images)
        logger.info(f"Step 3 done: {len(result.get('visual_recommendations', []))} visual recs")
        return result
    except Exception as e:
        logger.warning(f"Step 3 vision failed: {e}, falling back to text-based visual recs")
        return await run_step3_fallback(client, description, category)


async def run_step3_validate(
    client: GroqClient,
    description: str,
    category: str,
    images: List[Dict[str, str]],
) -> Dict[str, Any]:
    """
    Step 3 pre-check — verify that the uploaded images actually match
    the described product before running full image analysis.
    Returns a dict with keys: overall_match (bool), per_image, summary.
    """
    logger.info(f"Step 3 validation: checking {len(images)} image(s) against product description")
    prompt = prompts.step3_validate_image_match(description, category)
    try:
        result = await client.vision_json(prompt, images)
        logger.info(
            f"Step 3 validation done: overall_match={result.get('overall_match')}, "
            f"confidence={result.get('overall_confidence')}"
        )
        return result
    except Exception as e:
        logger.warning(f"Step 3 validation failed ({e}), skipping validation")
        # If validation itself errors, we allow the pipeline to continue (fail open)
        return {"overall_match": True, "summary": "Validation unavailable", "per_image": []}


async def run_step3_fallback(
    client: GroqClient,
    description: str,
    category: str,
) -> Dict[str, Any]:
    """Step 3 fallback — Generate visual recommendations via text model."""
    logger.info("Step 3: No images, generating visual recommendations via LLM")
    prompt = prompts.step3_visual_fallback(description, category)
    result = await client.complete_json(prompt)
    return result


async def run_step4(
    client: GroqClient,
    description: str,
    category: str,
    scraped_comments: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Step 4 — Comment/sentiment analysis."""
    logger.info("Step 4: Running sentiment analysis")
    prompt = prompts.step4_comment_analysis(description, category, scraped_comments)
    result = await client.complete_json(prompt)
    logger.info(f"Step 4 done: {result.get('sentiment_breakdown', {}).get('positive_pct', '?')}% positive")
    return result


async def run_step5(
    client: GroqClient,
    description: str,
    category: str,
    audience: Optional[str],
    preferred_angle: str,
    step1_data: Dict,
    step2_data: Dict,
    step4_data: Dict,
) -> Dict[str, Any]:
    """Step 5 — Strategy synthesis."""
    logger.info("Step 5: Synthesizing strategy")
    prompt = prompts.step5_strategy_synthesis(
        description, category, audience, preferred_angle,
        step1_data, step2_data, step4_data
    )
    result = await client.complete_json(prompt)
    logger.info(f"Step 5 done: angle={result.get('primary_angle')}, tone={result.get('tone_of_voice')}")
    return result


async def run_step6(
    client: GroqClient,
    description: str,
    category: str,
    audience: Optional[str],
    step1_data: Dict,
    step2_data: Dict,
    step3_data: Dict,
    step4_data: Dict,
    step5_data: Dict,
) -> Dict[str, Any]:
    """Step 6 — Final ad generation."""
    logger.info("Step 6: Generating final ad")

    visual_recs = step3_data.get("visual_recommendations", [])

    prompt = prompts.step6_ad_generation(
        description, category, audience,
        step1_data, step2_data, visual_recs,
        step4_data, step5_data
    )
    result = await client.complete_json(prompt)
    logger.info("Step 6 done: Ad generated successfully")
    return result
