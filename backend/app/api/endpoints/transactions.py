from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.db.database import get_db
from app.models.models import Transaction,Product
from app.schemas.schemas import TransactionCreate, TransactionUpdate, TransactionResponse
from typing import List
from datetime import date

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

# --- ROUTE ORDER IS CRITICAL ---
# 1. Specific static paths must go before dynamic {id} paths

@router.get("/summary")
def get_transaction_summary(db: Session = Depends(get_db)):
    """Get summarized transaction totals by product category"""
    # We join Transaction to Product to access the 'category' column
    results = db.query(
        Product.category, 
        func.sum(Transaction.total_price).label("total_amount")
    ).join(Product, Transaction.product_id == Product.id) \
     .group_by(Product.category).all()
    
    return [{"category": r.category, "total": float(r.total_amount)} for r in results]

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = 0, 
    limit: int = 100,
    product_id: int = Query(None),
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
):
    """Get transactions with optional filtering"""
    query = db.query(Transaction)
    
    if product_id:
        query = query.filter(Transaction.product_id == product_id)
    
    if start_date and end_date:
        query = query.filter(and_(
            Transaction.transaction_date >= start_date,
            Transaction.transaction_date <= end_date
        ))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    """Get a specific transaction by ID"""
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

# --- Other methods (POST, PUT, DELETE) follow ---

@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(transaction_id: int, transaction_update: TransactionUpdate, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    update_data = transaction_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(transaction, key, value)
    
    db.commit()
    db.refresh(transaction)
    return transaction

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    return None