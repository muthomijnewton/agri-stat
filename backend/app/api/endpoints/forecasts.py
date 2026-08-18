from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Forecast, Product, User
from app.schemas.schemas import ForecastCreate, ForecastUpdate, ForecastResponse
from app.core.security import get_current_user
from app.services.forecasting import ForecastingService
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])


@router.get("/", response_model=List[ForecastResponse])
def list_forecasts(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List forecasts with optional filtering by product and date range."""
    query = db.query(Forecast)

    if product_id:
        query = query.filter(Forecast.product_id == product_id)
    if start_date:
        query = query.filter(Forecast.forecast_date >= start_date)
    if end_date:
        query = query.filter(Forecast.forecast_date <= end_date)

    return query.order_by(Forecast.forecast_date).offset(skip).limit(limit).all()


# NOTE: static/specific paths (/product/..., /generate/...) MUST be registered
# before parameterised {forecast_id} paths so FastAPI doesn't try to cast the
# literal string to an integer.

@router.post("/generate/{product_id}", status_code=status.HTTP_201_CREATED)
def generate_forecast(
    product_id: int,
    model: str = Query(default="auto", enum=["auto", "prophet", "arima"]),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Trigger AI demand-forecast generation for a product.

    Deletes any existing forecasts for the product before inserting new ones
    (upsert-by-replace) so re-running never creates duplicate rows.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # ── upsert: remove existing forecasts for this product first ──────────
    db.query(Forecast).filter(Forecast.product_id == product_id).delete()
    db.flush()

    forecasts = ForecastingService.generate_forecast(db, product_id, forecast_type=model)

    if not forecasts:
        db.rollback()
        raise HTTPException(
            status_code=422,
            detail=(
                "Not enough transaction history to generate a forecast. "
                "Record at least 10 transactions for this product first."
            ),
        )

    db.commit()

    return {
        "message": f"Forecast generated successfully for '{product.name}'",
        "product_id": product_id,
        "model_used": model,
        "periods_generated": len(forecasts),
    }


def _run_generate_all(model: str, db: Session) -> None:
    """Background worker that generates forecasts for all active products."""
    products = db.query(Product).filter(Product.is_active == True).all()  # noqa: E712
    for product in products:
        try:
            db.query(Forecast).filter(Forecast.product_id == product.id).delete()
            db.flush()
            ForecastingService.generate_forecast(db, product.id, forecast_type=model)
            db.commit()
        except Exception as exc:
            db.rollback()
            import logging
            logging.getLogger(__name__).warning(
                "generate-all: failed for product %d (%s): %s", product.id, product.name, exc
            )


@router.post("/generate-all", status_code=status.HTTP_202_ACCEPTED)
def generate_all_forecasts(
    background_tasks: BackgroundTasks,
    model: str = Query(default="auto", enum=["auto", "prophet", "arima"]),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Enqueue forecast generation for every active product as a background task.

    Returns 202 Accepted immediately — the forecasts are generated
    asynchronously so the request doesn't time out on large product catalogues.
    """
    products = db.query(Product).filter(Product.is_active == True).all()  # noqa: E712

    if not products:
        raise HTTPException(status_code=404, detail="No active products found.")

    background_tasks.add_task(_run_generate_all, model, db)

    return {
        "message": f"Forecast generation started for {len(products)} product(s). "
                   "Results will be available shortly.",
        "total_products": len(products),
        "model_requested": model,
        "status": "queued",
    }


@router.get("/product/{product_id}", response_model=List[ForecastResponse])
def get_product_forecasts(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return up to `days` upcoming forecasts for a specific product."""
    today = date.today()
    return (
        db.query(Forecast)
        .filter(
            Forecast.product_id == product_id,
            Forecast.forecast_date >= today,
        )
        .order_by(Forecast.forecast_date)
        .limit(days)
        .all()
    )


@router.get("/{forecast_id}", response_model=ForecastResponse)
def get_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific forecast by ID."""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast


@router.post("/", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
def create_forecast(
    forecast: ForecastCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new forecast manually."""
    # Verify the product exists
    product = db.query(Product).filter(Product.id == forecast.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_forecast = Forecast(**forecast.model_dump())
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast


@router.put("/{forecast_id}", response_model=ForecastResponse)
def update_forecast(
    forecast_id: int,
    forecast_update: ForecastUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update a forecast."""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")

    for key, value in forecast_update.model_dump(exclude_unset=True).items():
        setattr(forecast, key, value)

    db.commit()
    db.refresh(forecast)
    return forecast


@router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forecast(
    forecast_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Delete a forecast."""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")

    db.delete(forecast)
    db.commit()
