from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from datetime import datetime, timezone

from app.services.scraper import scrape_listings
from app.services.rate_limiter import rate_limiter
from app.db.cache import get_cached_listing, upsert_listing
from app.db.logging import log_api_call

router = APIRouter()

RATE_LIMITS = {
    "free": {"max_urls": 10, "window_seconds": 120},
}

class PrecacheRequest(BaseModel):
    url: str

class PrecacheResponse(BaseModel):
    status: str
    url: str
    cached: bool = False

@router.post(
    "",
    response_model=PrecacheResponse,
    summary="Pre-cache a single car listing URL",
)
async def precache(payload: PrecacheRequest, request: Request):
    """
    Pre-caches a single URL synchronously.
    Returns after scraping completes with success/failure status.
    """
    url = payload.url
    start_time = datetime.now(timezone.utc)
    
    if not url:
        raise HTTPException(status_code=400, detail="URL cannot be empty")
    
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    ip = (
        request.headers.get("fly-client-ip")
        or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (request.client.host if request.client else "unknown")
    )
    
    # Check if already cached
    cached = get_cached_listing(url)
    if cached:
        print(f"[Precache] URL already cached: {url}")
        
        process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
        log_api_call(
            endpoint="/api/precache",
            userrole="free",
            url_count=1,
            process_time=process_time,
            status_code=200,
            status_text="cache_hit",
            ip_address=ip,
            request_id=None,
        )
        
        return PrecacheResponse(status="already_cached", url=url, cached=True)
    
    # Check rate limit
    config = RATE_LIMITS["free"]
    allowed, wait_time = rate_limiter.is_allowed(
        key=ip,
        max_urls=config["max_urls"],
        window_seconds=config["window_seconds"],
        url_count=1
    )
    
    if not allowed:
        print(f"[Precache] Rate limited for IP {ip}, wait {wait_time}s")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Try again in {int(wait_time)} seconds."
        )
    
    # Scrape synchronously
    print(f"[Precache] Scraping: {url}")
    status_text = "success"
    status_code = 200
    cached_successfully = False
    
    try:
        scraped, failed_urls = await scrape_listings([url])
        
        if failed_urls:
            print(f"[Precache] Failed to scrape: {url}")
            status_text = "scrape_failed"
            status_code = 500
        elif scraped and len(scraped) > 0:
            listing = scraped[0]
            if listing and listing.url:
                upsert_listing(listing.url, listing.model_dump())
                print(f"[Precache] Successfully cached: {url}")
                cached_successfully = True
            else:
                print(f"[Precache] Scrape returned empty data: {url}")
                status_text = "empty_data"
                status_code = 500
        else:
            print(f"[Precache] No results returned: {url}")
            status_text = "no_results"
            status_code = 500
            
    except Exception as e:
        print(f"[Precache] Error scraping {url}: {e}")
        status_text = f"error: {str(e)}"
        status_code = 500
    
    # Log the attempt
    process_time = (datetime.now(timezone.utc) - start_time).total_seconds()
    log_api_call(
        endpoint="/api/precache",
        userrole="free",
        url_count=1,
        process_time=process_time,
        status_code=status_code,
        status_text=status_text,
        ip_address=ip,
        request_id=None,
    )
    
    if cached_successfully:
        return PrecacheResponse(status="cached", url=url, cached=True)
    else:
        return PrecacheResponse(status=status_text, url=url, cached=False)