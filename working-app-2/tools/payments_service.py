# tools/payments_service.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import Dict, Any

app = FastAPI(title="Payments Tool (mock)")

class Recipient(BaseModel):
    name: str
    account_number: str
    sort_code: str

class PaymentRequest(BaseModel):
    amount: float
    currency: str
    recipient: Recipient
    idempotency_key: str

@app.post("/create_payment")
def create_payment(req: PaymentRequest):
    # Very simple validation
    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be > 0")
    # Fake business rules
    if req.currency != "GBP":
        raise HTTPException(status_code=400, detail="Only GBP supported in demo")

    payment_id = "pay_" + uuid.uuid4().hex[:12]
    # In a real tool, persist, call core banking, return status etc.
    return {"status": "success", "payment_id": payment_id, "amount": req.amount}
