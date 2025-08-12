# runtime/egress_demo.py
import requests, json, os

GATEWAY = os.getenv("EGRESS_GATEWAY", "http://127.0.0.1:9100/fetch")

def call(url: str, method="GET", body=None):
    payload = {"url": url, "method": method}
    if body is not None:
        payload["body"] = body
    r = requests.post(GATEWAY, json=payload, timeout=5)
    print(f"[egress_demo] {url} -> {r.status_code} {r.text[:200]}")

if __name__ == "__main__":
    print("[egress_demo] Allowed test (httpbin.org)")
    call("https://httpbin.org/get")

    print("[egress_demo] Forbidden test (example.com)")
    call("https://example.com/")
