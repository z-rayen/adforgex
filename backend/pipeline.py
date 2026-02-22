"""
backend/pipeline.py — Pipeline orchestrator with RAG auto-save and image RAG storage

New features:
  - After scraping: scraped ads are saved to RAG knowledge base automatically
  - After image analysis: visual descriptions are saved to RAG with embeddings
  - RAG grows richer with every pipeline run
"""
import logging
import asyncio
import uuid
import random
from typing import AsyncGenerator, Dict, Any, Optional, List

# ──────────────────────────────────────────────────────────────────────────────
# Funny roast messages for image mismatch — {detected} and {product} are filled in
# ──────────────────────────────────────────────────────────────────────────────
_MISMATCH_ROASTS = [
    "Bro really uploaded a {detected} to sell {product}. Bold strategy. Wrong, but bold.",
    "Plot twist: you're selling {product} but the image is screaming '{detected}'. We're confused. The AI is confused. Everyone is confused.",
    "We see a {detected}. You described {product}. One of these things is not like the other 🎵",
    "AI vision walked in, saw a {detected}, saw your '{product}' description, and immediately filed for early retirement.",
    "That's a lovely {detected} you've got there. Shame it has nothing to do with {product}.",
    "Sir/Ma'am, this is a {product} ad. WHY is there a {detected} in here?",
    "Your image: {detected}. Your product: {product}. Your energy: chaotic. We respect it. But no.",
    "Ad campaign idea: {detected} sells {product}. Rejected. Brilliantly, hilariously rejected.",
    "The AI looked at your {detected} image, looked at '{product}', looked back at the image... and chose peace. Please fix this.",
    "Image detected: {detected}. Product expected: {product}. Match found: absolutely not whatsoever.",
]

def _roast_mismatch(detected: str, product: str) -> str:
    template = random.choice(_MISMATCH_ROASTS)
    # Clean up product to first ~40 chars
    short_product = product.strip()[:40].rstrip(',. ')
    return template.format(detected=detected, product=short_product)

from backend.models import AdGenerationRequest, AdGenerationResponse, UserInsights
from backend.config import get_settings
from llm.groq_client import GroqClient
from llm import steps as llm_steps
from rag.rag_engine import RAGEngine

logger = logging.getLogger(__name__)


