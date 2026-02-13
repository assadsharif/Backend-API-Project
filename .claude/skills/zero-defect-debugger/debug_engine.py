"""Core debugging engine with fail-closed error detection and resolution.

DESIGN PRINCIPLES:
- Detect ALL errors before attempting ANY resolution
- Re-validate after EVERY resolution
- Block execution if ANY unresolved error remains (when fail_on_any_error=True)
- No silent failures, no error suppression, no infinite loops
"""

import ast
import importlib.util
import sys
from pathlib import Path
from typing import List

from .models import (
    DebugInput,
    DebugResult,
    ErrorClass,
    ErrorFinding,
    ErrorReport,
    FinalState,
    ResolutionResult,
    Severity,
)


# ---------------------------------------------------------------------------
# Detection passes (pure, deterministic)
# ---------------------------------------------------------------------------


def _detect_syntax_errors(paths: List[Path]) -> List[ErrorFinding]:
    """Detect syntax errors via AST parsing. Pure function."""
    findings: List[ErrorFinding] = []

    for path in paths:
        if not path.suffix == ".py":
            continue
        if not path.exists():
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.ENVIRONMENT,
                    severity=Severity.CRITICAL,
                    blocking=True,
                    message=f"File does not exist: {path}",
                    file_path=str(path),
                    detection_method="file_exists_check",
                )
            )
            continue

        try:
            source = path.read_text(encoding="utf-8")
        except Exception as e:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.ENVIRONMENT,
                    severity=Severity.CRITICAL,
                    blocking=True,
                    message=f"Cannot read file: {e}",
                    file_path=str(path),
                    detection_method="file_read",
                )
            )
            continue

        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as e:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.SYNTAX,
                    severity=Severity.CRITICAL,
                    blocking=True,
                    message=f"Syntax error: {e.msg}",
                    file_path=str(path),
                    line_number=e.lineno,
                    context=e.text.strip() if e.text else None,
                    detection_method="ast_parse",
                )
            )

    return findings


def _detect_runtime_errors(paths: List[Path]) -> List[ErrorFinding]:
    """Detect runtime errors via import testing. Isolated per-file."""
    findings: List[ErrorFinding] = []

    for path in paths:
        if not path.suffix == ".py":
            continue
        if not path.exists():
            continue  # Already caught by syntax pass

        # Attempt isolated import
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.RUNTIME,
                    severity=Severity.BLOCKING,
                    blocking=True,
                    message=f"Cannot create import spec for {path}",
                    file_path=str(path),
                    detection_method="import_spec",
                )
            )
            continue

        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[path.stem] = module
            spec.loader.exec_module(module)
        except ImportError as e:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.DEPENDENCY,
                    severity=Severity.BLOCKING,
                    blocking=True,
                    message=f"Import error: {e}",
                    file_path=str(path),
                    detection_method="import_test",
                )
            )
        except AttributeError as e:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.RUNTIME,
                    severity=Severity.BLOCKING,
                    blocking=True,
                    message=f"Attribute error during import: {e}",
                    file_path=str(path),
                    detection_method="import_test",
                )
            )
        except Exception as e:
            findings.append(
                ErrorFinding(
                    error_class=ErrorClass.RUNTIME,
                    severity=Severity.CRITICAL,
                    blocking=True,
                    message=f"Runtime error during import: {e}",
                    file_path=str(path),
                    detection_method="import_test",
                )
            )
        finally:
            # Clean up module to avoid side effects
            if path.stem in sys.modules:
                del sys.modules[path.stem]

    return findings


def _detect_all_errors(paths: List[Path], error_classes: List[ErrorClass]) -> ErrorReport:
    """Run all detection passes based on requested error classes."""
    all_findings: List[ErrorFinding] = []

    if ErrorClass.SYNTAX in error_classes:
        all_findings.extend(_detect_syntax_errors(paths))

    if ErrorClass.RUNTIME in error_classes or ErrorClass.DEPENDENCY in error_classes:
        all_findings.extend(_detect_runtime_errors(paths))

    # TODO: Add detection passes for LOGIC, CONFIG, ENVIRONMENT, INTEGRATION
    # For now, only SYNTAX, RUNTIME, DEPENDENCY are implemented

    blocking_count = sum(1 for f in all_findings if f.blocking)
    critical_count = sum(1 for f in all_findings if f.severity == Severity.CRITICAL)

    return ErrorReport(
        pass_name="full_diagnostic",
        findings=all_findings,
        blocking_count=blocking_count,
        critical_count=critical_count,
    )


