from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Forecast, Product, User
from app.schemas.schemas import ForecastCreate, ForecastUpdate, ForecastResponse
from app.core.security import get_current_user
from app.services.forecasting import ForecastingService
from typing import List
from datetime import date

router = APIRouter(prefix="/api/forecasts", tags=["forecasts"])


@router.get("/", response_model=List[ForecastResponse])
def list_forecasts(
    skip: int = 0,
    limit: int = 100,
    product_id: int = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
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

    Runs the ForecastingService (Prophet → ARIMA fallback) against the
    product's transaction history and persists the resulting forecast rows.
    Returns a summary with the number of rows generated.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    forecasts = ForecastingService.generate_forecast(db, product_id, forecast_type=model)

    if not forecasts:
        raise HTTPException(
            status_code=422,
            detail=(
                "Not enough transaction history to generate a forecast. "
                "Record at least 10 transactions for this product first."
            ),
        )

    return {
        "message": f"Forecast generated successfully for '{product.name}'",
        "product_id": product_id,
        "model_used": model,
        "periods_generated": len(forecasts),
    }


@router.post("/generate-all", status_code=status.HTTP_200_OK)
def generate_all_forecasts(
    model: str = Query(default="auto", enum=["auto", "prophet", "arima"]),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Trigger forecast generation for every active product in one call.

    Returns a per-product result list so the frontend can display a
    live progress log.  Products with insufficient transaction history
    are skipped with a 'skipped' status rather than aborting the whole run.
    """
    products = db.query(Product).filter(Product.is_active == True).all()  # noqa: E712

    if not products:
        raise HTTPException(status_code=404, detail="No active products found.")

    results = []
    total_periods = 0

    for product in products:
        try:
            forecasts = ForecastingService.generate_forecast(
                db, product.id, forecast_type=model
            )
            if forecasts:
                total_periods += len(forecasts)
                results.append({
                    "product_id":       product.id,
                    "product_name":     product.name,
                    "status":           "success",
                    "periods_generated": len(forecasts),
                    "model_used":       model,
                    "message":          f"{len(forecasts)} day(s) generated",
                })
            else:
                results.append({
                    "product_id":       product.id,
                    "product_name":     product.name,
                    "status":           "skipped",
                    "periods_generated": 0,
                    "model_used":       model,
                    "message":          "Not enough transaction history (need ≥ 10 records)",
                })
        except Exception as exc:
            results.append({
                "product_id":       product.id,
                "product_name":     product.name,
                "status":           "error",
                "periods_generated": 0,
                "model_used":       model,
                "message":          str(exc),
            })

    succeeded = sum(1 for r in results if r["status"] == "success")
    skipped   = sum(1 for r in results if r["status"] == "skipped")
    failed    = sum(1 for r in results if r["status"] == "error")

    return {
        "summary": {
            "total_products":  len(products),
            "succeeded":       succeeded,
            "skipped":         skipped,
            "failed":          failed,
            "total_periods":   total_periods,
            "model_used":      model,
        },
        "results": results,
    }


@router.get("/product/{product_id}", response_model=List[ForecastResponse])
def get_product_forecasts(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return up to `days` upcoming forecasts for a specific product."""
    return (
        db.query(Forecast)
        .filter(Forecast.product_id == product_id)
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
    """Create a new forecast."""
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
