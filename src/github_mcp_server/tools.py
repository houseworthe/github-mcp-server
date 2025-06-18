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
                            "description": "Repository in format 'owner/repo'"
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body content"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of labels to apply"
                        },
                        "assignees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of GitHub usernames to assign"
                        }
                    },
                    "required": ["repo", "title"]
                }
            ),
            types.Tool(
                name="github_list_issues",
                description="List issues in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "Issue state to filter by"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Labels to filter by"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of issues to return (default: 30)"
                        }
                    },
                    "required": ["repo"]
                }
            ),
            types.Tool(
                name="github_create_pr",
                description="Create a pull request in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'"
                        },
                        "title": {
                            "type": "string",
                            "description": "PR title"
                        },
                        "body": {
                            "type": "string",
                            "description": "PR description"
                        },
                        "head": {
                            "type": "string",
                            "description": "The name of the branch where your changes are implemented"
                        },
                        "base": {
                            "type": "string",
                            "description": "The name of the branch you want the changes pulled into"
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "Create as draft PR (default: false)"
                        }
                    },
                    "required": ["repo", "title", "head", "base"]
                }
            ),
            types.Tool(
                name="github_list_prs",
                description="List pull requests in a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'"
                        },
                        "state": {
                            "type": "string",
                            "enum": ["open", "closed", "all"],
                            "description": "PR state to filter by"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of PRs to return (default: 30)"
                        }
                    },
                    "required": ["repo"]
                }
            ),
            types.Tool(
                name="github_search_code",
                description="Search for code in GitHub repositories",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "repo": {
                            "type": "string",
                            "description": "Limit search to specific repository (owner/repo)"
                        },
                        "language": {
                            "type": "string",
                            "description": "Programming language to filter by"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 30)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            types.Tool(
                name="github_get_file",
                description="Get file content from a GitHub repository",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'"
                        },
                        "path": {
                            "type": "string",
                            "description": "File path in the repository"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Branch, tag, or commit SHA (default: main branch)"
                        }
                    },
                    "required": ["repo", "path"]
                }
            ),
            types.Tool(
                name="github_get_repo",
                description="Get repository information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "repo": {
                            "type": "string",
                            "description": "Repository in format 'owner/repo'"
                        }
                    },
                    "required": ["repo"]
                }
            ),
            types.Tool(
                name="github_get_user",
                description="Get GitHub user information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username (omit for authenticated user)"
                        }
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> list[types.TextContent]:
        """Handle tool calls."""
        try:
            if name == "github_create_issue":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                labels = arguments.get("labels", [])
                assignees = arguments.get("assignees", [])
                
                if not repo or not title:
                    return [types.TextContent(type="text", text="Error: 'repo' and 'title' are required")]
                
                issue = github_client.create_issue(repo, title, body, labels, assignees)
                result = {
                    "number": issue.number,
                    "title": issue.title,
                    "url": issue.html_url,
                    "state": issue.state,
                    "created_at": issue.created_at.isoformat()
                }
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "github_list_issues":
                repo = arguments.get("repo")
                if not repo:
                    return [types.TextContent(type="text", text="Error: 'repo' is required")]
                
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
                
                return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
            
            elif name == "github_create_pr":
                repo = arguments.get("repo")
                title = arguments.get("title")
                body = arguments.get("body", "")
                head = arguments.get("head")
                base = arguments.get("base")
                draft = arguments.get("draft", False)
                
                if not all([repo, title, head, base]):
                    return [types.TextContent(type="text", text="Error: 'repo', 'title', 'head', and 'base' are required")]
                
                pr = github_client.create_pull_request(repo, title, body, head, base, draft)
                result = {
                    "number": pr.number,
                    "title": pr.title,
                    "url": pr.html_url,
                    "state": pr.state,
                    "draft": pr.draft,
                    "created_at": pr.created_at.isoformat()
                }
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "github_list_prs":
                repo = arguments.get("repo")
                if not repo:
                    return [types.TextContent(type="text", text="Error: 'repo' is required")]
                
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
                
                return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
            
            elif name == "github_search_code":
                query = arguments.get("query")
                if not query:
                    return [types.TextContent(type="text", text="Error: 'query' is required")]
                
                repo = arguments.get("repo")
                language = arguments.get("language")
                limit = arguments.get("limit", 30)
                
                results = github_client.search_code(query, repo=repo, language=language, limit=limit)
                
                return [types.TextContent(type="text", text=json.dumps(results, indent=2))]
            
            elif name == "github_get_file":
                repo = arguments.get("repo")
                path = arguments.get("path")
                if not repo or not path:
                    return [types.TextContent(type="text", text="Error: 'repo' and 'path' are required")]
                
                ref = arguments.get("ref")
                content = github_client.get_file_content(repo, path, ref=ref)
                
                return [types.TextContent(type="text", text=content)]
            
            elif name == "github_get_repo":
                repo = arguments.get("repo")
                if not repo:
                    return [types.TextContent(type="text", text="Error: 'repo' is required")]
                
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
                
                return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
            
            elif name == "github_get_user":
                username = arguments.get("username")
                user_info = github_client.get_user_info(username)
                
                return [types.TextContent(type="text", text=json.dumps(user_info, indent=2))]
            
            else:
                return [types.TextContent(type="text", text=f"Unknown tool: {name}")]
                
        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]