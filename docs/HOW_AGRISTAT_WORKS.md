# How AgriStat works — a farm operator's guide

This guide describes the system actually implemented as of 15 November 2026. The blueprint also contains future components; a diagram in that blueprint does not mean every component is already deployed.

## Start with four different kinds of information

**Market prices** tell you what a source reports for a commodity, market and date. They can help compare selling conditions. They do not prove that your farm sold anything at that price.

**Inventory** tells you what physical produce your farm has, grouped into batches. A batch has a quantity, receipt date, cost and, when known, expiry. Harvesting adds stock. Selling removes stock. Expired produce must not be treated as saleable simply because it still exists physically.

**Sales** tell you what your business actually sold. A sale is a historical fact; a forecast is an estimate. The new farm ledger keeps the sale and the stock deductions together.

**Forecasts** estimate future buyer demand using complete sales history and earlier environmental conditions. They are neither crop-yield predictions nor promises. No website can supply private farm sales that have never been recorded.

## The infrastructure, one component at a time

| Component | Plain-language role | What happens if it stops? |
| --- | --- | --- |
| React web application | The forms, tables and navigation you see in the browser. | You lose this interface; stored records still exist. |
| Next.js | Serves the web application locally and builds its production bundle. | The local page on port 5173 is unavailable. It is not a database. |
| FastAPI | Checks login and permissions, validates input, reads records and applies business rules. | The browser cannot reliably load or submit business data. |
| PostgreSQL | The authoritative store for organizations, products, stock, sales, weather and model runs. | Business operations stop; an available frontend cannot replace it. |
| PostGIS | Adds geographic types and calculations inside PostgreSQL. | Spatial functions and migrations depending on it fail. It is not another database container. |
| TimescaleDB | Adds time-series facilities inside PostgreSQL; weather is partitioned as a hypertable. | Time-series operations requiring the extension fail. It shares the PostgreSQL service. |
| Redis | Holds background task messages, task results and short-lived ownership/cache information. | Queueing or checking background jobs fails. It is not the primary stock ledger. |
| Celery worker | Performs slower jobs such as weather fetches, road inspection, model training and planning. | Queued work waits or fails; a queued message does not mean the work is done. |
| Market worker | A separately configured Celery worker handling market imports. | Price refreshes wait while other workers can continue. |
| Celery Beat | A clock that submits scheduled jobs. It does not do those jobs itself. | Scheduled refreshes stop being submitted; manual jobs can still run. |
| Local Overpass | Answers questions about the imported Kenya OpenStreetMap roads and their tags. | Road-surface inspection cannot complete. Existing inspection records remain in PostgreSQL. |
| External OSRM | Supplies a candidate route geometry between coordinates. | New route calculations may fail even when local Overpass is healthy. |
| Open-Meteo | Supplies forecast weather and historical reanalysis from outside the app. | Weather-dependent work reports missing/unavailable inputs rather than inventing them. |
| KAMIS | Enabled public source for market observations. HDX/WFP is retired. | Refreshes can fail while previously imported observations remain visible with dates. |
| Alembic migration service | Updates the structure of database tables to match a new software version. | New code may fail if its required tables do not exist. |

The app now uses Next.js to host the React workspace. React Router remains the client routing bridge during this incremental migration. It runs on this computer, not a public hosting service. `localhost` means the computer on which the address is opened; another person's phone will not reach your laptop by entering that address.

## What Docker adds

An **image** is a packaged application and its dependencies. A **container** is a running instance of an image. **Compose** describes the related services, their network, settings, persistent storage and startup dependencies.

A **volume** stores data independently of a replaceable container. PostgreSQL records, Redis persistence and the imported Kenya road database have volumes. Rebuilding application containers does not mean re-downloading Kenya or deleting farm records. Removing volumes does.

The API, migration service and workers share application code but run different commands. They are separate processes with separate responsibilities. The migration service normally exits successfully after completing its work. A permanently running API has a different lifecycle.

A container's internal address is not its laptop address. Inside Compose, the API reaches `postgres:5432`, `redis:6379` and `overpass:80`. From the laptop, their exposed addresses differ:

| Local address | Purpose |
| --- | --- |
| http://localhost:5173 | Web application |
| http://localhost:8001/docs | Docker API documentation and authenticated API testing |
| 127.0.0.1:5433 | PostgreSQL for local tools/tests |
| 127.0.0.1:6380 | Redis for local tools/tests |
| http://127.0.0.1:8082/api/status | Local Overpass status |

These port bindings are restricted to the local computer in the Compose configuration. Production HTTPS, public hosting and broader hardening are separate work.

