"""Core manifest generation and validation logic.

All functions are pure and deterministic:
    - No network I/O
    - No randomness
    - No filesystem writes
    - Same input → same output, always

Input models are pre-validated by Pydantic before these functions receive them.
"""

from typing import Dict, List, Optional

import yaml

from .models import (
    ConfigMapInput,
    DeploymentInput,
    ManifestOutput,
    ResourceRequirements,
    ServiceInput,
    ServicePort,
    StackInput,
    ValidationResult,
)

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _base_labels(app_name: str, extra: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """Standard Kubernetes labels applied to every resource."""
    labels: Dict[str, str] = {
        "app": app_name,
        "app.kubernetes.io/name": app_name,
        "app.kubernetes.io/managed-by": "k8s-deployment-skill",
    }
    if extra:
        labels.update(extra)
    return labels


def _resource_block(resources: Optional[ResourceRequirements]) -> Optional[Dict]:
    """Convert ResourceRequirements → Kubernetes resources dict.  Returns None if empty."""
    if resources is None:
        return None
    block: Dict = {}
    reqs: Dict[str, str] = {}
    if resources.requests_cpu:
        reqs["cpu"] = resources.requests_cpu
    if resources.requests_memory:
        reqs["memory"] = resources.requests_memory
    if reqs:
        block["requests"] = reqs
    lims: Dict[str, str] = {}
    if resources.limits_cpu:
        lims["cpu"] = resources.limits_cpu
    if resources.limits_memory:
        lims["memory"] = resources.limits_memory
    if lims:
        block["limits"] = lims
    return block if block else None


def _to_yaml(doc: dict) -> str:
    """Serialize manifest dict → YAML string (no flow style, key order preserved)."""
    return yaml.dump(doc, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Public generation functions
# ---------------------------------------------------------------------------


def generate_deployment(input_data: DeploymentInput) -> ManifestOutput:
    """Generate a Kubernetes Deployment manifest.

    Deterministic: identical input always produces identical output.
    """
    labels = _base_labels(input_data.app_name, input_data.labels)
    selector_labels = {"app": input_data.app_name}

    container: dict = {
        "name": input_data.app_name,
        "image": input_data.image,
    }

    if input_data.ports:
        container["ports"] = [
            {
                "name": p.name,
                "containerPort": p.container_port,
                "protocol": p.protocol,
            }
            for p in input_data.ports
        ]

    if input_data.env_vars:
        container["env"] = [
            {"name": e.name, "value": e.value} for e in input_data.env_vars
        ]

    res_block = _resource_block(input_data.resources)
    if res_block:
        container["resources"] = res_block

    manifest = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": input_data.app_name,
            "namespace": input_data.namespace,
            "labels": labels,
        },
        "spec": {
            "replicas": input_data.replicas,
            "selector": {"matchLabels": selector_labels},
            "template": {
                "metadata": {"labels": labels},
                "spec": {"containers": [container]},
            },
        },
    }

    return ManifestOutput(
        kind="Deployment",
        name=input_data.app_name,
        namespace=input_data.namespace,
        manifest_yaml=_to_yaml(manifest),
    )


def generate_service(input_data: ServiceInput) -> ManifestOutput:
    """Generate a Kubernetes Service manifest."""
    labels = _base_labels(input_data.app_name)

    manifest = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": f"{input_data.app_name}-svc",
            "namespace": input_data.namespace,
            "labels": labels,
        },
        "spec": {
            "type": input_data.service_type,
            "selector": {"app": input_data.app_name},
            "ports": [
                {
                    "name": p.name,
                    "port": p.port,
                    "targetPort": p.target_port,
                    "protocol": p.protocol,
                }
                for p in input_data.ports
            ],
        },
    }

    return ManifestOutput(
        kind="Service",
        name=f"{input_data.app_name}-svc",
        namespace=input_data.namespace,
        manifest_yaml=_to_yaml(manifest),
    )


def generate_configmap(input_data: ConfigMapInput) -> ManifestOutput:
    """Generate a Kubernetes ConfigMap manifest."""
    labels = _base_labels(input_data.app_name)

    manifest = {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {
            "name": f"{input_data.app_name}-config",
            "namespace": input_data.namespace,
            "labels": labels,
        },
        "data": input_data.data,
    }

    return ManifestOutput(
        kind="ConfigMap",
        name=f"{input_data.app_name}-config",
        namespace=input_data.namespace,
        manifest_yaml=_to_yaml(manifest),
    )


