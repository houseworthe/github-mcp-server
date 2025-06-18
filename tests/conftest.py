"""Pytest configuration and fixtures for GitHub MCP Server tests."""

import pytest
from unittest.mock import Mock, AsyncMock
from github import Github
from github.Repository import Repository
from github.Issue import Issue
from github.PullRequest import PullRequest


@pytest.fixture
def mock_github():
    """Create a mock GitHub client."""
    return Mock(spec=Github)


@pytest.fixture
def mock_repo():
    """Create a mock repository."""
    repo = Mock(spec=Repository)
    repo.full_name = "test-owner/test-repo"
    repo.name = "test-repo"
    repo.owner.login = "test-owner"
    repo.description = "Test repository"
    repo.private = False
    repo.default_branch = "main"
    repo.stargazers_count = 42
    repo.forks_count = 10
    return repo


@pytest.fixture
def mock_issue():
    """Create a mock issue."""
    issue = Mock(spec=Issue)
    issue.number = 1
    issue.title = "Test Issue"
    issue.body = "This is a test issue"
    issue.state = "open"
    issue.user.login = "test-user"
    issue.created_at = "2024-01-01T00:00:00Z"
    issue.updated_at = "2024-01-01T00:00:00Z"
    issue.labels = []
    return issue


@pytest.fixture
def mock_pr():
    """Create a mock pull request."""
    pr = Mock(spec=PullRequest)
    pr.number = 1
    pr.title = "Test PR"
    pr.body = "This is a test pull request"
    pr.state = "open"
    pr.user.login = "test-user"
    pr.created_at = "2024-01-01T00:00:00Z"
    pr.updated_at = "2024-01-01T00:00:00Z"
    pr.base.ref = "main"
    pr.head.ref = "feature-branch"
    pr.mergeable = True
    pr.merged = False
    return pr


@pytest.fixture
def auth_env(monkeypatch):
    """Set up authentication environment variables."""
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")
    return "test-token"