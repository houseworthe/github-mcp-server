"""Tests for authentication module."""

import pytest
import os
from unittest.mock import patch, Mock
from github_mcp_server.auth import (
    get_github_client,
    handle_oauth_callback,
    start_oauth_flow,
    OAuthConfig
)


class TestAuthentication:
    """Test authentication functionality."""
    
    def test_get_github_client_with_token(self, auth_env):
        """Test GitHub client creation with personal access token."""
        with patch('github_mcp_server.auth.Github') as mock_github:
            client = get_github_client()
            mock_github.assert_called_once_with(auth="test-token")
            assert client == mock_github.return_value
    
    def test_get_github_client_no_auth(self, monkeypatch):
        """Test that client creation fails without authentication."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        with pytest.raises(ValueError, match="No GitHub authentication configured"):
            get_github_client()
    
    def test_get_github_client_enterprise(self, auth_env, monkeypatch):
        """Test GitHub Enterprise client creation."""
        monkeypatch.setenv("GITHUB_ENTERPRISE_URL", "https://github.company.com")
        with patch('github_mcp_server.auth.Github') as mock_github:
            client = get_github_client()
            mock_github.assert_called_once_with(
                base_url="https://github.company.com/api/v3",
                auth="test-token"
            )
    
    @pytest.mark.asyncio
    async def test_start_oauth_flow(self):
        """Test OAuth flow initialization."""
        config = OAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/callback"
        )
        
        auth_url, state = await start_oauth_flow(config)
        
        assert "https://github.com/login/oauth/authorize" in auth_url
        assert "client_id=test-client-id" in auth_url
        assert f"state={state}" in auth_url
        assert len(state) == 32  # Standard state length
    
    @pytest.mark.asyncio
    async def test_handle_oauth_callback_success(self):
        """Test successful OAuth callback handling."""
        config = OAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/callback"
        )
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.json = Mock(return_value={"access_token": "test-token"})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            token = await handle_oauth_callback(config, "test-code", "test-state")
            assert token == "test-token"
    
    @pytest.mark.asyncio
    async def test_handle_oauth_callback_error(self):
        """Test OAuth callback with error response."""
        config = OAuthConfig(
            client_id="test-client-id",
            client_secret="test-client-secret",
            redirect_uri="http://localhost:8080/callback"
        )
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.json = Mock(return_value={"error": "invalid_code"})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(Exception, match="OAuth error"):
                await handle_oauth_callback(config, "bad-code", "test-state")