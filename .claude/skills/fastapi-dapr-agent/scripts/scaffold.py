#!/usr/bin/env python3
"""Scaffold a FastAPI + Dapr microservice with OpenAI Agents SDK integration.

Usage:
    python scaffold.py --name order-svc --agents triage,fulfillment
    python scaffold.py --name order-svc --port 8001 --agents triage --output-dir ./services
"""
import argparse
import os
import sys
import textwrap


def write_file(path: str, content: str) -> None:
    """Write content to a file, creating parent directories as needed."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def scaffold_main_py(service_name: str, port: int, agents: list[str]) -> str:
    """Generate main.py content."""
    agent_imports = "\n".join(
        f"from agents.{a}_agent import {a.capitalize()}Agent" for a in agents
    )
    agent_registry = "\n".join(
        f'    "{a}": {a.capitalize()}Agent(),' for a in agents
    )
    return textwrap.dedent(f"""\
        \"\"\"FastAPI + Dapr microservice: {service_name}.\"\"\"
        from fastapi import FastAPI, Request
        from fastapi.responses import JSONResponse
        import logging
        import os

        {agent_imports}

        app = FastAPI(
            title="{service_name}",
            version="0.1.0",
            description="FastAPI microservice with Dapr sidecar and OpenAI Agents SDK",
        )

        logger = logging.getLogger("{service_name}")
        logging.basicConfig(level=logging.INFO)

        DAPR_PORT = os.getenv("DAPR_HTTP_PORT", "3500")

        # --- Agent registry ---
        AGENTS = {{
        {agent_registry}
        }}


        # --- Health ---
        @app.get("/health")
        async def health():
            return {{"status": "healthy", "service": "{service_name}"}}


        # --- Dapr pub/sub subscription ---
        @app.get("/dapr/subscribe")
        async def subscribe():
            \"\"\"Tell Dapr which topics this service subscribes to.\"\"\"
            return [
                {{
                    "pubsubname": "pubsub",
                    "topic": "{service_name}-events",
                    "route": "/events",
                }}
            ]


        @app.post("/events")
        async def handle_event(request: Request):
            \"\"\"Handle incoming Dapr pub/sub events.\"\"\"
            body = await request.json()
            logger.info("Received event: %s", body)
            return {{"status": "ok"}}


        @app.get("/agents")
        async def list_agents():
            \"\"\"List registered agents.\"\"\"
            return {{"agents": list(AGENTS.keys())}}


        if __name__ == "__main__":
            import uvicorn
            uvicorn.run(app, host="0.0.0.0", port={port})
    """)


def scaffold_agent(agent_name: str) -> str:
    """Generate an agent class file."""
    class_name = f"{agent_name.capitalize()}Agent"
    return textwrap.dedent(f"""\
        \"\"\"Agent definition: {agent_name}.\"\"\"
        from dataclasses import dataclass, field


        @dataclass
        class {class_name}:
            \"\"\"OpenAI Agents SDK agent for {agent_name} tasks.

            Wire this into the Agents SDK Runner in your orchestration layer:
                from agents import Agent, Runner
                agent = Agent(
                    name=self.name,
                    instructions=self.instructions,
                    model=self.model,
                )
                result = await Runner.run(agent, user_input)
            \"\"\"

            name: str = "{agent_name}"
            instructions: str = (
                "You are the {agent_name} agent. "
                "Follow your task-specific instructions carefully."
            )
            model: str = "gpt-4o"

            def to_sdk_kwargs(self) -> dict:
                \"\"\"Return kwargs suitable for agents.Agent(**kwargs).\"\"\"
                return {{
                    "name": self.name,
                    "instructions": self.instructions,
                    "model": self.model,
                }}
    """)


def scaffold_agent_init(agents: list[str]) -> str:
    """Generate agents/__init__.py."""
    lines = [f'"""Agent definitions for this service."""']
    for a in agents:
        class_name = f"{a.capitalize()}Agent"
        lines.append(f"from .{a}_agent import {class_name}")
    lines.append("")
    lines.append(f"__all__ = {[f'{a.capitalize()}Agent' for a in agents]}")
    lines.append("")
    return "\n".join(lines)


def scaffold_statestore_yaml() -> str:
    """Generate Dapr statestore component YAML."""
    return textwrap.dedent("""\
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: statestore
        spec:
          type: state.redis
          version: v1
          metadata:
            - name: redisHost
              value: "redis-master:6379"
            - name: redisPassword
              value: ""
            - name: actorStateStore
              value: "true"
    """)


def scaffold_pubsub_yaml(pubsub_type: str = "redis") -> str:
    """Generate Dapr pub/sub component YAML."""
    if pubsub_type == "kafka":
        return textwrap.dedent("""\
            apiVersion: dapr.io/v1alpha1
            kind: Component
            metadata:
              name: pubsub
            spec:
              type: pubsub.kafka
              version: v1
              metadata:
                - name: brokers
                  value: "kafka-broker-0.kafka-broker-headless.kafka.svc.cluster.local:9092"
                - name: consumerGroup
                  value: "default-group"
                - name: authType
                  value: "none"
        """)
    return textwrap.dedent("""\
        apiVersion: dapr.io/v1alpha1
        kind: Component
        metadata:
          name: pubsub
        spec:
          type: pubsub.redis
          version: v1
          metadata:
            - name: redisHost
              value: "redis-master:6379"
            - name: redisPassword
              value: ""
    """)


def scaffold_dapr_config() -> str:
    """Generate Dapr configuration YAML."""
    return textwrap.dedent("""\
        apiVersion: dapr.io/v1alpha1
        kind: Configuration
        metadata:
          name: dapr-config
        spec:
          tracing:
            samplingRate: "1"
            zipkin:
              endpointAddress: "http://zipkin.default.svc.cluster.local:9411/api/v2/spans"
          metric:
            enabled: true
    """)


def scaffold_dockerfile(service_name: str, port: int) -> str:
    """Generate Dockerfile."""
    return textwrap.dedent(f"""\
        FROM python:3.12-slim

        WORKDIR /app

        COPY requirements.txt .
        RUN pip install --no-cache-dir -r requirements.txt

        COPY . .

        EXPOSE {port}

        CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "{port}"]
    """)


def scaffold_requirements() -> str:
    """Generate requirements.txt."""
    return textwrap.dedent("""\
        fastapi>=0.109,<1.0
        uvicorn[standard]>=0.27,<1.0
        dapr>=1.14,<2.0
        openai-agents>=0.1,<1.0
        httpx>=0.27,<1.0
    """)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scaffold a FastAPI + Dapr microservice with OpenAI Agents SDK"
    )
    parser.add_argument(
        "--name",
        required=True,
        help="Service name (e.g., order-svc)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="FastAPI port (default: 8000)",
    )
    parser.add_argument(
        "--agents",
        required=True,
        help="Comma-separated agent names (e.g., triage,fulfillment)",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Output directory (default: current directory)",
    )
    parser.add_argument(
        "--pubsub",
        choices=["redis", "kafka"],
        default="redis",
        help="Pub/sub backend: redis (default) or kafka",
    )
    args = parser.parse_args()

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    if not agents:
        print("ERROR: At least one agent name is required.", file=sys.stderr)
        sys.exit(1)

    base = os.path.join(args.output_dir, args.name)
    created_files: list[str] = []

    # --- main.py ---
    path = os.path.join(base, "main.py")
    write_file(path, scaffold_main_py(args.name, args.port, agents))
    created_files.append(path)

    # --- agents/ ---
    path = os.path.join(base, "agents", "__init__.py")
    write_file(path, scaffold_agent_init(agents))
    created_files.append(path)

    for agent_name in agents:
        path = os.path.join(base, "agents", f"{agent_name}_agent.py")
        write_file(path, scaffold_agent(agent_name))
        created_files.append(path)

    # --- dapr/components/ ---
    path = os.path.join(base, "dapr", "components", "statestore.yaml")
    write_file(path, scaffold_statestore_yaml())
    created_files.append(path)

    path = os.path.join(base, "dapr", "components", "pubsub.yaml")
    write_file(path, scaffold_pubsub_yaml(args.pubsub))
    created_files.append(path)

    # --- dapr/config.yaml ---
    path = os.path.join(base, "dapr", "config.yaml")
    write_file(path, scaffold_dapr_config())
    created_files.append(path)

    # --- Dockerfile ---
    path = os.path.join(base, "Dockerfile")
    write_file(path, scaffold_dockerfile(args.name, args.port))
    created_files.append(path)

    # --- requirements.txt ---
    path = os.path.join(base, "requirements.txt")
    write_file(path, scaffold_requirements())
    created_files.append(path)

    # --- Summary ---
    print(f"=== Scaffolded: {args.name} ===")
    print(f"Port:    {args.port}")
    print(f"Agents:  {', '.join(agents)}")
    print(f"Pub/Sub: {args.pubsub}")
    print(f"Output:  {os.path.abspath(base)}")
    print("")
    print("Created files:")
    for f in created_files:
        print(f"  {f}")
    print("")
    print(f"Next steps:")
    print(f"  1. cd {base}")
    print(f"  2. pip install -r requirements.txt")
    print(f"  3. uvicorn main:app --reload --port {args.port}")
    print(f"  4. Apply Dapr components: bash init_dapr.sh {args.name}")


if __name__ == "__main__":
    main()
