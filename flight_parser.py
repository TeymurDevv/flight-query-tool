"""Command-line flight schedule CSV parser and JSON query tool."""

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

from csv_loader import parse_files
from query import run_queries
from validator import load_airports


STUDENT_ID = "251ADB097"
FIRST_NAME = "Teymur"
LAST_NAME = "Suleymanov"


def read_json_file(path: str):
    """Read and decode a JSON file using UTF-8."""
    with open(path, encoding="utf-8") as json_file:
        return json.load(json_file)


def make_argument_parser() -> argparse.ArgumentParser:
    """Build the command-line interface described in the assignment."""
    parser = argparse.ArgumentParser(
        description="Validate flight schedule CSV files and query a JSON database."
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", help="parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", help="parse CSV files in a folder")
    source.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list for CSV input")
    parser.add_argument("-o", metavar="FILE", help="database output path (CSV modes)")
    parser.add_argument("-q", metavar="FILE", help="JSON file containing queries")
    parser.add_argument("-r", metavar="FOLDER", default=".", help="query response folder")
    return parser


def get_csv_paths(folder: str) -> list[str]:
    """Return sorted CSV file paths directly inside a folder."""
    directory = Path(folder)
    if not directory.is_dir():
        raise FileNotFoundError(f"folder does not exist or is not a folder: {folder}")

    paths = sorted(
        str(path)
        for path in directory.iterdir()
        if path.is_file() and path.name.endswith(".csv")
    )
    if not paths:
        raise FileNotFoundError(f"folder contains no .csv files: {folder}")
    return paths


def write_database(path: str, records: list[dict]) -> None:
    """Write flight records as a UTF-8 JSON array."""
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(records, json_file, indent=2, ensure_ascii=False)
        json_file.write("\n")


def load_database(path: str) -> list[dict]:
    """Load a JSON array of flight record objects."""
    database = read_json_file(path)
    if not isinstance(database, list) or any(
        not isinstance(record, dict) for record in database
    ):
        raise ValueError("JSON database must be an array of objects")
    return database


def load_queries(path: str) -> dict | list:
    """Load one query object or an array of query objects from JSON."""
    queries = read_json_file(path)
    if not isinstance(queries, (dict, list)):
        raise ValueError("query file must contain an object or an array")
    return queries


def write_query_response(folder: str, responses: list[dict]) -> str:
    """Write query results to the required timestamped response filename."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    file_name = (
        f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{timestamp}.json"
    )
    response_path = Path(folder) / file_name
    with open(response_path, "w", encoding="utf-8") as response_file:
        json.dump(responses, response_file, indent=2, ensure_ascii=False)
        response_file.write("\n")
    return str(response_path)


def main(argv: list[str] | None = None) -> int:
    """Run the program and return an exit code instead of calling sys.exit."""
    parser = make_argument_parser()
    try:
        args = parser.parse_args(argv)

        if args.i is not None or args.d is not None:
            if args.a is None:
                parser.error("-a FILE is required with -i or -d")
            if args.o is not None and args.j is not None:
                parser.error("-o is only allowed with -i or -d")
        if args.j is not None and args.o is not None:
            parser.error("-o is only allowed with -i or -d")
    except SystemExit as error:
        return int(error.code)

    logger = logging.getLogger("flight_parser")
    handler = None
    old_level = logger.level
    old_propagate = logger.propagate

    try:
        if args.j is not None:
            records = load_database(args.j)
        else:
            if args.i is not None:
                csv_path = Path(args.i)
                if not csv_path.is_file():
                    raise FileNotFoundError(f"CSV file does not exist: {args.i}")
                csv_paths = [str(csv_path)]
            else:
                csv_paths = get_csv_paths(args.d)

            airports = load_airports(args.a)
            records, errors = parse_files(csv_paths, airports)

            database_path = args.o or "db.json"
            database_folder = Path(database_path).parent
            errors_path = database_folder / "errors.log"

            handler = logging.FileHandler(errors_path, mode="w", encoding="utf-8")
            handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s %(levelname)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            logger.setLevel(logging.INFO)
            logger.propagate = False
            logger.addHandler(handler)
            for message in errors:
                logger.warning(message)

            write_database(database_path, records)
            print(f"Saved {len(records)} valid flights to {database_path}.")
            print(f"Logged {len(errors)} invalid rows to {errors_path}.")

        if args.q is not None:
            queries = load_queries(args.q)
            responses = run_queries(records, queries)
            response_path = write_query_response(args.r, responses)
            print(f"Saved query results to {response_path}.")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        message = " ".join(str(error).splitlines())
        print(f"Error: {message}", file=sys.stderr)
        return 1
    finally:
        if handler is not None:
            logger.removeHandler(handler)
            handler.close()
        logger.setLevel(old_level)
        logger.propagate = old_propagate


if __name__ == "__main__":
    sys.exit(main())
