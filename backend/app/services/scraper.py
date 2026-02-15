import asyncio
import time
import logging
from playwright.async_api import async_playwright
from dataclasses import dataclass
from typing import Optional

from app.services.parser import parse_listing

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    url: str
    success: bool
    error: Optional[str] = None


async def fetch_html(context, url: str, semaphore: asyncio.Semaphore) -> tuple[str, str, Optional[str]]:
    """Fetch HTML with concurrency control. Returns (url, html, error)."""
    async with semaphore:
        start = time.time()
        logger.info(f"[FETCH] Starting: {url}")
        
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            logger.info(f"[FETCH] Page loaded in {time.time() - start:.2f}s: {url}")

            # Wait for selector but don't block for full timeout
            try:
                await page.wait_for_selector(
                    "div[class*='styles_titleContainer__']",
                    timeout=2000
                )
            except:
                pass

            html = await page.content()
            logger.info(f"[FETCH] Complete in {time.time() - start:.2f}s: {url}")
            return (url, html, None)
        except Exception as e:
            logger.error(f"[FETCH] Failed in {time.time() - start:.2f}s: {url} - {e}")
            return (url, "", str(e))
        finally:
            await page.close()


MAX_SAFE_URLS = 20
MAX_CONCURRENT = 3


async def scrape_listings(urls: list[str]) -> tuple[list, list[str]]:
    """
    Scrape listings and return (results, failed_urls).
    """
    total_start = time.time()
    logger.info(f"[SCRAPER] Starting scrape of {len(urls)} URLs")
    
    if len(urls) > MAX_SAFE_URLS:
        raise ValueError("URL batch exceeds limit.")

    browser_start = time.time()
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
                "--single-process",
                "--disable-software-rasterizer",
            ]
        )
        logger.info(f"[SCRAPER] Browser launched in {time.time() - browser_start:.2f}s")
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Use semaphore to limit concurrent fetches
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # Fetch all URLs in parallel (limited by semaphore)
        fetch_start = time.time()
        tasks = [fetch_html(context, url, semaphore) for url in urls]
        fetched = await asyncio.gather(*tasks)
        logger.info(f"[SCRAPER] All fetches complete in {time.time() - fetch_start:.2f}s")

        await browser.close()

    # Parse results, track failures
    parse_start = time.time()
    results = []
    failed_urls = []
    
    for url, html, fetch_error in fetched:
        if fetch_error or not html:
            failed_urls.append(url)
            logger.error(f"[SCRAPER] Fetch failed for {url}: {fetch_error}")
            continue
        try:
            results.append(parse_listing(html, url))
        except Exception as e:
            failed_urls.append(url)
            logger.error(f"[SCRAPER] Parse failed for {url}: {e}")
            continue
    
    logger.info(f"[SCRAPER] Parsing complete in {time.time() - parse_start:.2f}s")
    logger.info(f"[SCRAPER] Total time: {time.time() - total_start:.2f}s | Success: {len(results)} | Failed: {len(failed_urls)}")

    return results, failed_urls
