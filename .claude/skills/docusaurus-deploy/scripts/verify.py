#!/usr/bin/env python3
"""Verify Docusaurus deployment health on Kubernetes.

Usage:
    python verify.py --name my-docs                    # Default namespace: docs
    python verify.py --name my-docs --namespace my-ns  # Custom namespace
"""
import argparse
import json
import subprocess
import sys


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a shell command and return (returncode, stdout, stderr)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", str(e)


def check_deployment(name: str, namespace: str) -> dict:
    """Check the Deployment resource status."""
    rc, out, err = run_cmd([
        "kubectl", "get", "deployment", name,
        "-n", namespace,
        "-o", "json"
    ])
    if rc != 0:
        return {"exists": False, "error": err.strip()}

    data = json.loads(out)
    status = data.get("status", {})
    spec_replicas = data.get("spec", {}).get("replicas", 0)
    ready_replicas = status.get("readyReplicas", 0)
    available_replicas = status.get("availableReplicas", 0)

    return {
        "exists": True,
        "replicas": spec_replicas,
        "ready_replicas": ready_replicas,
        "available_replicas": available_replicas,
        "fully_ready": ready_replicas == spec_replicas and spec_replicas > 0
    }


def check_pods(name: str, namespace: str) -> list[dict]:
    """Check pod status for the deployment."""
    rc, out, err = run_cmd([
        "kubectl", "get", "pods",
        "-n", namespace,
        "-l", f"app={name}",
        "-o", "json"
    ])
    if rc != 0:
        return []

    data = json.loads(out)
    pods = []
    for item in data.get("items", []):
        pod_name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")
        containers = item.get("status", {}).get("containerStatuses", [])
        ready = sum(1 for c in containers if c.get("ready", False))
        total = len(containers)
        restart_count = sum(c.get("restartCount", 0) for c in containers)

        pods.append({
            "name": pod_name,
            "phase": phase,
            "ready": f"{ready}/{total}",
            "restarts": restart_count
        })

    return pods


def check_service(name: str, namespace: str) -> dict:
    """Check the Service resource status."""
    rc, out, err = run_cmd([
        "kubectl", "get", "svc", name,
        "-n", namespace,
        "-o", "json"
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
            "protocol": p.get("protocol", "TCP")
        }
        if "nodePort" in p:
            port_info["node_port"] = p["nodePort"]
        ports.append(port_info)

    return {
        "exists": True,
        "type": svc_type,
        "ports": ports
    }


def verify_docusaurus(name: str, namespace: str) -> dict:
    """Run full health verification and return a structured report."""
    report = {
        "name": name,
        "namespace": namespace,
        "deployment": check_deployment(name, namespace),
        "pods": check_pods(name, namespace),
        "service": check_service(name, namespace)
    }

    # Determine overall health
    deployment_ok = report["deployment"].get("fully_ready", False)
    pods_ok = len(report["pods"]) > 0 and all(
        p["phase"] == "Running" for p in report["pods"]
    )
    service_ok = report["service"].get("exists", False)

    report["healthy"] = deployment_ok and pods_ok and service_ok

    # Build access URL if service has a NodePort
    if service_ok:
        for port in report["service"].get("ports", []):
            if "node_port" in port:
                rc, ip_out, _ = run_cmd(["minikube", "ip"])
                if rc == 0:
                    minikube_ip = ip_out.strip()
                    report["access_url"] = f"http://{minikube_ip}:{port['node_port']}"
                break

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Verify Docusaurus deployment health on Kubernetes"
    )
    parser.add_argument(
        "--name", "-n",
        required=True,
        help="Name of the Docusaurus deployment"
    )
    parser.add_argument(
        "--namespace", "-s",
        default="docs",
        help="Kubernetes namespace (default: docs)"
    )
    args = parser.parse_args()

    result = verify_docusaurus(args.name, args.namespace)
    print(json.dumps(result, indent=2))

    if result.get("healthy"):
        print(f"\nDocusaurus site '{args.name}' is healthy")
        if "access_url" in result:
            print(f"Access URL: {result['access_url']}")
        sys.exit(0)
    else:
        print(f"\nDocusaurus site '{args.name}' is NOT healthy")
        if not result["deployment"].get("exists"):
            print("  - Deployment not found")
        elif not result["deployment"].get("fully_ready"):
            print("  - Deployment not fully ready")
        if not result["pods"]:
            print("  - No pods found")
        else:
            for pod in result["pods"]:
                if pod["phase"] != "Running":
                    print(f"  - Pod {pod['name']} is {pod['phase']}")
        if not result["service"].get("exists"):
            print("  - Service not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
