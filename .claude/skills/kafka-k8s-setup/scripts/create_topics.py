#!/usr/bin/env python3
"""Create Kafka topics on a K8s-deployed Kafka cluster.

Usage:
    python create_topics.py --topics events,notifications,user-actions
    python create_topics.py --topics events --namespace my-kafka --partitions 3
"""
import argparse
import json
import subprocess
import sys


def run_cmd(cmd: list[str], timeout: int = 60) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", str(e)


def create_topic(
    topic: str,
    namespace: str = "kafka",
    release: str = "kafka",
    partitions: int = 1,
    replication_factor: int = 1,
) -> dict:
    """Create a single Kafka topic via kubectl exec."""
    broker_pod = f"{release}-broker-0"
    cmd = [
        "kubectl", "exec", "-n", namespace, broker_pod, "--",
        "kafka-topics.sh",
        "--create",
        "--topic", topic,
        "--partitions", str(partitions),
        "--replication-factor", str(replication_factor),
        "--bootstrap-server", "localhost:9092",
        "--if-not-exists",
    ]

    rc, out, err = run_cmd(cmd)
    return {
        "topic": topic,
        "created": rc == 0,
        "message": out.strip() or err.strip(),
    }


def list_topics(namespace: str = "kafka", release: str = "kafka") -> list[str]:
    """List existing Kafka topics."""
    broker_pod = f"{release}-broker-0"
    cmd = [
        "kubectl", "exec", "-n", namespace, broker_pod, "--",
        "kafka-topics.sh", "--list",
        "--bootstrap-server", "localhost:9092",
    ]
    rc, out, _ = run_cmd(cmd)
    if rc != 0:
        return []
    return [t.strip() for t in out.strip().splitlines() if t.strip()]


def main():
    parser = argparse.ArgumentParser(description="Create Kafka topics")
    parser.add_argument("--topics", required=True, help="Comma-separated topic names")
    parser.add_argument("--namespace", "-n", default="kafka")
    parser.add_argument("--release", default="kafka")
    parser.add_argument("--partitions", "-p", type=int, default=1)
    parser.add_argument("--replication-factor", "-r", type=int, default=1)
    args = parser.parse_args()

    topics = [t.strip() for t in args.topics.split(",")]
    results = []

    for topic in topics:
        result = create_topic(
            topic, args.namespace, args.release,
            args.partitions, args.replication_factor,
        )
        results.append(result)

    # List all topics after creation
    all_topics = list_topics(args.namespace, args.release)

    output = {
        "created": results,
        "all_topics": all_topics,
    }

    print(json.dumps(output, indent=2))

    all_ok = all(r["created"] for r in results)
    if all_ok:
        print(f"\n✅ All {len(topics)} topic(s) created successfully")
    else:
        print(f"\n❌ Some topics failed to create")
        sys.exit(1)


if __name__ == "__main__":
    main()
