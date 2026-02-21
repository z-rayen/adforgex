"""
llm/groq_client.py — Groq API client for text and vision inference

Supports:
  - Text generation (llama-3.3-70b-versatile)
  - Vision/image analysis (meta-llama/llama-4-scout-17b-16e-instruct)
  - JSON mode
  - Async calls
  - Retry with exponential backoff
"""
import json
import asyncio
import logging
from typing import Optional, List, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqAPIError(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"Groq API [{status_code}]: {message}")


class GroqClient:
    """
    Async Groq API client.

    Usage:
        client = GroqClient(api_key="gsk_...")
        text = await client.complete("Tell me about UV purifiers")
        data = await client.complete_json("Extract pain points for: UV purifier", schema_hint={...})
        analysis = await client.vision("Analyze this ad image", images=[{"b64": "...", "mime": "image/jpeg"}])
    """

    def __init__(
        self,
        api_key: str,
        text_model: str = "llama-3.3-70b-versatile",
        vision_model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        max_tokens_text: int = 2000,
        max_tokens_vision: int = 1500,
        timeout: float = 60.0,
    ):
        self.api_key = api_key
        self.text_model = text_model
        self.vision_model = vision_model
        self.max_tokens_text = max_tokens_text
        self.max_tokens_vision = max_tokens_vision
        self.timeout = timeout
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    # ─────────────────────────────────────────────────
    # Core HTTP call
    # ─────────────────────────────────────────────────

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(GroqAPIError),
        reraise=True,
    )
    async def _post(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(
                GROQ_BASE_URL,
                headers=self._headers,
                json=payload,
            )

        if resp.status_code == 429:
            # Rate limit — retry
            raise GroqAPIError(429, "Rate limit hit, retrying...")
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("error", {}).get("message", resp.text)
            except Exception:
                detail = resp.text
            raise GroqAPIError(resp.status_code, detail)

        return resp.json()

    # ─────────────────────────────────────────────────
    # Text Completion
    # ─────────────────────────────────────────────────

    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Simple text completion. Returns the raw string response."""
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        if messages:
            msgs.extend(messages)
        else:
            msgs.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.text_model,
            "max_tokens": max_tokens or self.max_tokens_text,
            "messages": msgs,
        }

        data = await self._post(payload)
        return data["choices"][0]["message"]["content"]

    async def complete_json(
        self,
        prompt: str,
        system: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Text completion with JSON mode enforced.
        Returns a parsed Python dict.
        """
        msgs = []
        if system:
            msgs.append({"role": "system", "content": system})
        msgs.append({"role": "user", "content": prompt})

        payload = {
            "model": model or self.text_model,
            "max_tokens": max_tokens or self.max_tokens_text,
            "messages": msgs,
            "response_format": {"type": "json_object"},
        }

        data = await self._post(payload)
        raw = data["choices"][0]["message"]["content"]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Fallback: extract JSON block if wrapped in markdown
            import re
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Could not parse JSON from response: {raw[:200]}")

    # ─────────────────────────────────────────────────
    # Vision (Image Analysis)
    # ─────────────────────────────────────────────────

    async def vision(
        self,
        prompt: str,
        images: List[Dict[str, str]],  # [{"b64": "...", "mime": "image/jpeg"}, ...]
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Multimodal vision call. Analyzes images.

        Args:
            prompt: Text instruction/question
            images: List of dicts with "b64" (base64 string) and "mime" (image MIME type)
            model: Override model
            max_tokens: Override token limit

        Returns:
            String analysis from the vision model
        """
        content: List[Dict] = [{"type": "text", "text": prompt}]

        for img in images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{img['mime']};base64,{img['b64']}"
                }
            })

        payload = {
            "model": model or self.vision_model,
            "max_tokens": max_tokens or self.max_tokens_vision,
            "messages": [{"role": "user", "content": content}],
        }

        data = await self._post(payload)
        return data["choices"][0]["message"]["content"]

    async def vision_json(
        self,
        prompt: str,
        images: List[Dict[str, str]],
        model: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Vision call that returns parsed JSON."""
        full_prompt = prompt + "\n\nRespond ONLY with valid JSON, no markdown, no explanation."
        raw = await self.vision(full_prompt, images, model=model)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                return json.loads(match.group())
            raise ValueError(f"Vision model did not return valid JSON: {raw[:300]}")

    # ─────────────────────────────────────────────────
    # Batch / Parallel
    # ─────────────────────────────────────────────────

    async def batch_complete(self, prompts: List[str], system: Optional[str] = None) -> List[str]:
        """Run multiple prompts concurrently."""
        tasks = [self.complete(p, system=system) for p in prompts]
        return await asyncio.gather(*tasks)
