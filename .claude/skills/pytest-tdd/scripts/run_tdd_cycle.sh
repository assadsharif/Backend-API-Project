#!/usr/bin/env bash
# Run tests in watch mode for TDD workflow
#
# This script runs pytest in watch mode, automatically re-running tests
# when files change. Perfect for the TDD Red-Green-Refactor cycle.
#
# Usage:
#   ./run_tdd_cycle.sh [pytest args]
#
# Examples:
#   ./run_tdd_cycle.sh                    # Watch all tests
#   ./run_tdd_cycle.sh tests/unit         # Watch only unit tests
#   ./run_tdd_cycle.sh -k test_add        # Watch specific test
#   ./run_tdd_cycle.sh --lf               # Watch last failed tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TDD Cycle: Red → Green → Refactor${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if pytest-watch is installed
if ! command -v ptw &> /dev/null; then
    echo -e "${YELLOW}pytest-watch not found. Installing...${NC}"
    pip install pytest-watch
    echo ""
fi

# Default pytest args
PYTEST_ARGS="${@:---tb=short -v}"

echo -e "${GREEN}Watching for file changes...${NC}"
echo -e "Pytest args: ${PYTEST_ARGS}"
echo ""
echo -e "${YELLOW}TDD Workflow:${NC}"
echo "  1. ${RED}RED${NC}   - Write a failing test"
echo "  2. ${GREEN}GREEN${NC} - Write minimum code to pass"
echo "  3. ${BLUE}REFACTOR${NC} - Improve code quality"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run pytest-watch
# --clear: Clear screen between runs
# --nobeep: Don't beep on failures
# --runner: Custom pytest runner command
ptw --clear --nobeep --runner "pytest ${PYTEST_ARGS}"
