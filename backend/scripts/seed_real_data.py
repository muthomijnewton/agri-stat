#!/usr/bin/env python3
"""Import an attributed HDX/WFP or normalized KAMIS CSV atomically."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.real_data import MAX_BYTES, import_market_rows, parse_rows
from app.models.foundation import DEFAULT_ORGANIZATION_ID
from app.db.database import SessionLocal


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=["hdx", "kamis"], required=True)
    parser.add_argument("--file", type=Path, required=True)
    parser.add_argument("--source-url", required=True, help="Original public dataset URL for provenance")
    parser.add_argument("--organization", default=DEFAULT_ORGANIZATION_ID)
    parser.add_argument("--locations", type=Path, help="CSV: market,latitude,longitude for missing coordinates")
    parser.add_argument("--unit-kg", action="append", default=[], help="Explicit package mapping, e.g. crate=20")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rejects", type=Path, help="Explicitly skip invalid rows and write a JSON rejection report")
    parser.add_argument("--synthesize-opening-days", type=int, default=0,
                        help="Opt-in SIMULATED batches from reported daily volume, never from prices")
    args = parser.parse_args()
    try:
        if args.file.stat().st_size > MAX_BYTES:
            raise ValueError("CSV exceeds 20 MB")
        content = args.file.read_bytes()
        coordinates = {}
        if args.locations:
            with args.locations.open(newline="", encoding="utf-8-sig") as file:
                coordinates = {row["market"]: (row["latitude"], row["longitude"]) for row in csv.DictReader(file)}
        units = dict(value.split("=", 1) for value in args.unit_kg)
        rejects = [] if args.rejects else None
        rows = parse_rows(content, args.source, coordinates=coordinates, custom_kg=units, rejects=rejects)
        if args.rejects:
            args.rejects.write_text(json.dumps(rejects, indent=2))
        if args.dry_run:
            print(json.dumps({"valid_observations": len(rows), "rejected_rows": len(rejects or []), "source": args.source, "database_writes": 0}))
            return
        with SessionLocal.begin() as db:
            result = import_market_rows(db, rows, source=args.source, source_url=args.source_url,
                content_sha256=hashlib.sha256(content).hexdigest(), organization_id=args.organization,
                opening_days=args.synthesize_opening_days)
        print(json.dumps(result))
    except (ValueError, OSError) as error:
        parser.exit(2, f"Import failed: {error}\n")


if __name__ == "__main__":
    main()