class AdGenerationPipeline:

    def __init__(self, rag_engine: RAGEngine):
        self.rag = rag_engine
        self.settings = get_settings()

    def _make_client(self, api_key: Optional[str] = None) -> GroqClient:
        key = api_key or self.settings.groq_api_key
        if not key:
            raise ValueError("No Groq API key configured. Set GROQ_API_KEY in .env")
        return GroqClient(
            api_key=key,
            text_model=self.settings.text_model,
            vision_model=self.settings.vision_model,
            max_tokens_text=self.settings.max_tokens_text,
            max_tokens_vision=self.settings.max_tokens_vision,
        )

    # ─────────────────────────────────────────────────
    # RAG auto-save helpers
    # ─────────────────────────────────────────────────

    def _save_scraped_ads_to_rag(
        self,
        category: str,
        ads: List[str],
        comments: List[str],
        description: str,
    ) -> int:
        """
        Save scraped competitor ads and reviews into the RAG knowledge base.
        Each ad becomes a document so future runs can retrieve it.
        Returns number of documents saved.
        """
        if not self.rag or not ads:
            return 0

        saved = 0
        patterns = []

        # Save individual ad bullets as patterns
        for i, ad_text in enumerate(ads[:10]):
            if len(ad_text) < 30:
                continue
            patterns.append({
                "id": f"scraped_{uuid.uuid4().hex[:12]}",
                "category": category,
                "hook": ad_text[:80],
                "caption": ad_text,
                "visual_description": "Scraped from competitor listing",
                "pain_points": [],
                "performance_score": 5.0,
                "notes": f"Auto-scraped competitor data for: {description[:80]}",
            })

        # Save a combined review summary as one document
        if comments:
            combined_reviews = " | ".join(comments[:10])
            patterns.append({
                "id": f"reviews_{uuid.uuid4().hex[:12]}",
                "category": category,
                "hook": f"Customer reviews for {category}",
                "caption": combined_reviews[:1000],
                "visual_description": "Customer review data",
                "pain_points": [],
                "performance_score": 6.0,
                "notes": f"Auto-scraped customer reviews for: {description[:80]}",
            })

        try:
            ids = self.rag.bulk_add(patterns)
            saved = len(ids)
            logger.info(f"RAG auto-save: saved {saved} scraped documents for '{category}'")
        except Exception as e:
            logger.warning(f"RAG auto-save failed: {e}")

        return saved

    def _save_visual_analysis_to_rag(
        self,
        category: str,
        description: str,
        visual_data: Dict[str, Any],
        performance_hint: float = 7.0,
    ) -> int:
        """
        Save image visual analysis results into RAG.
        Stores visual descriptions, layout types, color moods as searchable documents.
        Returns number of documents saved.
        """
        if not self.rag or not visual_data:
            return 0

        saved = 0
        patterns = []

        # Save per-image analysis
        per_image = visual_data.get("per_image_analysis", [])
        for img_analysis in per_image:
            score = img_analysis.get("effectiveness_score", 5)
            objects = ", ".join(img_analysis.get("objects", []))
            colors = ", ".join(img_analysis.get("colors", []))
            layout = img_analysis.get("layout_type", "unknown")
            notes = img_analysis.get("notes", "")

            visual_desc = (
                f"Layout: {layout}. "
                f"Objects: {objects}. "
                f"Colors: {colors}. "
                f"Human presence: {img_analysis.get('human_presence', 'unknown')}. "
                f"Text overlay: {img_analysis.get('text_overlay', False)}. "
                f"Notes: {notes}"
            )

            patterns.append({
                "id": f"visual_{uuid.uuid4().hex[:12]}",
                "category": category,
                "hook": f"Visual pattern: {layout} layout for {category}",
                "caption": visual_desc,
                "visual_description": visual_desc,
                "pain_points": [],
                "performance_score": float(score),
                "notes": f"Auto-saved visual analysis for: {description[:80]}",
            })

        # Save the cross-image recommendations as a document
        cross_patterns = visual_data.get("cross_image_patterns", [])
        recs = visual_data.get("visual_recommendations", [])
        if cross_patterns or recs:
            combined = (
                "Cross-image patterns: " + " | ".join(cross_patterns) + ". "
                "Recommendations: " + " | ".join(recs)
            )
            patterns.append({
                "id": f"visual_recs_{uuid.uuid4().hex[:12]}",
                "category": category,
                "hook": f"Visual recommendations for {category} ads",
                "caption": combined,
                "visual_description": combined,
                "pain_points": [],
                "performance_score": performance_hint,
                "notes": f"Auto-saved visual recommendations for: {description[:80]}",
            })

        try:
            ids = self.rag.bulk_add(patterns)
            saved = len(ids)
            logger.info(f"RAG auto-save: saved {saved} visual analysis documents for '{category}'")
        except Exception as e:
            logger.warning(f"RAG visual save failed: {e}")

        return saved

    def _save_final_ad_to_rag(
        self,
        category: str,
        description: str,
        ad_result: Dict[str, Any],
        step4_data: Dict,
    ) -> None:
        """
        Save the final generated ad back to RAG.
        This means every generated ad enriches the knowledge base for future runs.
        """
        if not self.rag:
            return
        try:
            pain_points = step4_data.get("user_frustrations", [])[:4]
            doc_id = self.rag.add_ad_pattern(
                category=category,
                hook=ad_result.get("hook", ""),
                caption=ad_result.get("caption", ""),
                visual_description=" | ".join(ad_result.get("visual_recommendations", [])),
                pain_points=pain_points,
                performance_score=7.5,  # default — can be updated later via API
                notes=f"AI-generated ad for: {description[:80]}",
            )
            logger.info(f"RAG auto-save: saved generated ad as document {doc_id}")
        except Exception as e:
            logger.warning(f"RAG final ad save failed: {e}")

    # ─────────────────────────────────────────────────
    # Main streaming pipeline
    # ─────────────────────────────────────────────────

    async def run_streaming(
        self,
        request: AdGenerationRequest,
        api_key: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:

        client = self._make_client(api_key)

        def emit(step: int, name: str, status: str, msg: str, data: Any = None):
            event = {
                "type": "step",
                "step": step,
                "step_name": name,
                "status": status,
                "message": msg,
            }
            if data:
                event["data"] = data
            return event

        # ── Step 1: RAG retrieval + product analysis ──────────────────────
        yield emit(1, "RAG + Product Analysis", "running",
                   "Searching knowledge base for similar ad patterns...")

        rag_patterns = []
        rag_count = 0
        if request.use_rag and self.rag:
            try:
                rag_query = f"{request.product_category} {request.product_description[:100]}"
                rag_patterns = self.rag.search(rag_query, top_k=self.settings.rag_top_k)
                rag_count = len(rag_patterns)
                logger.info(f"RAG: retrieved {rag_count} patterns")
            except Exception as e:
                logger.warning(f"RAG search failed: {e}")

        step1_data = await llm_steps.run_step1(
            client,
            request.product_description,
            request.product_category,
            request.target_audience,
            rag_patterns if rag_patterns else None,
        )
        yield emit(1, "RAG + Product Analysis", "done",
                   f"Found {rag_count} RAG patterns. Extracted {len(step1_data.get('key_selling_points', []))} USPs.",
                   {"rag_patterns_found": rag_count})

        # ── Step 2: Scraping + competitor intelligence ────────────────────
        yield emit(2, "Competitor Intelligence", "running",
                   "Scraping competitor ads and reviews...")

        scraped_ads, scraped_comments, scraped_images = [], [], []
        scraper_count = 0
        rag_saved_from_scrape = 0

        if request.scrape_competitors:
            try:
                from scraper.scraper import AdScraper
                async with AdScraper(timeout=self.settings.scrape_timeout) as scraper:
                    scrape_result = await scraper.scrape_all(
                        query=f"{request.product_category} {request.product_description[:80]}",
                        category=request.product_category,
                    )
                    scraped_ads = scrape_result.get("ads", [])
                    scraped_comments = scrape_result.get("comments", [])
                    scraped_images = scrape_result.get("images", [])  # base64 images
                    scraper_count = len(scraped_ads)

                # ── AUTO-SAVE scraped data to RAG ─────────────────────────
                if request.use_rag and self.rag:
                    rag_saved_from_scrape = self._save_scraped_ads_to_rag(
                        category=request.product_category,
                        ads=scraped_ads,
                        comments=scraped_comments,
                        description=request.product_description,
                    )

            except Exception as e:
                logger.warning(f"Scraping failed (using LLM simulation): {e}", exc_info=True)
                yield emit(2, "Competitor Intelligence", "warn",
                           f"Scraper error — using LLM simulation")

        step2_data = await llm_steps.run_step2(
            client,
            request.product_description,
            request.product_category,
            scraped_ads if scraped_ads else None,
        )
        yield emit(2, "Competitor Intelligence", "done",
                   f"Scraped {scraper_count} ads, {len(scraped_images)} images. "
                   f"Saved {rag_saved_from_scrape} docs to RAG. "
                   f"Found {len(step2_data.get('opportunity_gaps', []))} gaps.",
                   {"scraped_count": scraper_count, "rag_saved": rag_saved_from_scrape})

        # ── Step 3: Image analysis ────────────────────────────────────────
        yield emit(3, "Image Analysis", "running",
                   "Analyzing ad images with vision model...")

        images_analyzed = 0
        step3_data = {}
        rag_saved_from_images = 0

        # Combine user-uploaded images + scraped images
        all_images = []
        if request.competitor_images_b64:
            mimes = request.image_mime_types or ["image/jpeg"] * len(request.competitor_images_b64)
            for b64, mime in zip(request.competitor_images_b64, mimes):
                all_images.append({"b64": b64, "mime": mime})

        # Add scraped images (already in b64 format)
        for img in scraped_images:
            if "b64" in img and "mime" in img:
                all_images.append({"b64": img["b64"], "mime": img["mime"]})

        if all_images:
            # ── VALIDATION: ensure uploaded images match the product ──────
            user_uploaded = []
            if request.competitor_images_b64:
                mimes_for_check = request.image_mime_types or ["image/jpeg"] * len(request.competitor_images_b64)
                user_uploaded = [
                    {"b64": b64, "mime": mime}
                    for b64, mime in zip(request.competitor_images_b64, mimes_for_check)
                ]

            if user_uploaded:
                validation = await llm_steps.run_step3_validate(
                    client,
                    request.product_description,
                    request.product_category,
                    user_uploaded[:5],
                )
                overall_match = validation.get("overall_match", True)

                if not overall_match:
                    # Pick the first mismatched image's detected subject for the roast
                    bad_images = [
                        img for img in validation.get("per_image", [])
                        if not img.get("matches_product", True)
                    ]
                    detected_subject = (
                        bad_images[0].get("detected_subject", "something totally unrelated")
                        if bad_images else "something totally unrelated"
                    )
                    roast = _roast_mismatch(detected_subject, request.product_description)

                    # 1. Regular step event — always hits the log regardless of buffering
                    yield emit(3, "Image Analysis", "error", f"🎭 {roast}")
                    # 2. Structured event — powers the banner in the frontend
                    yield {
                        "type": "image_mismatch",
                        "step": 3,
                        "step_name": "Image Analysis",
                        "status": "error",
                        "message": roast,
                        "detected": detected_subject,
                        "product": request.product_description[:80],
                    }
                    # 3. Ping — forces the buffer to flush before the connection closes
                    yield {"type": "ping"}
                    return  # ← STOP the pipeline entirely

            if all_images:
                step3_data = await llm_steps.run_step3_with_images(
                    client,
                    request.product_description,
                    request.product_category,
                    all_images[:5],  # max 5 images for vision model
                )
                images_analyzed = len(all_images[:5])

                # ── AUTO-SAVE visual analysis to RAG ─────────────────────────
                if request.use_rag and self.rag and isinstance(step3_data, dict):
                    rag_saved_from_images = self._save_visual_analysis_to_rag(
                        category=request.product_category,
                        description=request.product_description,
                        visual_data=step3_data,
                    )

                yield emit(3, "Image Analysis", "done",
                           f"Analyzed {images_analyzed} images "
                           f"({len(request.competitor_images_b64 or [])} uploaded + "
                           f"{len(scraped_images)} scraped). "
                           f"Saved {rag_saved_from_images} visual docs to RAG.")
            else:
                step3_data = await llm_steps.run_step3_fallback(
                    client,
                    request.product_description,
                    request.product_category,
                )
                yield emit(3, "Image Analysis", "done",
                           "No images to analyze — generated visual recommendations via LLM.")
        else:
            step3_data = await llm_steps.run_step3_fallback(
                client,
                request.product_description,
                request.product_category,
            )
            yield emit(3, "Image Analysis", "done",
                       "No images available — generated visual recommendations via LLM.")

        # ── Step 4: Sentiment analysis ────────────────────────────────────
        yield emit(4, "Sentiment Analysis", "running",
                   "Analyzing user comments and reviews...")

        step4_data = await llm_steps.run_step4(
            client,
            request.product_description,
            request.product_category,
            scraped_comments if scraped_comments else None,
        )
        sentiment = step4_data.get("sentiment_breakdown", {})
        yield emit(4, "Sentiment Analysis", "done",
                   f"Sentiment: {sentiment.get('positive_pct', '?')}% positive. "
                   f"Extracted {len(step4_data.get('common_questions', []))} questions.")

        # ── Step 5: Strategy synthesis ────────────────────────────────────
        yield emit(5, "Strategy Synthesis", "running",
                   "Synthesizing all insights into messaging strategy...")

        step5_data = await llm_steps.run_step5(
            client,
            request.product_description,
            request.product_category,
            request.target_audience,
            request.messaging_angle.value,
            step1_data,
            step2_data,
            step4_data,
        )
        yield emit(5, "Strategy Synthesis", "done",
                   f"Strategy: {step5_data.get('primary_angle')} angle | "
                   f"{step5_data.get('tone_of_voice')} tone")

        # ── Step 6: Ad generation ─────────────────────────────────────────
        yield emit(6, "Ad Generation", "running",
                   "Writing final high-conversion ad copy...")

        step6_data = await llm_steps.run_step6(
            client,
            request.product_description,
            request.product_category,
            request.target_audience,
            step1_data,
            step2_data,
            step3_data,
            step4_data,
            step5_data,
        )

        # ── AUTO-SAVE final generated ad to RAG ──────────────────────────
        if request.use_rag and self.rag:
            self._save_final_ad_to_rag(
                category=request.product_category,
                description=request.product_description,
                ad_result=step6_data,
                step4_data=step4_data,
            )

        # Build final response
        user_insights_raw = step6_data.get("user_insights", {})
        total_rag_saved = rag_saved_from_scrape + rag_saved_from_images + 1  # +1 for final ad

        response = AdGenerationResponse(
            hook=step6_data.get("hook", ""),
            caption=step6_data.get("caption", ""),
            cta=step6_data.get("cta", ""),
            visual_recommendations=step6_data.get("visual_recommendations", []),
            user_insights=UserInsights(
                pain_points=user_insights_raw.get("pain_points", []),
                questions=user_insights_raw.get("questions", []),
                desired_features=user_insights_raw.get("desired_features", []),
                use_cases=user_insights_raw.get("use_cases", []),
            ),
            strategy=step6_data.get("strategy", ""),
            rag_patterns_found=rag_count,
            scraper_results_found=scraper_count,
            images_analyzed=images_analyzed,
            pipeline_steps_completed=["step1", "step2", "step3", "step4", "step5", "step6"],
        )

        yield {
            "type": "complete",
            "step": 6,
            "step_name": "Ad Generation",
            "status": "done",
            "message": f"Pipeline complete! Ad generated. {total_rag_saved} new docs saved to RAG.",
            "result": response.model_dump(),
        }

    async def run(
        self,
        request: AdGenerationRequest,
        api_key: Optional[str] = None,
    ) -> AdGenerationResponse:
        result = None
        async for event in self.run_streaming(request, api_key):
            if event.get("type") == "complete":
                result = AdGenerationResponse(**event["result"])
        if result is None:
            raise RuntimeError("Pipeline completed without producing a result")
        return result