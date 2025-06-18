# Contributing to GitHub MCP Server

Thank you for your interest in contributing to GitHub MCP Server! We welcome contributions from the community and are grateful for any help you can provide.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code. Please report unacceptable behavior to the project maintainers.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/github-mcp-server.git
   cd github-mcp-server
   ```
3. Add the upstream repository as a remote:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/github-mcp-server.git
   ```

## Development Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install the package in development mode with all dependencies:
   ```bash
   pip install -e .[dev]
   ```

3. Set up pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

4. Copy the example environment file and configure it:
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub credentials
   ```

## Making Changes

1. Create a new branch for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. Make your changes, following the style guidelines below

3. Add or update tests as needed

4. Update documentation if you're changing functionality

## Testing

Run the test suite before submitting changes:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=github_mcp_server

# Run specific test file
pytest tests/test_specific.py

# Run tests in verbose mode
pytest -v
```

Also run the linters:

```bash
# Format code
black src/
isort src/

# Check code style
ruff check src/

# Type checking
mypy src/
```

## Submitting Changes

1. Commit your changes with a clear commit message:
   ```bash
   git commit -m "Add feature: brief description of changes"
   ```

2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

3. Create a Pull Request:
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill out the PR template with:
     - Clear description of changes
     - Related issue numbers (if any)
     - Testing performed
     - Screenshots (if UI changes)

4. Wait for review and address any feedback

## Style Guidelines

### Python Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use [Black](https://github.com/psf/black) for formatting (line length: 88)
- Use [isort](https://pydantic-docs.helpmanual.io/isort/) for import sorting
- Use type hints where possible
- Write descriptive docstrings for all public functions and classes

### Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

### Documentation

- Update the README.md if you change functionality
- Add docstrings to new functions and classes
- Include examples in docstrings where helpful
- Keep documentation clear and concise

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: How to reproduce the problem
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Environment**:
   - Python version
   - Operating system
   - GitHub MCP Server version
   - Relevant configuration

## Questions?

If you have questions about contributing, feel free to:
- Open a discussion on GitHub
- Ask in the issue tracker
- Contact the maintainers

Thank you for contributing to GitHub MCP Server!