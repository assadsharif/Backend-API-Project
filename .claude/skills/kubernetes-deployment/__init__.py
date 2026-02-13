"""Kubernetes Deployment Skill — deterministic manifest generation.

Public API:
    Models:  DeploymentInput, ServiceInput, ConfigMapInput, StackInput,
             ManifestOutput, ValidationResult
    Funcs:   generate_deployment, generate_service, generate_configmap,
             generate_stack, validate_manifest
"""

from .models import (
    DeploymentInput,
    ServiceInput,
    ConfigMapInput,
    StackInput,
    ManifestOutput,
    ValidationResult,
)
from .skill import (
    generate_deployment,
    generate_service,
    generate_configmap,
    generate_stack,
    validate_manifest,
)

__all__ = [
    # Models
    "DeploymentInput",
    "ServiceInput",
    "ConfigMapInput",
    "StackInput",
    "ManifestOutput",
    "ValidationResult",
    # Functions
    "generate_deployment",
    "generate_service",
    "generate_configmap",
    "generate_stack",
    "validate_manifest",
]
