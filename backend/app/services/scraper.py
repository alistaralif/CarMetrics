import asyncio
from playwright.async_api import async_playwright

from app.services.parser import parse_listing


async def fetch_html(context, url: str, semaphore: asyncio.Semaphore) -> tuple[str, str]:
    """Fetch HTML with concurrency control. Returns (url, html)."""
    async with semaphore:
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # Wait for selector but don't block for full timeout
            try:
                await page.wait_for_selector(
                    "div[class*='styles_titleContainer__']",
                    timeout=2000
                )
            except:
                pass

            html = await page.content()
            return (url, html)
        finally:
            await page.close()


MAX_SAFE_URLS = 20
MAX_CONCURRENT = 3  # Limit concurrent requests to avoid rate limiting

async def scrape_listings(urls: list[str]):
    if len(urls) > MAX_SAFE_URLS:
        raise ValueError("URL batch exceeds limit.")

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
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Use semaphore to limit concurrent fetches
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        # Fetch all URLs in parallel (limited by semaphore)
        tasks = [fetch_html(context, url, semaphore) for url in urls]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)

        await browser.close()

    # Parse results, skip failures
    results = []
    for item in fetched:
        if isinstance(item, Exception):
            continue
        url, html = item
        try:
            results.append(parse_listing(html, url))
        except Exception:
            continue

    return results
