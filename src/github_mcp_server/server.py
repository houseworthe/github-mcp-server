"""Main MCP server implementation for GitHub integration."""

import asyncio
import logging

import mcp.server.stdio
from dotenv import load_dotenv
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

from .auth import GitHubAuth
from .github_client import GitHubClient
from .resources import setup_resources
from .tools import setup_tools

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_server() -> Server:
    """Create and configure the MCP server."""
    server: Server = Server("github-mcp-server")

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

    return server


async def main() -> None:
    """Main entry point for the server."""
    logger.info("Starting GitHub MCP Server...")

    # Create server instance
    server = await create_server()

    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="github-mcp-server",
                server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


def run() -> None:
    """Entry point for the server."""
    asyncio.run(main())


if __name__ == "__main__":
    run()
