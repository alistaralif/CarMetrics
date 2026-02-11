import sqlite3
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import os

# Use mounted volume path in production, local path in development
DATA_DIR = Path("/data") if os.getenv("DATABASE_PATH") else Path(__file__).resolve().parents[2] / "data"

DB_PATH = DATA_DIR / "cache.db"
TTL_HOURS = 24 * 3 # 3 days

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_cache_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            url TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            scraped_at TEXT NOT NULL
        )
        """)
        
def get_cached_listing(url: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT data, scraped_at FROM listings WHERE url = ?",
            (url,)
        ).fetchone()

    if not row:
        return None

    data_json, scraped_at = row
    scraped_time = datetime.fromisoformat(scraped_at)

    if datetime.now(timezone.utc) - scraped_time > timedelta(hours=TTL_HOURS):
        return None

    return json.loads(data_json)

def upsert_listing(url: str, listing_dict: dict):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO listings (url, data, scraped_at)
        VALUES (?, ?, ?)
        ON CONFLICT(url) DO UPDATE SET
            data = excluded.data,
            scraped_at = excluded.scraped_at
        """, (
            url,
            json.dumps(listing_dict),
            datetime.now(timezone.utc).isoformat()
        ))