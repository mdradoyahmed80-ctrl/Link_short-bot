"""Keep-alive pinger: sends a request to the site's /health every 9-10 minutes
so free hosting (e.g. Render) does not put the service to sleep.
Uses only the Python standard library - no new dependencies."""
import os, random, threading, time, urllib.request
from datetime import datetime, timezone


def _site_url():
    url = (os.getenv("KEEPALIVE_URL", "").strip()
           or os.getenv("BASE_URL", "").strip()
           or os.getenv("RENDER_EXTERNAL_URL", "").strip()).rstrip("/")
    return url


def _loop(url):
    time.sleep(random.uniform(540, 600))  # first ping after 9-10 minutes
    while True:
        try:
            with urllib.request.urlopen(url + "/health", timeout=30) as r:
                print(f"[keepalive] {datetime.now(timezone.utc).isoformat()} ping OK: {r.status}", flush=True)
        except Exception as exc:
            print(f"[keepalive] ping failed: {type(exc).__name__}: {exc}", flush=True)
        time.sleep(random.uniform(540, 600))  # 9-10 minutes


def start_keepalive():
    url = _site_url()
    if not url.startswith("http"):
        print("[keepalive] not started: set BASE_URL (or KEEPALIVE_URL).", flush=True)
        return
    threading.Thread(target=_loop, args=(url,), name="keepalive", daemon=True).start()
    print(f"[keepalive] started for {url}", flush=True)
