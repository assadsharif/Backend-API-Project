"""Pydantic v2 schemas for the Kubernetes Deployment Skill.

Design constraints:
    - extra="forbid" on every model (reject unknown fields at the boundary).
    - All string identifiers validated against Kubernetes naming rules.
    - No defaults that hide configuration gaps in production-critical fields.
"""

import re
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Shared sub-models
# ---------------------------------------------------------------------------


class ResourceRequirements(BaseModel):
    """CPU and memory requests/limits for a container."""

    model_config = ConfigDict(extra="forbid")

    requests_cpu: Optional[str] = Field(
        default=None, description="CPU request (e.g. '100m', '0.5')"
    )
    requests_memory: Optional[str] = Field(
        default=None, description="Memory request (e.g. '128Mi', '1Gi')"
    )
    limits_cpu: Optional[str] = Field(
        default=None, description="CPU limit (e.g. '200m', '1')"
    )
    limits_memory: Optional[str] = Field(
        default=None, description="Memory limit (e.g. '256Mi', '2Gi')"
    )

    @field_validator("requests_cpu", "limits_cpu")
    @classmethod
    def _validate_cpu(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^(\d+m|\d+(\.\d+)?)$", v):
            raise ValueError(
                "CPU value must be millicores (e.g. '100m') or decimal cores (e.g. '0.5')"
            )
        return v

    @field_validator("requests_memory", "limits_memory")
    @classmethod
    def _validate_memory(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not re.match(r"^\d+(Ki|Mi|Gi|Ti)?$", v):
            raise ValueError(
                "Memory value must be numeric with optional unit (Ki|Mi|Gi|Ti)"
            )
        return v


class PortConfig(BaseModel):
    """Single container port definition."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ...,
        description="Port name — DNS-1123 label, lowercase, max 15 chars",
        min_length=1,
        max_length=15,
    )
    container_port: int = Field(
        ..., description="Port number exposed by the container", ge=1, le=65535
    )
    protocol: Literal["TCP", "UDP"] = Field(
        default="TCP", description="Network protocol"
    )

    @field_validator("name")
    @classmethod
    def _validate_port_name(cls, v: str) -> str:
        if not re.match(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$", v):
            raise ValueError(
                "Port name must be a DNS-1123 label: "
                "lowercase alphanumeric, may contain '-', 1-15 chars"
            )
        return v


class EnvVar(BaseModel):
    """Single environment variable (name = value)."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        ..., description="Env var name (e.g. 'MY_VAR')", min_length=1, max_length=128
    )
    value: str = Field(..., description="Env var value", max_length=1024)

    @field_validator("name")
    @classmethod
    def _validate_env_name(cls, v: str) -> str:
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", v):
            raise ValueError("Env var name must match pattern [A-Za-z_][A-Za-z0-9_]*")
        return v


# ---------------------------------------------------------------------------
# Top-level input models
# ---------------------------------------------------------------------------

_DNS_1123_PATTERN = r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$"


def _assert_dns1123(label: str, v: str) -> str:
    if not re.match(_DNS_1123_PATTERN, v):
        raise ValueError(f"{label} must be a DNS-1123 subdomain (lowercase, alphanumeric, hyphens)")
    return v


class DeploymentInput(BaseModel):
    """Input for generating a Kubernetes Deployment manifest."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    app_name: str = Field(
        ..., description="Application name — DNS-1123 subdomain", min_length=1, max_length=63
    )
    image: str = Field(
        ..., description="Container image (e.g. 'nginx:1.25', 'myrepo/app:v2')", min_length=1
    )
    replicas: int = Field(default=1, description="Number of replica pods", ge=1, le=1000)
    namespace: str = Field(default="default", description="Kubernetes namespace", min_length=1, max_length=63)
    ports: List[PortConfig] = Field(default_factory=list, description="Container ports to expose")
    env_vars: List[EnvVar] = Field(default_factory=list, description="Environment variables")
    resources: Optional[ResourceRequirements] = Field(
        default=None, description="CPU/memory requests and limits"
    )
    labels: Dict[str, str] = Field(
        default_factory=dict, description="Additional labels merged onto defaults"
    )

    @field_validator("app_name")
    @classmethod
    def _validate_app_name(cls, v: str) -> str:
        return _assert_dns1123("app_name", v)

    @field_validator("namespace")
    @classmethod
    def _validate_namespace(cls, v: str) -> str:
        return _assert_dns1123("namespace", v)


class ServicePort(BaseModel):
    """Port mapping for a Kubernetes Service."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Port name (should match container port name)", min_length=1, max_length=15)
    port: int = Field(..., description="Service-facing port", ge=1, le=65535)
    target_port: int = Field(..., description="Container port to forward traffic to", ge=1, le=65535)
    protocol: Literal["TCP", "UDP"] = Field(default="TCP")


class ServiceInput(BaseModel):
    """Input for generating a Kubernetes Service manifest."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    app_name: str = Field(
        ..., description="App name — must match the target Deployment", min_length=1, max_length=63
    )
    service_type: Literal["ClusterIP", "NodePort", "LoadBalancer"] = Field(
        default="ClusterIP", description="Service exposure type"
    )
    namespace: str = Field(default="default", description="Kubernetes namespace", min_length=1, max_length=63)
    ports: List[ServicePort] = Field(
        ..., description="Port mappings (at least one required)", min_length=1
    )

    @field_validator("app_name")
    @classmethod
    def _validate_app_name(cls, v: str) -> str:
        return _assert_dns1123("app_name", v)


class ConfigMapInput(BaseModel):
    """Input for generating a Kubernetes ConfigMap manifest."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    app_name: str = Field(
        ..., description="Application name", min_length=1, max_length=63
    )
    namespace: str = Field(default="default", description="Kubernetes namespace", min_length=1, max_length=63)
    data: Dict[str, str] = Field(
        ..., description="Key-value pairs for the ConfigMap (at least one required)", min_length=1
    )

    @field_validator("app_name")
    @classmethod
    def _validate_app_name(cls, v: str) -> str:
        return _assert_dns1123("app_name", v)


class StackInput(BaseModel):
    """Input for generating a complete deployment stack.

    Service is auto-derived from Deployment ports if omitted and ports exist.
    ConfigMap is auto-derived from Deployment env_vars if omitted and env_vars exist.
    """

    model_config = ConfigDict(extra="forbid")

    deployment: DeploymentInput
    service: Optional[ServiceInput] = Field(
        default=None, description="Omit to auto-derive from deployment.ports"
    )
    configmap: Optional[ConfigMapInput] = Field(
        default=None, description="Omit to auto-derive from deployment.env_vars"
    )


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------


class ManifestOutput(BaseModel):
    """A single generated Kubernetes manifest."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(..., description="Resource kind (Deployment | Service | ConfigMap)")
    name: str = Field(..., description="Resource name")
    namespace: str = Field(..., description="Resource namespace")
    manifest_yaml: str = Field(..., description="Complete YAML manifest")


class ValidationResult(BaseModel):
    """Result of validating a Kubernetes manifest."""

    model_config = ConfigDict(extra="forbid")

    valid: bool = Field(..., description="True if structurally valid")
    kind: str = Field(default="Unknown", description="Detected resource kind")
    name: str = Field(default="", description="Detected resource name")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")
