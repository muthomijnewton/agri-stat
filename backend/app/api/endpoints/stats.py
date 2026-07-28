from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.models import (
    Forecast,
    InventoryRecommendation,
    Product,
    Transaction,
    User,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Lightweight KPI counts for the Dashboard header cards."""
    return {
        "total_products": db.query(Product).filter(Product.is_active == True).count(),  # noqa: E712
        "total_transactions": db.query(Transaction).count(),
        "total_forecasts": db.query(Forecast).count(),
        "pending_recommendations": db.query(InventoryRecommendation)
            .filter(InventoryRecommendation.status == "pending")
            .count(),
        "approved_recommendations": db.query(InventoryRecommendation)
            .filter(InventoryRecommendation.status == "approved")
            .count(),
        "implemented_recommendations": db.query(InventoryRecommendation)
            .filter(InventoryRecommendation.status == "implemented")
            .count(),
    }


@router.get("/transactions-daily")
def get_daily_transactions(
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return daily transaction totals (quantity sold + revenue) for the last
    `days` days.  Used by the Dashboard bar chart.
    """
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Transaction.transaction_date.label("day"),
            func.sum(Transaction.quantity).label("total_quantity"),
            func.sum(Transaction.total_price).label("total_revenue"),
            func.count(Transaction.id).label("count"),
        )
        .filter(Transaction.transaction_date >= since)
        .group_by(Transaction.transaction_date)
        .order_by(Transaction.transaction_date)
        .all()
    )

    return [
        {
            "date": str(row.day),
            "quantity": int(row.total_quantity or 0),
            "revenue": float(row.total_revenue or 0),
            "count": int(row.count or 0),
        }
        for row in rows
    ]


@router.get("/revenue-by-product")
def get_revenue_by_product(
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return total revenue grouped by product for the last `days` days.
    Used by the Dashboard pie / bar chart.
    """
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Product.name.label("product"),
            func.sum(Transaction.total_price).label("revenue"),
            func.sum(Transaction.quantity).label("quantity"),
        )
        .join(Transaction, Transaction.product_id == Product.id)
        .filter(Transaction.transaction_date >= since)
        .group_by(Product.id, Product.name)
        .order_by(func.sum(Transaction.total_price).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "product": row.product,
            "revenue": float(row.revenue or 0),
            "quantity": int(row.quantity or 0),
        }
        for row in rows
    ]



# ---------------------------------------------------------------------------
# Analytics endpoints
# ---------------------------------------------------------------------------

@router.get("/transaction-type-split")
def get_transaction_type_split(
    days: int = Query(default=30, ge=7, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return the count and total revenue split between 'sale' and 'purchase'
    transactions for the last `days` days.
    Used by the Analytics pie/donut chart.
    """
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Transaction.transaction_type.label("type"),
            func.count(Transaction.id).label("count"),
            func.sum(Transaction.total_price).label("revenue"),
            func.sum(Transaction.quantity).label("quantity"),
        )
        .filter(Transaction.transaction_date >= since)
        .group_by(Transaction.transaction_type)
        .all()
    )

    return [
        {
            "type": row.type,
            "count": int(row.count or 0),
            "revenue": float(row.revenue or 0),
            "quantity": int(row.quantity or 0),
        }
        for row in rows
    ]


@router.get("/forecast-accuracy-trend")
def get_forecast_accuracy_trend(
    limit: int = Query(default=20, ge=5, le=100),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return the average forecast accuracy (MAPE) grouped by creation date,
    ordered chronologically.  Lower MAPE = better accuracy.
    Used by the Analytics line chart.
    """
    rows = (
        db.query(
            func.date(Forecast.created_at).label("day"),
            func.avg(Forecast.accuracy_score).label("avg_mape"),
            func.count(Forecast.id).label("count"),
        )
        .filter(Forecast.accuracy_score.isnot(None))
        .group_by(func.date(Forecast.created_at))
        .order_by(func.date(Forecast.created_at))
        .limit(limit)
        .all()
    )

    return [
        {
            "date": str(row.day),
            "avg_mape": round(float(row.avg_mape or 0), 2),
            "count": int(row.count or 0),
        }
        for row in rows
    ]


@router.get("/recommendation-status-breakdown")
def get_recommendation_status_breakdown(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return a count of inventory recommendations grouped by status
    (pending / approved / implemented).
    Used by the Analytics bar or donut chart.
    """
    rows = (
        db.query(
            InventoryRecommendation.status.label("status"),
            func.count(InventoryRecommendation.id).label("count"),
        )
        .group_by(InventoryRecommendation.status)
        .all()
    )

    # Ensure all three statuses always appear even if count is 0
    status_map = {"pending": 0, "approved": 0, "implemented": 0}
    for row in rows:
        status_map[row.status] = int(row.count or 0)

    return [{"status": k, "count": v} for k, v in status_map.items()]


@router.get("/top-products-by-quantity")
def get_top_products_by_quantity(
    days: int = Query(default=30, ge=7, le=365),
    limit: int = Query(default=10, ge=3, le=20),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Return the top `limit` products ranked by total quantity sold
    over the last `days` days.
    Used by the Analytics horizontal bar chart.
    """
    since = date.today() - timedelta(days=days)

    rows = (
        db.query(
            Product.name.label("product"),
            func.sum(Transaction.quantity).label("quantity"),
            func.sum(Transaction.total_price).label("revenue"),
        )
        .join(Transaction, Transaction.product_id == Product.id)
        .filter(
            Transaction.transaction_date >= since,
            Transaction.transaction_type == "sale",
        )
        .group_by(Product.id, Product.name)
        .order_by(func.sum(Transaction.quantity).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product": row.product,
            "quantity": int(row.quantity or 0),
            "revenue": float(row.revenue or 0),
        }
        for row in rows
    ]
