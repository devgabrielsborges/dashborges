from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date
import pandas as pd

from .database import get_db, Transaction

app = FastAPI(title="DashBorges API")


# Pydantic models for request/response
class TransactionBase(BaseModel):
    date: date
    category: str
    description: str
    amount: float
    type: str


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int

    class Config:
        orm_mode = True


# CRUD endpoints
@app.post("/transactions/", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    db_transaction = Transaction(
        date=transaction.date,
        category=transaction.category,
        description=transaction.description,
        amount=transaction.amount,
        type=transaction.type.lower(),
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.get("/transactions/", response_model=List[TransactionResponse])
def read_transactions(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)

    # Apply filters if provided
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)
    if category:
        query = query.filter(Transaction.category == category)
    if type:
        query = query.filter(Transaction.type == type.lower())

    transactions = query.offset(skip).limit(limit).all()
    return transactions


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int, transaction: TransactionCreate, db: Session = Depends(get_db)
):
    db_transaction = (
        db.query(Transaction).filter(Transaction.id == transaction_id).first()
    )
    if db_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Update transaction attributes
    db_transaction.date = transaction.date
    db_transaction.category = transaction.category
    db_transaction.description = transaction.description
    db_transaction.amount = transaction.amount
    db_transaction.type = transaction.type.lower()

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@app.post("/transactions/bulk/")
def bulk_upload_transactions(
    transactions: List[TransactionCreate], db: Session = Depends(get_db)
):
    db_transactions = []
    for transaction in transactions:
        db_transaction = Transaction(
            date=transaction.date,
            category=transaction.category,
            description=transaction.description,
            amount=transaction.amount,
            type=transaction.type.lower(),
        )
        db.add(db_transaction)
        db_transactions.append(db_transaction)

    db.commit()
    return {"message": f"{len(db_transactions)} transactions created successfully"}


# API endpoint to get summary statistics
@app.get("/summary/")
def get_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Transaction)
    if start_date:
        query = query.filter(Transaction.date >= start_date)
    if end_date:
        query = query.filter(Transaction.date <= end_date)

    transactions = query.all()

    # Convert to DataFrame for easier analysis
    if not transactions:
        return {
            "total_income": 0,
            "total_expenses": 0,
            "balance": 0,
            "period": "No data",
        }

    df = pd.DataFrame([t.to_dict() for t in transactions])
    total_income = df[df["type"] == "income"]["amount"].sum()
    total_expenses = df[df["type"] == "expense"]["amount"].sum()
    balance = total_income - total_expenses

    period = "All time"
    if start_date and end_date:
        period = f"{start_date} to {end_date}"
    elif start_date:
        period = f"Since {start_date}"
    elif end_date:
        period = f"Until {end_date}"

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "balance": balance,
        "period": period,
    }
