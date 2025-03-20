from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Float, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import uuid
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app = FastAPI()
# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)
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

@app.post("/transactions/credit")
def credit(transaction: TransactionRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == transaction.account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

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

    account.balance -= transaction.amount
    db.commit()

    return {"message": "Debit successful", "new_balance": account.balance}


@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.account_id == str(account_id)).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account.account_id, "balance": account.balance}

