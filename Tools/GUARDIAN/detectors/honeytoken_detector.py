# detectors/honeytoken_detector.py
from fastapi import FastAPI, Request
from pydantic import BaseModel
import os, pathlib, asyncio
import httpx

# --- Configuration ---
OOBSC_URL = os.getenv("OOBSC_URL", "http://127.0.0.1:8000")
HONEYPOT_HOST = os.getenv("HONEYPOT_HOST", "127.0.0.1")
HONEYPOT_PORT = int(os.getenv("HONEYPOT_PORT", "9000"))
DECOY_DIR = pathlib.Path("decoys")
DECOY_FILE = DECOY_DIR / "fake_key.txt"

# Ensure decoy exists (idempotent)
DECOY_DIR.mkdir(parents=True, exist_ok=True)
if not DECOY_FILE.exists():
    # You can change this value; keep it unique-ish.
    DECOY_FILE.write_text("FAKE_API_KEY=XYZ-123-SUPER-SECRET\n", encoding="utf-8")

TOKEN = DECOY_FILE.read_text(encoding="utf-8").strip()

app = FastAPI(title="HoneytokenDetector")

class InhibitReq(BaseModel):
    inhibit: bool

async def trigger_inhibit(reason: str):
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            await client.post(f"{OOBSC_URL}/inhibit", json={"inhibit": True})
            print(f"[detector] Inhibit triggered. Reason: {reason}", flush=True)
        except Exception as e:
            print(f"[detector] Failed to contact OOBSC: {e}", flush=True)

@app.get("/health")
async def health():
    return {"ok": True, "watching_for": TOKEN[:12] + "...(redacted)"}

@app.post("/ingest")
async def ingest(request: Request):
    body = await request.body()
    text = body.decode("utf-8", errors="ignore")
    print(f"[detector] Received {len(text)} bytes", flush=True)
    if TOKEN in text:
        await trigger_inhibit("Honeytoken observed in egress")
        return {"ok": True, "matched": True}
    return {"ok": True, "matched": False}
