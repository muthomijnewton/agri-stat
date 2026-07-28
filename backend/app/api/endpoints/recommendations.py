from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import InventoryRecommendation, Notification, User
from app.schemas.schemas import (
    InventoryRecommendationCreate,
    InventoryRecommendationUpdate,
    InventoryRecommendationResponse,
)
from app.core.security import get_current_user
from typing import List

router = APIRouter(prefix="/api/recommendations", tags=["inventory-recommendations"])

# ---------------------------------------------------------------------------
# Allowed state transitions for the recommendation workflow.
# pending → approved → implemented  (no skipping, no going back)
# ---------------------------------------------------------------------------
_VALID_TRANSITIONS = {
    "approved": "pending",       # can only approve a pending rec
    "implemented": "approved",   # can only implement an approved rec
}


@router.get("/", response_model=List[InventoryRecommendationResponse])
def list_recommendations(
    skip: int = 0,
    limit: int = 100,
    product_id: int = Query(None),
    status: str = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List recommendations with optional filtering."""
    query = db.query(InventoryRecommendation)

    if product_id:
        query = query.filter(InventoryRecommendation.product_id == product_id)
    if status:
        query = query.filter(InventoryRecommendation.status == status)

    return query.offset(skip).limit(limit).all()


# NOTE: /product/{product_id} MUST come before /{recommendation_id}
# to avoid FastAPI attempting to cast the literal "product" as an integer.
@router.get("/product/{product_id}", response_model=List[InventoryRecommendationResponse])
def get_product_recommendations(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return all recommendations for a specific product, newest first."""
    return (
        db.query(InventoryRecommendation)
        .filter(InventoryRecommendation.product_id == product_id)
        .order_by(InventoryRecommendation.recommendation_date.desc())
        .all()
    )


@router.get("/{recommendation_id}", response_model=InventoryRecommendationResponse)
def get_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific recommendation by ID."""
    rec = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return rec


@router.post(
    "/",
    response_model=InventoryRecommendationResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_recommendation(
    recommendation: InventoryRecommendationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Create a new inventory recommendation and generate a notification."""
    db_rec = InventoryRecommendation(**recommendation.model_dump())
    db.add(db_rec)
    db.commit()
    db.refresh(db_rec)

    db.add(Notification(
        title="New Recommendation",
        message=f"Recommendation #{db_rec.id} created for product #{db_rec.product_id}",
        type="info",
        read=False,
    ))
    db.commit()

    return db_rec


@router.put("/{recommendation_id}", response_model=InventoryRecommendationResponse)
def update_recommendation(
    recommendation_id: int,
    recommendation_update: InventoryRecommendationUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update an inventory recommendation."""
    rec = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    for key, value in recommendation_update.model_dump(exclude_unset=True).items():
        setattr(rec, key, value)

    db.commit()
    db.refresh(rec)
    return rec


@router.patch("/{recommendation_id}/approve", response_model=InventoryRecommendationResponse)
def approve_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Approve a pending recommendation (pending → approved)."""
    rec = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    required = _VALID_TRANSITIONS["approved"]
    if rec.status != required:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot approve a recommendation with status '{rec.status}'. "
                   f"Only '{required}' recommendations can be approved.",
        )

    rec.status = "approved"
    db.commit()
    db.refresh(rec)
    return rec


@router.patch("/{recommendation_id}/implement", response_model=InventoryRecommendationResponse)
def implement_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Mark an approved recommendation as implemented (approved → implemented)."""
    rec = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    required = _VALID_TRANSITIONS["implemented"]
    if rec.status != required:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot implement a recommendation with status '{rec.status}'. "
                   f"Only '{required}' recommendations can be implemented.",
        )

    rec.status = "implemented"
    db.commit()
    db.refresh(rec)
    return rec


@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Delete a recommendation."""
    rec = db.query(InventoryRecommendation).filter(
        InventoryRecommendation.id == recommendation_id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    db.delete(rec)
    db.commit()
