import os, time, threading, subprocess, sys, requests

OOBSC_URL = os.getenv("OOBSC_URL", "http://oobsc:8000")
HEARTBEAT_SOURCE = os.getenv("HEARTBEAT_SOURCE", "guarded_ai")
HB_INTERVAL = float(os.getenv("HB_INTERVAL_SEC", "2"))
REQ_TIMEOUT = float(os.getenv("REQ_TIMEOUT_SEC", "1.5"))
STARTUP_GRACE = float(os.getenv("STARTUP_GRACE_SEC", "8"))  # NEW

def wait_for_oobsc():
    deadline = time.time() + STARTUP_GRACE
    while time.time() < deadline:
        try:
            r = requests.get(f"{OOBSC_URL}/health", timeout=REQ_TIMEOUT)
            if r.ok:
                print("[watchdog] OOBSC is up", flush=True)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    print("[watchdog] OOBSC not reachable after grace; enforcing fail-closed", flush=True)
    return False

def start_ai():
    print("[ai] Launching AI subprocess...", flush=True)
    return subprocess.Popen([sys.executable, "-c", "import time; time.sleep(10**9)"])

def kill_ai(proc, reason: str):
    print(f"[watchdog] Terminating AI. Reason: {reason}", flush=True)
    try:
        proc.terminate(); proc.wait(timeout=3)
    except Exception:
        try: proc.kill()
        except Exception: pass
    os._exit(1)

def watchdog_loop(proc):
    # main loop after startup grace
    while True:
        try:
            requests.post(f"{OOBSC_URL}/heartbeat", json={"source": HEARTBEAT_SOURCE}, timeout=REQ_TIMEOUT)
            status = requests.get(f"{OOBSC_URL}/status", timeout=REQ_TIMEOUT).json()
            if status.get("inhibit", False):
                kill_ai(proc, "OOBSC inhibit=true")
        except Exception as e:
            kill_ai(proc, f"Lost contact with OOBSC ({e})")
        time.sleep(HB_INTERVAL)

def main():
    # Wait for controller to come up (grace)
    if not wait_for_oobsc():
        # still enforce fail-closed by killing immediately
        proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(1)"])
        kill_ai(proc, "OOBSC not reachable at startup")
    ai_proc = start_ai()
    t = threading.Thread(target=watchdog_loop, args=(ai_proc,), daemon=True)
    t.start()
    code = ai_proc.wait()
    print(f"[ai] AI subprocess exited with code {code}", flush=True)
    sys.exit(code)

if __name__ == "__main__":
    main()
