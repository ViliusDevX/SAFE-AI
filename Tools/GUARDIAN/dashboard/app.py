# dashboard/app.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import subprocess, sys, os, asyncio
import httpx
from typing import Optional
import docker, os
from fastapi.responses import PlainTextResponse

MANAGED = os.getenv("MANAGED_CONTAINERS", "guardian-oobsc,guardian-ai,guardian-honeytoken,guardian-egress").split(",")
app = FastAPI(title="Guardian Dashboard")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
PROJECT_PREFIX = os.getenv("PROJECT_PREFIX", "guardian")
OOBSC = os.getenv("OOBSC_URL", "http://127.0.0.1:8000")
HONEYPOT = os.getenv("HONEYPOT_URL", "http://127.0.0.1:9000")
EGRESS = os.getenv("EGRESS_URL", "http://127.0.0.1:9100")
PROJECT = os.getenv("PROJECT_NAME", "guardian")
AUTH = os.getenv("AUTH_TOKEN", "")
HEAD = {"x-guardian-auth": AUTH} if AUTH else {}


def list_project_containers(client):
    # Compose sets label com.docker.compose.project=<project>
    return client.containers.list(all=True, filters={"label": f"com.docker.compose.project={PROJECT}"})

def run(cmd: list[str], cwd: Optional[str] = None) -> tuple[int, str, str]:
    """Run a command and capture output (cross-platform)."""
    p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err

def docker_logs_tail(n: int = 200) -> str:
    try:
        client = docker.from_env()
        containers = client.containers.list(all=True)
        # Only our compose project
        containers = [c for c in containers if c.name.startswith(PROJECT_PREFIX)]
        order = ["oobsc","ai","honeytoken","egress","dashboard"]
        containers.sort(key=lambda c: next((i for i,k in enumerate(order) if k in c.name), 999))
        out = []
        for c in containers:
            try:
                logs = c.logs(tail=n).decode("utf-8", errors="ignore")
            except Exception as e:
                logs = f"<unable to read logs: {e}>"
            out.append(f"===== {c.name} =====\n{logs.rstrip()}\n")
        return "\n".join(out)
    except Exception as e:
        return f"error reading docker logs: {e}"

def get_client():
    return docker.from_env()

def get_by_name(client, name):
    try:
        return client.containers.get(name)
    except Exception:
        return None

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- Compose control ---
@app.post("/api/compose/down")
async def compose_down():
    try:
        client = get_client()
        stopped = []
        for name in MANAGED:
            c = get_by_name(client, name)
            if not c:
                continue
            c.reload()
            if c.status not in ("exited", "dead"):
                c.stop(timeout=5)
            stopped.append(name)
        return JSONResponse({"ok": True, "stopped": stopped})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

@app.post("/api/compose/up")
async def compose_up():
    try:
        client = get_client()
        started = []
        for name in MANAGED:
            c = get_by_name(client, name)
            if not c:
                continue
            c.reload()
            if c.status in ("exited", "created"):
                c.start()
            started.append(name)
        # optional: wait a moment for OOBSC to come up for a smoother UI
        return JSONResponse({"ok": True, "started": started})
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

# --- Status / inhibit (proxy to OOBSC) ---
@app.get("/api/status")
async def api_status():
    async with httpx.AsyncClient(timeout=2.0) as client:
        r = await client.get(f"{OOBSC}/status")
        return JSONResponse(r.json())

@app.post("/api/inhibit/{state}")
async def api_inhibit(state: str):
    val = True if state.lower() in ("1", "true", "on") else False
    async with httpx.AsyncClient(timeout=2.0) as client:
        r = await client.post(f"{OOBSC}/inhibit", json={"inhibit": val})
        return JSONResponse(r.json())

# --- Tripwires (trigger demo actions) ---
@app.post("/api/honeytoken")
async def api_honeytoken():
    token = "FAKE_API_KEY=XYZ-123-SUPER-SECRET"
    async with httpx.AsyncClient(timeout=3.0) as client:
        r = await client.post(f"{HONEYPOT}/ingest", content=token, headers={"Content-Type": "text/plain"})
        return JSONResponse(r.json())

@app.post("/api/egress/allowed")
async def api_egress_allowed():
    payload = {"url": "https://httpbin.org/get"}
    async with httpx.AsyncClient(timeout=6.0) as client:
        r = await client.post(f"{EGRESS}/fetch", json=payload)
        return JSONResponse({"status": r.status_code, "body": r.text})

@app.post("/api/egress/forbidden")
async def api_egress_forbidden():
    payload = {"url": "https://example.com"}
    async with httpx.AsyncClient(timeout=6.0) as client:
        r = await client.post(f"{EGRESS}/fetch", json=payload)
        # Forbidden fetch will also trigger inhibit
        return JSONResponse({"status": r.status_code, "body": r.text})

# --- Logs (grab last N lines from compose) ---
@app.get("/api/logs", response_class=PlainTextResponse)
async def api_logs(n: int = 200):
    return PlainTextResponse(docker_logs_tail(n))
# Run: uvicorn dashboard.app:app --host 127.0.0.1 --port 8080
