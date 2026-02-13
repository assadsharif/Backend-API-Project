#!/usr/bin/env bash
# Run FastAPI development server with auto-reload
#
# Usage:
#   ./run_dev.sh [port]
#
# Examples:
#   ./run_dev.sh         # Run on port 8000
#   ./run_dev.sh 8080    # Run on port 8080

set -e

PORT="${1:-8000}"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  FastAPI Development Server${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${GREEN}Creating .env from .env.example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "Please edit .env with your configuration"
    else
        echo "Warning: No .env.example found"
    fi
fi

echo -e "${GREEN}Starting server on port ${PORT}...${NC}"
echo ""
echo "API Docs:    http://localhost:${PORT}/docs"
echo "ReDoc:       http://localhost:${PORT}/redoc"
echo "Health:      http://localhost:${PORT}/health"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop${NC}"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port "${PORT}"
