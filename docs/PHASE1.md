# AgricStat Phase 1 — setup and verification

## Current status

The dashboard uses the Docker API and PostgreSQL. PostgreSQL 16, TimescaleDB and PostGIS,
migrations, authentication, Redis workers and live market imports have been verified. A full
container restart preserved 30,563 public price records and 280 markets. The selected automated
suite passes 53 tests, including the PostgreSQL integration test.

Local Kenya Overpass finished importing and passed live verification on 13 November 2026 at
04:43 Africa/Nairobi. Both direct road inspection and the Docker API/worker job passed, including
PostgreSQL readback and PostGIS geometry validation. Shared public Overpass services returned
capacity errors or timed out; the local service removes that query dependency.

## Start the system

```bash
cd ~/agri-stat
sudo bash infra/start_local_overpass.sh
cd web
npm run dev
```

Open http://localhost:5173/market-prices. The local development login is `admin@agri` / `1234`.
API documentation: http://localhost:8001/docs. The frontend's ignored `web/.env.local` selects
`NEXT_PUBLIC_API_URL=http://localhost:8001/api` (the earlier `VITE_API_URL` remains a compatibility fallback). This stack uses PostgreSQL on host port 5433 and Redis
on port 6380. The separate native SQLite stack is no longer the dashboard's configured backend.

Infrastructure secrets live in ignored `infra/.env`; never commit or publish that file.
Ordinary restarts preserve the named database volumes. Do not use `docker compose down -v`
for routine maintenance: it deletes the saved databases.

## Market data

Update, 15 November 2026: KAMIS is the only enabled market-price source. HDX/WFP is excluded from the application’s price results and refresh jobs. The earlier import totals below are historical verification evidence, not active coverage.

The Market prices page shows source links, publication dates and retrieval times. Administrators
can use **Fetch latest prices**. Failed imports leave previously committed records intact.

- HDX/WFP previously supplied monthly Kenyan food-price history. The verified PostgreSQL import has 29,298
  records, with the latest observation dated 15 October 2026.
- KAMIS supplies recent published pages for seven commodities: maize, tomatoes, Irish potatoes,
  Rosecoco beans, cabbage, dry onions and kale. The verified fresh import has 1,265 distinct quotes,
  with observations through 12 November 2026. This is a recent snapshot, not the complete KAMIS database.
- Repeated imports update matching source keys and retain older observations. Publisher corrections,
  missing values and unlocated markets remain visible; coordinates and demand are never invented.
- Quotes are normalized to known package weights/volumes. Provenance includes the source URL,
  retrieval time and content hash. These public prices do not become business sales or stock.

The fabricated business records were removed. Forecasts and inventory recommendations require
real business activity. No synthetic opening inventory was generated.

## Scheduled workers

Schedules use Africa/Nairobi and run only while their Docker services are running:

| Time | Job |
| --- | --- |
| 05:00 | Weather sync per organization/grid |
| 05:05 | Batch expiry status updates |
| 06:00 | Market-price refresh |

Market imports have a dedicated worker so weather backlogs cannot delay them.

## Local Kenya road data

The Overpass image is pinned to wiktorn/overpass-api v0.7.62.11 and its registry digest. It imports
Geofabrik's public Kenya extract (about 336 MB compressed when checked on 12 November 2026),
then checks regional changes hourly. Initial indexing can take time. Its database lives in the
persistent `overpass_kenya_data` volume. It is limited to 8 GB memory and 2 CPUs.

```bash
cd ~/agri-stat
sudo docker compose --env-file infra/.env -f infra/compose.yaml logs -f --tail=30 overpass
```

Host endpoint: http://127.0.0.1:8082/api/interpreter. Docker API and workers use
`http://overpass/api/interpreter`, selected by `OVERPASS_URL` in `infra/.env`. Native backend tools
use the host endpoint from `backend/.env`. Area generation and historical contributor metadata
are disabled because road inspection uses current road ways and node IDs.

OSRM still supplies driving routes through an external service. Overpass matches the actual
routed node pairs to mapped surface tags. Ratios are weighted by segment distance; untagged or
unmatched segments remain unknown. Surface tags are map observations, not current flood or road
condition reports. Weather-based lead-time adjustment belongs to Phase 2.

