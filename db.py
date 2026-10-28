import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill in "
            "your Neon Postgres connection string."
        )
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def fetch_all_crops():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM crops ORDER BY id;")
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()