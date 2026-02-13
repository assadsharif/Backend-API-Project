#!/usr/bin/env python3
"""Initialize pytest in a Python project with TDD best practices.

This script sets up:
- pytest and coverage dependencies
- Standard test directory structure
- pytest configuration
- Coverage configuration
- Example test file demonstrating TDD
"""
import argparse
import os
import sys
from pathlib import Path


def create_directory_structure(project_root: Path) -> None:
    """Create standard pytest directory structure."""
    directories = [
        project_root / "tests",
        project_root / "tests" / "unit",
        project_root / "tests" / "integration",
        project_root / "tests" / "fixtures",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {directory}")

    # Create __init__.py files
    for directory in directories:
        init_file = directory / "__init__.py"
        if not init_file.exists():
            init_file.write_text("")
            print(f"✓ Created {init_file}")


def create_pytest_ini(project_root: Path) -> None:
    """Create pytest.ini configuration file."""
    pytest_ini = project_root / "pytest.ini"

    content = """[pytest]
# Pytest configuration for TDD workflow

# Test discovery patterns
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Output options
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-branch

# Minimum coverage percentage (fail if below)
# --cov-fail-under=80

# Test paths
testpaths = tests

# Markers for organizing tests
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow-running tests
    wip: Work in progress tests

# Ignore paths
norecursedirs = .git .tox dist build *.egg __pycache__
"""

    pytest_ini.write_text(content)
    print(f"✓ Created {pytest_ini}")


def create_coverage_rc(project_root: Path) -> None:
    """Create .coveragerc configuration file."""
    coveragerc = project_root / ".coveragerc"

    content = """[run]
source = src
branch = True
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */site-packages/*
    */venv/*
    */.venv/*

[report]
precision = 2
show_missing = True
skip_covered = False

exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
    @abc.abstractmethod

[html]
directory = htmlcov
"""

    coveragerc.write_text(content)
    print(f"✓ Created {coveragerc}")


def create_conftest(project_root: Path) -> None:
    """Create conftest.py with common fixtures."""
    conftest = project_root / "tests" / "conftest.py"

    content = '''"""Pytest configuration and shared fixtures.

This file is automatically discovered by pytest and contains:
- Project-wide fixtures
- Pytest hooks
- Shared test utilities
"""
import pytest


# ============================================================================
# Session-scoped fixtures (run once per test session)
# ============================================================================

@pytest.fixture(scope="session")
def session_data():
    """Fixture that runs once per test session.

    Use for expensive setup that can be shared across all tests.
    """
    data = {"config": "test"}
    yield data
    # Cleanup happens here after all tests


# ============================================================================
# Module-scoped fixtures (run once per test module)
# ============================================================================

@pytest.fixture(scope="module")
def module_data():
    """Fixture that runs once per test module.

    Use for setup shared across a single test file.
    """
    data = {}
    yield data


# ============================================================================
# Function-scoped fixtures (run once per test function)
# ============================================================================

@pytest.fixture
def sample_data():
    """Fixture that runs for each test function.

    Default scope is 'function'. Use for test-specific setup.
    """
    return {"key": "value"}


# ============================================================================
# Parametrized fixtures
# ============================================================================

@pytest.fixture(params=["option1", "option2", "option3"])
def parametrized_fixture(request):
    """Fixture that runs test multiple times with different values.

    Each test using this fixture will run 3 times.
    """
    return request.param


# ============================================================================
# Pytest hooks
# ============================================================================

def pytest_configure(config):
    """Hook called after command line options have been parsed."""
    # Add custom configuration here
    pass


def pytest_collection_modifyitems(config, items):
    """Hook called after test collection.

    Use to modify or reorder test items.
    """
    # Example: Mark slow tests
    for item in items:
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)
'''

    conftest.write_text(content)
    print(f"✓ Created {conftest}")


def create_example_test(project_root: Path) -> None:
    """Create an example test demonstrating TDD workflow."""
    test_file = project_root / "tests" / "unit" / "test_example_tdd.py"

    content = '''"""Example test demonstrating TDD workflow.

TDD Cycle (Red-Green-Refactor):
1. RED: Write a failing test
2. GREEN: Write minimum code to pass
3. REFACTOR: Improve code while keeping tests green
"""
import pytest


# ============================================================================
# Example 1: Simple function testing
# ============================================================================

def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def test_add_positive_numbers():
    """Test adding positive numbers."""
    assert add(2, 3) == 5
    assert add(10, 20) == 30


def test_add_negative_numbers():
    """Test adding negative numbers."""
    assert add(-1, -1) == -2
    assert add(-5, 3) == -2


# ============================================================================
# Example 2: Parameterized testing
# ============================================================================

@pytest.mark.parametrize("a,b,expected", [
    (1, 1, 2),
    (2, 3, 5),
    (10, -5, 5),
    (0, 0, 0),
    (-1, -1, -2),
])
def test_add_parameterized(a, b, expected):
    """Test add function with multiple parameter combinations."""
    assert add(a, b) == expected


# ============================================================================
# Example 3: Testing with fixtures
# ============================================================================

@pytest.fixture
def calculator_data():
    """Fixture providing test data for calculator tests."""
    return {
        "operand1": 10,
        "operand2": 5,
        "add_result": 15,
        "subtract_result": 5,
    }


def test_with_fixture(calculator_data):
    """Test using fixture data."""
    result = add(calculator_data["operand1"], calculator_data["operand2"])
    assert result == calculator_data["add_result"]


# ============================================================================
# Example 4: Testing exceptions
# ============================================================================

def divide(a: float, b: float) -> float:
    """Divide a by b."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b


def test_divide_by_zero():
    """Test that dividing by zero raises ValueError."""
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(10, 0)


def test_divide_valid():
    """Test valid division."""
    assert divide(10, 2) == 5.0
    assert divide(9, 3) == 3.0


# ============================================================================
# Example 5: Class-based tests
# ============================================================================

class TestCalculator:
    """Group related tests in a class."""

    def test_addition(self):
        """Test addition."""
        assert add(1, 1) == 2

    def test_division(self):
        """Test division."""
        assert divide(10, 2) == 5.0

    @pytest.mark.parametrize("a,b", [(0, 0), (1, 0)])
    def test_division_edge_cases(self, a, b):
        """Test division edge cases."""
        if b == 0:
            with pytest.raises(ValueError):
                divide(a, b)
        else:
            assert divide(a, b) == 0.0
'''

    test_file.write_text(content)
    print(f"✓ Created {test_file}")


def update_gitignore(project_root: Path) -> None:
    """Add pytest and coverage artifacts to .gitignore."""
    gitignore = project_root / ".gitignore"

    pytest_ignores = """
# Pytest
.pytest_cache/
__pycache__/
*.pyc
*.pyo

# Coverage
.coverage
.coverage.*
htmlcov/
.tox/

# Test artifacts
.cache/
"""

    if gitignore.exists():
        content = gitignore.read_text()
        if ".pytest_cache" not in content:
            with gitignore.open("a") as f:
                f.write(pytest_ignores)
            print(f"✓ Updated {gitignore}")
    else:
        gitignore.write_text(pytest_ignores)
        print(f"✓ Created {gitignore}")


def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "="*60)
    print("✅ Pytest initialized successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Install dependencies:")
    print("   pip install pytest pytest-cov pytest-mock")
    print("   # or")
    print("   uv add --dev pytest pytest-cov pytest-mock")
    print("\n2. Run the example tests:")
    print("   pytest")
    print("\n3. Run tests with coverage:")
    print("   pytest --cov")
    print("\n4. Run tests in watch mode (TDD):")
    print("   pytest-watch  # Install with: pip install pytest-watch")
    print("\n5. Follow the TDD cycle:")
    print("   RED → Write a failing test")
    print("   GREEN → Write minimum code to pass")
    print("   REFACTOR → Improve code while keeping tests green")
    print("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Initialize pytest for TDD workflow"
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)"
    )

    args = parser.parse_args()
    project_root = Path(args.project_root).resolve()

    if not project_root.exists():
        print(f"Error: Directory {project_root} does not exist")
        sys.exit(1)

    print(f"Initializing pytest in {project_root}\n")

    # Create all the files
    create_directory_structure(project_root)
    create_pytest_ini(project_root)
    create_coverage_rc(project_root)
    create_conftest(project_root)
    create_example_test(project_root)
    update_gitignore(project_root)

    print_next_steps()


if __name__ == "__main__":
    main()
