"""Filter and sort flight records using JSON query objects."""

import math

from validator import parse_datetime


RECORD_KEYS = {
    "flight_id",
    "origin",
    "destination",
    "departure_datetime",
    "arrival_datetime",
    "price",
}
QUERY_KEYS = RECORD_KEYS | {"min_price", "sort_by", "order", "limit"}
STRING_KEYS = {"flight_id", "origin", "destination"}
DATETIME_KEYS = {"departure_datetime", "arrival_datetime"}


def is_number(value: object) -> bool:
    """Return True for finite JSON-style numeric values, excluding booleans."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def is_valid_query(query: object) -> bool:
    """Check allowed query keys, value types, and option combinations."""
    if not isinstance(query, dict) or any(key not in QUERY_KEYS for key in query):
        return False

    for key, value in query.items():
        if key in STRING_KEYS and not isinstance(value, str):
            return False
        if key in DATETIME_KEYS:
            if not isinstance(value, str):
                return False
            try:
                parse_datetime(value)
            except ValueError:
                return False
        if key in {"price", "min_price"} and not is_number(value):
            return False
        if key == "sort_by" and (
            not isinstance(value, str) or value not in RECORD_KEYS
        ):
            return False
        if key == "order" and (
            not isinstance(value, str) or value not in {"asc", "desc"}
        ):
            return False
        if key == "limit" and (type(value) is not int or value < 0):
            return False

    if "order" in query and "sort_by" not in query:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return matching full flight records for one query object."""
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    matches = []
    for flight in db:
        if "flight_id" in query and flight["flight_id"] != query["flight_id"]:
            continue
        if "origin" in query and flight["origin"] != query["origin"]:
            continue
        if "destination" in query and flight["destination"] != query["destination"]:
            continue
        if (
            "departure_datetime" in query
            and flight["departure_datetime"] < query["departure_datetime"]
        ):
            continue
        if (
            "arrival_datetime" in query
            and flight["arrival_datetime"] > query["arrival_datetime"]
        ):
            continue
        if "price" in query and flight["price"] > query["price"]:
            continue
        if "min_price" in query and flight["price"] < query["min_price"]:
            continue
        matches.append(flight)

    if "sort_by" in query:
        matches = sorted(
            matches,
            key=lambda flight: flight[query["sort_by"]],
            reverse=query.get("order", "asc") == "desc",
        )

    if "limit" in query:
        matches = matches[: query["limit"]]

    return {"query": query, "matches": matches}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept a query object or list and always return a list of responses."""
    if isinstance(queries, list):
        return [run_query(db, query) for query in queries]
    return [run_query(db, queries)]