def generate_stack(input_data: StackInput) -> List[ManifestOutput]:
    """Generate a full deployment stack: Deployment + Service + ConfigMap.

    Auto-derivation rules:
        - Service: derived from Deployment.ports if service input is None and ports exist.
        - ConfigMap: derived from Deployment.env_vars if configmap input is None and env_vars exist.
    """
    manifests: List[ManifestOutput] = []

    # Deployment — always generated
    manifests.append(generate_deployment(input_data.deployment))

    # Service — explicit or auto-derived
    svc_input = input_data.service
    if svc_input is None and input_data.deployment.ports:
        svc_input = ServiceInput(
            app_name=input_data.deployment.app_name,
            namespace=input_data.deployment.namespace,
            service_type="ClusterIP",
            ports=[
                ServicePort(
                    name=p.name,
                    port=p.container_port,
                    target_port=p.container_port,
                    protocol=p.protocol,
                )
                for p in input_data.deployment.ports
            ],
        )
    if svc_input:
        manifests.append(generate_service(svc_input))

    # ConfigMap — explicit or auto-derived
    cm_input = input_data.configmap
    if cm_input is None and input_data.deployment.env_vars:
        cm_input = ConfigMapInput(
            app_name=input_data.deployment.app_name,
            namespace=input_data.deployment.namespace,
            data={e.name: e.value for e in input_data.deployment.env_vars},
        )
    if cm_input:
        manifests.append(generate_configmap(cm_input))

    return manifests


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def validate_manifest(yaml_str: str) -> ValidationResult:
    """Validate a Kubernetes manifest YAML string.

    Checks:
        1. YAML parsability
        2. Required top-level fields: apiVersion, kind, metadata (with name)
        3. Kind-specific structural rules (Deployment, Service, ConfigMap)

    No network calls — purely structural.
    """
    errors: List[str] = []
    warnings: List[str] = []
    kind = "Unknown"
    name = ""

    # --- Parse ---
    try:
        doc = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return ValidationResult(valid=False, errors=[f"YAML parse error: {e}"])

    if not isinstance(doc, dict):
        return ValidationResult(valid=False, errors=["Manifest must be a YAML mapping"])

    # --- Top-level required fields ---
    for field in ("apiVersion", "kind", "metadata"):
        if field not in doc:
            errors.append(f"Missing required field: {field}")

    if "kind" in doc:
        kind = str(doc["kind"])

    if "metadata" in doc and isinstance(doc["metadata"], dict):
        name = doc["metadata"].get("name", "")
        if not name:
            errors.append("metadata.name is required and must be non-empty")

    # --- Kind-specific ---
    if kind == "Deployment":
        _validate_deployment(doc, errors, warnings)
    elif kind == "Service":
        _validate_service(doc, errors, warnings)
    elif kind == "ConfigMap":
        _validate_configmap(doc, errors, warnings)
    else:
        warnings.append(f"Unknown kind '{kind}' — kind-specific checks skipped")

    return ValidationResult(
        valid=len(errors) == 0, kind=kind, name=name, errors=errors, warnings=warnings
    )


# ---------------------------------------------------------------------------
# Kind-specific validators (internal)
# ---------------------------------------------------------------------------


def _validate_deployment(doc: dict, errors: List[str], warnings: List[str]) -> None:
    if doc.get("apiVersion") != "apps/v1":
        errors.append(f"Deployment requires apiVersion 'apps/v1', got '{doc.get('apiVersion')}'")

    spec = doc.get("spec", {})
    if not isinstance(spec, dict):
        errors.append("spec must be a mapping")
        return

    if "selector" not in spec:
        errors.append("spec.selector is required")
    if "template" not in spec:
        errors.append("spec.template is required")
    else:
        template = spec["template"]
        pod_spec = template.get("spec", {}) if isinstance(template, dict) else {}
        containers = pod_spec.get("containers", [])
        if not containers:
            errors.append("spec.template.spec.containers must contain at least one container")
        else:
            for i, c in enumerate(containers):
                if "name" not in c:
                    errors.append(f"containers[{i}].name is required")
                if "image" not in c:
                    errors.append(f"containers[{i}].image is required")

    replicas = spec.get("replicas", 1)
    if not isinstance(replicas, int) or replicas < 1:
        errors.append("spec.replicas must be a positive integer")

    # selector ⊆ template labels
    if "selector" in spec and "template" in spec:
        sel = spec.get("selector", {}).get("matchLabels", {})
        tmpl_labels = (
            spec.get("template", {}).get("metadata", {}).get("labels", {})
            if isinstance(spec.get("template"), dict)
            else {}
        )
        if sel and not all(tmpl_labels.get(k) == v for k, v in sel.items()):
            errors.append("spec.selector.matchLabels must be a subset of spec.template.metadata.labels")


def _validate_service(doc: dict, errors: List[str], warnings: List[str]) -> None:
    if doc.get("apiVersion") != "v1":
        errors.append(f"Service requires apiVersion 'v1', got '{doc.get('apiVersion')}'")

    spec = doc.get("spec", {})
    if not isinstance(spec, dict):
        errors.append("spec must be a mapping")
        return

    if "selector" not in spec:
        errors.append("spec.selector is required")
    if not spec.get("ports"):
        errors.append("spec.ports must contain at least one port")

    svc_type = spec.get("type", "ClusterIP")
    valid_types = {"ClusterIP", "NodePort", "LoadBalancer", "ExternalName"}
    if svc_type not in valid_types:
        errors.append(f"Invalid Service type '{svc_type}'. Must be one of {valid_types}")


def _validate_configmap(doc: dict, errors: List[str], warnings: List[str]) -> None:
    if doc.get("apiVersion") != "v1":
        errors.append(f"ConfigMap requires apiVersion 'v1', got '{doc.get('apiVersion')}'")
    if "data" not in doc and "binaryData" not in doc:
        warnings.append("ConfigMap has no data or binaryData field")
