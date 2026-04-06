from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Forecast
from app.schemas.schemas import ForecastCreate, ForecastUpdate, ForecastResponse
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
    db: Session = Depends(get_db)
):
    """Get forecasts with optional filtering by product and date range"""
    query = db.query(Forecast)
    
    if product_id:
        query = query.filter(Forecast.product_id == product_id)
    
    if start_date:
        query = query.filter(Forecast.forecast_date >= start_date)
    
    if end_date:
        query = query.filter(Forecast.forecast_date <= end_date)
    
    forecasts = query.order_by(Forecast.forecast_date).offset(skip).limit(limit).all()
    return forecasts

@router.get("/{forecast_id}", response_model=ForecastResponse)
def get_forecast(forecast_id: int, db: Session = Depends(get_db)):
    """Get a specific forecast by ID"""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    return forecast

@router.get("/product/{product_id}", response_model=List[ForecastResponse])
def get_product_forecasts(product_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get upcoming forecasts for a specific product"""
    forecasts = db.query(Forecast).filter(
        Forecast.product_id == product_id
    ).order_by(Forecast.forecast_date).limit(days).all()
    return forecasts

@router.post("/", response_model=ForecastResponse, status_code=status.HTTP_201_CREATED)
def create_forecast(forecast: ForecastCreate, db: Session = Depends(get_db)):
    """Create a new forecast"""
    db_forecast = Forecast(**forecast.dict())
    db.add(db_forecast)
    db.commit()
    db.refresh(db_forecast)
    return db_forecast

@router.put("/{forecast_id}", response_model=ForecastResponse)
def update_forecast(forecast_id: int, forecast_update: ForecastUpdate, db: Session = Depends(get_db)):
    """Update a forecast"""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    update_data = forecast_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(forecast, key, value)
    
    db.commit()
    db.refresh(forecast)
    return forecast

@router.delete("/{forecast_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forecast(forecast_id: int, db: Session = Depends(get_db)):
    """Delete a forecast"""
    forecast = db.query(Forecast).filter(Forecast.id == forecast_id).first()
    if not forecast:
        raise HTTPException(status_code=404, detail="Forecast not found")
    
    db.delete(forecast)
    db.commit()
    return None
