"""GitHub tools implementation for MCP server."""

import json
import logging
from typing import Any, Dict

import mcp.types as types
from mcp.server.lowlevel import Server

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


def setup_tools(server: Server, github_client: GitHubClient) -> None:
    """Setup GitHub tools for the MCP server."""

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools."""
        return [
            types.Tool(
                name="github_create_issue",
                description="Create a new issue in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "title": {"type": "string", "description": "Issue title"},
                        "body": {"type": "string", "description": "Issue body content"},
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of labels to apply",
                        },
                        "assignees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of GitHub usernames to assign",
                        },
                    },
                    "required": ["repo", "title"],
                },
            ),
            types.Tool(
                name="github_list_issues",
                description="List issues in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "Issue state to filter by",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Labels to filter by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of issues to return (default: 30)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_create_pr",
                description="Create a pull request in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "title": {"type": "string", "description": "PR title"},
                        "body": {"type": "string", "description": "PR description"},
                        "head": {
                            "type": "string",
                            "description": "The name of the branch where your changes are implemented",
                        },
                        "base": {
                            "type": "string",
                            "description": "The name of the branch you want the changes pulled into",
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Create as draft PR (default: false)",
                        },
                    },
                    "required": ["repo", "title", "head", "base"],
                },
            ),
            types.Tool(
                name="github_list_prs",
                description="List pull requests in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "PR state to filter by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of PRs to return (default: 30)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_search_code",
                description="Search for code in GitHub repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "repo": {
                            "type": "string",
                            "description": "Limit search to specific repository (owner/repo)",
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language to filter by",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 30)",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="github_get_file",
                description="Get file content from a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "path": {
                            "type": "string",
                            "description": "File path in the repository",
                        },
                        "ref": {
                            "type": "string",
                            "description": "Branch, tag, or commit SHA (default: main branch)",
                        },
                    },
                    "required": ["repo", "path"],
                },
            ),
            types.Tool(
                name="github_get_repo",
                description="Get repository information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        }
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_get_user",
                description="Get GitHub user information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username (omit for authenticated user)",
                        }
                    },
                },
            ),
            types.Tool(
                name="github_update_issue",
                description="Update an existing issue in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "Issue number to update",
                        },
                        "title": {"type": "string", "description": "New issue title"},
                        "body": {
                            "type": "string",
                            "description": "New issue body content",
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed"],
                            "description": "Issue state",
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New list of labels (replaces existing)",
                        },
                        "assignees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "New list of assignees (replaces existing)",
                        },
                        "state_reason": {
                            "type": "string",
                            "enum": ["completed", "not_planned", "reopened"],
                            "description": "Reason for state change (when closing)",
                        },
                    },
                    "required": ["repo", "issue_number"],
                },
            ),
            types.Tool(
                name="github_update_pr",
                description="Update an existing pull request in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "pr_number": {
                            "type": "integer",
                            "description": "Pull request number to update",
                        },
                        "title": {"type": "string", "description": "New PR title"},
                        "body": {
                            "type": "string",
                            "description": "New PR body content",
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed"],
                            "description": "PR state",
                        },
                        "base": {"type": "string", "description": "New base branch"},
                    },
                    "required": ["repo", "pr_number"],
                },
            ),
            types.Tool(
                name="github_add_comment",
                description="Add a comment to an issue or pull request",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "number": {
                            "type": "integer",
                            "description": "Issue or PR number",
                        },
                        "comment": {
                            "type": "string",
                            "description": "Comment text to add",
                        },
                    },
                    "required": ["repo", "number", "comment"],
                },
            ),
            types.Tool(
                name="github_create_branch",
                description="Create a new branch in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name for the new branch",
                        },
                        "from_branch": {
                            "type": "string",
                            "description": "Source branch to create from (default: repository default branch)",
                        },
                    },
                    "required": ["repo", "branch_name"],
                },
            ),
            types.Tool(
                name="github_delete_branch",
                description="Delete a branch from a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "branch_name": {
                            "type": "string",
                            "description": "Name of the branch to delete",
                        },
                    },
                    "required": ["repo", "branch_name"],
                },
            ),
            types.Tool(
                name="github_list_branches",
                description="List branches in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of branches to return (default: 30)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_get_commits",
                description="Get commit history from a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "sha": {
                            "type": "string",
                            "description": "SHA or branch to start listing commits from",
                        },
                        "path": {
                            "type": "string",
                            "description": "Only commits affecting this path",
                        },
                        "author": {
                            "type": "string",
                            "description": "GitHub username or email to filter by",
                        },
                        "since": {
                            "type": "string",
                            "description": "ISO 8601 date string (e.g., '2023-01-01T00:00:00Z')",
                        },
                        "until": {
                            "type": "string",
                            "description": "ISO 8601 date string (e.g., '2023-12-31T23:59:59Z')",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of commits to return (default: 30)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_get_workflow_runs",
                description="Get GitHub Actions workflow runs",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        },
                        "workflow_id": {
                            "type": "integer",
                            "description": "Specific workflow ID to filter by",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["queued", "in_progress", "completed"],
                            "description": "Filter by run status",
                        },
                        "branch": {"type": "string", "description": "Filter by branch"},
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of runs to return (default: 30)",
                        },
                    },
                    "required": ["repo"],
                },
            ),
            types.Tool(
                name="github_list_workflows",
                description="List GitHub Actions workflows in a repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'",
                        }
                    },
                    "required": ["repo"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: Dict[str, Any]
    ) -> list[types.TextContent]:
        """Handle tool calls."""
        try:
            if name == "github_create_issue":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                labels = arguments.get("labels", [])
                assignees = arguments.get("assignees", [])

                if not repo or not title:
                    return [
                        types.TextContent(
                            type="text", text="Error: 'repo' and 'title' are required"
                        )
                    ]

                issue = github_client.create_issue(repo, title, body, labels, assignees)
                result = {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat(),
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_list_issues":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                state = arguments.get("state", "open")
                labels = arguments.get("labels", [])
                limit = arguments.get("limit", 30)

                issues = github_client.list_issues(
                    repo, state=state, labels=labels, limit=limit
                )
                results = []
                for issue in issues:
                    results.append(
                        {
                            "number": issue.number,
                            "title": issue.title,
                            "state": issue.state,
                            "labels": [label.name for label in issue.labels],
                            "created_at": issue.created_at.isoformat(),
                            "updated_at": issue.updated_at.isoformat(),
                            "html_url": issue.html_url,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_create_pr":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                head = arguments.get("head")
                base = arguments.get("base")
                draft = arguments.get("draft", False)

                if not all([repo, title, head, base]):
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo', 'title', 'head', and 'base' are required",
                        )
                    ]

                pr = github_client.create_pull_request(
                    repo, title, body, head, base, draft
                )
                result = {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "state": pr.state,
                    "draft": pr.draft,
                    "created_at": pr.created_at.isoformat(),
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_list_prs":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                state = arguments.get("state", "open")
                limit = arguments.get("limit", 30)

                prs = github_client.list_pull_requests(repo, state=state, limit=limit)
                results = []
                for pr in prs:
                    results.append(
                        {
                            "number": pr.number,
                            "title": pr.title,
                            "state": pr.state,
                            "draft": pr.draft,
                            "created_at": pr.created_at.isoformat(),
                            "updated_at": pr.updated_at.isoformat(),
                            "html_url": pr.html_url,
                            "head": pr.head.ref,
                            "base": pr.base.ref,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_search_code":
                query = arguments.get("query")
                if not query:
                    return [
                        types.TextContent(
                            type="text", text="Error: 'query' is required"
                        )
                    ]

                repo = arguments.get("repo")
                language = arguments.get("language")
                limit = arguments.get("limit", 30)

                results = github_client.search_code(
                    query, repo=repo, language=language, limit=limit
                )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_get_file":
                repo = arguments.get("repo")
                path = arguments.get("path")
                if not repo or not path:
                    return [
                        types.TextContent(
                            type="text", text="Error: 'repo' and 'path' are required"
                        )
                    ]

                ref = arguments.get("ref")
                content = github_client.get_file_content(repo, path, ref=ref)

                return [types.TextContent(type="text", text=content)]

            elif name == "github_get_repo":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                repository = github_client.get_repository(repo)
                result = {
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "description": repository.description,
                    "private": repository.private,
                    "fork": repository.fork,
                    "created_at": repository.created_at.isoformat(),
                    "updated_at": repository.updated_at.isoformat(),
                    "pushed_at": (
                        repository.pushed_at.isoformat()
                        if repository.pushed_at
                        else None
                    ),
                    "homepage": repository.homepage,
                    "size": repository.size,
                    "stargazers_count": repository.stargazers_count,
                    "watchers_count": repository.watchers_count,
                    "language": repository.language,
                    "forks_count": repository.forks_count,
                    "open_issues_count": repository.open_issues_count,
                    "default_branch": repository.default_branch,
                    "html_url": repository.html_url,
                    "clone_url": repository.clone_url,
                    "ssh_url": repository.ssh_url,
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_get_user":
                username = arguments.get("username")
                user_info = github_client.get_user_info(username)

                return [
                    types.TextContent(type="text", text=json.dumps(user_info, indent=2))
                ]

            elif name == "github_update_issue":
                repo = arguments.get("repo")
                issue_number = arguments.get("issue_number")
                if not repo or issue_number is None:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo' and 'issue_number' are required",
                        )
                    ]

                # Get optional parameters
                title = arguments.get("title")
                body = arguments.get("body")
                state = arguments.get("state")
                labels = arguments.get("labels")
                assignees = arguments.get("assignees")
                state_reason = arguments.get("state_reason")

                issue = github_client.update_issue(
                    repo,
                    issue_number,
                    title=title,
                    body=body,
                    state=state,
                    labels=labels,
                    assignees=assignees,
                    state_reason=state_reason,
                )

                result = {
                    "number": issue.number,
                    "title": issue.title,
                    "state": issue.state,
                    "labels": [label.name for label in issue.labels],
                    "assignees": [user.login for user in issue.assignees],
                    "updated_at": issue.updated_at.isoformat(),
                    "html_url": issue.html_url,
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_update_pr":
                repo = arguments.get("repo")
                pr_number = arguments.get("pr_number")
                if not repo or pr_number is None:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo' and 'pr_number' are required",
                        )
                    ]

                # Get optional parameters
                title = arguments.get("title")
                body = arguments.get("body")
                state = arguments.get("state")
                base = arguments.get("base")

                pr = github_client.update_pull_request(
                    repo, pr_number, title=title, body=body, state=state, base=base
                )

                result = {
                    "number": pr.number,
                    "title": pr.title,
                    "state": pr.state,
                    "updated_at": pr.updated_at.isoformat(),
                    "html_url": pr.html_url,
                    "base": pr.base.ref,
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_add_comment":
                repo = arguments.get("repo")
                number = arguments.get("number")
                comment = arguments.get("comment")
                if not repo or number is None or not comment:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo', 'number', and 'comment' are required",
                        )
                    ]

                comment_obj = github_client.add_comment(repo, number, comment)

                result = {
                    "id": comment_obj.id,
                    "body": comment_obj.body,
                    "user": comment_obj.user.login,
                    "created_at": comment_obj.created_at.isoformat(),
                    "html_url": comment_obj.html_url,
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_create_branch":
                repo = arguments.get("repo")
                branch_name = arguments.get("branch_name")
                if not repo or not branch_name:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo' and 'branch_name' are required",
                        )
                    ]

                from_branch = arguments.get("from_branch")
                ref = github_client.create_branch(repo, branch_name, from_branch)

                result = {"ref": ref.ref, "sha": ref.object.sha, "url": ref.url}

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_delete_branch":
                repo = arguments.get("repo")
                branch_name = arguments.get("branch_name")
                if not repo or not branch_name:
                    return [
                        types.TextContent(
                            type="text",
                            text="Error: 'repo' and 'branch_name' are required",
                        )
                    ]

                success = github_client.delete_branch(repo, branch_name)

                result = {
                    "success": success,
                    "message": (
                        f"Branch '{branch_name}' deleted successfully"
                        if success
                        else "Failed to delete branch"
                    ),
                }

                return [
                    types.TextContent(type="text", text=json.dumps(result, indent=2))
                ]

            elif name == "github_list_branches":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                limit = arguments.get("limit", 30)
                branches = github_client.list_branches(repo, limit=limit)

                results = []
                for branch in branches:
                    results.append(
                        {
                            "name": branch.name,
                            "protected": branch.protected,
                            "commit_sha": branch.commit.sha,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_get_commits":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                # Get optional parameters
                sha = arguments.get("sha")
                path = arguments.get("path")
                author = arguments.get("author")
                since = arguments.get("since")
                until = arguments.get("until")
                limit = arguments.get("limit", 30)

                # Parse date strings if provided
                from datetime import datetime

                if since:
                    since = datetime.fromisoformat(since.replace("Z", "+00:00"))
                if until:
                    until = datetime.fromisoformat(until.replace("Z", "+00:00"))

                commits = github_client.get_commits(
                    repo,
                    sha=sha,
                    path=path,
                    author=author,
                    since=since,
                    until=until,
                    limit=limit,
                )

                results = []
                for commit in commits:
                    results.append(
                        {
                            "sha": commit.sha,
                            "message": commit.commit.message,
                            "author": {
                                "name": commit.commit.author.name,
                                "email": commit.commit.author.email,
                                "date": commit.commit.author.date.isoformat(),
                            },
                            "committer": {
                                "name": commit.commit.committer.name,
                                "email": commit.commit.committer.email,
                                "date": commit.commit.committer.date.isoformat(),
                            },
                            "html_url": commit.html_url,
                            "files_changed": len(commit.files) if commit.files else 0,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_get_workflow_runs":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                workflow_id = arguments.get("workflow_id")
                status = arguments.get("status")
                branch = arguments.get("branch")
                limit = arguments.get("limit", 30)

                runs = github_client.get_workflow_runs(
                    repo,
                    workflow_id=workflow_id,
                    status=status,
                    branch=branch,
                    limit=limit,
                )

                results = []
                for run in runs:
                    results.append(
                        {
                            "id": run.id,
                            "name": run.name,
                            "status": run.status,
                            "conclusion": run.conclusion,
                            "branch": run.head_branch,
                            "event": run.event,
                            "created_at": run.created_at.isoformat(),
                            "updated_at": run.updated_at.isoformat(),
                            "html_url": run.html_url,
                            "run_number": run.run_number,
                            "workflow_id": run.workflow_id,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            elif name == "github_list_workflows":
                repo = arguments.get("repo")
                if not repo:
                    return [
                        types.TextContent(type="text", text="Error: 'repo' is required")
                    ]

                workflows = github_client.list_workflows(repo)

                results = []
                for workflow in workflows:
                    results.append(
                        {
                            "id": workflow.id,
                            "name": workflow.name,
                            "path": workflow.path,
                            "state": workflow.state,
                            "created_at": workflow.created_at.isoformat(),
                            "updated_at": workflow.updated_at.isoformat(),
                            "html_url": workflow.html_url,
                        }
                    )

                return [
                    types.TextContent(type="text", text=json.dumps(results, indent=2))
                ]

            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]
