#!/usr/bin/env python3
"""Run SQL migrations against a K8s-deployed PostgreSQL instance.

Executes .sql files from a directory in alphabetical order via kubectl exec
on the PostgreSQL pod.

Usage:
    python migrate.py --sql-dir ./migrations
    python migrate.py --sql-dir ./migrations --namespace my-pg --database mydb
    python migrate.py --sql-dir ./migrations --user postgres --password secret123
"""
import argparse
import json
import os
import subprocess
import sys


def run_cmd(cmd: list[str], timeout: int = 120, stdin_data: str = None) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True,
            timeout=timeout, input=stdin_data
        )
        return r.returncode, r.stdout, r.stderr
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        return 1, "", str(e)


def find_postgres_pod(namespace: str, release: str) -> str:
    """Find the primary PostgreSQL pod name."""
    rc, out, err = run_cmd([
        "kubectl", "get", "pods", "-n", namespace,
        "-l", f"app.kubernetes.io/instance={release},app.kubernetes.io/component=primary",
        "-o", "jsonpath={.items[0].metadata.name}"
    ])
    if rc != 0 or not out.strip():
        # Fallback: try the conventional pod name
        return f"{release}-0"
    return out.strip()


def run_migration(
    sql_file: str,
    pod_name: str,
    namespace: str,
    database: str,
    user: str,
    password: str,
) -> dict:
    """Run a single .sql file against PostgreSQL via kubectl exec."""
    filename = os.path.basename(sql_file)

    # Read the SQL file content
    try:
        with open(sql_file, "r") as f:
            sql_content = f.read()
    except OSError as e:
        return {
            "file": filename,
            "success": False,
            "error": f"Cannot read file: {e}",
        }

    # Build kubectl exec command to run psql
    env_prefix = ""
    if password:
        env_prefix = f"PGPASSWORD={password} "

    cmd = [
        "kubectl", "exec", "-n", namespace, pod_name, "--",
        "bash", "-c",
        f"{env_prefix}psql -U {user} -d {database} -v ON_ERROR_STOP=1"
    ]

    rc, out, err = run_cmd(cmd, timeout=120, stdin_data=sql_content)

    return {
        "file": filename,
        "success": rc == 0,
        "output": out.strip() if out.strip() else None,
        "error": err.strip() if rc != 0 and err.strip() else None,
    }


def discover_sql_files(sql_dir: str) -> list[str]:
    """Find all .sql files in a directory, sorted alphabetically."""
    if not os.path.isdir(sql_dir):
        print(f"Error: SQL directory not found: {sql_dir}", file=sys.stderr)
        sys.exit(1)

    files = sorted([
        os.path.join(sql_dir, f)
        for f in os.listdir(sql_dir)
        if f.endswith(".sql")
    ])

    if not files:
        print(f"Warning: No .sql files found in {sql_dir}", file=sys.stderr)

    return files


def main():
    parser = argparse.ArgumentParser(description="Run PostgreSQL migrations on Kubernetes")
    parser.add_argument("--sql-dir", required=True, help="Directory containing .sql migration files")
    parser.add_argument("--host", default=None, help="PostgreSQL host (unused for kubectl exec, reserved for future use)")
    parser.add_argument("--port", default="5432", help="PostgreSQL port (default: 5432)")
    parser.add_argument("--database", "-d", default="appdb", help="Target database name (default: appdb)")
    parser.add_argument("--user", "-U", default="postgres", help="Database user (default: postgres)")
    parser.add_argument("--password", "-p", default="", help="Database password")
    parser.add_argument("--namespace", "-n", default="postgres", help="Kubernetes namespace (default: postgres)")
    parser.add_argument("--release", default="postgresql", help="Helm release name (default: postgresql)")
    args = parser.parse_args()

    # Discover SQL files
    sql_files = discover_sql_files(args.sql_dir)
    if not sql_files:
        print(json.dumps({"migrations": [], "total": 0, "succeeded": 0, "failed": 0}, indent=2))
        return

    # Find the PostgreSQL pod
    pod_name = find_postgres_pod(args.namespace, args.release)
    print(f"Using pod: {pod_name}")
    print(f"Database:  {args.database}")
    print(f"Found {len(sql_files)} migration file(s)")
    print("")

    # Run each migration in order
    results = []
    for sql_file in sql_files:
        print(f"Running: {os.path.basename(sql_file)} ... ", end="", flush=True)
        result = run_migration(
            sql_file=sql_file,
            pod_name=pod_name,
            namespace=args.namespace,
            database=args.database,
            user=args.user,
            password=args.password,
        )
        results.append(result)

        if result["success"]:
            print("OK")
        else:
            print("FAILED")
            print(f"  Error: {result.get('error', 'unknown')}")
            # Stop on first failure (ON_ERROR_STOP behavior)
            print("Stopping migrations due to failure.")
            break

    succeeded = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])

    report = {
        "migrations": results,
        "total": len(sql_files),
        "executed": len(results),
        "succeeded": succeeded,
        "failed": failed,
    }

    print("")
    print(json.dumps(report, indent=2))

    if failed > 0:
        print(f"\nMigration failed: {failed} error(s)")
        sys.exit(1)
    else:
        print(f"\nAll {succeeded} migration(s) completed successfully")


if __name__ == "__main__":
    main()
