#!/bin/bash
set -e

echo "GitHub MCP Server Installation Script"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Error: Python $REQUIRED_VERSION or higher is required. Found Python $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -e .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "IMPORTANT: Please edit .env and add your GitHub authentication credentials:"
    echo "  - For Personal Access Token: Set GITHUB_TOKEN"
    echo "  - For OAuth: Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "Installation complete!"
echo ""
echo "To run the server:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Configure your authentication in .env"
echo "  3. Run: python -m github_mcp_server.server"
echo ""
echo "Or use the installed command: github-mcp-server"
echo ""