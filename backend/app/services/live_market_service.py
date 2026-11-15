"""Fetch public source data; retain observation dates and retrieval provenance."""
import csv
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path

import httpx

from app.models.foundation import (ImportRun, InventoryBatch, Location, MarketObservation,
                                  SupplyRoute, WeatherObservation)
from app.models.planning import DemandDay, ForecastRun
from app.models.operations import SaleAllocation, SalesOrderItem, SalesOrder
from app.models.models import Forecast, InventoryRecommendation, Notification, Product, Transaction
from app.services.real_data import MAX_BYTES, import_market_rows, parse_rows

HDX_URL = "https://data.humdata.org/dataset/e0d3fba6-f9a2-45d7-b949-140c455197ff/resource/517ee1bf-2437-4f8c-aa1b-cb9925b9d437/download/wfp_food_prices_ken.csv"
KAMIS_PRODUCTS = (1, 61, 163, 64, 58, 158, 154)  # maize, tomatoes, potatoes, beans, cabbage, onions, kale
KAMIS_URLS = [f"https://kamis.kilimo.go.ke/site/market?product={product}&per_page=100" for product in KAMIS_PRODUCTS]


class MarketTableParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tables, self.table, self.row, self.cell = [], None, None, None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.table = []
        elif tag == "tr" and self.table is not None:
            self.row = []
        elif tag in {"td", "th"} and self.row is not None:
            self.cell = []

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if tag in {"td", "th"} and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            self.table.append(self.row)
            self.row = None
        elif tag == "table" and self.table is not None:
            self.tables.append(self.table)
            self.table = None


def kamis_csv(html):
    parser = MarketTableParser()
    parser.feed(html)
    for table in parser.tables:
        if table and {"Commodity", "Market", "Date", "Wholesale", "Retail"} <= set(table[0]):
            stream = io.StringIO()
            writer = csv.writer(stream)
            writer.writerows(table)
            return stream.getvalue().encode()
    raise ValueError("KAMIS market table was not found; the publisher may have changed its page layout")


def download(url):
    with httpx.Client(timeout=60, follow_redirects=True, headers={"User-Agent": "AgricStatDash/1.0 (public market research)"}) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            raw = bytearray()
            for part in response.iter_bytes():
                raw.extend(part)
                if len(raw) > MAX_BYTES:
                    raise ValueError("Public source exceeds the 20 MB import limit")
            return bytes(raw)


def prepare_live_sources(*, fetch=download, cache_directory=None):
    """Download and validate both sources before any business records are changed."""
    sources = []
    for index, (source, url) in enumerate([("hdx", HDX_URL)] + [("kamis", url) for url in KAMIS_URLS]):
        raw = fetch(url)
        content = kamis_csv(raw.decode("utf-8")) if source == "kamis" else raw
        rejects = []
        rows = parse_rows(content, source, allow_unlocated=True, rejects=rejects)
        if len(rejects) > len(rows):
            raise ValueError(f"{source}: more rejected than valid rows; review the publisher format")
        dataset = dict(source=source, source_url=url, content_sha256=hashlib.sha256(raw).hexdigest(),
                       rows=rows, rejects=rejects)
        if cache_directory:
            directory = Path(cache_directory)
            directory.mkdir(parents=True, exist_ok=True)
            (directory / f"{source}-{index}-latest.csv").write_bytes(content)
            (directory / f"{source}-{index}-rejects.json").write_text(json.dumps(rejects, indent=2))
        sources.append(dataset)
    return sources


def clear_demo_business_data(db, organization_id):
    """Explicit one-time reset. Never called by scheduled refresh jobs."""
    # Legacy ledger tables are single-organization; only allow reset of that local setup.
    from app.models.foundation import DEFAULT_ORGANIZATION_ID, Organization
    if organization_id != DEFAULT_ORGANIZATION_ID or db.query(Organization).count() != 1:
        raise ValueError("Demo reset is only supported for the original single-organization setup")
    for model in (ForecastRun, DemandDay, SaleAllocation, SalesOrderItem, SalesOrder, MarketObservation, ImportRun, WeatherObservation, InventoryBatch, SupplyRoute,
                  Forecast, InventoryRecommendation, Transaction, Notification, Location, Product):
        db.query(model).delete(synchronize_session=False)
    db.flush()


def load_live_sources(db, sources, *, organization_id, replace_demo=False):
    if replace_demo:
        clear_demo_business_data(db, organization_id)
    results = []
    for dataset in sources:
        result = import_market_rows(db, dataset["rows"], source=dataset["source"], source_url=dataset["source_url"],
            content_sha256=dataset["content_sha256"], organization_id=organization_id)
        result.update(source=dataset["source"], rejected_rows=len(dataset["rejects"]),
                      latest_observation=str(max(row["date"] for row in dataset["rows"])),
                      rows_without_coordinates=sum(row["latitude"] is None for row in dataset["rows"]))
        results.append(result)
    return results
