"""Load test: 30 simulated raters against a fresh server with synthetic clips.

python -m listening_test.load_test --raters 30 --seconds 120

Starts its own server on a free port with a temporary database, so it never touches
the real classroom data. Passes when there are zero errors and the results page
reflects new ratings within 5 seconds.
"""

import argparse
import io
import random
import socket
import sys
import tempfile
import threading
import time
import zipfile
from pathlib import Path

import numpy as np
import requests
import soundfile as sf
from waitress.server import create_server

from .app import create_app
from .pair_codes import ensure_codes

FRESHNESS_LIMIT_S = 5.0


def synthetic_zip(seed):
    rng = np.random.default_rng(seed)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name in ("real.wav", "clone_3s.wav", "clone_6s.wav", "clone_10s.wav"):
            sr = 24000
            t = np.arange(int(sr * rng.uniform(4, 7))) / sr
            wav = 0.2 * np.sin(2 * np.pi * rng.uniform(120, 300) * t) + 0.01 * rng.standard_normal(len(t))
            clip = io.BytesIO()
            sf.write(clip, wav.astype(np.float32), sr, format="WAV", subtype="PCM_16")
            zf.writestr(name, clip.getvalue())
    return buf.getvalue()


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Stats:
    def __init__(self):
        self.lock = threading.Lock()
        self.ratings = 0
        self.requests = 0
        self.errors = []

    def ok(self, rated=False):
        with self.lock:
            self.requests += 1
            if rated:
                self.ratings += 1

    def error(self, what):
        with self.lock:
            self.requests += 1
            self.errors.append(what)


def rater_loop(base, codes, stats, stop_at, seed):
    rng = random.Random(seed)
    while time.time() < stop_at:
        session = requests.Session()
        try:
            r = session.post(base + "beoordelen", data={"code": rng.choice(codes)}, allow_redirects=False, timeout=10)
            stats.ok() if r.status_code == 302 else stats.error(f"login {r.status_code}")
            while time.time() < stop_at:
                r = session.get(base + "api/next", timeout=10)
                if r.status_code != 200:
                    stats.error(f"next {r.status_code}")
                    break
                stats.ok()
                data = r.json()
                if data["done"]:
                    break  # this rater heard everything; start over as a new rater
                r = session.get(base + data["url"].lstrip("/"), timeout=10)
                stats.ok() if r.status_code == 200 and r.content[:4] == b"RIFF" else stats.error(f"clip {r.status_code}")
                time.sleep(rng.uniform(0.05, 0.4))  # "listening"
                r = session.post(base + "api/rate", json={"clip_id": data["clip_id"],
                                                          "answer": rng.choice(["echt", "nep"])}, timeout=10)
                stats.ok(rated=True) if r.status_code == 200 else stats.error(f"rate {r.status_code}")
        except requests.RequestException as e:
            stats.error(type(e).__name__)


def freshness_probe(base, stats, stop_at, lags):
    """Note the client-side rating count, then time how long until /api/results shows it."""
    while time.time() < stop_at:
        with stats.lock:
            target = stats.ratings
        t0 = time.time()
        while time.time() - t0 < 30:
            try:
                if requests.get(base + "api/results", timeout=10).json()["ratings"] >= target:
                    break
            except requests.RequestException:
                pass
            time.sleep(0.25)
        lags.append(time.time() - t0)
        time.sleep(1)


def run(raters=30, seconds=120, pairs=20):
    with tempfile.TemporaryDirectory() as tmp:
        base_dir = Path(tmp)
        codes = ensure_codes(base_dir, pairs)
        port = free_port()
        server = create_server(create_app(base_dir), host="127.0.0.1", port=port, threads=24, connection_limit=200)
        threading.Thread(target=server.run, daemon=True).start()
        base = f"http://127.0.0.1:{port}/"
        time.sleep(0.5)

        for i, code in enumerate(codes):
            for speaker in ("A", "B"):
                r = requests.post(base + "upload", data={"code": code, "speaker": speaker},
                                  files={"file": (f"{code}-{speaker}.zip", synthetic_zip(i * 2 + ord(speaker)))})
                if r.status_code != 200:
                    print(f"Upload failed for {code}-{speaker}: {r.status_code}")
                    return False
        print(f"Uploaded {len(codes) * 2} sets ({len(codes) * 8} clips). Running {raters} raters for {seconds} s...")

        stats, lags = Stats(), []
        stop_at = time.time() + seconds
        threads = [threading.Thread(target=rater_loop, args=(base, codes, stats, stop_at, i)) for i in range(raters)]
        threads.append(threading.Thread(target=freshness_probe, args=(base, stats, stop_at, lags)))
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        final = requests.get(base + "api/results", timeout=10).json()
        # The server thread is a daemon; closing it mid-select only prints a spurious traceback.

    max_lag = max(lags) if lags else 0.0
    print(f"Requests: {stats.requests}, ratings: {stats.ratings} (server counted {final['ratings']}), "
          f"errors: {len(stats.errors)}, max results lag: {max_lag:.2f} s")
    if stats.errors:
        print("First errors:", stats.errors[:10])
    passed = not stats.errors and final["ratings"] == stats.ratings and max_lag <= FRESHNESS_LIMIT_S
    print("PASS" if passed else "FAIL")
    return passed


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--raters", type=int, default=30)
    parser.add_argument("--seconds", type=int, default=120)
    args = parser.parse_args()
    sys.exit(0 if run(args.raters, args.seconds) else 1)


if __name__ == "__main__":
    main()
