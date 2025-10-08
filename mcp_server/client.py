"""HTTP client for FastAPI backend communication."""

import os
from typing import Optional

import httpx


class APIClient:
    """Async HTTP client for FastAPI backend communication.

    This client provides a centralized interface for all MCP server tools
    and resources to communicate with the FastAPI backend. It uses httpx
    for async HTTP requests and automatically raises errors for failed requests.

    Attributes:
        base_url: Base URL of the FastAPI backend
        client: Underlying httpx.AsyncClient instance
    """

    def __init__(self, base_url: Optional[str] = None):
        """Initialize API client with configurable base URL.

        Args:
            base_url: FastAPI backend URL. Defaults to API_BASE_URL env var,
                     or http://localhost:8000 if not set.
        """
        self.base_url = base_url or os.getenv("API_BASE_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,  # 30s timeout for semantic search queries
        )

    async def get(self, path: str, **kwargs) -> httpx.Response:
        """Send GET request to FastAPI backend.

        Args:
            path: API endpoint path (e.g., "/cards/Lightning Bolt")
            **kwargs: Additional arguments passed to httpx.get()

        Returns:
            httpx.Response object

        Raises:
            httpx.HTTPStatusError: If response status indicates error (4xx, 5xx)
            httpx.RequestError: If request fails (network error, timeout, etc.)
        """
        response = await self.client.get(path, **kwargs)
        response.raise_for_status()
        return response

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self.client.aclose()

    async def __aenter__(self) -> "APIClient":
        """Enter async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager and close connection."""
        await self.close()


# Global singleton instance
# Using module-level singleton to avoid creating multiple HTTP clients
_client: Optional[APIClient] = None


def get_client() -> APIClient:
    """Get or create the singleton API client instance.

    This function implements a simple singleton pattern to ensure only one
    APIClient instance is created and reused across all MCP server operations.

    Returns:
        Shared APIClient instance
    """
    global _client
    if _client is None:
        _client = APIClient()
    return _client
