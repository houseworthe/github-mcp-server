"""GitHub API client wrapper."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from github import Github
from github.GithubException import GithubException
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.Branch import Branch
from github.Commit import Commit
from github.GitRef import GitRef
from github.Workflow import Workflow
from github.WorkflowRun import WorkflowRun

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
    
    def update_issue(
        self,
        repo_name: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        state_reason: Optional[str] = None
    ) -> Issue:
        """Update an existing issue."""
        try:
            repo = self.get_repository(repo_name)
            issue = repo.get_issue(issue_number)
            
            # Build kwargs for edit, only including non-None values
            kwargs = {}
            if title is not None:
                kwargs['title'] = title
            if body is not None:
                kwargs['body'] = body
            if state is not None:
                kwargs['state'] = state
            if labels is not None:
                kwargs['labels'] = labels
            if assignees is not None:
                kwargs['assignees'] = assignees
            if state_reason is not None:
                kwargs['state_reason'] = state_reason
            
            issue.edit(**kwargs)
            return issue
        except GithubException as e:
            logger.error(f"Failed to update issue {issue_number} in {repo_name}: {e}")
            raise
    
    def update_pull_request(
        self,
        repo_name: str,
        pr_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        base: Optional[str] = None
    ) -> PullRequest:
        """Update an existing pull request."""
        try:
            repo = self.get_repository(repo_name)
            pr = repo.get_pull(pr_number)
            
            # Build kwargs for edit, only including non-None values
            kwargs = {}
            if title is not None:
                kwargs['title'] = title
            if body is not None:
                kwargs['body'] = body
            if state is not None:
                kwargs['state'] = state
            if base is not None:
                kwargs['base'] = base
            
            pr.edit(**kwargs)
            return pr
        except GithubException as e:
            logger.error(f"Failed to update pull request {pr_number} in {repo_name}: {e}")
            raise
    
    def add_comment(
        self,
        repo_name: str,
        number: int,
        comment: str
    ) -> IssueComment:
        """Add a comment to an issue or pull request."""
        try:
            repo = self.get_repository(repo_name)
            # Both issues and PRs use the same comment system
            issue = repo.get_issue(number)
            return issue.create_comment(comment)
        except GithubException as e:
            logger.error(f"Failed to add comment to #{number} in {repo_name}: {e}")
            raise
    
    def create_branch(
        self,
        repo_name: str,
        branch_name: str,
        from_branch: Optional[str] = None
    ) -> GitRef:
        """Create a new branch."""
        try:
            repo = self.get_repository(repo_name)
            
            # Get the source branch ref
            if from_branch:
                source_ref = repo.get_git_ref(f"heads/{from_branch}")
            else:
                # Use default branch if not specified
                source_ref = repo.get_git_ref(f"heads/{repo.default_branch}")
            
            # Create new branch
            ref = repo.create_git_ref(
                ref=f"refs/heads/{branch_name}",
                sha=source_ref.object.sha
            )
            return ref
        except GithubException as e:
            logger.error(f"Failed to create branch {branch_name} in {repo_name}: {e}")
            raise
    
    def delete_branch(self, repo_name: str, branch_name: str) -> bool:
        """Delete a branch."""
        try:
            repo = self.get_repository(repo_name)
            ref = repo.get_git_ref(f"heads/{branch_name}")
            ref.delete()
            return True
        except GithubException as e:
            logger.error(f"Failed to delete branch {branch_name} in {repo_name}: {e}")
            raise
    
    def list_branches(self, repo_name: str, limit: int = 30) -> List[Branch]:
        """List repository branches."""
        try:
            repo = self.get_repository(repo_name)
            branches = repo.get_branches()
            return list(branches[:limit])
        except GithubException as e:
            logger.error(f"Failed to list branches in {repo_name}: {e}")
            raise
    
    def get_commits(
        self,
        repo_name: str,
        sha: Optional[str] = None,
        path: Optional[str] = None,
        author: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None,
        limit: int = 30
    ) -> List[Commit]:
        """Get commit history."""
        try:
            repo = self.get_repository(repo_name)
            
            # Build kwargs for get_commits
            kwargs = {}
            if sha:
                kwargs['sha'] = sha
            if path:
                kwargs['path'] = path
            if author:
                kwargs['author'] = author
            if since:
                kwargs['since'] = since
            if until:
                kwargs['until'] = until
            
            commits = repo.get_commits(**kwargs)
            return list(commits[:limit])
        except GithubException as e:
            logger.error(f"Failed to get commits from {repo_name}: {e}")
            raise
    
    def get_workflow_runs(
        self,
        repo_name: str,
        workflow_id: Optional[int] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        limit: int = 30
    ) -> List[WorkflowRun]:
        """Get workflow runs."""
        try:
            repo = self.get_repository(repo_name)
            
            # Build kwargs for get_workflow_runs
            kwargs = {}
            if status:
                kwargs['status'] = status
            if branch:
                kwargs['branch'] = branch
            
            if workflow_id:
                workflow = repo.get_workflow(workflow_id)
                runs = workflow.get_runs(**kwargs)
            else:
                runs = repo.get_workflow_runs(**kwargs)
            
            return list(runs[:limit])
        except GithubException as e:
            logger.error(f"Failed to get workflow runs from {repo_name}: {e}")
            raise
    
    def list_workflows(self, repo_name: str) -> List[Workflow]:
        """List repository workflows."""
        try:
            repo = self.get_repository(repo_name)
            workflows = repo.get_workflows()
            return list(workflows)
        except GithubException as e:
            logger.error(f"Failed to list workflows in {repo_name}: {e}")
            raise