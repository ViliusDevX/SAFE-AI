from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import time, threading, os

app = FastAPI()
AUTH = os.getenv("AUTH_TOKEN", "")

class Heartbeat(BaseModel):
    source: str | None = None
    agent: str | None = None

class InhibitRequest(BaseModel):
    inhibit: bool

STATE = {
    "inhibit": False,
    "heartbeats": {},  # source/agent -> unix time
}

def clear_inhibit_after(seconds=10):
    def _clr():
        time.sleep(seconds)
        STATE["inhibit"] = False
        print(f"[oobsc] Auto-cleared inhibit after {seconds}s", flush=True)
    threading.Thread(target=_clr, daemon=True).start()

def check_auth(request: Request):
    token = request.headers.get("x-guardian-auth", "")
    if AUTH and token != AUTH:
        raise HTTPException(status_code=401, detail="unauthorized")

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/heartbeat")
def heartbeat(hb: Heartbeat):
    who = hb.source or hb.agent or "guarded_ai"
    STATE["heartbeats"][who] = time.time()
    return {"ok": True, "agent": who}

@app.get("/status")
def status():
    now = time.time()
    ages = {src: now - ts for src, ts in STATE["heartbeats"].items()}
    return {"inhibit": STATE["inhibit"], "heartbeat_ages_sec": ages}

@app.post("/inhibit")
def set_inhibit(req: InhibitRequest, request: Request):
    check_auth(request)
    STATE["inhibit"] = req.inhibit
    # if req.inhibit:
    #     clear_inhibit_after(10)  # remove for stability
    return {"inhibit": STATE["inhibit"]}
