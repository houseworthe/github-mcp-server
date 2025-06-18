"""GitHub resources implementation for MCP server."""

import json
import logging
from typing import Any
from urllib.parse import urlparse

import mcp.types as types
from mcp.server.lowlevel import Server
from pydantic import AnyUrl

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


def setup_resources(server: Server, github_client: GitHubClient) -> None:
    """Setup GitHub resources for the MCP server."""

    @server.list_resources()
    async def handle_list_resources() -> list[dict[str, Any]]:
        """List available resources."""
        return [
            {
                "uri": "github://repository/{owner}/{repo}",
                "name": "GitHub Repository",
                "description": "Access GitHub repository information",
                "mimeType": "application/json",
            },
            {
                "uri": "github://issues/{owner}/{repo}",
                "name": "GitHub Issues",
                "description": "Access repository issues",
                "mimeType": "application/json",
            },
            {
                "uri": "github://pulls/{owner}/{repo}",
                "name": "GitHub Pull Requests",
                "description": "Access repository pull requests",
                "mimeType": "application/json",
            },
        ]

    @server.read_resource()
    async def handle_read_resource(uri: str) -> types.ReadResourceResult:
        """Handle resource reads."""
        try:
            # Parse the URI
            parsed = urlparse(uri)
            if parsed.scheme != "github":
                return types.ReadResourceResult(
                    contents=[
                        types.TextResourceContents(
                            uri=AnyUrl(uri), text=f"Unsupported scheme: {parsed.scheme}"
                        )
                    ]
                )

            # Extract path components
            path_parts = parsed.path.strip("/").split("/")

            if len(path_parts) < 2:
                return types.ReadResourceResult(
                    contents=[
                        types.TextResourceContents(
                            uri=AnyUrl(uri), text="Invalid GitHub URI format"
                        )
                    ]
                )

            resource_type = path_parts[0]

            if resource_type == "repository" and len(path_parts) >= 3:
                owner = path_parts[1]
                repo = path_parts[2]
                repo_name = f"{owner}/{repo}"

                try:
                    repository = github_client.get_repository(repo_name)
                    repo_info = {
                        "name": repository.name,
                        "full_name": repository.full_name,
                        "description": repository.description,
                        "html_url": repository.html_url,
                        "clone_url": repository.clone_url,
                        "created_at": repository.created_at.isoformat(),
                        "updated_at": repository.updated_at.isoformat(),
                        "pushed_at": (
                            repository.pushed_at.isoformat()
                            if repository.pushed_at
                            else None
                        ),
                        "size": repository.size,
                        "stargazers_count": repository.stargazers_count,
                        "watchers_count": repository.watchers_count,
                        "language": repository.language,
                        "forks_count": repository.forks_count,
                        "open_issues_count": repository.open_issues_count,
                        "default_branch": repository.default_branch,
                        "topics": repository.get_topics(),
                        "has_issues": repository.has_issues,
                        "has_projects": repository.has_projects,
                        "has_wiki": repository.has_wiki,
                        "has_pages": repository.has_pages,
                        "has_downloads": repository.has_downloads,
                        "archived": repository.archived,
                        "disabled": repository.disabled,
                        "visibility": repository.visibility,
                        "license": (
                            repository.license.name if repository.license else None
                        ),
                    }

                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri), text=json.dumps(repo_info, indent=2)
                            )
                        ]
                    )
                except Exception as e:
                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri),
                                text=f"Error fetching repository: {str(e)}",
                            )
                        ]
                    )

            elif resource_type == "issues" and len(path_parts) >= 3:
                owner = path_parts[1]
                repo = path_parts[2]
                repo_name = f"{owner}/{repo}"

                try:
                    issues = github_client.list_issues(
                        repo_name, state="all", limit=100
                    )
                    issues_data = []
                    for issue in issues:
                        issues_data.append(
                            {
                                "number": issue.number,
                                "title": issue.title,
                                "state": issue.state,
                                "body": issue.body,
                                "user": issue.user.login,
                                "labels": [label.name for label in issue.labels],
                                "assignees": [
                                    assignee.login for assignee in issue.assignees
                                ],
                                "comments": issue.comments,
                                "created_at": issue.created_at.isoformat(),
                                "updated_at": issue.updated_at.isoformat(),
                                "closed_at": (
                                    issue.closed_at.isoformat()
                                    if issue.closed_at
                                    else None
                                ),
                                "html_url": issue.html_url,
                            }
                        )

                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri), text=json.dumps(issues_data, indent=2)
                            )
                        ]
                    )
                except Exception as e:
                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri), text=f"Error fetching issues: {str(e)}"
                            )
                        ]
                    )

            elif resource_type == "pulls" and len(path_parts) >= 3:
                owner = path_parts[1]
                repo = path_parts[2]
                repo_name = f"{owner}/{repo}"

                try:
                    pulls = github_client.list_pull_requests(
                        repo_name, state="all", limit=100
                    )
                    pulls_data = []
                    for pr in pulls:
                        pulls_data.append(
                            {
                                "number": pr.number,
                                "title": pr.title,
                                "state": pr.state,
                                "body": pr.body,
                                "user": pr.user.login,
                                "labels": [label.name for label in pr.labels],
                                "assignees": [
                                    assignee.login for assignee in pr.assignees
                                ],
                                "draft": pr.draft,
                                "head": {"ref": pr.head.ref, "sha": pr.head.sha},
                                "base": {"ref": pr.base.ref, "sha": pr.base.sha},
                                "created_at": pr.created_at.isoformat(),
                                "updated_at": (
                                    pr.updated_at.isoformat() if pr.updated_at else None
                                ),
                                "closed_at": (
                                    pr.closed_at.isoformat() if pr.closed_at else None
                                ),
                                "merged_at": (
                                    pr.merged_at.isoformat() if pr.merged_at else None
                                ),
                                "html_url": pr.html_url,
                                "diff_url": pr.diff_url,
                                "patch_url": pr.patch_url,
                            }
                        )

                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri), text=json.dumps(pulls_data, indent=2)
                            )
                        ]
                    )
                except Exception as e:
                    return types.ReadResourceResult(
                        contents=[
                            types.TextResourceContents(
                                uri=AnyUrl(uri),
                                text=f"Error fetching pull requests: {str(e)}",
                            )
                        ]
                    )

            else:
                return types.ReadResourceResult(
                    contents=[
                        types.TextResourceContents(
                            uri=AnyUrl(uri),
                            text=f"Unknown resource type: {resource_type}",
                        )
                    ]
                )

        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return types.ReadResourceResult(
                contents=[
                    types.TextResourceContents(uri=AnyUrl(uri), text=f"Error: {str(e)}")
                ]
            )
