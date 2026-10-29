import csv
import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")
CSV_PATH = os.path.join(os.path.dirname(__file__), "crops.csv")

COLUMNS = [
    "crop_name", "ph_min", "ph_max", "moisture_min", "moisture_max",
    "soil_type", "temperature_min", "temperature_max", "rainfall_min",
    "rainfall_max", "location", "month_start", "month_end",
    "nitrogen", "phosphorus", "potassium",
]

TEXT_COLUMNS = ["crop_name", "soil_type", "location"]
NUMERIC_COLUMNS = [c for c in COLUMNS if c not in TEXT_COLUMNS]
MIN_MAX_PAIRS = [
    ("ph_min", "ph_max"),
    ("moisture_min", "moisture_max"),
    ("temperature_min", "temperature_max"),
    ("rainfall_min", "rainfall_max"),
]

INSERT_SQL = f"""
    INSERT INTO crops ({", ".join(COLUMNS)})
    VALUES ({", ".join(["%s"] * len(COLUMNS))})
"""

def clean_text(row):
    for col in TEXT_COLUMNS:
        value = (row.get(col) or "").strip()
        row[col] = " ".join(value.split()).title()
    return row


def convert_numeric(row):
    for col in NUMERIC_COLUMNS:
        value = (row.get(col) or "").strip()
        try:
            row[col] = float(value)
        except ValueError:
            row[col] = None
    return row


def swap_min_max(row):
    for low, high in MIN_MAX_PAIRS:
        if row[low] is not None and row[high] is not None and row[low] > row[high]:
            row[low], row[high] = row[high], row[low]
    return row


def is_valid(row):
    if not row["crop_name"]:
        return False
    required = [c for pair in MIN_MAX_PAIRS for c in pair]
    if any(row[c] is None for c in required):
        return False
    if not (0 <= row["ph_min"] <= 14 and 0 <= row["ph_max"] <= 14):
        return False
    if not (0 <= row["moisture_min"] <= 100 and 0 <= row["moisture_max"] <= 100):
        return False
    for col in ["month_start", "month_end"]:
        if row[col] is not None and not (1 <= row[col] <= 12):
            return False
    for col in ["nitrogen", "phosphorus", "potassium", "rainfall_min", "rainfall_max"]:
        if row[col] is not None and row[col] < 0:
            return False
    return True


def remove_duplicates(rows):
    seen = set()
    unique = []
    for row in rows:
        key = row["crop_name"].lower()
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique


def fill_missing_nutrients(rows):
    for col in ["nitrogen", "phosphorus", "potassium"]:
        values = [r[col] for r in rows if r[col] is not None]
        avg = sum(values) / len(values) if values else 0
        for r in rows:
            if r[col] is None:
                r[col] = round(avg, 2)
    return rows


def clean_rows(raw_rows):
    cleaned = []
    for row in raw_rows:
        row = clean_text(row)
        row = convert_numeric(row)
        row = swap_min_max(row)
        if is_valid(row):
            cleaned.append(row)
    cleaned = remove_duplicates(cleaned)
    cleaned = fill_missing_nutrients(cleaned)
    return cleaned


def main():
    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env and fill in "
            "your Neon Postgres connection string."
        )

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        raw_rows = list(csv.DictReader(f))

    cleaned = clean_rows(raw_rows)
    rows = [tuple(row[col] for col in COLUMNS) for row in cleaned]
    print(f"Read {len(raw_rows)} rows, kept {len(rows)} after cleaning.")

    conn = psycopg2.connect(DATABASE_URL, sslmode="require")
    cur = conn.cursor()
    cur.executemany(INSERT_SQL, rows)
    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted {len(rows)} crops into the database.")


if __name__ == "__main__":
    main()