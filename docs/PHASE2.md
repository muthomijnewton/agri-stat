# Phase 2 — Farm demand and replenishment

Updated 13 November 2026 (Africa/Nairobi).

## What this delivery implements

The first business is a farm selling its produce. Two pages now support that workflow:

- **Farm stock & sales** records harvest receipts and real sales, deducting the earliest-expiring usable batches first (FEFO).
- **Demand planning** confirms daily totals, submits background model training, displays evaluation and 14-day P10/P50/P90 forecasts when a model passes, and requests weather-adjusted purchased-stock plans.

These features were introduced in the React application during Phase 2. Phase 3 now hosts the responsive workspace through Next.js; see [the dashboard guide](PHASE3.md). The older Transactions, Forecasts and Recommendations screens use the original ledger; use the new pages for this farm workflow. Their figures are not silently combined.

## Completion has three separate meanings

1. **Engineering:** the ledger, training pipeline, validation gate, planning formulas, API, migrations and basic web workflow are implemented.
2. **Deployment:** verified on 14 November 2026. The running API exposes Phase 2 endpoints, the database is at migration 0005, the application worker registers the new tasks, and PostgreSQL integration tests pass.
3. **Farm validation:** a real farm model must be trained and checked on genuine records. The project does not currently have the required confirmed farm history. Do not describe test-fixture accuracy as real farm accuracy or mark this acceptance item complete.

No synthetic farm history is seeded. Historical price observations remain market observations. Test fixtures live only in isolated test databases.

## From harvest to prediction

### 1. Set up real locations and produce

Create the farm using its verified coordinates. A product's base unit must match its quantities: kilograms, litres or individual units. Configure shelf life and temperature limits only when appropriate for the actual crop, handling and storage conditions.

Create a second verified location and a connecting supply route through the local API documentation. Enter the usual delivery lead time in **days**, including handling/loading if relevant. Request a road inspection to obtain route geometry and the paved, unpaved and unknown surface fractions.

### 2. Record harvest receipts

A receipt creates an inventory batch, not income. Record the batch code, quantity, unit cost, arrival time and known expiry. Unknown expiry is shown explicitly; it is not proof that produce cannot spoil. Product shelf life and a particular batch's expiry are different pieces of information.

### 3. Record sales

A sale records quantity and selling price and consumes real stock. The API excludes synthetic, expired and not-yet-received batches. It uses known earliest expiry first, then batches without an expiry. A sale spanning several batches retains each allocation for audit.

For example, a 15 kg sale could use 10 kg from an earlier-expiring batch and 5 kg from a later one. This is an explanation, not a record inserted into your farm.

PostgreSQL commits the entire sale together. A shortage in any item rolls back the whole cart. Concurrent requests cannot oversell the same stock. Replaying the same event ID and payload returns the existing sale; changing the payload under that ID is rejected. The browser preserves an uncertain submission in the current tab's session storage so a network retry uses the same ID. This is not the full offline mobile outbox planned for Phase 4.

### 4. Confirm completed days

A manager confirms yesterday's total only after reconciling all sales. The ledger option calculates the quantity automatically using Africa/Nairobi day boundaries. Historical daily totals may be entered from a genuine farm record, with a source note. They do not create receipts or alter current stock.

Explicit zero-sale days are valid. Missing dates are not automatically zero. Flag stockout days because observed sales can understate actual demand when stock is unavailable. Records cannot silently overwrite an already-confirmed day; a correction workflow is still needed before routine operational adoption.

The initial training policy requires at least **120 consecutive confirmed days through yesterday**, with no flagged stockouts in the selected period. It uses at most the latest 365 records. This is a software eligibility threshold, not a statistical guarantee. It does not establish annual seasonality or solve demand censored by stockouts.

### 5. Train in the background

The API saves a run and sends its ID to Celery through Redis. A worker reads the organization's daily totals, downloads historical Open-Meteo ERA5-Seamless reanalysis for the farm, route origin and route midpoint, then trains the models. The wetter origin/midpoint value is used for route rainfall. These are coarse modelled weather estimates, not measurements from a sensor on the farm or every point on the route.

