from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.database import get_db
from app.models.models import Transaction, Product, User
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from app.core.security import get_current_user
from typing import List
from datetime import date

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

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
    """Return total transaction value grouped by product category."""
    results = (
        db.query(
            Product.category,
            func.sum(Transaction.total_price).label("total_amount"),
        )
        .join(Product, Transaction.product_id == Product.id)
        .group_by(Product.category)
        .all()
    )
    return [{"category": r.category, "total": float(r.total_amount)} for r in results]


@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0,
    limit: int = 100,
    product_id: int = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """List transactions with optional filtering by product and date range."""
    query = db.query(Transaction)

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
    _: User = Depends(get_current_user),
):
    """Record a new transaction."""
    db_transaction = Transaction(**transaction.model_dump())
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
    """Update a transaction."""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in transaction_update.model_dump(exclude_unset=True).items():
        setattr(transaction, key, value)

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
