"""
llm/prompts.py — All LLM prompt templates for the 6-step pipeline

Each function returns a fully-formed prompt string.
Keep prompts here so they are easy to tune without touching logic.
"""
from typing import List, Optional, Dict, Any
import json


# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Product analysis & RAG pattern extraction
# ──────────────────────────────────────────────────────────────────────────────

def step1_product_analysis(
    description: str,
    category: str,
    audience: Optional[str],
    rag_patterns: Optional[List[Dict]] = None,
) -> str:
    rag_section = ""
    if rag_patterns:
        rag_section = f"""
RETRIEVED AD PATTERNS FROM KNOWLEDGE BASE:
{json.dumps(rag_patterns, indent=2)}

Use these retrieved patterns as a foundation. Extract what made them successful.
"""
    return f"""You are a senior performance marketer with 10+ years running DTC ads on Meta, TikTok, and Google.

Analyze this product and extract ad intelligence.

PRODUCT: {description}
CATEGORY: {category}
TARGET AUDIENCE: {audience or "General consumer market"}
{rag_section}

Extract the following in JSON:
{{
  "similar_product_patterns": "Brief description of what types of ads typically work for this category",
  "successful_caption_styles": ["style 1", "style 2", "style 3"],
  "key_selling_points": ["USP 1", "USP 2", "USP 3", "USP 4"],
  "customer_pain_points": ["pain 1", "pain 2", "pain 3", "pain 4"],
  "psychological_triggers": ["trigger 1", "trigger 2", "trigger 3"],
  "top_emotions_to_evoke": ["emotion 1", "emotion 2"],
  "objections_to_preempt": ["objection 1", "objection 2"]
}}"""


# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Competitor intelligence
# ──────────────────────────────────────────────────────────────────────────────

def step2_competitor_intelligence(
    description: str,
    category: str,
    scraped_ads: Optional[List[Dict]] = None,
) -> str:
    scrape_section = ""
    if scraped_ads:
        scrape_section = f"""
SCRAPED COMPETITOR ADS FROM THE WEB:
{json.dumps(scraped_ads[:10], indent=2)}

Analyze these REAL competitor ads in your response.
"""
    else:
        scrape_section = """
No live scraped data available. Simulate realistic competitor analysis based on your knowledge
of this product category's advertising ecosystem.
"""
    return f"""You are a competitive intelligence analyst specializing in digital advertising.

PRODUCT: {description}
CATEGORY: {category}
{scrape_section}

Produce competitor analysis in JSON:
{{
  "competitor_hooks": ["hook 1", "hook 2", "hook 3"],
  "competitor_caption_patterns": ["pattern 1", "pattern 2"],
  "common_ctas": ["cta 1", "cta 2"],
  "common_weaknesses": ["weakness 1", "weakness 2"],
  "opportunity_gaps": ["gap 1", "gap 2", "gap 3"],
  "differentiators_to_exploit": ["diff 1", "diff 2"]
}}"""


# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — Image / visual analysis (used with vision model)
# ──────────────────────────────────────────────────────────────────────────────

def step3_image_analysis(product_context: str) -> str:
    return f"""You are a visual creative director analyzing competitor ad images.

PRODUCT CONTEXT: {product_context}

For EACH image provided, analyze:
1. Objects and props present
2. Color palette (dominant colors, mood)
3. Layout (product-only, lifestyle, before/after, testimonial, etc.)
4. Presence of humans (none / hands-only / full-person / face closeup)
5. Text overlay (yes/no, font style, placement)
6. Overall visual quality and professionalism
7. What makes it effective or ineffective for conversion

Then synthesize across all images:
- Common visual patterns in high-performing ads
- What visual elements correlate with strong engagement
- Recommended visual structure for a new ad in this category

Respond in JSON:
{{
  "per_image_analysis": [
    {{
      "image_index": 0,
      "objects": [],
      "colors": [],
      "layout_type": "",
      "human_presence": "",
      "text_overlay": true,
      "effectiveness_score": 7,
      "notes": ""
    }}
  ],
  "cross_image_patterns": [],
  "visual_recommendations": ["rec 1", "rec 2", "rec 3", "rec 4", "rec 5"]
}}"""


def step3_visual_fallback(description: str, category: str) -> str:
    """Used when no images are provided."""
    return f"""You are a visual creative director. Based on your expertise in {category} advertising,
recommend the ideal visual creative structure for:

PRODUCT: {description}

What should the ad image/video show to maximize conversion?

Respond in JSON:
{{
  "visual_recommendations": [
    "recommendation 1",
    "recommendation 2",
    "recommendation 3",
    "recommendation 4",
    "recommendation 5"
  ],
  "best_layout_type": "lifestyle|product-only|before-after|ugc|testimonial",
  "color_mood": "...",
  "human_presence": "none|hands|full-person|face"
}}"""


# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — Comment/sentiment analysis
# ──────────────────────────────────────────────────────────────────────────────

