"""GitHub MCP Server - A Model Context Protocol server for GitHub integration."""

__version__ = "0.1.0"

from .server import create_server, main

__all__ = ["create_server", "main"]