# detectors/egress_gateway.py
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from urllib.parse import urlparse
import os, httpx, asyncio

OOBSC_URL = os.getenv("OOBSC_URL", "http://127.0.0.1:8000")
ALLOWED = set(
    d.strip().lower()
    for d in os.getenv("ALLOWED_DOMAINS", "httpbin.org").split(",")
    if d.strip()
)
TIMEOUT = float(os.getenv("FETCH_TIMEOUT_SEC", "5"))

app = FastAPI(title="EgressAllowlistGateway")

class FetchReq(BaseModel):
    url: str
    method: str = "GET"
    headers: dict | None = None
    body: str | None = None

async def trigger_inhibit(reason: str):
    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            await client.post(f"{OOBSC_URL}/inhibit", json={"inhibit": True})
            print(f"[egress] Inhibit triggered: {reason}", flush=True)
        except Exception as e:
            print(f"[egress] Failed to contact OOBSC: {e}", flush=True)

@app.get("/health")
async def health():
    return {"ok": True, "allowed_domains": sorted(ALLOWED)}

@app.post("/fetch")
async def fetch(req: FetchReq):
    # Parse hostname
    parsed = urlparse(req.url)
    host = (parsed.hostname or "").lower()

    if not host:
        raise HTTPException(status_code=400, detail="Invalid URL")

    # Enforce allow-list
    if host not in ALLOWED:
        await trigger_inhibit(f"Outbound to forbidden domain: {host}")
        raise HTTPException(status_code=403, detail=f"Domain not allowed: {host}")

    # Forward the request
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=True) as client:
            resp = await client.request(
                req.method.upper(),
                req.url,
                headers=req.headers,
                content=(req.body.encode("utf-8") if req.body is not None else None),
            )
            # Return a trimmed response (status + text)
            text = resp.text
            # Keep it small for logs
            if len(text) > 2000:
                text = text[:2000] + "...(truncated)"
            return {
                "status_code": resp.status_code,
                "headers": dict(resp.headers),
                "text": text,
            }
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Upstream error: {e}")
