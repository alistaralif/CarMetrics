import asyncio
from playwright.async_api import async_playwright

from app.services.parser import parse_listing


async def fetch_html(context, url: str) -> str:
    page = await context.new_page()
    await page.goto(url, wait_until="domcontentloaded", timeout=60000)

    try:
        await page.wait_for_selector(
            "div[class*='styles_titleContainer__']",
            timeout=3000
        )
    except:
        pass

    html = await page.content()
    await page.close()
    return html

MAX_SAFE_URLS = 20
FETCH_DELAY_SECONDS = 2.5  # Delay between each fetch to avoid rate limiting

async def scrape_listings(urls: list[str]):
    if len(urls) > MAX_SAFE_URLS:
        raise ValueError("URL batch exceeds limit.")
    
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )

        # Sequential fetching with delays to avoid rate limiting
        for i, url in enumerate(urls):
            if i > 0:
                await asyncio.sleep(FETCH_DELAY_SECONDS)
            
            try:
                html = await fetch_html(context, url)
                results.append(parse_listing(html, url))
            except Exception:
                continue  # Skip failed URLs

        await browser.close()

    return results
