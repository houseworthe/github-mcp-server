"""GitHub tools implementation for MCP server."""

import json
import logging
from typing import Any, Dict

from mcp.server import Server
from mcp.server.models import CallToolResult, TextContent
from mcp.types import Tool

from .github_client import GitHubClient

logger = logging.getLogger(__name__)


def setup_tools(server: Server, github_client: GitHubClient) -> None:
    """Setup GitHub tools for the MCP server."""
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle tool calls."""
        try:
            if name == "github_create_issue":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                labels = arguments.get("labels", [])
                assignees = arguments.get("assignees", [])
                
                if not repo or not title:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo' and 'title' are required")]
                    )
                
                issue = github_client.create_issue(repo, title, body, labels, assignees)
                result = {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat()
                }
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(result, indent=2))]
                )
            
            elif name == "github_list_issues":
                repo = arguments.get("repo")
                if not repo:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo' is required")]
                    )
                
                state = arguments.get("state", "open")
                labels = arguments.get("labels", [])
                limit = arguments.get("limit", 30)
                
                issues = github_client.list_issues(repo, state=state, labels=labels, limit=limit)
                results = []
                for issue in issues:
                    results.append({
                        "number": issue.number,
                        "title": issue.title,
                        "state": issue.state,
                        "labels": [label.name for label in issue.labels],
                        "created_at": issue.created_at.isoformat(),
                        "updated_at": issue.updated_at.isoformat(),
                        "html_url": issue.html_url
                    })
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(results, indent=2))]
                )
            
            elif name == "github_create_pr":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                head = arguments.get("head")
                base = arguments.get("base")
                draft = arguments.get("draft", False)
                
                if not all([repo, title, head, base]):
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo', 'title', 'head', and 'base' are required")]
                    )
                
                pr = github_client.create_pull_request(repo, title, body, head, base, draft)
                result = {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "state": pr.state,
                    "draft": pr.draft,
                    "created_at": pr.created_at.isoformat()
                }
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(result, indent=2))]
                )
            
            elif name == "github_list_prs":
                repo = arguments.get("repo")
                if not repo:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo' is required")]
                    )
                
                state = arguments.get("state", "open")
                limit = arguments.get("limit", 30)
                
                prs = github_client.list_pull_requests(repo, state=state, limit=limit)
                results = []
                for pr in prs:
                    results.append({
                        "number": pr.number,
                        "title": pr.title,
                        "state": pr.state,
                        "draft": pr.draft,
                        "created_at": pr.created_at.isoformat(),
                        "updated_at": pr.updated_at.isoformat(),
                        "html_url": pr.html_url,
                        "head": pr.head.ref,
                        "base": pr.base.ref
                    })
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(results, indent=2))]
                )
            
            elif name == "github_search_code":
                query = arguments.get("query")
                if not query:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'query' is required")]
                    )
                
                repo = arguments.get("repo")
                language = arguments.get("language")
                limit = arguments.get("limit", 30)
                
                results = github_client.search_code(query, repo=repo, language=language, limit=limit)
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(results, indent=2))]
                )
            
            elif name == "github_get_file":
                repo = arguments.get("repo")
                path = arguments.get("path")
                if not repo or not path:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo' and 'path' are required")]
                    )
                
                ref = arguments.get("ref")
                content = github_client.get_file_content(repo, path, ref=ref)
                
                return CallToolResult(
                    content=[TextContent(text=content)]
                )
            
            elif name == "github_get_repo":
                repo = arguments.get("repo")
                if not repo:
                    return CallToolResult(
                        content=[TextContent(text="Error: 'repo' is required")]
                    )
                
                repository = github_client.get_repository(repo)
                result = {
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "description": repository.description,
                    "private": repository.private,
                    "fork": repository.fork,
                    "created_at": repository.created_at.isoformat(),
                    "updated_at": repository.updated_at.isoformat(),
                    "pushed_at": repository.pushed_at.isoformat() if repository.pushed_at else None,
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
                    "ssh_url": repository.ssh_url
                }
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(result, indent=2))]
                )
            
            elif name == "github_get_user":
                username = arguments.get("username")
                user_info = github_client.get_user_info(username)
                
                return CallToolResult(
                    content=[TextContent(text=json.dumps(user_info, indent=2))]
                )
            
            else:
                return CallToolResult(
                    content=[TextContent(text=f"Unknown tool: {name}")]
                )
                
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return CallToolResult(
                content=[TextContent(text=f"Error: {str(e)}")]
            )