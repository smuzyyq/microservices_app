#!/usr/bin/env python3
import argparse
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def perform_request(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Tuple[float, bool]:
    started = time.perf_counter()
    ok = True
    request = Request(url, headers=headers or {})
    try:
        with urlopen(request, timeout=timeout) as response:
            response.read()
            if response.status >= 400:
                ok = False
    except (HTTPError, URLError, TimeoutError, Exception):
        ok = False
    return time.perf_counter() - started, ok


def summarize(mode: str, durations: list[float], errors: int, elapsed: float) -> dict:
    sorted_durations = sorted(durations)
    p95_index = max(int(len(sorted_durations) * 0.95) - 1, 0) if sorted_durations else 0
    total = len(durations)
    return {
        "mode": mode,
        "requests_total": total,
        "errors": errors,
        "elapsed_seconds": round(elapsed, 3),
        "rps": round(total / max(elapsed, 0.001), 2),
        "avg_latency_ms": round((sum(durations) / total) * 1000, 2) if total else 0,
        "p95_latency_ms": round(sorted_durations[p95_index] * 1000, 2) if sorted_durations else 0,
    }


def run_public_read_load(base_url: str, concurrency: int, requests_per_worker: int) -> dict:
    routes = [
        "/api/products/products/restaurants",
        "/api/products/products/search?q=plov",
        "/api/products/products/search?q=lagman",
        "/api/products/products/search?q=tea",
    ]
    jobs = []
    durations: list[float] = []
    errors = 0

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for worker_id in range(concurrency):
            for request_id in range(requests_per_worker):
                route = routes[(worker_id + request_id) % len(routes)]
                jobs.append(pool.submit(perform_request, f"{base_url}{route}"))

        for job in as_completed(jobs):
            duration, ok = job.result()
            durations.append(duration)
            if not ok:
                errors += 1

    return summarize("public-read", durations, errors, time.perf_counter() - started)


def run_order_read_load(base_url: str, token: str, concurrency: int, requests_per_worker: int) -> dict:
    jobs = []
    durations: list[float] = []
    errors = 0
    headers = {"Authorization": f"Bearer {token}"}

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=concurrency) as pool:
        for _ in range(concurrency):
            for _ in range(requests_per_worker):
                jobs.append(pool.submit(perform_request, f"{base_url}/api/orders/orders", headers))

        for job in as_completed(jobs):
            duration, ok = job.result()
            durations.append(duration)
            if not ok:
                errors += 1

    return summarize("order-read-authenticated", durations, errors, time.perf_counter() - started)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple load generator for Assignment 6 capacity testing.")
    parser.add_argument("--base-url", default="http://localhost", help="Base URL of the deployed application.")
    parser.add_argument("--mode", choices=["public-read", "order-read"], default="public-read")
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--requests-per-worker", type=int, default=50)
    parser.add_argument("--token-file", help="Path to a file containing a bearer token for authenticated order reads.")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    if args.mode == "order-read":
        if not args.token_file:
            raise SystemExit("--token-file is required for order-read mode.")
        token = Path(args.token_file).read_text(encoding="utf-8").strip()
        result = run_order_read_load(base_url, token, args.concurrency, args.requests_per_worker)
    else:
        result = run_public_read_load(base_url, args.concurrency, args.requests_per_worker)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
