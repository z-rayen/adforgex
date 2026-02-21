"""
scraper/scraper.py — HTTP scraper with image extraction

Scrapes text + images from competitor pages.
Images are downloaded and returned as base64 for vision analysis.
"""
import logging
import base64
import re
import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from urllib.parse import quote_plus, urljoin

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=2)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
}


def _get(url: str, timeout: int = 15) -> BeautifulSoup | None:
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return BeautifulSoup(r.text, "lxml")
    except Exception as e:
        logger.warning(f"GET failed [{url[:60]}]: {e}")
        return None


def _download_image_b64(url: str, timeout: int = 10) -> Dict[str, str] | None:
    """Download an image URL and return as base64 dict."""
    try:
        from PIL import Image
        import io
        r = requests.get(url, headers=HEADERS, timeout=timeout, stream=True)
        if r.status_code != 200:
            return None
        mime = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        if not mime.startswith("image/"):
            return None
        img_data = r.content
        if len(img_data) < 5000:  # skip tiny icons
            return None
        # Resize if too large
        try:
            img = Image.open(io.BytesIO(img_data))
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            if max(img.size) > 1024:
                img.thumbnail((1024, 1024), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=82)
            img_data = buf.getvalue()
            mime = "image/jpeg"
        except Exception:
            pass
        return {
            "b64": base64.b64encode(img_data).decode(),
            "mime": mime,
            "url": url,
        }
    except Exception as e:
        logger.debug(f"Image download failed [{url[:50]}]: {e}")
        return None


def _extract_images_from_soup(
    soup: BeautifulSoup,
    base_url: str,
    max_images: int = 5,
    timeout: int = 10,
) -> List[Dict[str, str]]:
    """
    Extract and download meaningful product/ad images from a page.
    Filters out icons, logos, and tiny images.
    """
    images = []
    seen_urls = set()

    for img_tag in soup.find_all("img"):
        if len(images) >= max_images:
            break

        src = img_tag.get("src") or img_tag.get("data-src") or img_tag.get("data-lazy-src")
        if not src:
            continue

        # Build absolute URL
        if src.startswith("//"):
            src = "https:" + src
        elif src.startswith("/"):
            src = urljoin(base_url, src)
        elif not src.startswith("http"):
            continue

        if src in seen_urls:
            continue
        seen_urls.add(src)

        # Skip obvious non-product images
        skip_keywords = ["logo", "icon", "sprite", "pixel", "tracker", "1x1", "badge", "star", "rating"]
        if any(kw in src.lower() for kw in skip_keywords):
            continue

        # Check width/height attributes — skip small images
        try:
            w = int(img_tag.get("width", 0))
            h = int(img_tag.get("height", 0))
            if (w > 0 and w < 100) or (h > 0 and h < 100):
                continue
        except Exception:
            pass

        result = _download_image_b64(src, timeout=timeout)
        if result:
            images.append(result)
            logger.debug(f"Image captured: {src[:60]}")

    return images


def _scrape_google(query: str, timeout: int) -> tuple[List[str], List[Dict]]:
    ads, images = [], []
    soup = _get(
        f"https://www.google.com/search?q={quote_plus(query + ' buy review')}&num=20",
        timeout,
    )
    if not soup:
        return ads, images
    for r in soup.select("div.g"):
        title = r.select_one("h3")
        snippet = r.select_one(".VwiC3b, .s3v9rd, .st")
        if title and snippet:
            ads.append(f"{title.get_text()} — {snippet.get_text()}")
    logger.info(f"Google: {len(ads)} results")
    return ads, images


def _scrape_amazon(query: str, timeout: int) -> tuple[List[str], List[str], List[Dict]]:
    ads, comments, images = [], [], []

    soup = _get(f"https://www.amazon.com/s?k={quote_plus(query)}", timeout)
    if not soup:
        return ads, comments, images

    for item in soup.select("[data-component-type='s-search-result']"):
        title_el = item.select_one("h2 span")
        if title_el:
            ads.append(title_el.get_text(strip=True))

    product_links = []
    for a in soup.select("a.a-link-normal.s-underline-text"):
        href = a.get("href", "")
        if "/dp/" in href:
            full = "https://www.amazon.com" + href.split("?")[0]
            if full not in product_links:
                product_links.append(full)
        if len(product_links) >= 3:
            break

    for url in product_links[:2]:
        psoup = _get(url, timeout)
        if not psoup:
            continue
        for b in psoup.select("#feature-bullets li span.a-list-item"):
            t = b.get_text(strip=True)
            if len(t) > 20:
                ads.append(t)
        for rev in psoup.select("[data-hook='review-body'] span"):
            t = rev.get_text(strip=True)
            if len(t) > 30:
                comments.append(t[:500])
        desc = psoup.select_one("#productDescription p")
        if desc:
            ads.append(desc.get_text(strip=True)[:300])

        # Extract product images
        page_images = _extract_images_from_soup(
            psoup, url, max_images=3, timeout=timeout
        )
        images.extend(page_images)

    logger.info(f"Amazon: {len(ads)} bullets, {len(comments)} reviews, {len(images)} images")
    return ads, comments, images


