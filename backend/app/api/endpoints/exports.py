"""
CSV export endpoints.

Each endpoint streams a CSV file directly to the client without writing
anything to disk.  The token is passed as a query parameter because the
browser's native download mechanism cannot set custom headers.
"""

import csv
import io
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import Forecast, InventoryRecommendation, Product, Transaction, User
from app.core.security import get_current_user

router = APIRouter(prefix="/api/exports", tags=["exports"])


def _csv_response(rows: list[dict], filename: str) -> StreamingResponse:
    """
    Build a StreamingResponse that sends `rows` as a UTF-8 CSV file.
    Includes a BOM (\\xef\\xbb\\xbf) so Excel opens it correctly on Windows.
    """
    if not rows:
        # Return an empty file rather than an error
        output = io.StringIO()
        content = output.getvalue()
        return StreamingResponse(
            iter(["\xef\xbb\xbf"]),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

    # Prepend BOM
    csv_content = "\xef\xbb\xbf" + output.getvalue()

    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ---------------------------------------------------------------------------
# Transactions CSV
# ---------------------------------------------------------------------------

@router.get("/transactions", summary="Export transactions as CSV")
def export_transactions(
    product_id: Optional[int]  = Query(None, description="Filter by product ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date:   Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: User     = Depends(get_current_user),
):
    """
    Download all transactions (optionally filtered) as a CSV file.
    Supports the same product_id / start_date / end_date filters as the
    regular transactions list endpoint.
    """
    query = (
        db.query(
            Transaction.id,
            Transaction.transaction_date,
            Transaction.transaction_type,
            Product.name.label("product"),
            Product.category,
            Transaction.quantity,
            Transaction.unit_price,
            Transaction.total_price,
            Transaction.notes,
        )
        .join(Product, Transaction.product_id == Product.id)
    )

    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    if start_date and end_date:
        query = query.filter(
            and_(
                Transaction.transaction_date >= start_date,
                Transaction.transaction_date <= end_date,
            )
        )
    elif start_date:
        query = query.filter(Transaction.transaction_date >= start_date)
    elif end_date:
        query = query.filter(Transaction.transaction_date <= end_date)

    rows_raw = query.order_by(Transaction.transaction_date.desc()).all()

    rows = [
        {
            "ID":               r.id,
            "Date":             str(r.transaction_date),
            "Type":             r.transaction_type,
            "Product":          r.product,
            "Category":         r.category or "",
            "Quantity":         r.quantity,
            "Unit Price (KES)": float(r.unit_price or 0),
            "Total Price (KES)":float(r.total_price or 0),
            "Notes":            r.notes or "",
        }
        for r in rows_raw
    ]

    today = date.today().isoformat()
    return _csv_response(rows, f"transactions_{today}.csv")


# ---------------------------------------------------------------------------
# Forecasts CSV
# ---------------------------------------------------------------------------

@router.get("/forecasts", summary="Export forecasts as CSV")
def export_forecasts(
    product_id: Optional[int]  = Query(None, description="Filter by product ID"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date:   Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: User     = Depends(get_current_user),
):
    """
    Download all forecasts (optionally filtered) as a CSV file.
    """
    query = (
        db.query(
            Forecast.id,
            Forecast.forecast_date,
            Product.name.label("product"),
            Product.category,
            Forecast.predicted_demand,
            Forecast.confidence_lower,
            Forecast.confidence_upper,
            Forecast.model_type,
            Forecast.accuracy_score,
        )
        .join(Product, Forecast.product_id == Product.id)
    )

    if product_id:
        query = query.filter(Forecast.product_id == product_id)
    if start_date:
        query = query.filter(Forecast.forecast_date >= start_date)
    if end_date:
        query = query.filter(Forecast.forecast_date <= end_date)

    rows_raw = query.order_by(Forecast.forecast_date).all()

    rows = [
        {
            "ID":                   r.id,
            "Forecast Date":        str(r.forecast_date),
            "Product":              r.product,
            "Category":             r.category or "",
            "Predicted Demand":     r.predicted_demand,
            "Confidence Lower":     float(r.confidence_lower or 0),
            "Confidence Upper":     float(r.confidence_upper or 0),
            "Model":                r.model_type or "",
            "Accuracy (MAPE %)":    float(r.accuracy_score or 0),
        }
        for r in rows_raw
    ]

    today = date.today().isoformat()
    return _csv_response(rows, f"forecasts_{today}.csv")


# ---------------------------------------------------------------------------
# Recommendations CSV
# ---------------------------------------------------------------------------

@router.get("/recommendations", summary="Export recommendations as CSV")
def export_recommendations(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    status:     Optional[str] = Query(None, description="Filter by status (pending/approved/implemented)"),
    db: Session = Depends(get_db),
    _: User     = Depends(get_current_user),
):
    """
    Download all inventory recommendations (optionally filtered) as a CSV file.
    """
    query = (
        db.query(
            InventoryRecommendation.id,
            InventoryRecommendation.recommendation_date,
            Product.name.label("product"),
            Product.category,
            InventoryRecommendation.recommended_quantity,
            InventoryRecommendation.current_quantity,
            InventoryRecommendation.min_quantity,
            InventoryRecommendation.max_quantity,
            InventoryRecommendation.status,
            InventoryRecommendation.reason,
        )
        .join(Product, InventoryRecommendation.product_id == Product.id)
    )

    if product_id:
        query = query.filter(InventoryRecommendation.product_id == product_id)
    if status:
        query = query.filter(InventoryRecommendation.status == status)

    rows_raw = query.order_by(InventoryRecommendation.recommendation_date.desc()).all()

    rows = [
        {
            "ID":                   r.id,
            "Date":                 str(r.recommendation_date),
            "Product":              r.product,
            "Category":             r.category or "",
            "Recommended Qty":      r.recommended_quantity,
            "Current Qty":          r.current_quantity or "",
            "Min Qty":              r.min_quantity or "",
            "Max Qty":              r.max_quantity or "",
            "Status":               r.status,
            "Reason":               r.reason or "",
        }
        for r in rows_raw
    ]

    today = date.today().isoformat()
    return _csv_response(rows, f"recommendations_{today}.csv")
