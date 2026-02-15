from fastapi import APIRouter
from app.api.routes import scrape, precache

api_router = APIRouter()

# Scraping and ingestion endpoints
api_router.include_router(
    scrape.router,
    prefix="/scrape",
    tags=["scrape"],
)

# Pre-caching endpoint
api_router.include_router(
    precache.router,
    prefix="/precache",
    tags=["precache"],
)