def _scrape_reddit(query: str, timeout: int) -> tuple[List[str], List[Dict]]:
    comments, images = [], []
    try:
        r = requests.get(
            f"https://www.reddit.com/search.json?q={quote_plus(query)}&sort=relevance&limit=25",
            headers={**HEADERS, "Accept": "application/json"},
            timeout=timeout,
        )
        if r.status_code == 200:
            for post in r.json().get("data", {}).get("children", []):
                data = post["data"]
                selftext = data.get("selftext", "")
                title = data.get("title", "")
                if len(selftext) > 30:
                    comments.append(selftext[:500])
                elif title:
                    comments.append(title)
                # Reddit post images
                url = data.get("url", "")
                if url and any(url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                    img = _download_image_b64(url, timeout=timeout)
                    if img:
                        images.append(img)
    except Exception as e:
        logger.warning(f"Reddit JSON API failed: {e}")
    logger.info(f"Reddit: {len(comments)} comments, {len(images)} images")
    return comments, images


def _scrape_bing(query: str, timeout: int) -> List[str]:
    ads = []
    soup = _get(
        f"https://www.bing.com/search?q={quote_plus(query + ' advertisement buy')}",
        timeout,
    )
    if not soup:
        return ads
    for result in soup.select(".b_algo"):
        title = result.select_one("h2")
        snippet = result.select_one(".b_caption p")
        if title and snippet:
            ads.append(f"{title.get_text()} — {snippet.get_text()}")
    logger.info(f"Bing: {len(ads)} results")
    return ads


def _scrape_sync(query: str, category: str, timeout: int) -> Dict[str, Any]:
    logger.info(f"Scraper thread started: '{query[:60]}'")
    ads, comments, images = [], [], []

    try:
        g_ads, g_imgs = _scrape_google(query, timeout)
        ads.extend(g_ads)
        images.extend(g_imgs)

        a_ads, a_comments, a_imgs = _scrape_amazon(query, timeout)
        ads.extend(a_ads)
        comments.extend(a_comments)
        images.extend(a_imgs)

        r_comments, r_imgs = _scrape_reddit(query, timeout)
        comments.extend(r_comments)
        images.extend(r_imgs)

        b_ads = _scrape_bing(query, timeout)
        ads.extend(b_ads)

        logger.info(
            f"Scraper done: {len(ads)} ads, {len(comments)} comments, {len(images)} images"
        )
    except Exception as e:
        logger.error(f"Scraper error: {e}\n{traceback.format_exc()}")
        raise

    return {
        "ads": ads[:20],
        "comments": comments[:50],
        "images": images[:5],  # max 5 images for vision model
        "raw_text": "\n\n".join(
            [f"AD: {a}" for a in ads[:20]] +
            [f"COMMENT: {c}" for c in comments[:50]]
        ),
    }


class AdScraper:
    def __init__(self, timeout: int = 15, headless: bool = True):
        self.timeout = timeout

    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

    async def scrape_all(self, query: str, category: str, max_results: int = 10) -> Dict[str, Any]:
        logger.info(f"Scraper: dispatching for '{query[:60]}'")
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor, _scrape_sync, query, category, self.timeout
        )
        return result


async def download_images_as_b64(image_urls: List[str], max_images: int = 5) -> List[Dict[str, str]]:
    import httpx
    from PIL import Image
    import io
    results = []
    async with httpx.AsyncClient(timeout=10) as client:
        for url in image_urls[:max_images]:
            try:
                r = await client.get(url, follow_redirects=True)
                if r.status_code != 200: continue
                mime = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
                if not mime.startswith("image/"): continue
                img_data = r.content
                try:
                    img = Image.open(io.BytesIO(img_data))
                    if img.mode in ("RGBA", "P"): img = img.convert("RGB")
                    if max(img.size) > 1024:
                        img.thumbnail((1024, 1024), Image.LANCZOS)
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=82)
                    img_data = buf.getvalue()
                    mime = "image/jpeg"
                except Exception: pass
                results.append({"b64": base64.b64encode(img_data).decode(), "mime": mime})
            except Exception as e:
                logger.warning(f"Image download: {e}")
    return results