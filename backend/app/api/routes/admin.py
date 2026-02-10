from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

BASE_DIR = Path(__file__).resolve().parents[3]
ARCHIVE_DIR = BASE_DIR / "data" / "archives"

@router.get("/logs/{filename}")
def download_log_archive(filename: str):
    path = ARCHIVE_DIR / filename
    # filename: api_logs_{YYYY-MM}.csv.gz"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Archive not found")

    return FileResponse(
        path,
        media_type="application/gzip",
        filename=filename,
    )