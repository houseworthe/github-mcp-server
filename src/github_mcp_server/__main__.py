"""Main entry point for the GitHub MCP server."""

import asyncio

from .server import main

if __name__ == "__main__":
    asyncio.run(main())
