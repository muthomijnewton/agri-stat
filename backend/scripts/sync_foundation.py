#!/usr/bin/env python3
"""Run a weather-grid or road-profile sync directly, without a queue."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import SessionLocal
from app.models.foundation import DEFAULT_ORGANIZATION_ID, Location, SupplyRoute
from app.services.weather_service import sync_location_weather
from app.services.routing_service import inspect_route


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--weather-location")
    group.add_argument("--route")
    parser.add_argument("--organization", default=DEFAULT_ORGANIZATION_ID)
    args = parser.parse_args()
    with SessionLocal.begin() as db:
        model, identifier, sync = (Location, args.weather_location, sync_location_weather) if args.weather_location else (SupplyRoute, args.route, inspect_route)
        record = db.get(model, identifier)
        if record is None or record.organization_id != args.organization:
            parser.error("Record not found in this organization")
        result = sync(db, record)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
