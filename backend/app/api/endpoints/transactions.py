from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.database import get_db
from app.models.models import Transaction, Product, User
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.core.security import get_current_user
from typing import List, Optional
from datetime import date

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

VALID_TYPES = {"sale", "purchase"}

# ---------------------------------------------------------------------------
# ROUTE ORDER IS CRITICAL
# Static/specific paths must be registered before parameterised {id} paths
# so FastAPI does not swallow "summary" as an integer transaction_id.
# ---------------------------------------------------------------------------


@router.get("/summary")
def get_transaction_summary(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Return total sales revenue grouped by product category (purchases excluded)."""
    results = (
        db.query(
            Product.category,
            func.sum(Transaction.total_price).label("total_amount"),
        )
        .join(Product, Transaction.product_id == Product.id)
        .filter(Transaction.transaction_type == "sale")
        .group_by(Product.category)
        .all()
    )
    return [
        {"category": r.category, "total": float(r.total_amount or 0)}
        for r in results
    ]


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    product_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    transaction_type: Optional[str] = Query(None, description="Filter by 'sale' or 'purchase'"),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List transactions with optional filtering by product, date range, and type."""
    query = db.query(Transaction)

    if product_id:
        query = query.filter(Transaction.product_id == product_id)

    if transaction_type:
        if transaction_type not in VALID_TYPES:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"transaction_type must be 'sale' or 'purchase', got '{transaction_type}'",
            )
        query = query.filter(Transaction.transaction_type == transaction_type)

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

    return query.order_by(Transaction.transaction_date.desc()).offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Get a specific transaction by ID."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Record a new transaction. total_price is always recomputed server-side."""
    # Validate transaction_type
    txn_type = transaction.transaction_type or "sale"
    if txn_type not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"transaction_type must be 'sale' or 'purchase', got '{txn_type}'",
        )

    # Verify product exists
    product = db.query(Product).filter(
        Product.id == transaction.product_id,
        Product.is_active == True,  # noqa: E712
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Always compute total_price server-side — never trust the client value
    computed_total = (
        Decimal(str(transaction.unit_price)) * transaction.quantity
    ).quantize(Decimal("0.01"))

    db_transaction = Transaction(
        product_id=transaction.product_id,
        user_id=current_user.id,          # always injected from the JWT
        transaction_type=txn_type,
        quantity=transaction.quantity,
        unit_price=transaction.unit_price,
        total_price=computed_total,
        transaction_date=transaction.transaction_date,
        notes=transaction.notes,
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_update: TransactionUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Update a transaction. Recomputes total_price if quantity or unit_price changes."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = transaction_update.model_dump(exclude_unset=True)

    # Validate type if provided
    if "transaction_type" in updates and updates["transaction_type"] not in VALID_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"transaction_type must be 'sale' or 'purchase'",
        )

    # Apply scalar updates first
    for key, value in updates.items():
        if key != "total_price":   # total_price is always recomputed
            setattr(transaction, key, value)

    # Recompute total_price from current quantity × unit_price
    transaction.total_price = (
        Decimal(str(transaction.unit_price)) * transaction.quantity
    ).quantize(Decimal("0.01"))

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Delete a transaction."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