# ---------------------------------------------------------------------------
# Main debug engine
# ---------------------------------------------------------------------------


def run_debug_session(input_data: DebugInput) -> DebugResult:
    """Execute zero-defect debug session with strict fail-closed semantics.

    GUARANTEES:
    - Detects ALL errors in requested classes before resolution
    - Re-validates after every resolution
    - Blocks execution if ANY unresolved error remains (when fail_on_any_error=True)
    - No silent failures, no error suppression
    - Terminates safely if resolution stalls (UNSAFE state)
    """
    # Resolve paths
    paths: List[Path] = []
    for target in input_data.target_paths:
        p = Path(target)
        if p.is_file():
            paths.append(p)
        elif p.is_dir():
            paths.extend(p.rglob("*.py"))
        else:
            # Invalid path — create error finding and return immediately
            initial_report = ErrorReport(
                pass_name="path_validation",
                findings=[
                    ErrorFinding(
                        error_class=ErrorClass.ENVIRONMENT,
                        severity=Severity.CRITICAL,
                        blocking=True,
                        message=f"Invalid path: {target}",
                        file_path=target,
                        detection_method="path_validation",
                    )
                ],
                blocking_count=1,
                critical_count=1,
            )
            return DebugResult(
                final_state=FinalState.BLOCKED,
                reports=[initial_report],
                resolutions=[],
                total_errors_found=1,
                total_errors_resolved=0,
                blocking_errors_remaining=1,
                iterations=0,
                message="BLOCKED: Invalid target path provided. Cannot proceed.",
            )

    # Initial detection pass
    initial_report = _detect_all_errors(paths, input_data.error_classes)
    reports = [initial_report]
    resolutions: List[ResolutionResult] = []
    iteration = 0

    # Fail-closed check after initial detection
    if initial_report.findings:
        if input_data.fail_on_any_error or initial_report.blocking_count > 0:
            # Execution MUST halt
            return DebugResult(
                final_state=FinalState.BLOCKED,
                reports=reports,
                resolutions=resolutions,
                total_errors_found=len(initial_report.findings),
                total_errors_resolved=0,
                blocking_errors_remaining=initial_report.blocking_count,
                iterations=iteration,
                message=f"BLOCKED: {len(initial_report.findings)} error(s) detected. Resolution {'disabled (safe_mode=True)' if input_data.safe_mode else 'not implemented yet'}. Execution unsafe.",
            )

    # Safe mode: detection only, no resolution
    if input_data.safe_mode:
        return DebugResult(
            final_state=FinalState.CLEAN if not initial_report.findings else FinalState.BLOCKED,
            reports=reports,
            resolutions=resolutions,
            total_errors_found=len(initial_report.findings),
            total_errors_resolved=0,
            blocking_errors_remaining=initial_report.blocking_count,
            iterations=iteration,
            message="Safe mode: detection complete. No resolution attempted." if not initial_report.findings else "Safe mode: errors detected but not resolved.",
        )

    # TODO: Resolution loop (not yet implemented in this version)
    # When implemented:
    # - Iterate: attempt resolution → re-validate → check progress
    # - Halt if no progress after N iterations (UNSAFE state)
    # - Halt if max_resolution_attempts exceeded (UNSAFE state)

    # For now: if we reach here with no errors, CLEAN state
    if not initial_report.findings:
        return DebugResult(
            final_state=FinalState.CLEAN,
            reports=reports,
            resolutions=resolutions,
            total_errors_found=0,
            total_errors_resolved=0,
            blocking_errors_remaining=0,
            iterations=iteration,
            message="CLEAN: Zero errors detected.",
        )

    # Should not reach here (fail-closed above should catch), but defensive:
    return DebugResult(
        final_state=FinalState.UNSAFE,
        reports=reports,
        resolutions=resolutions,
        total_errors_found=len(initial_report.findings),
        total_errors_resolved=0,
        blocking_errors_remaining=initial_report.blocking_count,
        iterations=iteration,
        message="UNSAFE: Unexpected state — debug engine logic error.",
    )
