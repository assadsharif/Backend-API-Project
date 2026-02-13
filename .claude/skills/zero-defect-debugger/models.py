"""Pydantic v2 models for zero-defect-debugger.

All models enforce strict validation with extra="forbid".
No optional ambiguity — explicit blocking flags required.
"""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ErrorClass(str, Enum):
    """Exhaustive error classification — no catch-all."""

    SYNTAX = "syntax"  # Parse errors, invalid syntax
    RUNTIME = "runtime"  # Import errors, name errors, attribute errors
    LOGIC = "logic"  # Incorrect behavior, assertion failures
    CONFIG = "config"  # Missing/invalid configuration, env vars
    DEPENDENCY = "dependency"  # Missing packages, version conflicts
    ENVIRONMENT = "environment"  # OS-level issues, permissions, paths
    INTEGRATION = "integration"  # External API failures, boundary issues


class Severity(str, Enum):
    """Error severity with explicit blocking semantics."""

    CRITICAL = "critical"  # System-wide failure, execution impossible
    BLOCKING = "blocking"  # Component fails, must fix before proceeding
    WARNING = "warning"  # Non-fatal but must be addressed


class ResolutionType(str, Enum):
    """Deterministic resolution categories."""

    CODE_FIX = "code_fix"  # Source code modification
    CONFIG_FIX = "config_fix"  # Configuration update
    DEPENDENCY_INSTALL = "dependency_install"  # Package installation
    ENVIRONMENT_FIX = "environment_fix"  # Env var or path fix
    NO_RESOLUTION = "no_resolution"  # Cannot be auto-resolved


class FinalState(str, Enum):
    """Terminal states for debug session — fail-closed."""

    CLEAN = "clean"  # Zero errors remain
    BLOCKED = "blocked"  # Unresolvable errors present, execution unsafe
    UNSAFE = "unsafe"  # Resolution stalled or exceeded safety limits


# ---------------------------------------------------------------------------
# Detection Models
# ---------------------------------------------------------------------------


class ErrorFinding(BaseModel):
    """Single detected error with full context."""

    model_config = ConfigDict(extra="forbid")

    error_class: ErrorClass = Field(..., description="Error classification")
    severity: Severity = Field(..., description="Severity level")
    blocking: bool = Field(..., description="If true, execution MUST halt until resolved")
    message: str = Field(..., min_length=1, description="Error message")
    file_path: Optional[str] = Field(None, description="File where error was detected")
    line_number: Optional[int] = Field(None, ge=1, description="Line number if applicable")
    context: Optional[str] = Field(None, description="Surrounding code or context")
    detection_method: str = Field(..., description="How this error was detected (e.g., 'ast_parse', 'import_test')")


class ErrorReport(BaseModel):
    """Collection of findings from a single detection pass."""

    model_config = ConfigDict(extra="forbid")

    pass_name: str = Field(..., description="Name of this diagnostic pass")
    findings: List[ErrorFinding] = Field(default_factory=list, description="All errors found in this pass")
    blocking_count: int = Field(0, ge=0, description="Number of blocking errors")
    critical_count: int = Field(0, ge=0, description="Number of critical errors")


# ---------------------------------------------------------------------------
# Resolution Models
# ---------------------------------------------------------------------------


class ResolutionAction(BaseModel):
    """Deterministic action taken to resolve an error."""

    model_config = ConfigDict(extra="forbid")

    resolution_type: ResolutionType = Field(..., description="Type of resolution performed")
    description: str = Field(..., min_length=1, description="What was changed")
    file_path: Optional[str] = Field(None, description="File modified (if applicable)")
    line_range: Optional[tuple[int, int]] = Field(None, description="(start, end) lines modified")
    old_content: Optional[str] = Field(None, description="Original content (for rollback)")
    new_content: Optional[str] = Field(None, description="New content applied")
    success: bool = Field(..., description="Whether resolution succeeded")
    error_message: Optional[str] = Field(None, description="Error message if failed")


class ResolutionResult(BaseModel):
    """Result of attempting to resolve a single error."""

    model_config = ConfigDict(extra="forbid")

    original_finding: ErrorFinding = Field(..., description="The error that was addressed")
    action: ResolutionAction = Field(..., description="Action taken")
    new_findings: List[ErrorFinding] = Field(
        default_factory=list, description="New errors introduced by this resolution (must be empty for success)"
    )
    resolved: bool = Field(..., description="True if error is eliminated AND no new errors introduced")


# ---------------------------------------------------------------------------
# Input/Output Models
# ---------------------------------------------------------------------------


class DebugInput(BaseModel):
    """Strict input for zero-defect debugging session."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    target_paths: List[str] = Field(
        ..., min_length=1, description="Paths to debug (files or directories)"
    )
    error_classes: List[ErrorClass] = Field(
        default_factory=lambda: list(ErrorClass),
        description="Error classes to check (default: all)",
    )
    fail_on_any_error: bool = Field(
        True, description="If True, ANY error triggers BLOCKED state. If False, only blocking errors trigger BLOCKED."
    )
    max_resolution_attempts: int = Field(
        10, ge=1, le=100, description="Max resolution iterations before declaring UNSAFE"
    )
    safe_mode: bool = Field(
        True, description="If True, do NOT auto-resolve (only detect and classify). If False, attempt resolution."
    )


class DebugResult(BaseModel):
    """Structured, deterministic debug session output."""

    model_config = ConfigDict(extra="forbid")

    final_state: FinalState = Field(..., description="Terminal state of debug session")
    reports: List[ErrorReport] = Field(default_factory=list, description="All diagnostic pass reports")
    resolutions: List[ResolutionResult] = Field(default_factory=list, description="All resolution attempts")
    total_errors_found: int = Field(0, ge=0, description="Total errors detected across all passes")
    total_errors_resolved: int = Field(0, ge=0, description="Total errors successfully resolved")
    blocking_errors_remaining: int = Field(0, ge=0, description="Blocking errors that remain unresolved")
    iterations: int = Field(0, ge=0, description="Number of detect-resolve-revalidate cycles executed")
    message: str = Field(..., description="Summary message for user")
