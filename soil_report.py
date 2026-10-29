import re

from pypdf import PdfReader
from pypdf.errors import PdfReadError

FIELD_LABELS = {
    "ph": r"\bph\b",
    "moisture": r"moisture(?:\s+content)?",
    "temperature": r"temperature",
    "rainfall": r"rainfall",
    "nitrogen": r"nitrogen",
    "phosphorus": r"phosphorus",
    "potassium": r"potassium",
}

VALID_RANGES = {
    "ph": (0, 14),
    "moisture": (0, 100),
    "temperature": (-10, 60),
    "rainfall": (0, 1000),
    "nitrogen": (0, 2000),
    "phosphorus": (0, 2000),
    "potassium": (0, 2000),
}

SOIL_TYPE_ALIASES = [
    ("sandy clay loam", "Sandy Loam"),
    ("sandy loam", "Sandy Loam"),
    ("loamy sand", "Sandy"),
    ("clay loam", "Clay"),
    ("silty clay", "Clay"),
    ("silt loam", "Loam"),
    ("loam", "Loam"),
    ("clay", "Clay"),
    ("sandy", "Sandy"),
]

CLIMATE_ZONES = ["Semi-arid", "Tropical", "Temperate", "Arid"]


def extract_text(stream):
    try:
        reader = PdfReader(stream)
        if reader.is_encrypted:
            raise ValueError("This PDF is password-protected.")
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except PdfReadError:
        raise ValueError("This file could not be read as a PDF.")
    if not text.strip():
        raise ValueError(
            "No text found in this PDF. Scanned reports need OCR, which is not supported."
        )
    return text


def normalise(text):
    text = re.sub(r"\([^)]*\)", " ", text)
    text = re.sub(r"\b(?:P2O5|K2O)\b", " ", text)
    return re.sub(r"\s+", " ", text)


def extract_number(text, label_pattern):
    match = re.search(
        label_pattern + r"[^0-9]{0,40}?(-?\d+(?:\.\d+)?)", text, re.IGNORECASE
    )
    return float(match.group(1)) if match else None


def extract_soil_type(text):
    match = re.search(
        r"soil\s+(?:texture|type|class)\W{0,5}([A-Za-z\- ]{3,30})", text, re.IGNORECASE
    )
    if not match:
        return None
    chunk = match.group(1).lower()
    hits = [
        (chunk.find(needle), -len(needle), name)
        for needle, name in SOIL_TYPE_ALIASES
        if needle in chunk
    ]
    return min(hits)[2] if hits else None


def extract_climate_zone(text):
    match = re.search(
        r"climate(?:\s+zone)?\W{0,5}([A-Za-z\- ]{3,25})", text, re.IGNORECASE
    )
    if not match:
        return None
    chunk = match.group(1).lower().replace("semi arid", "semi-arid")
    for zone in CLIMATE_ZONES:
        if zone.lower() in chunk:
            return zone
    return None


def parse_soil_report(text):
    clean = normalise(text)
    values = {key: extract_number(clean, pattern) for key, pattern in FIELD_LABELS.items()}
    for key, (low, high) in VALID_RANGES.items():
        if values[key] is not None and not low <= values[key] <= high:
            values[key] = None
    values["soil_type"] = extract_soil_type(clean)
    values["location"] = extract_climate_zone(clean)
    return values


def read_soil_report(stream):
    values = parse_soil_report(extract_text(stream))
    found = [key for key, value in values.items() if value is not None]
    missing = [key for key, value in values.items() if value is None]
    return {"values": values, "found": found, "missing": missing}