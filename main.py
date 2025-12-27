from fastapi import FastAPI, Request, HTTPException
import requests
import os
import time
import uuid

app = FastAPI()

LIQUID_BASE = "https://api.liquidcharts.com/dxsca-web"

LIQUID_LOGIN = os.getenv("LIQUID_LOGIN")
LIQUID_DOMAIN = os.getenv("LIQUID_DOMAIN")
LIQUID_PASSWORD = os.getenv("LIQUID_PASSWORD")
LIQUID_ACCOUNT = os.getenv("LIQUID_ACCOUNT")

SESSION_TOKEN = None
SESSION_TIME = 0

def liquid_login():
    global SESSION_TOKEN, SESSION_TIME

    if SESSION_TOKEN and time.time() - SESSION_TIME < 600:
        return SESSION_TOKEN

    r = requests.post(
        f"{LIQUID_BASE}/login",
        json={
            "username": LIQUID_LOGIN,
            "domain": LIQUID_DOMAIN,
            "password": LIQUID_PASSWORD
        },
        timeout=10
    )

    r.raise_for_status()
    data = r.json()

    SESSION_TOKEN = data["token"]
    SESSION_TIME = time.time()
    return SESSION_TOKEN

@app.post("/webhook")
async def webhook(req: Request):
    body = await req.json()

    try:
        symbol = body["symbol"]
        instrument = body["instrument"]
        side = body["side"]
        qty = int(body["qty"])
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid payload")

    token = liquid_login()
    account = LIQUID_ACCOUNT.replace(":", "%3A")

    order = {
        "orderCode": f"tv-{uuid.uuid4()}",
        "type": "MARKET",
        "instrument": instrument,
        "quantity": qty,
        "side": side
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    r = requests.post(
        f"{LIQUID_BASE}/accounts/{account}/orders",
        json=order,
        headers=headers,
        timeout=10
    )

    r.raise_for_status()
    return r.json()

@app.get("/")
def health():
    return {"status": "ok"}
