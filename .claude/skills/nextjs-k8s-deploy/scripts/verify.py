#!/usr/bin/env python3
"""Verify a Next.js Kubernetes deployment health.

Checks deployment replicas, pod status, and service endpoints.
Outputs a JSON health report and exits 0 (healthy) or 1 (unhealthy).

Usage:
    python verify.py --app-name myapp
    python verify.py --app-name myapp --namespace staging
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def check_deployment(app_name: str, namespace: str) -> dict:
    """Check deployment replica status."""
    rc, out, err = run_cmd([
        "kubectl", "get", "deployment", app_name,
        "-n", namespace, "-o", "json"
    ])
    if rc != 0:
        return {"exists": False, "error": err.strip()}

    data = json.loads(out)
    spec_replicas = data.get("spec", {}).get("replicas", 0)
    status = data.get("status", {})
    ready_replicas = status.get("readyReplicas", 0)
    available_replicas = status.get("availableReplicas", 0)
    updated_replicas = status.get("updatedReplicas", 0)

    return {
        "exists": True,
        "desired_replicas": spec_replicas,
        "ready_replicas": ready_replicas,
        "available_replicas": available_replicas,
        "updated_replicas": updated_replicas,
        "fully_available": ready_replicas == spec_replicas and spec_replicas > 0,
    }


def check_pods(app_name: str, namespace: str) -> dict:
    """Check pod status for the application."""
    rc, out, err = run_cmd([
        "kubectl", "get", "pods",
        "-n", namespace,
        "-l", f"app={app_name}",
        "-o", "json"
    ])
    if rc != 0:
        return {"error": err.strip(), "pods": [], "all_running": False}

    data = json.loads(out)
    pods = []
    all_running = True
    warnings = []

    for item in data.get("items", []):
        name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")
        container_statuses = item.get("status", {}).get("containerStatuses", [])
        ready_count = sum(1 for c in container_statuses if c.get("ready", False))
        total_count = len(container_statuses)

        restart_count = sum(
            c.get("restartCount", 0) for c in container_statuses
        )

        pod_info = {
            "name": name,
            "phase": phase,
            "ready": f"{ready_count}/{total_count}",
            "restarts": restart_count,
        }
        pods.append(pod_info)

        if phase != "Running":
            all_running = False
            if phase == "CrashLoopBackOff":
                warnings.append(f"{name} is in CrashLoopBackOff")
            elif phase == "Pending":
                warnings.append(f"{name} is still Pending")
            elif phase == "ImagePullBackOff":
                warnings.append(f"{name} cannot pull image (ImagePullBackOff)")

        if restart_count > 3:
            warnings.append(f"{name} has {restart_count} restarts")

    return {
        "pod_count": len(pods),
        "all_running": all_running,
        "pods": pods,
        "warnings": warnings,
    }


def check_service(app_name: str, namespace: str) -> dict:
    """Check service endpoints for the application."""
    rc, out, err = run_cmd([
        "kubectl", "get", "service", app_name,
        "-n", namespace, "-o", "json"
    ])
    if rc != 0:
        return {"exists": False, "error": err.strip()}

    data = json.loads(out)
    spec = data.get("spec", {})
    svc_type = spec.get("type", "")
    ports = []
    for p in spec.get("ports", []):
        port_info = {
            "port": p.get("port"),
            "target_port": p.get("targetPort"),
            "protocol": p.get("protocol", "TCP"),
        }
        if p.get("nodePort"):
            port_info["node_port"] = p["nodePort"]
        ports.append(port_info)

    # Check endpoints
    rc2, out2, _ = run_cmd([
        "kubectl", "get", "endpoints", app_name,
        "-n", namespace, "-o", "json"
    ])
    endpoint_count = 0
    if rc2 == 0:
        ep_data = json.loads(out2)
        subsets = ep_data.get("subsets", [])
        for subset in subsets:
            addresses = subset.get("addresses", [])
            endpoint_count += len(addresses)

    return {
        "exists": True,
        "type": svc_type,
        "ports": ports,
        "endpoint_count": endpoint_count,
        "has_endpoints": endpoint_count > 0,
    }


def verify_deployment(app_name: str, namespace: str) -> dict:
    """Run full verification and produce health report."""
    report = {
        "app_name": app_name,
        "namespace": namespace,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deployment": check_deployment(app_name, namespace),
        "pods": check_pods(app_name, namespace),
        "service": check_service(app_name, namespace),
    }

    # Determine overall health
    deployment_ok = report["deployment"].get("fully_available", False)
    pods_ok = report["pods"].get("all_running", False) and report["pods"].get("pod_count", 0) > 0
    service_ok = report["service"].get("has_endpoints", False)

    report["healthy"] = deployment_ok and pods_ok and service_ok
    report["summary"] = {
        "deployment_ready": deployment_ok,
        "pods_running": pods_ok,
        "service_reachable": service_ok,
    }

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Verify Next.js Kubernetes deployment health"
    )
    parser.add_argument(
        "--app-name", required=True,
        help="Application name (Helm release name and label selector)"
    )
    parser.add_argument(
        "--namespace", "-n", default="default",
        help="Kubernetes namespace (default: default)"
    )
    args = parser.parse_args()

    result = verify_deployment(args.app_name, args.namespace)
    print(json.dumps(result, indent=2))

    if result["healthy"]:
        print(f"\nDeployment '{args.app_name}' is healthy.")
        sys.exit(0)
    else:
        print(f"\nDeployment '{args.app_name}' is NOT healthy.")
        # Print specific issues
        if not result["summary"]["deployment_ready"]:
            print("  - Deployment replicas not fully available")
        if not result["summary"]["pods_running"]:
            print("  - Not all pods are running")
        if not result["summary"]["service_reachable"]:
            print("  - Service has no endpoints")
        for warning in result["pods"].get("warnings", []):
            print(f"  - {warning}")
        sys.exit(1)


if __name__ == "__main__":
    main()
