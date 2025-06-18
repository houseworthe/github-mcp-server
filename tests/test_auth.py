"""Tests for authentication module."""

import pytest
import os
from unittest.mock import patch, Mock, AsyncMock
from github_mcp_server.auth import GitHubAuth


class TestAuthentication:
    """Test authentication functionality."""
    
    @pytest.mark.asyncio
    async def test_authenticate_with_token(self, auth_env):
        """Test authentication with personal access token."""
        auth = GitHubAuth()
        token = await auth.authenticate()
        
        assert token == "test-token"
        assert auth.token == "test-token"
        assert auth.auth_method == "pat"
        assert auth.is_authenticated
    
    @pytest.mark.asyncio
    async def test_authenticate_no_token_no_oauth(self, monkeypatch):
        """Test that authentication fails without any credentials."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.delenv("GITHUB_CLIENT_ID", raising=False)
        monkeypatch.delenv("GITHUB_CLIENT_SECRET", raising=False)
        
        auth = GitHubAuth()
        with pytest.raises(ValueError, match="GitHub OAuth requires"):
            await auth.authenticate()
    
    def test_get_auth_headers(self, auth_env):
        """Test getting authentication headers."""
        auth = GitHubAuth()
        auth.token = "test-token"
        
        headers = auth.get_auth_headers()
        assert headers == {"Authorization": "Bearer test-token"}
    
    def test_get_auth_headers_not_authenticated(self):
        """Test getting headers when not authenticated."""
        auth = GitHubAuth()
        
        with pytest.raises(ValueError, match="Not authenticated"):
            auth.get_auth_headers()
    
    def test_is_authenticated(self):
        """Test authentication status check."""
        auth = GitHubAuth()
        assert not auth.is_authenticated
        
        auth.token = "test-token"
        assert auth.is_authenticated
    
    @pytest.mark.asyncio
    async def test_oauth_flow_exchange_code_success(self, monkeypatch):
        """Test successful OAuth code exchange."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test-client-secret")
        
        auth = GitHubAuth()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={"access_token": "oauth-token"})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            token = await auth._exchange_code_for_token(
                "test-code", "test-client-id", "test-client-secret"
            )
            assert token == "oauth-token"
    
    @pytest.mark.asyncio
    async def test_oauth_flow_exchange_code_error(self, monkeypatch):
        """Test OAuth code exchange with error response."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test-client-secret")
        
        auth = GitHubAuth()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={"error": "invalid_grant"})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ValueError, match="OAuth error"):
                await auth._exchange_code_for_token(
                    "bad-code", "test-client-id", "test-client-secret"
                )
    
    @pytest.mark.asyncio
    async def test_oauth_flow_no_access_token(self, monkeypatch):
        """Test OAuth code exchange with no access token in response."""
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)
        monkeypatch.setenv("GITHUB_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("GITHUB_CLIENT_SECRET", "test-client-secret")
        
        auth = GitHubAuth()
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = Mock()
            mock_response.json = AsyncMock(return_value={})
            mock_post.return_value.__aenter__.return_value = mock_response
            
            with pytest.raises(ValueError, match="No access token received"):
                await auth._exchange_code_for_token(
                    "test-code", "test-client-id", "test-client-secret"
                )