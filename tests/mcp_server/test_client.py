"""Unit tests for MCP server HTTP client."""

import os

# Import the module we're testing
# Use importlib to avoid import errors if module structure changes
import sys
from pathlib import Path

import httpx
import pytest
from pytest_httpx import HTTPXMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from mcp_server.client import APIClient, get_client  # noqa: E402


class TestAPIClient:
    """Test suite for APIClient class."""

    @pytest.mark.asyncio
    async def test_client_initialization_default_url(self):
        """Test client initializes with default base URL from environment."""
        # Clear any existing env var
        original = os.environ.get("API_BASE_URL")
        if "API_BASE_URL" in os.environ:
            del os.environ["API_BASE_URL"]

        client = APIClient()
        assert client.base_url == "http://localhost:8000"
        await client.close()

        # Restore original
        if original:
            os.environ["API_BASE_URL"] = original

    @pytest.mark.asyncio
    async def test_client_initialization_custom_url(self):
        """Test client initializes with custom base URL."""
        client = APIClient(base_url="http://test:8000")
        assert client.base_url == "http://test:8000"
        await client.close()

    @pytest.mark.asyncio
    async def test_client_initialization_env_url(self):
        """Test client initializes with URL from environment variable."""
        os.environ["API_BASE_URL"] = "http://env-test:9000"

        client = APIClient()
        assert client.base_url == "http://env-test:9000"
        await client.close()

        # Clean up
        del os.environ["API_BASE_URL"]

    @pytest.mark.asyncio
    async def test_get_success(self, httpx_mock: HTTPXMock):
        """Test successful GET request."""
        httpx_mock.add_response(
            url="http://test:8000/health", json={"status": "ok"}, status_code=200
        )

        async with APIClient(base_url="http://test:8000") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}

    @pytest.mark.asyncio
    async def test_get_with_params(self, httpx_mock: HTTPXMock):
        """Test GET request with query parameters."""
        httpx_mock.add_response(
            url="http://test:8000/cards/search?lang=en&page_count=10",
            json={"cards": []},
            status_code=200,
        )

        async with APIClient(base_url="http://test:8000") as client:
            response = await client.get(
                "/cards/search", params={"lang": "en", "page_count": 10}
            )
            assert response.status_code == 200
            assert response.json() == {"cards": []}

    @pytest.mark.asyncio
    async def test_get_404_error(self, httpx_mock: HTTPXMock):
        """Test 404 error handling."""
        httpx_mock.add_response(
            url="http://test:8000/nonexistent",
            status_code=404,
            json={"error": "Not Found"},
        )

        async with APIClient(base_url="http://test:8000") as client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.get("/nonexistent")
            assert exc_info.value.response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_500_error(self, httpx_mock: HTTPXMock):
        """Test 500 error handling."""
        httpx_mock.add_response(
            url="http://test:8000/error",
            status_code=500,
            json={"error": "Internal Server Error"},
        )

        async with APIClient(base_url="http://test:8000") as client:
            with pytest.raises(httpx.HTTPStatusError) as exc_info:
                await client.get("/error")
            assert exc_info.value.response.status_code == 500

    @pytest.mark.asyncio
    async def test_context_manager(self, httpx_mock: HTTPXMock):
        """Test context manager properly closes client."""
        httpx_mock.add_response(json={"status": "ok"})

        async with APIClient(base_url="http://test:8000") as client:
            # Client should be usable
            response = await client.get("/health")
            assert response.status_code == 200

        # After exiting context, client should be closed
        assert client.client.is_closed

    @pytest.mark.asyncio
    async def test_timeout_configuration(self):
        """Test client has proper timeout configured."""
        client = APIClient()
        assert client.client.timeout.connect == 30.0
        await client.close()


class TestGetClient:
    """Test suite for get_client singleton function."""

    def test_singleton_returns_same_instance(self):
        """Test get_client returns the same instance on multiple calls."""
        # Reset singleton for test isolation
        import mcp_server.client

        mcp_server.client._client = None

        client1 = get_client()
        client2 = get_client()

        assert client1 is client2

        # Clean up - close the singleton client
        import asyncio

        asyncio.run(client1.close())
        mcp_server.client._client = None

    def test_singleton_uses_env_config(self):
        """Test singleton client uses environment configuration."""
        # Reset singleton
        import mcp_server.client

        mcp_server.client._client = None

        os.environ["API_BASE_URL"] = "http://singleton-test:8000"

        client = get_client()
        assert client.base_url == "http://singleton-test:8000"

        # Clean up
        import asyncio

        asyncio.run(client.close())
        mcp_server.client._client = None
        del os.environ["API_BASE_URL"]