Run the uncached live verifier after initialization:

```bash
cd ~/agri-stat
sudo docker compose --env-file infra/.env -f infra/compose.yaml exec api python scripts/verify_live_route.py --origin 36.8172 -1.2864 --destination 36.8200 -1.2830 --report /tmp/live-route-report.json
```

This short Nairobi test corridor is not business supply-route data. The verifier must return
`passed`, a nonempty road-way count, matched surface information and a database roundtrip. All
temporary test records are rolled back. The source timestamp is recorded in its JSON report.
The initial background verification report is saved to `work/local-overpass-verification.json`.

## Foundation and remaining phases

Implemented: organizations, locations, routes, products, inventory batches, weather observations,
public market observations and import provenance; authenticated versioned endpoints with scoped
new entities and admin-only writes; PostGIS geography indexes and a Timescale weather hypertable.

Weather uses approximately 5 km grids. Missing archive values are skipped; forecasts remain
separate from observed weather. Forecast soil moisture estimates are explicitly labelled.
Existing integer product IDs remain compatible with the current clients.

Phase 2 adds weather-aware models, dynamic reorder calculations and FEFO allocation. Phase 3
covers the full dashboard redesign; Phase 4 covers offline mobile synchronization. Phase 5
covers full legacy-API tenant isolation, RLS and production hardening. This development setup
is not a hardened production deployment. No changes have been pushed to GitHub.

## Sources and attribution

- HDX/WFP: https://data.humdata.org/dataset/wfp-food-prices-for-kenya
- KAMIS: https://kamis.kilimo.go.ke/site/market
- Open-Meteo: https://open-meteo.com/en/docs
- OSRM: https://project-osrm.org/docs/v5.24.0/api/
- Overpass container: https://github.com/wiktorn/Overpass-API
- Kenya extracts: https://download.geofabrik.de/africa/kenya.html
- Map data: © OpenStreetMap contributors, ODbL; extracts processed by Geofabrik.

## Resumable import fix — 13 November 2026

The original image restarted interrupted downloads from zero. Container disk-write counters
therefore overstated the size of the current downloaded file. Direct file-size checks and logs
revealed repeated connection resets. The mounted initialization hook now pins the resolved extract
URL, retains partial downloads, resumes using HTTP ranges, and verifies the publisher's MD5
checksum before import. A legacy partial is reused only if the final full checksum matches;
incompatible files are preserved separately before retrying cleanly. Three fault-injection tests
cover resets, reuse of a partial file, and incompatible legacy content.

Apply without deleting the data volume:

```bash
cd ~/agri-stat
sudo docker compose --env-file infra/.env -f infra/compose.yaml up -d --no-deps --force-recreate overpass
sudo docker compose --env-file infra/.env -f infra/compose.yaml logs -f --tail=20 overpass
```

The resumable partial is now `/db/download-cache/kenya.osm.pbf`. The hook logs the byte offset
on each attempt. The import still has to finish and live verification must pass.

## Completed live verification — 13 November 2026

The uncached test route was 4.3456 km. Local Overpass returned 75 road ways in 0.26 seconds,
using OSM data timestamped 12 November 2026 at 16:41:57 UTC. Matched surface classification:
93.71% paved, 0% unpaved, 6.29% unknown. These values apply only to this test route.
The Docker API-to-Celery inspection also succeeded, saved the route, and passed PostGIS geometry
validation. All temporary test records were removed. This resolves the outstanding live Overpass
verification. OSRM remains an external dependency, and map surface tags do not establish current
road conditions. Raw evidence: `work/local-overpass-worker-verification.json`.

## Phase 2 weather-source correction — 13 November 2026

A live archive check found that selecting ERA5-Land alone returns null rainfall even when temperature and soil moisture are present. Current weather ingestion and demand training use Open-Meteo ERA5-Seamless instead. A live three-day Nairobi probe returned rainfall and soil moisture successfully; see `work/phase2-live-weather-check.json`. Missing values remain missing, never zero-imputed.
