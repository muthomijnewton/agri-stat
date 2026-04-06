from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import InventoryRecommendation
from app.schemas.schemas import InventoryRecommendationCreate, InventoryRecommendationUpdate, InventoryRecommendationResponse
from typing import List
from datetime import date

router = APIRouter(prefix="/api/recommendations", tags=["inventory-recommendations"])

@router.get("/", response_model=List[InventoryRecommendationResponse])
def list_recommendations(
    skip: int = 0,
    limit: int = 100,
    product_id: int = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db)
):
    """Get inventory recommendations with optional filtering"""
    query = db.query(InventoryRecommendation)
    
    if product_id:
        query = query.filter(InventoryRecommendation.product_id == product_id)
    
    if status:
        query = query.filter(InventoryRecommendation.status == status)
    
    recommendations = query.offset(skip).limit(limit).all()
    return recommendations

@router.get("/{recommendation_id}", response_model=InventoryRecommendationResponse)
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    """Get a specific recommendation by ID"""
    recommendation = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return recommendation

@router.get("/product/{product_id}", response_model=List[InventoryRecommendationResponse])
def get_product_recommendations(product_id: int, db: Session = Depends(get_db)):
    """Get all recommendations for a specific product"""
    recommendations = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.product_id == product_id
    ).order_by(InventoryRecommendation.recommendation_date.desc()).all()
    return recommendations

@router.post("/", response_model=InventoryRecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(
    recommendation: InventoryRecommendationCreate,
    db: Session = Depends(get_db)
):
    """Create a new inventory recommendation"""
    db_recommendation = InventoryRecommendation(**recommendation.dict())
    db.add(db_recommendation)
    db.commit()
    db.refresh(db_recommendation)
    return db_recommendation

@router.put("/{recommendation_id}", response_model=InventoryRecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_update: InventoryRecommendationUpdate,
    db: Session = Depends(get_db)
):
    """Update an inventory recommendation"""
    recommendation = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    update_data = recommendation_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recommendation, key, value)
    
    db.commit()
    db.refresh(recommendation)
    return recommendation

@router.patch("/{recommendation_id}/approve", response_model=InventoryRecommendationResponse)
def approve_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    """Approve an inventory recommendation"""
    recommendation = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = "approved"
    db.commit()
    db.refresh(recommendation)
    return recommendation

@router.patch("/{recommendation_id}/implement", response_model=InventoryRecommendationResponse)
def implement_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    """Mark a recommendation as implemented"""
    recommendation = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    recommendation.status = "implemented"
    db.commit()
    db.refresh(recommendation)
    return recommendation

@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    """Delete a recommendation"""
    recommendation = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    db.delete(recommendation)
    db.commit()
    return None
