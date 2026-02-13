#!/usr/bin/env python3
"""
Convert an MCP server into a complete Skill + Code Execution package.

Reads .mcp.json to find the server, discovers its tools via tools/list,
and generates:
  - SKILL.md with frontmatter, scope, tool map, and execution examples
  - scripts/mcp_client.py (copied from this skill's client)
  - scripts/<tool_name>.py wrapper for each discovered tool
  - recipe.yaml for Goose cross-platform compatibility

Usage:
    python3 convert_mcp_to_skill.py \
        --server-name docker_containerization_mcp \
        --output-dir .claude/skills/docker-generated \
        --description "Generate Dockerfiles and container configs"

    python3 convert_mcp_to_skill.py \
        --server-name helm_packaging_mcp \
        --output-dir .claude/skills/helm-generated
"""

import argparse
import json
import shutil
import subprocess
import sys
import textwrap
import threading
import queue
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# MCP client (inline, minimal -- mirrors mcp_client.py logic)
# ---------------------------------------------------------------------------

class StdioMCPClient:
    """Minimal stdio MCP client for tool discovery."""

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
        self._process = subprocess.Popen(
            [self._command] + self._args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._reader_thread = threading.Thread(
            target=self._read_responses, daemon=True
        )
        self._reader_thread.start()

        init_id = self._next_id()
        self._send({
            "jsonrpc": "2.0",
            "id": init_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "convert-mcp-to-skill", "version": "1.0.0"},
            },
        })
        resp = self._wait_for(init_id, timeout=15)
        if "error" in resp:
            raise RuntimeError(f"Init failed: {resp['error']}")

        self._send({
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        })

    def _read_responses(self):
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
                        pass
            except Exception:
                break

    def _send(self, message: dict):
        if not self._process or self._process.poll() is not None:
            raise RuntimeError("Server process is not running.")
        self._process.stdin.write(json.dumps(message) + "\n")
        self._process.stdin.flush()

    def _wait_for(self, request_id: int, timeout: float = 30) -> dict:
        try:
            while True:
                resp = self._response_queue.get(timeout=timeout)
                if resp.get("id") == request_id:
                    return resp
                self._response_queue.put(resp)
        except queue.Empty:
            raise TimeoutError(f"Timeout waiting for response {request_id}")

    def list_tools(self) -> list:
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

    def stop(self):
        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=5)
            except Exception:
                self._process.kill()
            self._process = None


# ---------------------------------------------------------------------------
# .mcp.json helpers
# ---------------------------------------------------------------------------

def find_mcp_json(start_dir: Optional[str] = None) -> Path:
    """Walk up from start_dir to find .mcp.json."""
    search = Path(start_dir).resolve() if start_dir else Path(__file__).resolve().parent
    for _ in range(20):
        candidate = search / ".mcp.json"
        if candidate.is_file():
            return candidate
        parent = search.parent
        if parent == search:
            break
        search = parent
    raise FileNotFoundError("Could not find .mcp.json in any parent directory.")


def load_server_config(mcp_json_path: Path, server_name: str) -> dict:
    with open(mcp_json_path, "r") as f:
        config = json.load(f)
    servers = config.get("mcpServers", {})
    if server_name not in servers:
        available = ", ".join(sorted(servers.keys()))
        raise KeyError(
            f"Server '{server_name}' not found.\nAvailable: {available}"
        )
    return servers[server_name]


# ---------------------------------------------------------------------------
# Code generators
# ---------------------------------------------------------------------------

def server_name_to_skill_name(server_name: str) -> str:
    """Convert 'docker_containerization_mcp' to 'docker-containerization'."""
    name = server_name.replace("_mcp", "").replace("_", "-")
    return name


def tool_name_to_filename(tool_name: str) -> str:
    """Convert 'docker_generate_dockerfile' to 'docker_generate_dockerfile.py'."""
    return f"{tool_name}.py"


