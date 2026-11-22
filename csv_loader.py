"""Read flight CSV files, validate their rows, and find duplicates."""

import csv
from pathlib import Path

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Return valid flight records and one error message per invalid row."""
    records = []
    errors = []
    seen_flights = set()

    for path in paths:
        file_name = Path(path).name
        with open(path, encoding="utf-8", newline="") as csv_file:
            for line_number, line in enumerate(csv_file, start=1):
                if line_number == 1:
                    continue
                if not line.strip() or line.lstrip().startswith("#"):
                    continue

                original_line = line.rstrip("\r\n")
                try:
                    fields = next(csv.reader([line]))
                except (csv.Error, StopIteration):
                    fields = []

                error_code = validate_row(fields, airports)
                if error_code is not None:
                    errors.append(
                        f"{file_name}:{line_number}: {error_code} | {original_line}"
                    )
                    continue

                record = to_record(fields)
                duplicate_key = (record["flight_id"], record["departure_datetime"])
                if duplicate_key in seen_flights:
                    errors.append(
                        f"{file_name}:{line_number}: DUPLICATE_FLIGHT | {original_line}"
                    )
                    continue

                seen_flights.add(duplicate_key)
                records.append(record)

    return records, errors