Features include weekday, month, lagged sales, rolling sales, 7/14-day rainfall totals, soil moisture and 3-day route rainfall. Demand features lag **14 days** and weather features lag **21 days**. This deliberate first-version choice keeps every regressor knowable for the whole 14-day forecast and allows for delayed weather archives. It sacrifices sensitivity to immediate changes. Fresh future weather drives transit planning separately; it is not used to invent historical knowledge during backtesting.

LightGBM trains three quantile models. Prophet provides a second candidate with an 80% predictive interval and lagged regressors. Weekly seasonality is enabled; annual seasonality is not asserted from a short history. Predictions are clipped to nonnegative values and ordered to prevent crossing ranges.

### 6. Test before accepting

The last 14 days are hidden during fitting. Both candidates are compared with a weekly-repeat baseline whose intervals are estimated from earlier weekly residuals.

- **MAE:** average quantity error, in the product's base units per day.
- **Pinball loss:** evaluates the three quantiles, penalizing errors according to their quantile.
- **MAPE:** shown only on nonzero-demand days, with the count of excluded zero days; division by zero is not hidden.
- **Coverage:** how often observed demand fell inside P10–P90 on the holdout.

A candidate must be no worse than the baseline on both MAE and average pinball loss. Among passing candidates, the lower pinball loss wins. The winner is refitted on the available history to forecast the next 14 days. A failed candidate does not automatically publish an optimistic forecast.

The stored run contains evaluation results, input snapshots and their SHA-256 fingerprint, the selected model's serialized text/JSON artifact, package version and forecast. Artifacts remain in PostgreSQL, not in a temporary worker directory. This supports inspection and reproducibility; exact results may still depend on runtime/library versions.

**One holdout is a first acceptance check, not proof of dependable long-term accuracy.** Repeated rolling evaluation and monitoring remain production-hardening work. P10/P50/P90 are estimated predictive quantiles, not guaranteed minimum/maximum sales.

### 7. Calculate purchased-stock planning

For purchased replenishment, the selected route must point into the farm (the farm is the destination). Outbound routes remain usable for demand training and dispatch context. The worker requires a validated forecast starting today, road inspection no older than 30 days, and fresh 14-day route weather. Missing weather or insufficient forecast coverage blocks the plan. The adjusted lead time plus the 7-day review period must fit within the forecast horizon.

The blueprint formulas are implemented with explicit assumptions:

- Rain severity rises from zero at 15 mm of three-day rainfall to one at 50 mm.
- Adjusted lead time = base time × (1 + 1.5 × effective unpaved fraction × rain severity).
- Unknown surfaces are conservatively included in that effective fraction, and the assumption is reported.
- Reorder point = median average daily demand × adjusted lead time + safety stock.
- Safety stock = 1.645 × historical daily demand standard deviation × square root of lead time.
- Order target covers lead time plus a 7-day review period.
- The shelf-life cap subtracts stock expected to remain when the shipment arrives, avoiding double-counting that stock as spare capacity.
- If the delivery reaches the shelf-life limit, suggested purchase quantity is zero.
- More than half the shelf life in transit, or heat above the product limit, raises a HIGH risk flag.

The constants are **uncalibrated blueprint heuristics**. Historical demand variability is a proxy, not a measured lead-time forecast-error distribution. Confirm transport times, crop handling, shelf-life origin and supplier commitments before using the result commercially. Existing batches are counted if usable now; expiry before later demand, outstanding purchase orders and stock reservations need manual review. The saved plan is timestamped and must be recalculated after stock changes.

For a farm that only sells what it grows, use demand estimates to plan sales and dispatch. Purchased replenishment applies if the farm buys produce from other growers or aggregates produce. This system does not yet predict yields, planting dates, crop growth or time to the next harvest.

## Local deployment

From the project directory:

```bash
cd ~/agri-stat
sudo docker compose --env-file infra/.env -f infra/compose.yaml up --build -d
sudo docker compose --env-file infra/.env -f infra/compose.yaml ps -a
sudo docker compose --env-file infra/.env -f infra/compose.yaml logs --no-color --tail=60 migrate api worker
```

The rebuild installs LightGBM and its native OpenMP dependency. The migration service adds the ledger and planning tables; it does not erase existing records. A successful migration container normally shows **Exited (0)** because its job finishes. API and worker containers must remain running.

If the development frontend is not running, use a second terminal:

```bash
cd ~/agri-stat/web
npm run dev
```