def generate_skill_md(
    skill_name: str,
    server_name: str,
    description: str,
    tools: list,
) -> str:
    """Generate SKILL.md content."""
    # Build tool map rows
    tool_rows = []
    for tool in tools:
        name = tool.get("name", "unknown")
        desc = tool.get("description", "No description")[:80]
        tool_rows.append(
            f"| `scripts/{tool_name_to_filename(name)}` | {desc} "
            f"| `python3 scripts/{tool_name_to_filename(name)} --help` |"
        )
    tool_table = "\n".join(tool_rows)

    # Build trigger phrases from tool names
    triggers = ", ".join(
        f'"{t.get("name", "").replace("_", " ")}"' for t in tools[:5]
    )

    # Build execution examples for first 2 tools
    examples = []
    for tool in tools[:2]:
        name = tool.get("name", "unknown")
        schema = tool.get("inputSchema", {})
        props = schema.get("properties", {})
        required = schema.get("required", [])
        arg_parts = []
        for prop_name in list(required)[:3] or list(props.keys())[:3]:
            arg_parts.append(f'"{prop_name}": "<value>"')
        args_json = "{" + ", ".join(arg_parts) + "}" if arg_parts else "{}"
        examples.append(
            f"# {tool.get('description', name)}\n"
            f"python3 scripts/{tool_name_to_filename(name)} --args '{args_json}'"
        )
    examples_block = "\n\n".join(examples)

    return textwrap.dedent(f"""\
        ---
        name: {skill_name}
        description: |
          {description}
          Generated from MCP server: {server_name}.
          Triggers on: {triggers}.
        ---

        # {skill_name.replace("-", " ").title()}

        {description}

        ## Scope

        **Does**: Call tools from `{server_name}` via executable scripts with zero context token cost.

        **Does NOT**: Run or manage the MCP server process. Modify server source code.

        ---

        ## Tool Map

        | Script | Purpose | Usage |
        |--------|---------|-------|
        {tool_table}

        ---

        ## Execution Pattern

        ```bash
        {examples_block}
        ```

        All scripts accept `--args` as a JSON string matching the tool's input schema.
        Run any script with `--help` for argument details.

        ---

        ## Clarification Triggers

        Before executing, confirm if not clear from context:
        1. Which tool to call (see Tool Map above)
        2. Required arguments for the selected tool

        ---

        ## Must Follow

        - [ ] Always use the wrapper scripts; never load MCP schemas into context
        - [ ] Pass valid JSON to --args matching the tool's input schema
        - [ ] Check script exit code; non-zero means failure

        ## Must Avoid

        - Loading tool definitions into the context window
        - Hardcoding server paths (resolved from .mcp.json at runtime)
        - Leaving server processes running (scripts handle lifecycle)
    """)


def generate_wrapper_script(server_name: str, tool: dict) -> str:
    """Generate a wrapper script for a single MCP tool."""
    name = tool.get("name", "unknown")
    desc = tool.get("description", f"Call {name} on {server_name}")
    schema = tool.get("inputSchema", {})
    props = schema.get("properties", {})
    required = set(schema.get("required", []))

    # Build argparse arguments
    arg_lines = []
    for prop_name, prop_def in props.items():
        prop_desc = prop_def.get("description", prop_name)
        is_required = prop_name in required
        flag = f"--{prop_name.replace('_', '-')}"
        if is_required:
            arg_lines.append(
                f'    parser.add_argument("{flag}", required=True, help="{prop_desc}")'
            )
        else:
            default = prop_def.get("default", "")
            arg_lines.append(
                f'    parser.add_argument("{flag}", default="{default}", help="{prop_desc}")'
            )

    arg_block = "\n".join(arg_lines) if arg_lines else '    # No parameters defined in schema'

    # Build argument dict construction
    dict_lines = []
    for prop_name in props:
        attr_name = prop_name.replace("-", "_")
        dict_lines.append(f'        "{prop_name}": args.{attr_name},')
    dict_block = "\n".join(dict_lines) if dict_lines else '        # No parameters'

    return textwrap.dedent(f'''\
        #!/usr/bin/env python3
        """{desc}

        Wrapper script for {server_name}.{name}.
        Calls mcp_client.py with the correct server and tool name.
        """

        import argparse
        import json
        import subprocess
        import sys
        from pathlib import Path


        def main():
            parser = argparse.ArgumentParser(description="{desc}")
        {arg_block}
            parser.add_argument(
                "--args", "-a",
                help="Raw JSON args (overrides individual flags)",
            )
            args = parser.parse_args()

            # Build tool arguments from flags or raw JSON
            if args.args:
                tool_args = args.args
            else:
                tool_args = json.dumps({{
        {dict_block}
                }})

            # Locate mcp_client.py in the same directory
            script_dir = Path(__file__).resolve().parent
            client_path = script_dir / "mcp_client.py"

            result = subprocess.run(
                [
                    sys.executable,
                    str(client_path),
                    "--server", "{server_name}",
                    "--tool", "{name}",
                    "--args", tool_args,
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(result.stderr, file=sys.stderr)
                sys.exit(1)

            print(result.stdout)


        if __name__ == "__main__":
            main()
    ''')


