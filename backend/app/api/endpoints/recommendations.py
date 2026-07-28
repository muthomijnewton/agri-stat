from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import InventoryRecommendation, Notification, Product, User
from app.schemas.schemas import (
    InventoryRecommendationCreate,
    InventoryRecommendationUpdate,
    InventoryRecommendationResponse,
)
from app.core.security import get_current_user
from app.services.forecasting import ForecastingService
from typing import List
from datetime import date

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


# ---------------------------------------------------------------------------
# Generate endpoints
# ---------------------------------------------------------------------------

@router.post("/generate/{product_id}", status_code=status.HTTP_201_CREATED)
def generate_recommendation(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Generate an inventory recommendation for a single product using the
    latest forecast data.  Creates a new 'pending' recommendation and a
    matching notification.
    """
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.is_active == True,  # noqa: E712
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    result = ForecastingService.calculate_inventory_recommendation(db, product_id)

    if result["recommended_quantity"] == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Cannot generate recommendation for '{product.name}': no forecasts available. "
                   "Generate a forecast first.",
        )

    rec = InventoryRecommendation(
        product_id=product_id,
        recommended_quantity=result["recommended_quantity"],
        recommendation_date=date.today(),
        reason=result["reason"],
        status="pending",
    )
    db.add(rec)
    db.flush()

    db.add(Notification(
        title="New Recommendation Generated",
        message=(
            f"Recommendation for '{product.name}': "
            f"stock {result['recommended_quantity']} units "
            f"(avg daily demand {result.get('average_daily_demand', '?')})"
        ),
        type="info",
        read=False,
    ))
    db.commit()
    db.refresh(rec)

    return {
        "message": f"Recommendation generated for '{product.name}'",
        "recommendation_id": rec.id,
        "recommended_quantity": rec.recommended_quantity,
        "reason": rec.reason,
    }


@router.post("/generate-all", status_code=status.HTTP_200_OK)
def generate_all_recommendations(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """
    Generate inventory recommendations for every active product that has
    at least one forecast.  Products with no forecasts are skipped.
    Returns a per-product summary identical in shape to the batch forecast
    response so the frontend can reuse the same log UI.
    """
    products = db.query(Product).filter(Product.is_active == True).all()  # noqa: E712

    results = []
    succeeded = skipped = failed = 0

    for product in products:
        try:
            result = ForecastingService.calculate_inventory_recommendation(db, product.id)

            if result["recommended_quantity"] == 0:
                results.append({
                    "product_id": product.id,
                    "product_name": product.name,
                    "status": "skipped",
                    "message": "No forecasts available — generate a forecast first",
                })
                skipped += 1
                continue

            rec = InventoryRecommendation(
                product_id=product.id,
                recommended_quantity=result["recommended_quantity"],
                recommendation_date=date.today(),
                reason=result["reason"],
                status="pending",
            )
            db.add(rec)
            db.flush()

            db.add(Notification(
                title="Recommendation Generated",
                message=(
                    f"'{product.name}': stock {result['recommended_quantity']} units"
                ),
                type="info",
                read=False,
            ))

            results.append({
                "product_id": product.id,
                "product_name": product.name,
                "status": "success",
                "message": f"Recommended quantity: {result['recommended_quantity']} units",
                "recommended_quantity": result["recommended_quantity"],
            })
            succeeded += 1

        except Exception as exc:
            results.append({
                "product_id": product.id,
                "product_name": product.name,
                "status": "error",
                "message": str(exc),
            })
            failed += 1

    db.commit()

    return {
        "summary": {
            "total_products": len(products),
            "succeeded": succeeded,
            "skipped": skipped,
            "failed": failed,
        },
        "results": results,
    }
