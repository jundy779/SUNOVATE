"""Small, dependency-free load probe for the proposed 25-user SUNOVATE demo.

The target is restricted to loopback by default. A caller must opt in to an
RFC1918/ULA address explicitly; public targets and hostnames are always rejected.
No credentials, document content, or business data are sent.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from ipaddress import ip_address, ip_network
from pathlib import Path
from threading import Barrier
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener

PRIVATE_NETWORKS = (
    ip_network("10.0.0.0/8"),
    ip_network("172.16.0.0/12"),
    ip_network("192.168.0.0/16"),
    ip_network("fc00::/7"),
)


@dataclass(frozen=True)
class RequestResult:
    status: int
    duration_ms: float
    error: str | None = None


def validate_target(raw_url: str, *, allow_private_target: bool) -> str:
    parsed = urlsplit(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Target harus berupa URL http/https yang lengkap")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Target tidak boleh memuat kredensial atau fragment")
    if parsed.hostname == "localhost":
        return raw_url
    try:
        address = ip_address(parsed.hostname)
    except ValueError as exc:
        raise ValueError("Gunakan localhost atau alamat IP privat literal, bukan hostname") from exc
    if address.is_loopback:
        return raw_url
    is_private = any(
        address.version == network.version and address in network for network in PRIVATE_NETWORKS
    )
    if allow_private_target and is_private:
        return raw_url
    raise ValueError("Target non-loopback memerlukan --allow-private-target dan IP privat")


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile * len(ordered)) - 1)
    return round(ordered[index], 2)


def _virtual_user(
    target: str, requests_per_user: int, timeout_seconds: float, start: Barrier
) -> list[RequestResult]:
    opener = build_opener(ProxyHandler({}))
    start.wait()
    results: list[RequestResult] = []
    for _ in range(requests_per_user):
        request = Request(  # noqa: S310 - target scheme/address validated before execution
            target, headers={"User-Agent": "SUNOVATE-Demo-Load-Probe/1.0"}
        )
        started = time.perf_counter()
        try:
            with opener.open(request, timeout=timeout_seconds) as response:
                response.read(4_096)
                status = response.status
            error = None if 200 <= status < 400 else f"HTTP_{status}"
        except HTTPError as exc:
            status = exc.code
            error = f"HTTP_{exc.code}"
        except (TimeoutError, URLError, OSError) as exc:
            status = 0
            error = type(exc).__name__
        results.append(
            RequestResult(
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1_000, 2),
                error=error,
            )
        )
    return results


def run_probe(
    *, target: str, users: int, requests_per_user: int, timeout_seconds: float
) -> tuple[dict[str, object], list[RequestResult]]:
    start = Barrier(users)
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as executor:
        batches = list(
            executor.map(
                lambda _: _virtual_user(target, requests_per_user, timeout_seconds, start),
                range(users),
            )
        )
    elapsed = time.perf_counter() - started
    results = [result for batch in batches for result in batch]
    durations = [result.duration_ms for result in results]
    failures = [result for result in results if result.error is not None]
    status_counts = Counter(str(result.status) for result in results)
    summary: dict[str, object] = {
        "dataLabel": "SIMULATED_DATA",
        "target": target,
        "virtualUsers": users,
        "requestsPerUser": requests_per_user,
        "requestsTotal": len(results),
        "successfulRequests": len(results) - len(failures),
        "failedRequests": len(failures),
        "errorRate": round(len(failures) / len(results), 4),
        "elapsedSeconds": round(elapsed, 3),
        "requestsPerSecond": round(len(results) / elapsed, 2),
        "latencyMs": {
            "min": round(min(durations), 2),
            "p50": _percentile(durations, 0.50),
            "p95": _percentile(durations, 0.95),
            "p99": _percentile(durations, 0.99),
            "max": round(max(durations), 2),
        },
        "statusCounts": dict(sorted(status_counts.items())),
    }
    return summary, results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Probe beban demo SUNOVATE dengan data simulasi")
    parser.add_argument("--target", default="http://127.0.0.1:8080/api/v1/health")
    parser.add_argument("--users", type=int, default=25)
    parser.add_argument("--requests-per-user", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=float, default=5.0)
    parser.add_argument("--max-error-rate", type=float, default=0.01)
    parser.add_argument("--max-p95-ms", type=float, default=1_500.0)
    parser.add_argument("--allow-private-target", action="store_true")
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not 1 <= args.users <= 100:
        raise SystemExit("--users harus antara 1 dan 100")
    if not 1 <= args.requests_per_user <= 100:
        raise SystemExit("--requests-per-user harus antara 1 dan 100")
    if args.timeout_seconds <= 0:
        raise SystemExit("--timeout-seconds harus lebih besar dari 0")
    try:
        target = validate_target(args.target, allow_private_target=args.allow_private_target)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    summary, results = run_probe(
        target=target,
        users=args.users,
        requests_per_user=args.requests_per_user,
        timeout_seconds=args.timeout_seconds,
    )
    latency = summary["latencyMs"]
    assert isinstance(latency, dict)
    passed = bool(
        float(summary["errorRate"]) <= args.max_error_rate
        and float(latency["p95"]) <= args.max_p95_ms
    )
    report = {
        "summary": summary,
        "thresholds": {
            "maxErrorRate": args.max_error_rate,
            "maxP95Ms": args.max_p95_ms,
        },
        "passed": passed,
        "failures": [asdict(result) for result in results if result.error is not None][:20],
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
