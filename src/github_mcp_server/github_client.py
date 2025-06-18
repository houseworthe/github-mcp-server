"""GitHub API client wrapper."""

import logging
from typing import Any, Dict, List, Optional

from github import Github
from github.GithubException import GithubException
from github.Issue import Issue
from github.PullRequest import PullRequest
from github.Repository import Repository

logger = logging.getLogger(__name__)


class GitHubClient:
    """Wrapper around PyGithub for MCP server usage."""
    
    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub client with optional token."""
        self.github = Github(token) if token else Github()
        self._token = token
    
    def get_repository(self, repo_name: str) -> Repository:
        """Get a repository by name (format: owner/repo)."""
        try:
            return self.github.get_repo(repo_name)
        except GithubException as e:
            logger.error(f"Failed to get repository {repo_name}: {e}")
            raise
    
    def create_issue(
        self,
        repo_name: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> Issue:
        """Create a new issue in a repository."""
        try:
            repo = self.get_repository(repo_name)
            return repo.create_issue(
                title=title,
                body=body or "",
                labels=labels or [],
                assignees=assignees or []
            )
        except GithubException as e:
            logger.error(f"Failed to create issue in {repo_name}: {e}")
            raise
    
    def list_issues(
        self,
        repo_name: str,
        state: str = "open",
        labels: Optional[List[str]] = None,
        sort: str = "created",
        direction: str = "desc",
        limit: int = 30
    ) -> List[Issue]:
        """List issues in a repository."""
        try:
            repo = self.get_repository(repo_name)
            issues = repo.get_issues(
                state=state,
                labels=labels or [],
                sort=sort,
                direction=direction
            )
            return list(issues[:limit])
        except GithubException as e:
            logger.error(f"Failed to list issues in {repo_name}: {e}")
            raise
    
    def create_pull_request(
        self,
        repo_name: str,
        title: str,
        body: str,
        head: str,
        base: str,
        draft: bool = False
    ) -> PullRequest:
        """Create a new pull request."""
        try:
            repo = self.get_repository(repo_name)
            return repo.create_pull(
                title=title,
                body=body,
                head=head,
                base=base,
                draft=draft
            )
        except GithubException as e:
            logger.error(f"Failed to create pull request in {repo_name}: {e}")
            raise
    
    def list_pull_requests(
        self,
        repo_name: str,
        state: str = "open",
        sort: str = "created",
        direction: str = "desc",
        limit: int = 30
    ) -> List[PullRequest]:
        """List pull requests in a repository."""
        try:
            repo = self.get_repository(repo_name)
            pulls = repo.get_pulls(
                state=state,
                sort=sort,
                direction=direction
            )
            return list(pulls[:limit])
        except GithubException as e:
            logger.error(f"Failed to list pull requests in {repo_name}: {e}")
            raise
    
    def search_code(
        self,
        query: str,
        repo: Optional[str] = None,
        language: Optional[str] = None,
        limit: int = 30
    ) -> List[Dict[str, Any]]:
        """Search for code in GitHub."""
        try:
            search_query = query
            if repo:
                search_query += f" repo:{repo}"
            if language:
                search_query += f" language:{language}"
            
            results = self.github.search_code(search_query)
            
            code_results = []
            for idx, code in enumerate(results):
                if idx >= limit:
                    break
                code_results.append({
                    "name": code.name,
                    "path": code.path,
                    "repository": code.repository.full_name,
                    "html_url": code.html_url,
                    "sha": code.sha
                })
            
            return code_results
        except GithubException as e:
            logger.error(f"Failed to search code: {e}")
            raise
    
    def get_file_content(self, repo_name: str, path: str, ref: Optional[str] = None) -> str:
        """Get file content from a repository."""
        try:
            repo = self.get_repository(repo_name)
            file_content = repo.get_contents(path, ref=ref)
            if isinstance(file_content, list):
                raise ValueError(f"Path {path} is a directory, not a file")
            return file_content.decoded_content.decode("utf-8")
        except GithubException as e:
            logger.error(f"Failed to get file content from {repo_name}/{path}: {e}")
            raise
    
    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Get user information."""
        try:
            user = self.github.get_user(username) if username else self.github.get_user()
            return {
                "login": user.login,
                "name": user.name,
                "email": user.email,
                "bio": user.bio,
                "company": user.company,
                "location": user.location,
                "html_url": user.html_url,
                "public_repos": user.public_repos,
                "followers": user.followers,
                "following": user.following
            }
        except GithubException as e:
            logger.error(f"Failed to get user info: {e}")
            raise