#!/usr/bin/env python3
"""
MCP Client -- Call any MCP tool defined in .mcp.json via CLI.

Reads the project's .mcp.json to find server config, spawns the server
process over stdio, sends a JSON-RPC tool call, and prints the result.

Usage:
    # Call a tool
    python3 mcp_client.py --server docker_containerization_mcp \
        --tool docker_generate_dockerfile \
        --args '{"app_type": "python", "framework": "fastapi"}'

    # List tools on a server
    python3 mcp_client.py --server docker_containerization_mcp --list-tools

    # Use a custom .mcp.json path
    python3 mcp_client.py --server myserver --tool mytool \
        --args '{}' --mcp-json /path/to/.mcp.json
"""

import argparse
import json
import subprocess
import sys
import threading
import queue
from pathlib import Path
from typing import Optional


def find_mcp_json(start_dir: Optional[str] = None) -> Path:
    """Walk up from start_dir (or script location) to find .mcp.json."""
    if start_dir:
        search = Path(start_dir).resolve()
    else:
        # Start from the script's directory, walk up to find project root
        search = Path(__file__).resolve().parent

    for _ in range(20):  # Safety limit
        candidate = search / ".mcp.json"
        if candidate.is_file():
            return candidate
        parent = search.parent
        if parent == search:
            break
        search = parent

    raise FileNotFoundError(
        "Could not find .mcp.json in any parent directory. "
        "Ensure you are running from within the project, or pass --mcp-json."
    )


def load_server_config(mcp_json_path: Path, server_name: str) -> dict:
    """Load and validate server config from .mcp.json."""
    with open(mcp_json_path, "r") as f:
        config = json.load(f)

    servers = config.get("mcpServers", {})
    if server_name not in servers:
        available = ", ".join(sorted(servers.keys()))
        raise KeyError(
            f"Server '{server_name}' not found in {mcp_json_path}.\n"
            f"Available servers: {available}"
        )

    server = servers[server_name]
    if "command" not in server:
        raise ValueError(f"Server '{server_name}' missing 'command' field.")

    return server


class StdioMCPClient:
    """Minimal MCP client using stdio JSON-RPC transport."""

    def __init__(self, command: str, args: list):
        self._command = command
        self._args = args
        self._process: Optional[subprocess.Popen] = None
        self._request_id = 0
        self._response_queue: queue.Queue = queue.Queue()
        self._reader_thread: Optional[threading.Thread] = None

    def _next_id(self) -> int:
        self._request_id += 1
        return self._request_id

    def start(self):
        """Spawn the MCP server and perform initialization handshake."""
        self._process = subprocess.Popen(
            [self._command] + self._args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        # Start background reader
        self._reader_thread = threading.Thread(
            target=self._read_responses, daemon=True
        )
        self._reader_thread.start()

        # Send initialize
        init_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": init_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-code-execution", "version": "1.0.0"},
            },
        })

        # Wait for initialize response
        resp = self._wait_for(init_id, timeout=15)
        if "error" in resp:
            err = resp["error"]
            raise RuntimeError(
                f"Server initialization failed: {err.get('message', err)}"
            )

        # Send initialized notification
        self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })

    def _read_responses(self):
        """Background thread: read JSON lines from server stdout."""
        while self._process and self._process.poll() is None:
            try:
                line = self._process.stdout.readline()
                if not line:
                    break
                line = line.strip()
                if line:
                    try:
                        msg = json.loads(line)
                        if "id" in msg:
                            self._response_queue.put(msg)
                    except json.JSONDecodeError:
                        pass  # Skip non-JSON output (e.g. log lines)
            except Exception:
                break

    def _send(self, message: dict):
        """Write a JSON-RPC message to server stdin."""
        if not self._process or self._process.poll() is not None:
            raise RuntimeError("Server process is not running.")
        line = json.dumps(message) + "\n"
        self._process.stdin.write(line)
        self._process.stdin.flush()

    def _wait_for(self, request_id: int, timeout: float = 30) -> dict:
        """Wait for a response matching the given request ID."""
        try:
            while True:
                resp = self._response_queue.get(timeout=timeout)
                if resp.get("id") == request_id:
                    return resp
                # Put back responses for other IDs
                self._response_queue.put(resp)
        except queue.Empty:
            raise TimeoutError(
                f"Timeout ({timeout}s) waiting for response to request {request_id}."
            )

    def list_tools(self) -> list:
        """Call tools/list and return the tools array."""
        req_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/list",
        })
        resp = self._wait_for(req_id)
        if "error" in resp:
            raise RuntimeError(f"tools/list failed: {resp['error']}")
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, tool_name: str, arguments: dict) -> dict:
        """Call tools/call with the given tool name and arguments."""
        req_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": req_id,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        })
        resp = self._wait_for(req_id)
        if "error" in resp:
            err = resp["error"]
            raise RuntimeError(
                f"Tool call '{tool_name}' failed: {err.get('message', err)}"
            )
        return resp.get("result", {})

    def stop(self):
        """Terminate the server process."""
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                self._process.kill()
            self._process = None


def main():
    parser = argparse.ArgumentParser(
        description="Call MCP tools defined in .mcp.json via stdio JSON-RPC.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 mcp_client.py --server docker_containerization_mcp \\\n"
            "      --tool docker_generate_dockerfile \\\n"
            "      --args '{\"app_type\": \"python\"}'\n"
            "\n"
            "  python3 mcp_client.py --server helm_packaging_mcp --list-tools\n"
        ),
    )

    parser.add_argument(
        "--server", "-s",
        required=True,
        help="MCP server name (key in .mcp.json mcpServers)",
    )
    parser.add_argument(
        "--tool", "-t",
        help="Tool name to call on the server",
    )
    parser.add_argument(
        "--args", "-a",
        default="{}",
        help='JSON string of tool arguments (default: "{}")',
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all tools on the server instead of calling one",
    )
    parser.add_argument(
        "--mcp-json",
        help="Path to .mcp.json (default: auto-detect by walking up directories)",
    )

    args = parser.parse_args()

    # Validate: must specify either --tool or --list-tools
    if not args.list_tools and not args.tool:
        parser.error("Must specify --tool <name> or --list-tools")

    # Find and load config
    try:
        if args.mcp_json:
            mcp_json_path = Path(args.mcp_json).resolve()
        else:
            mcp_json_path = find_mcp_json()

        server_config = load_server_config(mcp_json_path, args.server)
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse tool arguments
    try:
        tool_arguments = json.loads(args.args)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in --args: {e}", file=sys.stderr)
        sys.exit(1)

    # Create client and execute
    client = StdioMCPClient(
        command=server_config["command"],
        args=server_config.get("args", []),
    )

    try:
        client.start()

        if args.list_tools:
            tools = client.list_tools()
            print(json.dumps(tools, indent=2))
        else:
            result = client.call_tool(args.tool, tool_arguments)
            print(json.dumps(result, indent=2))

    except (RuntimeError, TimeoutError) as e:
        print(f"MCP error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(130)
    finally:
        client.stop()


if __name__ == "__main__":
    main()
