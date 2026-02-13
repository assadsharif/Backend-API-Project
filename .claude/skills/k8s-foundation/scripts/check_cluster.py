#!/usr/bin/env python3
"""Check Kubernetes cluster health and verify deployments.

Usage:
    python check_cluster.py                    # Full cluster health check
    python check_cluster.py --verify <ns>      # Verify pods in namespace
    python check_cluster.py --context <ctx>    # Use specific kubeconfig context
"""
import argparse
import json
import subprocess
import sys


def run_cmd(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", f"Command timed out after {timeout}s"
    except FileNotFoundError:
        return 1, "", f"Command not found: {cmd[0]}"


def check_cluster_connectivity(context: str | None = None) -> dict:
    """Check if kubectl can reach the cluster."""
    cmd = ["kubectl", "cluster-info"]
    if context:
        cmd.extend(["--context", context])

    rc, stdout, stderr = run_cmd(cmd)
    return {
        "connected": rc == 0,
        "info": stdout.strip() if rc == 0 else stderr.strip(),
    }


def check_nodes(context: str | None = None) -> list[dict]:
    """Get node status."""
    cmd = ["kubectl", "get", "nodes", "-o", "json"]
    if context:
        cmd.extend(["--context", context])

    rc, stdout, stderr = run_cmd(cmd)
    if rc != 0:
        return [{"error": stderr.strip()}]

    data = json.loads(stdout)
    nodes = []
    for item in data.get("items", []):
        name = item["metadata"]["name"]
        conditions = item.get("status", {}).get("conditions", [])
        ready = any(
            c["type"] == "Ready" and c["status"] == "True"
            for c in conditions
        )
        version = item.get("status", {}).get("nodeInfo", {}).get(
            "kubeletVersion", "unknown"
        )
        nodes.append(
            {"name": name, "ready": ready, "version": version}
        )
    return nodes


def check_system_pods(context: str | None = None) -> list[dict]:
    """Check kube-system pods."""
    cmd = [
        "kubectl", "get", "pods", "-n", "kube-system", "-o", "json"
    ]
    if context:
        cmd.extend(["--context", context])

    rc, stdout, stderr = run_cmd(cmd)
    if rc != 0:
        return [{"error": stderr.strip()}]

    data = json.loads(stdout)
    pods = []
    for item in data.get("items", []):
        name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")
        pods.append({"name": name, "phase": phase})
    return pods


def check_helm() -> dict:
    """Check Helm availability and repos."""
    rc, stdout, stderr = run_cmd(["helm", "version", "--short"])
    if rc != 0:
        return {"available": False, "error": stderr.strip()}

    rc2, stdout2, _ = run_cmd(["helm", "repo", "list", "-o", "json"])
    repos = []
    if rc2 == 0:
        try:
            repos = json.loads(stdout2)
        except json.JSONDecodeError:
            pass

    return {
        "available": True,
        "version": stdout.strip(),
        "repos": [r.get("name", "") for r in repos],
    }


def verify_namespace(
    namespace: str, context: str | None = None
) -> dict:
    """Verify all pods in a namespace."""
    cmd = [
        "kubectl", "get", "pods", "-n", namespace, "-o", "json"
    ]
    if context:
        cmd.extend(["--context", context])

    rc, stdout, stderr = run_cmd(cmd)
    if rc != 0:
        return {"namespace": namespace, "error": stderr.strip()}

    data = json.loads(stdout)
    pods = []
    all_running = True
    warnings = []

    for item in data.get("items", []):
        name = item["metadata"]["name"]
        phase = item.get("status", {}).get("phase", "Unknown")

        # Check container statuses
        container_statuses = item.get("status", {}).get(
            "containerStatuses", []
        )
        ready_containers = sum(
            1 for cs in container_statuses if cs.get("ready", False)
        )
        total_containers = len(container_statuses)

        pod_info = {
            "name": name,
            "phase": phase,
            "ready": f"{ready_containers}/{total_containers}",
        }
        pods.append(pod_info)

        if phase != "Running" and phase != "Succeeded":
            all_running = False
            if phase == "CrashLoopBackOff":
                warnings.append(
                    f"⚠️  {name} in CrashLoopBackOff"
                )
            elif phase == "Pending":
                warnings.append(f"⚠️  {name} still Pending")

    return {
        "namespace": namespace,
        "pod_count": len(pods),
        "all_healthy": all_running,
        "pods": pods,
        "warnings": warnings,
    }


def full_health_check(context: str | None = None) -> dict:
    """Run full cluster health check."""
    report = {
        "cluster": check_cluster_connectivity(context),
        "nodes": check_nodes(context),
        "system_pods": check_system_pods(context),
        "helm": check_helm(),
    }

    # Overall status
    cluster_ok = report["cluster"]["connected"]
    nodes_ok = all(n.get("ready", False) for n in report["nodes"])
    system_ok = all(
        p.get("phase") in ("Running", "Succeeded")
        for p in report["system_pods"]
        if "error" not in p
    )

    report["overall"] = {
        "healthy": cluster_ok and nodes_ok and system_ok,
        "cluster_connected": cluster_ok,
        "nodes_ready": nodes_ok,
        "system_pods_healthy": system_ok,
        "helm_available": report["helm"]["available"],
    }

    return report


def main():
    parser = argparse.ArgumentParser(
        description="Kubernetes cluster health check"
    )
    parser.add_argument(
        "--context", default=None, help="Kubeconfig context"
    )
    parser.add_argument(
        "--verify", default=None, help="Verify pods in namespace"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        default=True,
        help="Output as JSON",
    )
    args = parser.parse_args()

    if args.verify:
        result = verify_namespace(args.verify, args.context)
    else:
        result = full_health_check(args.context)

    print(json.dumps(result, indent=2))

    # Exit code based on health
    if args.verify:
        sys.exit(0 if result.get("all_healthy", False) else 1)
    else:
        sys.exit(
            0 if result.get("overall", {}).get("healthy", False) else 1
        )


if __name__ == "__main__":
    main()
