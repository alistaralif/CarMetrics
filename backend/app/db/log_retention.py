import sqlite3
import csv
import gzip
import os
from datetime import datetime, timezone
from pathlib import Path

DATA_DIR = Path("/data") if os.getenv("DATABASE_PATH") else Path(__file__).resolve().parents[2] / "data"
DB_PATH = DATA_DIR / "logging.db"
ARCHIVE_DIR = DATA_DIR / "archives"

def archive_completed_months():
    """
    Archives all completed calendar months into compressed CSV files
    and removes them from logging.db. Keeps the current month live.
    """

    ARCHIVE_DIR.mkdir(exist_ok=True)

    now = datetime.now(timezone.utc)
    current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Find months that have data but are fully completed
    rows = cur.execute("""
        SELECT DISTINCT substr(timestamp, 1, 7) AS month
        FROM api_logs
        WHERE timestamp < ?
        ORDER BY month
    """, (current_month_start.isoformat(),)).fetchall()

    for (month,) in rows:
        # month is 'YYYY-MM'
        archive_path = ARCHIVE_DIR / f"api_logs_{month}.csv.gz"

        # Fetch all logs for that month
        data = cur.execute("""
            SELECT *
            FROM api_logs
            WHERE substr(timestamp, 1, 7) = ?
        """, (month,)).fetchall()

        if not data:
            continue

        # Column names
        columns = [desc[0] for desc in cur.description]

        # Write compressed CSV
        with gzip.open(archive_path, "wt", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(columns)
            writer.writerows(data)

        # Delete archived rows
        cur.execute("""
            DELETE FROM api_logs
            WHERE substr(timestamp, 1, 7) = ?
        """, (month,))

        conn.commit()

    conn.close()
