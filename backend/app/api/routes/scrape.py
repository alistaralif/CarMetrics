from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional

from app.models.car import CarListing
from app.services.scraper import scrape_listings
from app.services.rate_limiter import rate_limiter
from app.db.cache import get_cached_listing, upsert_listing

router = APIRouter()

RATE_LIMITS = {
    "free": {"max_urls": 10, "window_seconds": 120},
    "premium": {"max_urls": 20, "window_seconds": 120},
}

class ScrapeRequest(BaseModel):
    urls: List[str]
    userrole: str = "free"

class ScrapeResponse(BaseModel):
    results: List[CarListing]
    failed_urls: List[str] = []
    message: Optional[str] = None

@router.post(
    "",
    response_model=ScrapeResponse,
    summary="Scrape and analyse car listings",
)
async def scrape(payload: ScrapeRequest, request: Request):
    """
    Scrapes a batch of car listing URLs with role-based limits.
    """
    urls = payload.urls
    role = payload.userrole.lower()

    if not urls:
        raise HTTPException(status_code=400, detail="URL list cannot be empty. Paste at least one URL from Sgcarmart and press Enter.")

    config = RATE_LIMITS.get(role, RATE_LIMITS["free"])
    
    ip = (
        request.headers.get("fly-client-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )
    
    # Check cache first
    results = []
    urls_to_scrape = []
    
    for url in urls:
        cached = get_cached_listing(url)
        if cached:
            results.append(cached)
        else:
            urls_to_scrape.append(url)
    
    failed_urls = []
    
    # Only rate limit and scrape uncached URLs
    if urls_to_scrape:
        allowed, wait_time = rate_limiter.is_allowed(
            key=ip,
            max_urls=config["max_urls"],
            window_seconds=config["window_seconds"],
            url_count=len(urls_to_scrape)
        )
        
        if not allowed:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {int(wait_time)} seconds."
            )
        
        # Scrape uncached URLs
        scraped, failed_urls = await scrape_listings(urls_to_scrape)
        
        # Cache the new results (only successful ones with valid data)
        for listing in scraped:
            if listing and listing.url:
                upsert_listing(listing.url, listing.model_dump())
        
        results.extend(scraped)

    # Attach metadata for logging
    request.state.userrole = role
    request.state.url_count = len(urls)
    
    message = None
    if failed_urls:
        message = f"{len(failed_urls)} link(s) could not be scraped"
    
    return ScrapeResponse(
        results=results,
        failed_urls=failed_urls,
        message=message
    )