"""
Multi-format Import endpoint — bulk-load transactions and products from
CSV, Excel (.xlsx/.xls), JSON, TSV, or ODS files.

Supported transaction columns (case-insensitive, flexible naming):
  date / transaction_date / trans_date / sale_date
  product / product_name / name / item / crop
  type / transaction_type / txn_type / kind      (sale | purchase)
  quantity / qty / amount / units
  unit_price / price / cost / rate
  notes / note / comment / remarks / description

Supported product columns:
  name / product_name / product / item / crop
  category / type / group
  unit / unit_of_measure / uom
  unit_price / price / cost
  description / desc / notes
"""

import io
import csv
import json
import logging
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Product, Transaction, User
from app.core.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/imports", tags=["imports"])

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_FILE_BYTES = 10 * 1024 * 1024   # 10 MB hard cap (read before parsing)
MAX_ROWS       = 5_000

ALLOWED_EXTENSIONS = {".csv", ".tsv", ".xlsx", ".xls", ".ods", ".json"}

ALLOWED_MIME_TYPES = {
    # CSV
    "text/csv",
    "application/csv",
    "text/plain",
    # Excel
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.ms-excel",
    # ODS
    "application/vnd.oasis.opendocument.spreadsheet",
    # JSON
    "application/json",
    "text/json",
    # TSV / generic
    "text/tab-separated-values",
    "application/octet-stream",   # browsers sometimes report this for .ods/.xlsx
}

# ---------------------------------------------------------------------------
# File parsing helpers
# ---------------------------------------------------------------------------

def _get_extension(filename: str) -> str:
    """Return lowercase file extension including the dot."""
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def _validate_upload(upload: UploadFile) -> bytes:
    """
    Read the upload, enforce the byte-size cap, and validate extension /
    content-type.  Returns the raw bytes.
    """
    ext = _get_extension(upload.filename or "")
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. "
                   f"Accepted: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    ct = (upload.content_type or "").split(";")[0].strip().lower()
    if ct and ct not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported content type '{ct}'.",
        )

    raw = upload.file.read()
    if len(raw) > MAX_FILE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File is {len(raw) // 1024} KB — exceeds the "
                   f"{MAX_FILE_BYTES // 1024 // 1024} MB limit.",
        )
    return raw


def _to_dataframe(raw: bytes, filename: str) -> pd.DataFrame:
    """Parse raw bytes into a DataFrame based on file extension."""
    ext = _get_extension(filename)

    if ext == ".csv":
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        return pd.read_csv(io.StringIO(text), dtype=str, keep_default_na=False)

    if ext == ".tsv":
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        return pd.read_csv(io.StringIO(text), sep="\t", dtype=str, keep_default_na=False)

    if ext == ".xlsx":
        return pd.read_excel(io.BytesIO(raw), dtype=str, engine="openpyxl", keep_default_na=False)

    if ext == ".xls":
        return pd.read_excel(io.BytesIO(raw), dtype=str, engine="xlrd", keep_default_na=False)

    if ext == ".ods":
        return pd.read_excel(io.BytesIO(raw), dtype=str, engine="odf", keep_default_na=False)

    if ext == ".json":
        data = json.loads(raw.decode("utf-8"))
        if isinstance(data, list):
            return pd.DataFrame(data).astype(str)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="JSON file must contain a top-level array of objects.",
        )

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail=f"Cannot parse '{ext}' files.",
    )


def _normalise(df: pd.DataFrame) -> list[dict]:
    """Lowercase + strip column names, return list of row dicts."""
    df.columns = [str(c).strip().lower() for c in df.columns]
    if len(df) > MAX_ROWS:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File has {len(df):,} data rows — exceeds the {MAX_ROWS:,} row limit. "
                   "Split it into smaller files.",
        )
    return df.fillna("").to_dict(orient="records")


# ---------------------------------------------------------------------------
# Column-finding helpers
# ---------------------------------------------------------------------------

def _find_col(row: dict, *candidates: str) -> Optional[str]:
    for c in candidates:
        if c in row:
            return c
    return None


def _str(row: dict, *candidates: str) -> str:
    col = _find_col(row, *candidates)
    return row.get(col, "").strip() if col else ""


def _parse_date(value: str) -> Optional[date]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d",
                "%Y%m%d", "%d.%m.%Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_decimal(value: str) -> Optional[Decimal]:
    try:
        cleaned = value.replace(",", "").replace(" ", "").strip()
        return Decimal(cleaned) if cleaned else None
    except (InvalidOperation, AttributeError):
        return None


def _get_or_create_product(name: str, db: Session) -> Product:
    product = (
        db.query(Product)
        .filter(Product.name.ilike(name.strip()))
        .filter(Product.is_active == True)  # noqa: E712
        .first()
    )
    if not product:
        product = Product(name=name.strip(), is_active=True)
        db.add(product)
        db.flush()
    return product


# ---------------------------------------------------------------------------
# POST /api/imports/transactions
# ---------------------------------------------------------------------------

