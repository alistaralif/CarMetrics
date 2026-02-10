from fastapi import APIRouter
from app.api.routes import scrape

api_router = APIRouter()

# Scraping and ingestion endpoints
api_router.include_router(
    scrape.router,
    prefix="/scrape",
    tags=["scrape"],
)