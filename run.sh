#!/bin/bash
set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run ./install.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure your credentials."
    exit 1
fi

# Check if authentication is configured
if ! grep -q "GITHUB_TOKEN=\|GITHUB_CLIENT_ID=" .env | grep -v "^#" | grep -v "your_"; then
    echo "Warning: No authentication credentials found in .env file."
    echo "Please configure either:"
    echo "  - GITHUB_TOKEN for Personal Access Token authentication"
    echo "  - GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET for OAuth authentication"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting GitHub MCP Server..."
echo ""

# Run the server
python -m github_mcp_server.server