@router.post(
    "/transactions",
    summary="Import transactions from CSV / Excel / JSON / TSV / ODS",
    status_code=status.HTTP_200_OK,
)
def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk-import transactions from a file.

    Required columns: date, product, quantity
    Optional columns: unit_price, transaction_type (sale|purchase), notes

    New products are created automatically.
    Duplicate rows (same product + date + quantity + type) are skipped.
    Returns: { inserted, skipped, total_errors, errors[] }
    """
    raw  = _validate_upload(file)
    df   = _to_dataframe(raw, file.filename or "upload")
    rows = _normalise(df)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The file is empty or contains no data rows.",
        )

    inserted     = 0
    skipped      = 0
    total_errors = 0
    errors: list[dict] = []

    for i, row in enumerate(rows, start=2):

        # ── date ──────────────────────────────────────────────────────────
        raw_date = _str(row, "date", "transaction_date", "trans_date", "sale_date", "purchase_date")
        if not raw_date:
            errors.append({"row": i, "error": "Missing date value"})
            skipped += 1; total_errors += 1; continue
        txn_date = _parse_date(raw_date)
        if not txn_date:
            errors.append({"row": i, "error": f"Unrecognised date format: '{raw_date}'"})
            skipped += 1; total_errors += 1; continue

        # ── product ───────────────────────────────────────────────────────
        product_name = _str(row, "product", "product_name", "name", "item", "crop", "commodity")
        if not product_name:
            errors.append({"row": i, "error": "Missing product name"})
            skipped += 1; total_errors += 1; continue

        # ── quantity ──────────────────────────────────────────────────────
        raw_qty = _str(row, "quantity", "qty", "amount", "units", "volume")
        if not raw_qty:
            errors.append({"row": i, "error": "Missing quantity value"})
            skipped += 1; total_errors += 1; continue
        try:
            quantity = round(float(raw_qty.replace(",", "")))
        except ValueError:
            errors.append({"row": i, "error": f"Invalid quantity: '{raw_qty}'"})
            skipped += 1; total_errors += 1; continue
        if quantity <= 0:
            errors.append({"row": i, "error": f"Quantity must be positive, got {quantity}"})
            skipped += 1; total_errors += 1; continue

        # ── unit_price ────────────────────────────────────────────────────
        raw_price = _str(row, "unit_price", "price", "cost", "rate", "unit price")
        unit_price = _parse_decimal(raw_price) if raw_price else Decimal("0.00")
        if unit_price is None:
            unit_price = Decimal("0.00")

        total_price = (unit_price * quantity).quantize(Decimal("0.01"))

        # ── transaction_type ──────────────────────────────────────────────
        raw_type = _str(row, "transaction_type", "type", "txn_type", "kind", "direction").lower()
        txn_type = "purchase" if "purchase" in raw_type or raw_type in ("buy", "in", "bought") else "sale"

        # ── notes ─────────────────────────────────────────────────────────
        notes = _str(row, "notes", "note", "comment", "remarks", "description") or None

        # ── duplicate detection ───────────────────────────────────────────
        try:
            product = _get_or_create_product(product_name, db)

            duplicate = db.query(Transaction).filter(
                Transaction.product_id == product.id,
                Transaction.transaction_date == txn_date,
                Transaction.quantity == quantity,
                Transaction.transaction_type == txn_type,
                Transaction.user_id == current_user.id,
            ).first()

            if duplicate:
                skipped += 1
                continue

            txn = Transaction(
                product_id=product.id,
                user_id=current_user.id,
                transaction_type=txn_type,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                transaction_date=txn_date,
                notes=notes,
            )
            db.add(txn)
            inserted += 1

        except Exception as exc:
            logger.warning("Row %d failed: %s", i, exc)
            errors.append({"row": i, "error": str(exc)})
            skipped += 1
            total_errors += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while saving: {exc}",
        )

    return {
        "message": f"Import complete. {inserted} rows inserted, {skipped} skipped.",
        "inserted": inserted,
        "skipped": skipped,
        "total_errors": total_errors,
        "errors": errors[:50],
    }


# ---------------------------------------------------------------------------
# POST /api/imports/products
# ---------------------------------------------------------------------------

@router.post(
    "/products",
    summary="Import products from CSV / Excel / JSON / TSV / ODS",
    status_code=status.HTTP_200_OK,
)
def import_products(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Bulk-import products from a file.

    Required columns: name
    Optional columns: category, unit, unit_price, description

    Exact-match duplicates (case-insensitive) are skipped.
    Returns: { inserted, skipped, total_errors, errors[] }
    """
    raw  = _validate_upload(file)
    df   = _to_dataframe(raw, file.filename or "upload")
    rows = _normalise(df)

    if not rows:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The file is empty or contains no data rows.",
        )

    inserted     = 0
    skipped      = 0
    total_errors = 0
    errors: list[dict] = []

    for i, row in enumerate(rows, start=2):
        product_name = _str(row, "name", "product_name", "product", "item", "crop", "commodity")
        if not product_name:
            errors.append({"row": i, "error": "Missing product name"})
            skipped += 1; total_errors += 1; continue

        existing = db.query(Product).filter(Product.name.ilike(product_name)).first()
        if existing:
            skipped += 1
            continue

        raw_price = _str(row, "unit_price", "price", "cost")
        unit_price = _parse_decimal(raw_price) if raw_price else None

        try:
            product = Product(
                name=product_name,
                category=_str(row, "category", "type", "group") or None,
                unit=_str(row, "unit", "unit_of_measure", "uom") or None,
                unit_price=unit_price,
                description=_str(row, "description", "desc", "notes") or None,
                is_active=True,
            )
            db.add(product)
            inserted += 1
        except Exception as exc:
            errors.append({"row": i, "error": str(exc)})
            skipped += 1
            total_errors += 1

    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while saving: {exc}",
        )

    return {
        "message": f"Import complete. {inserted} products inserted, {skipped} skipped.",
        "inserted": inserted,
        "skipped": skipped,
        "total_errors": total_errors,
        "errors": errors[:50],
    }