## Follow a sale through the system

1. You choose a farm and produce, enter quantity and selling price, and press Record sale.
2. The browser generates an event ID and sends an authenticated request to FastAPI.
3. FastAPI determines your organization from your login, checks location and product ownership, and checks available stock.
4. PostgreSQL serializes competing checkouts for the organization. The service selects eligible batches in FEFO order.
5. The sale, its line items, allocations and stock decrements are written in one transaction.
6. Only a successful commit makes the whole sale permanent. An error causes rollback.
7. The API returns the receipt, and the browser refreshes available stock and history.

**Atomic** means the sale and all deductions succeed together. **Idempotent** means repeating the same event does not create a second sale. **Concurrent** means requests can arrive at almost the same time; database controls protect against both selling the same last kilogram.

Redis and Celery are not needed to perform the physical stock deduction. A sale should not sit in a background queue while the browser falsely says that stock has already changed.

## Follow a training request

1. A manager confirms complete daily totals, including genuine zero-sale days and stockout flags.
2. The API checks ownership, route connection and basic data eligibility, then saves a queued run.
3. Redis carries a message containing the run ID to a Celery worker.
4. The worker reads records, fetches historical weather, creates lagged features, trains and backtests candidates.
5. If a candidate meets the acceptance rule, the worker refits it and saves forecasts and the serialized model in PostgreSQL. Otherwise the run says rejected, blocked or failed.
6. The browser reads the run's stored status. Refreshing the page does not retrain the model.

**Queued** means requested; **running** means claimed by a worker; **validated** means the initial holdout check passed. **Blocked** means required data is missing or unsuitable. **Rejected** means the models did not meet the comparison rule. None of these labels means a purchase was placed.

P50 is the middle predicted quantity. P10 and P90 describe a lower and upper predictive quantile. In an appropriately calibrated model, about 80% of comparable future outcomes would fall between P10 and P90. A small backtest does not establish that calibration; the interface shows observed holdout coverage so it can be assessed.

## Follow a live-data update

Beat submits a scheduled refresh. A worker contacts the relevant public provider. The application validates and normalizes the response, then writes observations with their source and date. A successful HTTP request does not automatically mean the source data is current; the observation date and retrieval time are separate.

Overpass is different: it first imports a large Kenya snapshot into its own indexed files, then checks regional updates. That import is separate from PostgreSQL. Download completion, import completion and query readiness are three different milestones. A downloaded file alone is not proof that road queries work.

Local Overpass removes dependence on overloaded public Overpass servers, but it does not remove every external dependency. Kenya updates, OSRM routing, market sources and weather still use network services.

## What model inputs and output do not prove

Recorded sales can understate demand when customers leave because stock is exhausted. Weather reanalysis is a modelled estimate of earlier weather, not a direct measurement at your farm. OpenStreetMap surface tags can be missing or outdated. A road's surface does not fully describe its passability, bridges, vehicle type or actual delivery delays.

The planning formulas therefore expose their assumptions and freshness checks. High risk is a prompt for a manager to investigate, not a verified road closure. Replenishment is a planning suggestion, not an automatic order or a crop-growing plan.

## Daily operating routine

1. Record real received harvest batches and their dates.
2. Record sales through Farm stock & sales.
3. Review available, expired and unknown-expiry stock.
4. Reconcile the previous day's records, then confirm the daily total on Demand planning.
5. When sufficient genuine history exists, request training and inspect its validation result.
6. If buying additional produce, request a fresh plan and review its assumptions, supplier commitments and batch expiry before acting.

Use the [Phase 2 guide](PHASE2.md) for formulas, endpoint details, acceptance criteria and deployment instructions. Keep recording real operations even when a forecast is unavailable; reliable records are useful before any machine-learning model is trustworthy.

## Restarting the laptop

On 14 November 2026, Compose was updated so PostgreSQL, Redis, the API, both workers and Beat use `restart: unless-stopped`, like Overpass. Once applied with `docker compose up -d`, these services restart with Docker after a reboot unless you explicitly stopped them. The migration job remains one-shot and is not kept in a restart loop. The Next.js web server is still a separate terminal process; start it with `cd ~/agri-stat/web && npm run dev` when needed. Restart policies are not a substitute for backups or health monitoring.

## The Phase 3 workspace

The [dashboard guide](PHASE3.md) explains the overview, forecast band, map layers and CSV preview/confirmation flow with screenshots. Web requests read tenant-scoped summaries from FastAPI; the interface does not maintain a second stock ledger. CSV history imports add confirmed demand days without rewriting current inventory.
