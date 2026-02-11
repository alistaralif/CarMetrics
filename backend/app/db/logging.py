import sqlite3
import os
from datetime import datetime, timezone
from pathlib import Path

# Use mounted volume path in production, local path in development
DATA_DIR = Path(os.getenv("DATABASE_PATH", Path(__file__).resolve().parents[2] / "data")).parent
if os.getenv("DATABASE_PATH"):
    DATA_DIR = Path("/data")

DB_PATH = DATA_DIR / "logging.db"
ARCHIVE_DIR = DATA_DIR / "archives"

def get_conn():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_logging_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS api_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            request_id TEXT,
            ip_address TEXT,
            userrole TEXT,
            endpoint TEXT NOT NULL,
            url_count INTEGER,
            process_time REAL,
            status_code INTEGER,
            status_text TEXT
        );
        """)

def log_api_call(
    endpoint: str,
    userrole: str,
    url_count: int,
    process_time: float,
    status_code: int,
    status_text: str,
    ip_address: str | None,
    request_id: str | None,
):
    with get_conn() as conn:
        conn.execute("""
        INSERT INTO api_logs (
            timestamp,
            endpoint,
            userrole,
            url_count,
            process_time,
            status_code,
            status_text,
            ip_address,
            request_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            datetime.now(timezone.utc).isoformat(),
            endpoint,
            userrole,
            url_count,
            process_time,
            status_code,
            status_text,
            ip_address,
            request_id
        ))