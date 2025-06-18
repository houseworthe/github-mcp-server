"""Authentication module for GitHub MCP server."""

import asyncio
import logging
import os
import secrets
import webbrowser
from typing import Dict, Optional
from urllib.parse import urlencode

from aiohttp import web

logger = logging.getLogger(__name__)


class GitHubAuth:
    """Handle GitHub authentication via OAuth or Personal Access Token."""

    def __init__(self) -> None:
        self.token: Optional[str] = None
        self.auth_method: Optional[str] = None

    async def authenticate(self) -> str:
        """Authenticate with GitHub and return access token."""
        # First try environment variable (PAT)
        token = os.getenv("GITHUB_TOKEN")
        if token:
            logger.info("Using GitHub Personal Access Token from environment")
            self.token = token
            self.auth_method = "pat"
            return token

        # Try OAuth if no PAT found
        logger.info("No GITHUB_TOKEN found, attempting OAuth authentication")
        return await self._oauth_flow()

    async def _oauth_flow(self) -> str:
        """Perform OAuth authentication flow."""
        client_id = os.getenv("GITHUB_CLIENT_ID")
        client_secret = os.getenv("GITHUB_CLIENT_SECRET")

        if not client_id or not client_secret:
            raise ValueError(
                "GitHub OAuth requires GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables. "
                "Alternatively, set GITHUB_TOKEN for Personal Access Token authentication."
            )

        # Generate state for CSRF protection
        state = secrets.token_urlsafe(32)

        # OAuth parameters
        auth_params = {
            "client_id": client_id,
            "redirect_uri": "http://localhost:8080/callback",
            "scope": "repo read:org read:user",
            "state": state,
        }

        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(auth_params)}"

        # Start local server to receive callback
        token_future: asyncio.Future[str] = asyncio.Future()

        async def handle_callback(request: web.Request) -> web.Response:
            """Handle OAuth callback."""
            query_params = request.rel_url.query

            # Verify state
            if query_params.get("state") != state:
                return web.Response(text="Invalid state parameter", status=400)

            code = query_params.get("code")
            if not code:
                return web.Response(text="No authorization code received", status=400)

            # Exchange code for token
            try:
                token = await self._exchange_code_for_token(
                    code, client_id, client_secret
                )
                token_future.set_result(token)
                return web.Response(
                    text="<html><body><h1>Authentication successful!</h1>"
                    "<p>You can now close this window and return to the terminal.</p></body></html>",
                    content_type="text/html",
                )
            except Exception as e:
                token_future.set_exception(e)
                return web.Response(text=f"Authentication failed: {str(e)}", status=500)

        # Create web app
        app = web.Application()
        app.router.add_get("/callback", handle_callback)

        # Start server
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "localhost", 8080)
        await site.start()

        logger.info("Opening browser for GitHub authentication...")
        webbrowser.open(auth_url)

        try:
            # Wait for token
            token = await asyncio.wait_for(
                token_future, timeout=300
            )  # 5 minute timeout
            self.token = token
            self.auth_method = "oauth"
            return token
        finally:
            await runner.cleanup()

    async def _exchange_code_for_token(
        self, code: str, client_id: str, client_secret: str
    ) -> str:
        """Exchange authorization code for access token."""
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                },
            ) as response:
                data = await response.json()

                if "error" in data:
                    raise ValueError(
                        f"OAuth error: {data.get('error_description', data['error'])}"
                    )

                access_token = data.get("access_token")
                if not access_token:
                    raise ValueError("No access token received from GitHub")

                return str(access_token)

    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        if not self.token:
            raise ValueError("Not authenticated")

        return {"Authorization": f"Bearer {self.token}"}

    @property
    def is_authenticated(self) -> bool:
        """Check if authenticated."""
        return self.token is not None
