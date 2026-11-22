"""Load airport codes and validate one flight row at a time."""

import math
import re
from datetime import datetime


DATE_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")
FLIGHT_ID_PATTERN = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT_PATTERN = re.compile(r"[A-Z]{3}")


def load_airports(path: str) -> set[str]:
    """Read airport codes, skipping blank lines and comment lines."""
    with open(path, encoding="utf-8") as airport_file:
        return {
            line.strip()
            for line in airport_file
            if line.strip() and not line.strip().startswith("#")
        }


def parse_datetime(value: str) -> datetime:
    """Parse the exact YYYY-MM-DD HH:MM format used in this project."""
    if not DATE_PATTERN.fullmatch(value):
        raise ValueError("Date and time must use YYYY-MM-DD HH:MM.")
    return datetime.strptime(value, "%Y-%m-%d %H:%M")


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Return the first validation error code, or None when the row is valid."""
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"

    values = [field.strip() for field in fields]
    if any(not value for value in values):
        return "MISSING_FIELD"

    flight_id, origin, destination, departure, arrival, price_text = values

    if not FLIGHT_ID_PATTERN.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not AIRPORT_PATTERN.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT_PATTERN.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    try:
        departure_time = parse_datetime(departure)
    except ValueError:
        return "INVALID_DEPARTURE"

    try:
        arrival_time = parse_datetime(arrival)
    except ValueError:
        return "INVALID_ARRIVAL"

    if arrival_time <= departure_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    try:
        price = float(price_text)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(price):
        return "INVALID_PRICE"
    if price <= 0:
        return "NON_POSITIVE_PRICE"

    return None


def to_record(fields: list[str]) -> dict:
    """Convert a valid CSV row into a flight record dictionary."""
    values = [field.strip() for field in fields]
    return {
        "flight_id": values[0],
        "origin": values[1],
        "destination": values[2],
        "departure_datetime": values[3],
        "arrival_datetime": values[4],
        "price": float(values[5]),
    }
