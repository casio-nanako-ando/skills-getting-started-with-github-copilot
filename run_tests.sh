#!/bin/bash
# Test runner script for the High School Management System API

echo "Running FastAPI tests..."
echo "========================="

# Activate virtual environment and run tests with coverage
/workspaces/skills-getting-started-with-github-copilot/.venv/bin/python -m pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -v

echo ""
echo "Test run complete!"
echo "Coverage report saved to htmlcov/index.html"