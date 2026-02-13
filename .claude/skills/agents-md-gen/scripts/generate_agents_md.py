#!/usr/bin/env python3
"""Generate AGENTS.md by scanning a repository for AI agent configurations.

Scans for:
- .claude/skills/*/SKILL.md files
- .mcp.json MCP server configurations
- .goose/ or goose config files
- CLAUDE.md project instructions
- recipe.yaml Goose recipes

Usage:
    python generate_agents_md.py --repo-path /path/to/repo
    python generate_agents_md.py  # defaults to current directory
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path


def scan_skills(repo_path: Path) -> list[dict]:
    """Scan .claude/skills/ for SKILL.md files."""
    skills = []
    skills_dir = repo_path / ".claude" / "skills"
    if not skills_dir.exists():
        return skills

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        name = skill_dir.name
        description = ""
        has_scripts = (skill_dir / "scripts").exists()
        has_references = (skill_dir / "references").exists() or (
            skill_dir / "REFERENCE.md"
        ).exists()

        # Parse SKILL.md frontmatter for description
        content = skill_md.read_text(encoding="utf-8", errors="replace")
        fm_match = re.search(
            r"^---\s*\n(.*?)\n---", content, re.DOTALL
        )
        if fm_match:
            for line in fm_match.group(1).splitlines():
                if line.strip().startswith("description:"):
                    desc_line = line.split("description:", 1)[1].strip()
                    if desc_line and desc_line != "|":
                        description = desc_line
                    break

        if not description:
            # Grab first non-heading, non-empty line after frontmatter
            in_body = False
            for line in content.splitlines():
                if in_body and line.strip() and not line.startswith("#"):
                    description = line.strip()[:120]
                    break
                if line.strip() == "---":
                    in_body = not in_body if not in_body else True

        # Count scripts
        script_count = 0
        if has_scripts:
            scripts_path = skill_dir / "scripts"
            script_count = len(
                [f for f in scripts_path.iterdir() if f.is_file()]
            )

        skills.append(
            {
                "name": name,
                "description": description,
                "has_scripts": has_scripts,
                "script_count": script_count,
                "has_references": has_references,
                "path": str(skill_dir.relative_to(repo_path)),
            }
        )
    return skills


def scan_mcp_servers(repo_path: Path) -> list[dict]:
    """Scan .mcp.json for MCP server configurations."""
    servers = []
    mcp_json = repo_path / ".mcp.json"
    if not mcp_json.exists():
        return servers

    data = json.loads(mcp_json.read_text(encoding="utf-8"))
    mcp_servers = data.get("mcpServers", {})

    for name, config in sorted(mcp_servers.items()):
        command = config.get("command", "")
        args = config.get("args", [])
        script_path = args[0] if args else ""
        servers.append(
            {
                "name": name,
                "command": command,
                "script": script_path,
            }
        )
    return servers


def scan_goose_config(repo_path: Path) -> dict:
    """Check for Goose configuration."""
    goose_info = {"found": False, "configs": []}
    goose_dir = repo_path / ".goose"
    if goose_dir.exists():
        goose_info["found"] = True
        for f in goose_dir.iterdir():
            goose_info["configs"].append(str(f.name))

    # Check for recipe.yaml files
    for recipe in repo_path.rglob("recipe.yaml"):
        goose_info["found"] = True
        goose_info["configs"].append(str(recipe.relative_to(repo_path)))

    return goose_info


def scan_claude_md(repo_path: Path) -> str:
    """Extract summary from CLAUDE.md."""
    claude_md = repo_path / "CLAUDE.md"
    if not claude_md.exists():
        return ""
    content = claude_md.read_text(encoding="utf-8", errors="replace")
    # Get first paragraph after the title
    lines = content.splitlines()
    summary_lines = []
    found_content = False
    for line in lines:
        if line.startswith("# "):
            continue
        if line.strip() and not found_content:
            found_content = True
        if found_content:
            if not line.strip() and summary_lines:
                break
            summary_lines.append(line.strip())
    return " ".join(summary_lines)[:300]


def generate_agents_md(
    repo_path: Path, output_path: Path | None = None
) -> str:
    """Generate AGENTS.md content."""
    skills = scan_skills(repo_path)
    mcp_servers = scan_mcp_servers(repo_path)
    goose = scan_goose_config(repo_path)
    claude_summary = scan_claude_md(repo_path)

    skills_with_scripts = [s for s in skills if s["has_scripts"]]
    total_scripts = sum(s["script_count"] for s in skills)

    lines = []
    lines.append("# AGENTS.md")
    lines.append("")
    lines.append(
        f"> Auto-generated on {date.today().isoformat()} by "
        f"agents-md-gen skill"
    )
    lines.append("")

    # Summary
    lines.append("## Summary")
    lines.append("")
    lines.append(f"| Metric | Count |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Skills | {len(skills)} |")
    lines.append(
        f"| Skills with Scripts (MCP Code Execution) "
        f"| {len(skills_with_scripts)} |"
    )
    lines.append(f"| Total Scripts | {total_scripts} |")
    lines.append(f"| MCP Servers | {len(mcp_servers)} |")
    lines.append(
        f"| Goose Compatible | {'Yes' if goose['found'] else 'No'} |"
    )
    lines.append("")

    if claude_summary:
        lines.append("## Project Agent Instructions")
        lines.append("")
        lines.append(f"{claude_summary}")
        lines.append("")

    # Skills inventory
    lines.append("## Skills Inventory")
    lines.append("")
    lines.append(
        "| Skill | Scripts | References | Pattern | Path |"
    )
    lines.append(
        "|-------|---------|------------|---------|------|"
    )
    for s in skills:
        pattern = (
            "MCP Code Execution" if s["has_scripts"] else "Prompt-only"
        )
        scripts_str = (
            f"{s['script_count']} scripts" if s["has_scripts"] else "-"
        )
        refs = "Yes" if s["has_references"] else "-"
        lines.append(
            f"| {s['name']} | {scripts_str} | {refs} "
            f"| {pattern} | `{s['path']}` |"
        )
    lines.append("")

    # MCP Servers
    if mcp_servers:
        lines.append("## MCP Servers")
        lines.append("")
        lines.append("| Server | Script |")
        lines.append("|--------|--------|")
        for srv in mcp_servers:
            script_name = Path(srv["script"]).name if srv["script"] else "-"
            lines.append(f"| {srv['name']} | `{script_name}` |")
        lines.append("")

    # Goose compatibility
    if goose["found"]:
        lines.append("## Goose Configuration")
        lines.append("")
        for cfg in goose["configs"]:
            lines.append(f"- `{cfg}`")
        lines.append("")

    # Architecture pattern
    lines.append("## Architecture: Skills + Code Execution Pattern")
    lines.append("")
    lines.append("```")
    lines.append(
        "SKILL.md (~100 tokens) → scripts/*.py (executed, 0 tokens) "
        "→ minimal result"
    )
    lines.append("```")
    lines.append("")
    lines.append(
        "Skills with the **MCP Code Execution** pattern keep the AI "
        "context window lean by executing scripts externally rather "
        "than loading MCP tool definitions directly."
    )
    lines.append("")

    content = "\n".join(lines)

    # Write output
    if output_path is None:
        output_path = repo_path / "AGENTS.md"
    output_path.write_text(content, encoding="utf-8")

    # Print summary
    print(f"✅ Generated {output_path}")
    print(f"   Skills: {len(skills)} ({len(skills_with_scripts)} with scripts)")
    print(f"   MCP Servers: {len(mcp_servers)}")
    print(f"   Total Scripts: {total_scripts}")

    return str(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="Generate AGENTS.md for a repository"
    )
    parser.add_argument(
        "--repo-path",
        default=".",
        help="Repository root path (default: current directory)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: <repo-path>/AGENTS.md)",
    )
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    output_path = Path(args.output).resolve() if args.output else None

    if not repo_path.exists():
        print(f"❌ Repository path does not exist: {repo_path}")
        raise SystemExit(1)

    generate_agents_md(repo_path, output_path)


if __name__ == "__main__":
    main()
