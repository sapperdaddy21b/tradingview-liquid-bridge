from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class WebhookPayload(BaseModel):
    symbol: str
    side: str
    qty: int
    entry: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None

@app.get("/")
def root():
    return {"status": "ok"}

@app.post("/webhook")
def webhook(payload: WebhookPayload):
    # For now we just confirm we received it correctly
    return {"status": "ok", "received": payload.dict()}
