#!/usr/bin/env python3
"""Uncached live route verification. Test database records are always rolled back."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import SessionLocal
from app.models.foundation import DEFAULT_ORGANIZATION_ID, Location, SupplyRoute
from app.services.external_data import fetch_json
from app.services.routing_service import inspect_route
from app.services.weather_service import weather_grid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--origin', nargs=2, type=float, required=True, metavar=('LONGITUDE', 'LATITUDE'))
    parser.add_argument('--destination', nargs=2, type=float, required=True, metavar=('LONGITUDE', 'LATITUDE'))
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    for lon, lat in (args.origin, args.destination):
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            parser.error('Coordinates outside valid longitude/latitude range')
    report = {'checked_at': datetime.now(timezone.utc).isoformat(), 'status': 'failed',
              'requests': [], 'test_records': 'rolled back'}

    def live_fetch(url, **kwargs):
        entry = {'provider_host': urlsplit(url).hostname, 'method': 'POST' if kwargs.get('data') else 'GET'}
        report['requests'].append(entry)
        start = time.monotonic()
        try:
            result = fetch_json(url, cache_seconds=0, **kwargs)
            entry['received'] = True
            if kwargs.get('data'):
                entry['road_ways'] = sum(e.get('type') == 'way' for e in result.get('elements', []))
                entry['osm_timestamp'] = result.get('osm3s', {}).get('timestamp_osm_base')
            return result
        except Exception as exc:
            entry['error_type'] = type(exc).__name__
            response = getattr(exc, 'response', None)
            if response is not None:
                entry['http_status'] = response.status_code
            raise
        finally:
            entry['seconds'] = round(time.monotonic() - start, 2)

    try:
        with SessionLocal() as db:
            try:
                endpoints = []
                for name, (lon, lat) in [('origin', args.origin), ('destination', args.destination)]:
                    row = Location(name='Live verification ' + name, location_type='MARKET',
                        latitude=lat, longitude=lon, weather_grid_key=weather_grid(lat, lon)[0],
                        organization_id=DEFAULT_ORGANIZATION_ID)
                    db.add(row)
                    endpoints.append(row)
                db.flush()
                route = SupplyRoute(name='Temporary live verification route',
                    origin_location_id=endpoints[0].id, dest_location_id=endpoints[1].id,
                    base_lead_time_days=1, organization_id=DEFAULT_ORGANIZATION_ID)
                db.add(route)
                db.flush()
                report['route'] = inspect_route(db, route, fetch=live_fetch)
                db.expire(route)
                assert route.route_geometry and route.inspected_at and route.total_distance_km > 0
                report['database_roundtrip'] = True
                if not sum(entry.get('road_ways', 0) for entry in report['requests']):
                    raise ValueError('No road ways returned; live enrichment not verified')
                if route.unknown_surface_ratio >= 1:
                    raise ValueError('No matched surface tags; classification remains unverified')
                report['status'] = 'passed'
            finally:
                db.rollback()
    except Exception as exc:
        report['error_type'] = type(exc).__name__
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