def generate_recipe_yaml(skill_name: str, description: str, tools: list) -> str:
    """Generate a Goose-compatible recipe.yaml."""
    lines = [
        f"name: {skill_name}",
        f"description: {description}",
        "steps:",
    ]

    for tool in tools:
        name = tool.get("name", "unknown")
        desc = tool.get("description", name)[:80]
        filename = tool_name_to_filename(name)
        lines.append(f"  - name: {name.replace('_', '-')}")
        lines.append(f"    command: python3 scripts/{filename} --args '{{{{args}}}}'")
        lines.append(f"    description: {desc}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert an MCP server into a Skill + Code Execution package.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 convert_mcp_to_skill.py \\\n"
            "      --server-name docker_containerization_mcp \\\n"
            "      --output-dir .claude/skills/docker-generated\n"
            "\n"
            "  python3 convert_mcp_to_skill.py \\\n"
            "      --server-name helm_packaging_mcp \\\n"
            "      --output-dir .claude/skills/helm-generated \\\n"
            "      --description 'Package apps into Helm charts'\n"
        ),
    )

    parser.add_argument(
        "--server-name",
        required=True,
        help="MCP server name (key in .mcp.json mcpServers)",
    )
    parser.add_argument(
        "--output-dir",
        required=True,
        help="Directory to write the generated skill into",
    )
    parser.add_argument(
        "--description",
        default="",
        help="Skill description (auto-generated if omitted)",
    )
    parser.add_argument(
        "--mcp-json",
        help="Path to .mcp.json (default: auto-detect)",
    )

    args = parser.parse_args()

    # Resolve paths
    output_dir = Path(args.output_dir).resolve()
    scripts_dir = output_dir / "scripts"

    # Find server config
    try:
        if args.mcp_json:
            mcp_json_path = Path(args.mcp_json).resolve()
        else:
            mcp_json_path = find_mcp_json()
        server_config = load_server_config(mcp_json_path, args.server_name)
    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

    # Discover tools
    print(f"Connecting to {args.server_name}...")
    client = StdioMCPClient(
        command=server_config["command"],
        args=server_config.get("args", []),
    )

    try:
        client.start()
        tools = client.list_tools()
    except (RuntimeError, TimeoutError) as e:
        print(f"MCP error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        client.stop()

    if not tools:
        print(f"Warning: No tools discovered on {args.server_name}.", file=sys.stderr)

    print(f"Discovered {len(tools)} tools.")

    # Derive names
    skill_name = server_name_to_skill_name(args.server_name)
    description = args.description or f"Tools from {args.server_name} wrapped for code execution"

    # Create output directories
    output_dir.mkdir(parents=True, exist_ok=True)
    scripts_dir.mkdir(parents=True, exist_ok=True)

    generated_files = []

    # 1. Generate SKILL.md
    skill_md = generate_skill_md(skill_name, args.server_name, description, tools)
    skill_md_path = output_dir / "SKILL.md"
    skill_md_path.write_text(skill_md)
    generated_files.append(str(skill_md_path))

    # 2. Copy mcp_client.py
    source_client = Path(__file__).resolve().parent / "mcp_client.py"
    dest_client = scripts_dir / "mcp_client.py"
    if source_client.is_file():
        shutil.copy2(source_client, dest_client)
    else:
        # Fallback: write a note
        dest_client.write_text(
            "# mcp_client.py not found at expected location.\n"
            "# Copy from .claude/skills/mcp-code-execution/scripts/mcp_client.py\n"
        )
    generated_files.append(str(dest_client))

    # 3. Generate wrapper script for each tool
    for tool in tools:
        tool_name = tool.get("name", "unknown")
        wrapper_code = generate_wrapper_script(args.server_name, tool)
        wrapper_path = scripts_dir / tool_name_to_filename(tool_name)
        wrapper_path.write_text(wrapper_code)
        generated_files.append(str(wrapper_path))

    # 4. Generate recipe.yaml
    recipe_yaml = generate_recipe_yaml(skill_name, description, tools)
    recipe_path = output_dir / "recipe.yaml"
    recipe_path.write_text(recipe_yaml)
    generated_files.append(str(recipe_path))

    # Summary
    print(f"\nGenerated skill: {skill_name}")
    print(f"Output directory: {output_dir}")
    print(f"Files created ({len(generated_files)}):")
    for f in generated_files:
        rel = Path(f).relative_to(output_dir) if Path(f).is_relative_to(output_dir) else f
        print(f"  {rel}")
    print(f"\nTools wrapped: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.get('name', 'unknown')}: {tool.get('description', '')[:60]}")


if __name__ == "__main__":
    main()