def step4_comment_analysis(
    description: str,
    category: str,
    scraped_comments: Optional[List[str]] = None,
) -> str:
    comment_section = ""
    if scraped_comments:
        comment_section = f"""
REAL COMMENTS SCRAPED FROM COMPETITOR ADS / REVIEWS:
{json.dumps(scraped_comments[:50], indent=2)}

Analyze these REAL comments.
"""
    else:
        comment_section = """
No live comments scraped. Simulate realistic user comments and sentiment
based on typical buyer behavior for this product category.
"""
    return f"""You are a social listening analyst specializing in consumer sentiment for e-commerce.

PRODUCT: {description}
CATEGORY: {category}
{comment_section}

Perform full sentiment and thematic analysis. Respond in JSON:
{{
  "sentiment_breakdown": {{
    "positive_pct": 65,
    "negative_pct": 20,
    "neutral_pct": 15
  }},
  "common_questions": ["question 1", "question 2", "question 3", "question 4"],
  "user_frustrations": ["frustration 1", "frustration 2", "frustration 3"],
  "desired_features": ["feature 1", "feature 2", "feature 3"],
  "alternative_use_cases": ["use case 1", "use case 2", "use case 3"],
  "positive_themes": ["theme 1", "theme 2"],
  "negative_themes": ["theme 1", "theme 2"]
}}"""


# ──────────────────────────────────────────────────────────────────────────────
# STEP 5 — Strategy synthesis
# ──────────────────────────────────────────────────────────────────────────────

def step5_strategy_synthesis(
    description: str,
    category: str,
    audience: Optional[str],
    preferred_angle: str,
    step1_data: Dict,
    step2_data: Dict,
    step4_data: Dict,
) -> str:
    return f"""You are a conversion optimization strategist. Synthesize all research into a clear ad strategy.

PRODUCT: {description}
CATEGORY: {category}
AUDIENCE: {audience or "General"}
PREFERRED ANGLE: {preferred_angle}

RESEARCH INPUTS:
Pain Points: {json.dumps(step1_data.get("customer_pain_points", []))}
USPs: {json.dumps(step1_data.get("key_selling_points", []))}
Psychological Triggers: {json.dumps(step1_data.get("psychological_triggers", []))}
Objections to Preempt: {json.dumps(step1_data.get("objections_to_preempt", []))}
Competitor Gaps: {json.dumps(step2_data.get("opportunity_gaps", []))}
Differentiators: {json.dumps(step2_data.get("differentiators_to_exploit", []))}
User Questions: {json.dumps(step4_data.get("common_questions", []))}
User Frustrations: {json.dumps(step4_data.get("user_frustrations", []))}
Positive Themes: {json.dumps(step4_data.get("positive_themes", []))}

Define the optimal ad strategy. If preferred_angle is "auto", pick the best one.

Respond in JSON:
{{
  "primary_angle": "problem-solution|luxury|ugc|fear|social-proof|discount|lifestyle",
  "value_proposition": "One punchy sentence capturing the core value",
  "primary_objection_to_preempt": "The #1 objection to address in the ad",
  "tone_of_voice": "urgent|playful|authoritative|empathetic|aspirational|conversational",
  "key_message": "The single most important thing the ad must communicate",
  "secondary_messages": ["msg 1", "msg 2"],
  "strategy_summary": "2-3 sentence paragraph explaining the full strategy"
}}"""


# ──────────────────────────────────────────────────────────────────────────────
# STEP 6 — Ad generation
# ──────────────────────────────────────────────────────────────────────────────

def step6_ad_generation(
    description: str,
    category: str,
    audience: Optional[str],
    step1_data: Dict,
    step2_data: Dict,
    step3_visual: List[str],
    step4_data: Dict,
    step5_data: Dict,
) -> str:
    return f"""You are a world-class performance copywriter who has generated $50M+ in ad revenue.
Write a complete, battle-tested, high-conversion ad using ALL provided research.

═══ PRODUCT BRIEF ═══
Product: {description}
Category: {category}
Audience: {audience or "General consumer"}

═══ STRATEGY ═══
Angle: {step5_data.get("primary_angle")}
Tone: {step5_data.get("tone_of_voice")}
Core Value Prop: {step5_data.get("value_proposition")}
Key Message: {step5_data.get("key_message")}
Objection to Preempt: {step5_data.get("primary_objection_to_preempt")}
Strategy: {step5_data.get("strategy_summary")}

═══ SELLING POINTS TO USE ═══
{json.dumps(step1_data.get("key_selling_points", []))}

═══ COMPETITOR HOOKS TO AVOID (too cliché) ═══
{json.dumps(step2_data.get("competitor_hooks", [])[:3])}

═══ OPPORTUNITY GAPS TO EXPLOIT ═══
{json.dumps(step2_data.get("opportunity_gaps", []))}

═══ USER INSIGHTS ═══
Pain Points: {json.dumps(step4_data.get("user_frustrations", []))}
Questions to Answer: {json.dumps(step4_data.get("common_questions", [])[:2])}

═══ VISUAL CONTEXT ═══
{json.dumps(step3_visual)}

RULES FOR COPY:
- Hook must be ≤15 words, creates a PATTERN INTERRUPT, makes the viewer stop scrolling
- Hook must NOT start with "Are you", "Do you", or "Introducing"
- Caption: 150-250 words, natural flow, includes social proof element
- Address the main objection within the caption
- CTA: 3-6 words, action-oriented, creates urgency
- Visual recs: 5 SPECIFIC, actionable visual directions

Respond ONLY in this exact JSON:
{{
  "hook": "...",
  "caption": "...",
  "cta": "...",
  "visual_recommendations": ["...", "...", "...", "...", "..."],
  "user_insights": {{
    "pain_points": {json.dumps(step1_data.get("customer_pain_points", [])[:4])},
    "questions": {json.dumps(step4_data.get("common_questions", [])[:4])},
    "desired_features": {json.dumps(step4_data.get("desired_features", [])[:4])},
    "use_cases": {json.dumps(step4_data.get("alternative_use_cases", [])[:4])}
  }},
  "strategy": {json.dumps(step5_data.get("strategy_summary", ""))}
}}"""
