"""Integration tests for base router endpoints.

This module tests the basic API endpoints that don't require database access,
validating that the test infrastructure is working correctly.
"""

import pytest


@pytest.mark.integration
def test_ping_endpoint_returns_pong(test_client):
    """Test that /ping endpoint returns 'pong' with 200 status.

    This is the simplest integration test, validating that:
    - TestClient is configured correctly
    - FastAPI app is properly loaded
    - Basic routing works
    """
    response = test_client.get("/ping")

    assert response.status_code == 200
    assert response.text == "pong"
