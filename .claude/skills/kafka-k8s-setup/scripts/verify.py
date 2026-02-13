#!/usr/bin/env python3
"""Verify Kafka deployment health on Kubernetes.

Usage:
    python verify.py                    # Default namespace: kafka
    python verify.py --namespace my-ns  # Custom namespace
"""
import argparse
import json
import subprocess
import sys


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", str(e)


def verify_kafka(namespace: str = "kafka", release: str = "kafka") -> dict:
    """Verify Kafka pods, services, and broker readiness."""
    report = {"namespace": namespace, "release": release}

    # Check pods
    rc, out, err = run_cmd([
        "kubectl", "get", "pods", "-n", namespace,
        "-l", f"app.kubernetes.io/instance={release}",
        "-o", "json"
    ])
    if rc != 0:
        report["error"] = err.strip()
        return report

    data = json.loads(out)
    pods = []
    all_running = True
    for item in data.get("items", []):
        name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")
        containers = item.get("status", {}).get("containerStatuses", [])
        ready = sum(1 for c in containers if c.get("ready", False))
        total = len(containers)
        pods.append({"name": name, "phase": phase, "ready": f"{ready}/{total}"})
        if phase != "Running":
            all_running = False

    report["pods"] = pods
    report["all_running"] = all_running

    # Check services
    rc2, out2, _ = run_cmd([
        "kubectl", "get", "svc", "-n", namespace,
        "-l", f"app.kubernetes.io/instance={release}",
        "-o", "json"
    ])
    if rc2 == 0:
        svc_data = json.loads(out2)
        services = []
        for item in svc_data.get("items", []):
            name = item["metadata"]["name"]
            svc_type = item.get("spec", {}).get("type", "")
            ports = [
                f"{p.get('port')}/{p.get('protocol', 'TCP')}"
                for p in item.get("spec", {}).get("ports", [])
            ]
            services.append({"name": name, "type": svc_type, "ports": ports})
        report["services"] = services

    report["healthy"] = all_running and len(pods) > 0
    return report


def main():
    parser = argparse.ArgumentParser(description="Verify Kafka deployment")
    parser.add_argument("--namespace", "-n", default="kafka")
    parser.add_argument("--release", default="kafka")
    args = parser.parse_args()

    result = verify_kafka(args.namespace, args.release)
    print(json.dumps(result, indent=2))

    if result.get("healthy"):
        print("\n✅ Kafka is healthy")
    else:
        print("\n❌ Kafka is not healthy")
        sys.exit(1)


if __name__ == "__main__":
    main()
