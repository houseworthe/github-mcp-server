# Changelog

All notable changes to the GitHub MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of GitHub MCP Server
- Core MCP server implementation with GitHub integration
- Authentication support (Personal Access Token and OAuth)
- Tool implementations:
  - `github_create_issue` - Create new issues in repositories
  - `github_list_issues` - List and filter repository issues
  - `github_create_pr` - Create pull requests
  - `github_list_prs` - List and filter pull requests
  - `github_search_code` - Search for code across GitHub
  - `github_get_file` - Retrieve file contents from repositories
  - `github_get_repo` - Get repository information
  - `github_get_user` - Get user information
- Resource providers:
  - Repository information and metadata
  - Repository issues
  - Repository pull requests
- GitHub Enterprise Server support
- Rate limiting and retry logic
- Comprehensive error handling
- Installation and run scripts
- Full test suite with pytest
- Documentation and examples

### Security
- Secure credential handling through environment variables
- OAuth CSRF protection with state parameter
- No hardcoded secrets or credentials

## [0.1.0] - TBD

Initial public release.

[Unreleased]: https://github.com/houseworthe/github-mcp-server/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/houseworthe/github-mcp-server/releases/tag/v0.1.0