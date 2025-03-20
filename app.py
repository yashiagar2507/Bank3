from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, Column, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base
import uuid
import joblib  # For loading pre-trained ML model
import numpy as np

# Load the pre-trained AI fraud detection model
fraud_model = joblib.load("fraud_detection_model.pkl")

# Define Base class
Base = declarative_base()

# Define Account Model
class Account(Base):
    __tablename__ = "accounts"
    account_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    balance = Column(Float, nullable=False, default=0.0)

# Define Transaction Model
class Transaction(Base):
    __tablename__ = "transactions"
    transaction_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(String, ForeignKey("accounts.account_id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # Enum: "debit" or "credit"

# FastAPI app
app = FastAPI()

# Database setup
DATABASE_URL = "postgresql://myuser:mypassword@localhost/banking"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Request Model
class TransactionRequest(BaseModel):
    account_id: str
    amount: float

# Fraud Detection Function
def is_fraudulent(transaction_amount: float) -> bool:
    """Predict whether a transaction is fraudulent based on amount and AI model."""
    prediction = fraud_model.predict(np.array([[transaction_amount]]))
    return bool(prediction[0])  # Return True if fraudulent, False otherwise

@app.post("/transactions/credit")
def credit(transaction: TransactionRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    # AI Fraud Detection
    if is_fraudulent(transaction.amount):
        raise HTTPException(status_code=403, detail="Fraudulent transaction detected!")

    account.balance += transaction.amount
    db.commit()

    return {"message": "Credit successful", "new_balance": account.balance}

@app.post("/transactions/debit")
def debit(transaction: TransactionRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    if account.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    # AI Fraud Detection
    if is_fraudulent(transaction.amount):
        raise HTTPException(status_code=403, detail="Fraudulent transaction detected!")

    account.balance -= transaction.amount
    db.commit()

    return {"message": "Debit successful", "new_balance": account.balance}

@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == str(account_id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account.account_id, "balance": account.balance}
