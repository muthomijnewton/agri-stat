#!/usr/bin/env python3
"""Fetch the enabled KAMIS market pages, then upsert atomically."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import SessionLocal, engine
from app.db.migrate import migrate_database
from app.models.foundation import DEFAULT_ORGANIZATION_ID
from app.services.live_market_service import load_live_sources, prepare_live_sources


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization", default=DEFAULT_ORGANIZATION_ID)
    parser.add_argument("--replace-demo", action="store_true", help="Delete existing business records, retain login accounts")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--cache-directory", type=Path)
    args = parser.parse_args()
    sources = prepare_live_sources(cache_directory=args.cache_directory)
    if args.dry_run:
        print(json.dumps([{"source": source["source"], "observations": len(source["rows"]),
                           "rejected_rows": len(source["rejects"])} for source in sources]))
        return
    migrate_database(engine)
    with SessionLocal.begin() as db:
        results = load_live_sources(db, sources, organization_id=args.organization, replace_demo=args.replace_demo)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
