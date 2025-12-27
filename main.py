import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")  # set in Railway Variables

class WebhookPayload(BaseModel):
    symbol: str
    side: str
    qty: int
    entry: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None
    secret: str  # REQUIRED now

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/webhook")
def webhook(payload: WebhookPayload):
    # 1) Secret check
    if not WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Server missing WEBHOOK_SECRET")
    if payload.secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # 2) Confirm received (safe for now)
    data = payload.dict()
    data.pop("secret", None)  # don't echo secret back
    return {"status": "ok", "received": data}
