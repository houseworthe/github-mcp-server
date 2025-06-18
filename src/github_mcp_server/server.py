"""Main MCP server implementation for GitHub integration."""

import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool
from dotenv import load_dotenv

from .auth import GitHubAuth
from .github_client import GitHubClient
from .resources import setup_resources
from .tools import setup_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def create_server() -> Server:
    """Create and configure the MCP server."""
    server = Server("github-mcp-server")
    
    # Handle authentication
    auth = GitHubAuth()
    try:
        github_token = await auth.authenticate()
        logger.info(f"Successfully authenticated via {auth.auth_method}")
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        github_token = None
    
    # Initialize GitHub client
    github_client = GitHubClient(token=github_token)
    
    # Setup server capabilities
    setup_tools(server, github_client)
    setup_resources(server, github_client)
    
    @server.list_tools()
    async def handle_list_tools() -> List[Tool]:
        """List available tools."""
        return [
            Tool(
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
            Tool(
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
            Tool(
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
            Tool(
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
            Tool(
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
            Tool(
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
            Tool(
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
            Tool(
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
    
    @server.list_resources()
    async def handle_list_resources() -> List[Dict[str, Any]]:
        """List available resources."""
        return [
            {
                "uri": "github://repository/{owner}/{repo}",
                "name": "GitHub Repository",
                "description": "Access GitHub repository information",
                "mimeType": "application/json"
            },
            {
                "uri": "github://issues/{owner}/{repo}",
                "name": "GitHub Issues",
                "description": "Access repository issues",
                "mimeType": "application/json"
            },
            {
                "uri": "github://pulls/{owner}/{repo}",
                "name": "GitHub Pull Requests",
                "description": "Access repository pull requests",
                "mimeType": "application/json"
            }
        ]
    
    return server


async def main():
    """Main entry point for the server."""
    logger.info("Starting GitHub MCP Server...")
    
    # Create server instance
    server = await create_server()
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="github-mcp-server",
                server_version="0.1.0"
            )
        )


if __name__ == "__main__":
    asyncio.run(main())