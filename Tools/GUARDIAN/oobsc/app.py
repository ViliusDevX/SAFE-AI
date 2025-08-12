from fastapi import FastAPI
from pydantic import BaseModel
import time
import threading
import os

app = FastAPI()
AUTH = os.getenv("AUTH_TOKEN", "")

class Heartbeat(BaseModel):
    source: str

class InhibitRequest(BaseModel):
    inhibit: bool

STATE = {
    "inhibit": False,
    "last_heartbeat": {},  # source -> unix time
}

def clear_inhibit_after(seconds=10):
    def _clr():
        time.sleep(seconds)
        STATE["inhibit"] = False
        print(f"[oobsc] Auto-cleared inhibit after {seconds}s", flush=True)
    threading.Thread(target=_clr, daemon=True).start()

def check_auth(request):
    token = request.headers.get("x-guardian-auth", "")
    if AUTH and token != AUTH:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/heartbeat")
def heartbeat(hb: Heartbeat):
    STATE["last_heartbeat"][hb.source] = time.time()
    return {"ok": True}

@app.get("/status")
def status():
    now = time.time()
    ages = {src: now - ts for src, ts in STATE["last_heartbeat"].items()}
    return {"inhibit": STATE["inhibit"], "heartbeat_ages_sec": ages}

@app.post("/inhibit")
def set_inhibit(req: InhibitRequest, request: Request):
    check_auth(request)
    STATE["inhibit"] = req.inhibit
    return {"inhibit": STATE["inhibit"]}

@app.post("/inhibit")
def set_inhibit(req: InhibitRequest):
    STATE["inhibit"] = req.inhibit
    if req.inhibit:
        clear_inhibit_after(10)   # remove for production
    return {"inhibit": STATE["inhibit"]}
