# GitHub MCP Server

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-Compatible-green)](https://github.com/modelcontextprotocol)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server that provides seamless integration with GitHub, enabling AI assistants to interact with repositories, issues, pull requests, and more.

## Why GitHub MCP Server?

- **Seamless AI Integration**: Let Claude and other AI assistants work directly with your GitHub repositories
- **Comprehensive API Coverage**: Access issues, PRs, code search, and more through simple MCP tools
- **Enterprise Ready**: Full support for GitHub Enterprise Server
- **Secure**: OAuth and PAT authentication with proper credential handling
- **Well-Tested**: Comprehensive test suite and CI/CD pipeline

## Features

### Tools
- **github_create_issue** - Create new issues in repositories
- **github_list_issues** - List and filter repository issues
- **github_create_pr** - Create pull requests
- **github_list_prs** - List and filter pull requests
- **github_search_code** - Search for code across GitHub
- **github_get_file** - Retrieve file contents from repositories
- **github_get_repo** - Get repository information
- **github_get_user** - Get user information

### Resources
- `github://repository/{owner}/{repo}` - Repository information and metadata
- `github://issues/{owner}/{repo}` - Repository issues
- `github://pulls/{owner}/{repo}` - Repository pull requests

## Installation

### Prerequisites
- Python 3.8 or higher
- GitHub account with appropriate permissions

### Quick Start

1. Clone the repository:
```bash
git clone https://github.com/houseworthe/github-mcp-server.git
cd github-mcp-server
```

2. Run the installation script:
```bash
./install.sh
```

3. Configure authentication (see Authentication section below)

4. Run the server:
```bash
./run.sh
```

### Manual Installation

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -e .
```

3. Copy the environment template:
```bash
cp .env.example .env
```

4. Configure your authentication credentials in `.env`

## Authentication

The server supports two authentication methods:

### Option 1: Personal Access Token (Recommended)

1. Go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
2. Click "Generate new token" (classic)
3. Select scopes: `repo`, `read:org`, `read:user`
4. Copy the token
5. Add to `.env`:
```bash
GITHUB_TOKEN=your_personal_access_token_here
```

### Option 2: OAuth App

1. Go to [GitHub Settings > Developer settings > OAuth Apps](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set Authorization callback URL to `http://localhost:8080/callback`
4. Copy the Client ID and Client Secret
5. Add to `.env`:
```bash
GITHUB_CLIENT_ID=your_client_id
GITHUB_CLIENT_SECRET=your_client_secret
```

## Usage

### With Claude Desktop

Add the server to your Claude Desktop configuration:

1. Open Claude Desktop settings
2. Go to "Developer" section
3. Add to the MCP servers configuration:

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["-m", "github_mcp_server.server"],
      "cwd": "/path/to/github-mcp-server",
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Example Commands

Once connected, you can ask Claude to:

- "Create an issue in owner/repo about the bug in the login system"
- "List all open pull requests in owner/repo"
- "Search for 'TODO' comments in the owner/repo codebase"
- "Get the contents of README.md from owner/repo"
- "Show me information about the GitHub user 'octocat'"

### Accessing Resources

Resources can be accessed using special URIs:

- Repository info: `github://repository/facebook/react`
- Issues: `github://issues/facebook/react`
- Pull requests: `github://pulls/facebook/react`

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GITHUB_TOKEN` | Personal Access Token for authentication | Yes (unless using OAuth) |
| `GITHUB_CLIENT_ID` | OAuth App Client ID | Only for OAuth |
| `GITHUB_CLIENT_SECRET` | OAuth App Client Secret | Only for OAuth |
| `GITHUB_ENTERPRISE_URL` | GitHub Enterprise Server URL | No |
| `GITHUB_DEFAULT_ORG` | Default organization for operations | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

### Type Checking
```bash
mypy src/
```

## Troubleshooting

### Authentication Issues
- Ensure your token has the required scopes
- Check that the token hasn't expired
- For OAuth, ensure the callback URL matches exactly

### Connection Issues
- Check your internet connection
- Verify GitHub API is accessible
- Check for rate limiting (authenticated requests have higher limits)

### Debug Mode
Enable debug logging by setting:
```bash
LOG_LEVEL=DEBUG
```

## Security Considerations

- Never commit your `.env` file or expose your tokens
- Use environment-specific tokens for different environments
- Regularly rotate your access tokens
- Be cautious when granting repository access

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Showcase

### Example Use Cases

1. **Automated Issue Management**
   ```python
   # AI assistant can create issues based on code analysis
   "Create an issue for the TODO comment in auth.py line 45"
   ```

2. **Code Search & Analysis**
   ```python
   # Search across entire organizations
   "Find all uses of deprecated_function in our repos"
   ```

3. **PR Automation**
   ```python
   # Create PRs with AI-generated descriptions
   "Create a PR for the feature branch with a summary of changes"
   ```

### Integration Example

```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["-m", "github_mcp_server"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Community & Support

- **Issues**: [Report bugs or request features](https://github.com/houseworthe/github-mcp-server/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/houseworthe/github-mcp-server/discussions)
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines

## Acknowledgments

- Built on the [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API interaction
- Inspired by the official MCP servers repository