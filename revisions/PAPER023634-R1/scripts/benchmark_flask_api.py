"""SCOBY Watch Major Issue 5: local HTTP Flask API latency benchmark.

Run against a locally running instance of the REAL api/app.py service.
Measures client-observed HTTP round-trip time, NOT server-only processing time
and NOT ESP32 -> Node-RED -> dashboard latency.

Usage (from repository root):
  python revisions/PAPER023634-R1/scripts/benchmark_flask_api.py --requests 300 --warmup 30
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_PAYLOAD = {
    "batch_id": "KB-BENCH-001",
    "recipe_id": "R1",
    "tea_type": "black_tea",
    "sugar_g_per_l": 80,
    "starter_ml": 150,
    "water_volume_l": 1.0,
    "day": 7,
    "room_temp_c": 24.4,
    "humidity_percent": 68.0,
    "ph": 3.56,
    "brix": 7.71,
}


def percentile(data: list[float], p: float) -> float:
    if not data:
        return float("nan")
    s = sorted(data)
    pos = (len(s) - 1) * p / 100.0
    lo = int(pos)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


def send_predict(url: str, timeout: float, payload: dict) -> tuple[float, int | None, bool, str]:
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = Request(url, encoded, headers={"Content-Type": "application/json"}, method="POST")
    status = None
    valid = False
    error = ""
    start = time.perf_counter_ns()
    try:
        with urlopen(req, timeout=timeout) as resp:
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            valid = (status == 200 and isinstance(body, dict) and
                     body.get("batch_id") == payload["batch_id"] and
                     body.get("final_status") in {
                         "balanced", "too_sour", "too_early", "still_sweet",
                         "manual_check", "temperature_warning"})
            if not valid:
                error = "unexpected JSON payload or HTTP status"
    except HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}"
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    elapsed_ms = (time.perf_counter_ns() - start) / 1e6
    return elapsed_ms, status, valid, error


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:5000/predict")
    parser.add_argument("--requests", type=int, default=300)
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--interval-ms", type=float, default=0.0,
                        help="Fixed pause between measured requests. Default: 0 ms.")
    parser.add_argument("--output-dir", type=Path, default=Path("revisions/PAPER023634-R1/results/api_benchmark"))
    args = parser.parse_args()
    if args.requests < 20 or args.warmup < 0 or args.timeout <= 0 or args.interval_ms < 0:
        parser.error("requests >= 20; warmup >= 0; timeout > 0; interval-ms >= 0")
    if not (args.url.startswith("http://127.0.0.1:") or args.url.startswith("http://localhost:")):
        parser.error("Only local loopback URLs are allowed (localhost/127.0.0.1)")

    print(f"Target: {args.url}")
    print(f"Sequential requests: {args.requests}; warmups: {args.warmup}; timeout: {args.timeout}s")
    print("Measurement: local HTTP round-trip incl. JSON serialization, routing, and model inference")

    # Fail fast if the real local service is not accessible.
    first = send_predict(args.url, args.timeout, DEFAULT_PAYLOAD)
    if not first[2]:
        print(f"ERROR: local /predict check failed: status={first[1]} {first[3]}", file=sys.stderr)
        print("Start the original API in another terminal: python api/app.py", file=sys.stderr)
        return 2

    for _ in range(args.warmup):
        send_predict(args.url, args.timeout, DEFAULT_PAYLOAD)

    rows = []
    for i in range(1, args.requests + 1):
        latency, status, success, error = send_predict(args.url, args.timeout, DEFAULT_PAYLOAD)
        rows.append({"request_index": i, "elapsed_ms": round(latency, 6),
                     "http_status": status, "valid_response": int(success),
                     "error": error})
        if i % 50 == 0 or i == args.requests:
            print(f"Measured {i}/{args.requests} requests")
        if args.interval_ms:
            time.sleep(args.interval_ms / 1000)

    samples = [float(r["elapsed_ms"]) for r in rows if r["valid_response"]]
    success_count = len(samples)
    failure_count = args.requests - success_count
    duration_ms = sum(float(r["elapsed_ms"]) for r in rows) + args.interval_ms * args.requests
    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source": "real locally running SCOBY Watch Flask HTTP API",
        "endpoint": args.url,
        "scope": "client-observed single-process sequential HTTP RTT; NOT MQTT or dashboard latency",
        "request_count": args.requests,
        "warmup_count": args.warmup,
        "success_count": success_count,
        "failure_count": failure_count,
        "error_rate_percent": failure_count / args.requests * 100,
        "interval_ms": args.interval_ms,
        "concurrency": 1,
        "successful_latency_mean_ms": statistics.mean(samples) if samples else None,
        "successful_latency_sd_ms": statistics.stdev(samples) if len(samples) > 1 else None,
        "successful_latency_min_ms": min(samples) if samples else None,
        "successful_latency_median_p50_ms": percentile(samples, 50) if samples else None,
        "successful_latency_p95_ms": percentile(samples, 95) if samples else None,
        "successful_latency_p99_ms": percentile(samples, 99) if samples else None,
        "successful_latency_max_ms": max(samples) if samples else None,
        "approx_completed_requests_per_second": args.requests / (duration_ms / 1000) if duration_ms else None,
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "note": "No claims of hardware deployment, public-network resilience, MQTT QoS, or end-to-end dashboard latency are supported by this test."
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    raw = args.output_dir / "api_latency_raw.csv"
    with raw.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["request_index", "elapsed_ms", "http_status", "valid_response", "error"])
        writer.writeheader()
        writer.writerows(rows)
    output = args.output_dir / "api_latency_summary.json"
    output.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Success: {success_count}/{args.requests}; errors: {failure_count} ({summary['error_rate_percent']:.2f}%)")
    if samples:
        print(f"HTTP RTT ms: P50={summary['successful_latency_median_p50_ms']:.3f}, "
              f"P95={summary['successful_latency_p95_ms']:.3f}, "
              f"P99={summary['successful_latency_p99_ms']:.3f}")
    print(f"Raw: {raw.resolve()}\nSummary: {output.resolve()}")
    return 0 if success_count == args.requests else 1


if __name__ == "__main__":
    sys.exit(main())
