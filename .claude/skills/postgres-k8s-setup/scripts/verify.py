#!/usr/bin/env python3
"""Verify PostgreSQL deployment health on Kubernetes.

Usage:
    python verify.py                        # Default namespace: postgres
    python verify.py --namespace my-pg      # Custom namespace
    python verify.py --release pg-main      # Custom release name
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


def verify_postgres(namespace: str = "postgres", release: str = "postgresql") -> dict:
    """Verify PostgreSQL pods, services, and PVC status."""
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

    # Check PVCs
    rc3, out3, _ = run_cmd([
        "kubectl", "get", "pvc", "-n", namespace,
        "-l", f"app.kubernetes.io/instance={release}",
        "-o", "json"
    ])
    if rc3 == 0:
        pvc_data = json.loads(out3)
        pvcs = []
        for item in pvc_data.get("items", []):
            name = item["metadata"]["name"]
            phase = item.get("status", {}).get("phase", "Unknown")
            capacity = item.get("status", {}).get("capacity", {}).get("storage", "N/A")
            pvcs.append({"name": name, "phase": phase, "capacity": capacity})
        report["pvcs"] = pvcs
        report["all_pvcs_bound"] = all(
            p["phase"] == "Bound" for p in pvcs
        ) if pvcs else False
    else:
        report["pvcs"] = []
        report["all_pvcs_bound"] = False

    report["healthy"] = all_running and len(pods) > 0 and report.get("all_pvcs_bound", False)
    return report


def main():
    parser = argparse.ArgumentParser(description="Verify PostgreSQL deployment")
    parser.add_argument("--namespace", "-n", default="postgres")
    parser.add_argument("--release", default="postgresql")
    args = parser.parse_args()

    result = verify_postgres(args.namespace, args.release)
    print(json.dumps(result, indent=2))

    if result.get("healthy"):
        print("\nPostgreSQL is healthy")
    else:
        print("\nPostgreSQL is not healthy")
        sys.exit(1)


if __name__ == "__main__":
    main()