Open `http://localhost:5173/farm-operations` and `http://localhost:5173/demand-planning`. The Docker API documentation is `http://localhost:8001/docs`. A restart alone does not rebuild changed application code. Do not use `down -v`; that removes persistent database volumes, including the Kenya map import.

## API map

All new APIs require authentication and scope records to the signed-in organization. Setup, daily confirmation, training and planning require an administrator.

| Endpoint | Purpose |
| --- | --- |
| POST /api/v1/sales | Atomic FEFO sale; accepts a client event UUID |
| GET /api/v1/sales | Recent own-organization sales and batch allocations |
| GET /api/v1/stock | Available, expired and unknown-expiry quantities |
| POST /api/v1/planning/demand-days | Confirm a completed day or enter a genuine historical total |
| GET /api/v1/planning/demand-days | Review up to 365 daily records |
| POST /api/v1/planning/train | Queue training for a location, product and connected route |
| GET /api/v1/planning/runs | Recent model runs and their results |
| GET /api/v1/planning/runs/{id} | Inspect one run |
| POST /api/v1/planning/runs/{id}/plan | Queue live-weather purchased-stock planning |
| GET /api/v1/jobs/{id} | Check background job status |

The model ledger is stored in ordinary PostgreSQL tables. The blueprint proposed sales hypertables, but a normal transactional table preserves a simple unique organization/event key for idempotent checkout without time-partition uniqueness complications. Weather remains a Timescale hypertable.

## Verification and remaining acceptance

Automated checks cover FEFO allocation, transaction rollback, duplicate retries, invalid numeric input, tenant isolation, timezone day boundaries, missing records/weather, leakage prevention, real model-library execution, validation rejection, expiry caps, heat guards and freshness requirements. PostgreSQL integration additionally checks migrations/extensions and concurrent stock changes when the Docker database is available.

The current real-data acceptance gap is **genuine complete farm daily-sales history**. Public prices and downloaded roads cannot fill it. Model execution tests do not close that gap. Phase 3 can proceed alongside collecting records, but reporting Phase 2 as fully farm-validated would be inaccurate.

Known limits: no general sale-void/return or daily-record correction UI; no stockout-demand estimation; no full offline sync; no autonomous purchasing; no crop-yield model; no calibrated road-delay coefficients; no automatic alternative-supplier selection; no bulk farm-history CSV UI yet. A hard-killed worker may leave a run marked running; inspect the worker and submit a new run after recovery. Old runs remain auditable.

Model references: https://lightgbm.readthedocs.io/en/stable/Parameters.html and https://facebook.github.io/prophet/docs/uncertainty_intervals.html.

Live verification caught a provider mismatch: ERA5-Land alone returns null rainfall in this API. The integration now selects ERA5-Seamless, which supplies the required rainfall and soil-moisture series. Source: https://open-meteo.com/en/docs/historical-weather-api.

## Verification checkpoint for this delivery

Local checks passed: the 90-test combined suite, the expanded 22-test planning suite, the real-model promotion/refit test, and the updated route-direction test. The 51-test weather/planning regression suite also passed after correcting the archive model. The frontend production build passed (with the existing large-bundle warning). Browser checks verified a 5 kg test sale from 10 kg stock for KES 250 and a daily-total confirmation in an isolated SQLite database. A live Nairobi weather probe passed with ERA5-Seamless.

Docker deployment was verified on 14 November 2026 after startup. Migration `0005_planning` is applied, the API returns HTTP 200, new endpoints require authentication, and a worker with both planning tasks consumes the application queue. All three PostgreSQL integration tests passed, including stock concurrency and duplicate retries. A deployed worker refreshed 30 weather rows for the existing Adele Center public market; PostgreSQL contains 16 ERA5-Seamless archive rows with non-null rainfall and soil moisture, confirming the correction is in the running image. Real-farm model validation remains pending genuine history. No test farm data was inserted into the operational PostgreSQL database. Evidence: `work/phase2-deployment-verification.json` and `work/phase2-deployed-weather-job.json`.

The laptop restart exposed missing restart policies. PostgreSQL, Redis, API, workers and Beat now use `restart: unless-stopped`; the migration service remains one-shot. Compose configuration validation passed, and the user applied it with `up -d`. Automatic recovery across another reboot has not been separately tested.
