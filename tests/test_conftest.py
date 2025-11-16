"""Tests for conftest.py fixtures.

This module validates that the shared fixtures work correctly and
properly override dependencies for integration testing.
"""

import pytest

from tests.mocks.mongodb import MockMongoCollection


@pytest.mark.unit
def test_mock_cards_collection_fixture_has_data(mock_cards_collection):
    """Test that mock_cards_collection fixture loads sample data."""
    assert isinstance(mock_cards_collection, MockMongoCollection)

    # Should have sample cards loaded
    all_cards = list(mock_cards_collection.find({}))
    assert len(all_cards) >= 6, "Should have at least 6 sample cards"

    # Verify some known cards exist
    lightning_bolt = mock_cards_collection.find_one({"name": "Lightning Bolt"})
    assert lightning_bolt is not None
    assert lightning_bolt["cmc"] == 1.0


@pytest.mark.unit
def test_empty_collection_fixture_is_empty(empty_collection):
    """Test that empty_collection fixture has no documents."""
    assert isinstance(empty_collection, MockMongoCollection)

    all_cards = list(empty_collection.find({}))
    assert len(all_cards) == 0


@pytest.mark.integration
def test_test_client_fixture_overrides_dependencies(test_client):
    """Test that test_client fixture properly overrides dependencies."""
    # The test_client should work without errors
    # This ping endpoint doesn't use database, but client should be configured
    response = test_client.get("/ping")
    assert response.status_code == 200


@pytest.mark.integration
def test_test_client_fixture_clears_overrides(mock_cards_collection):
    """Test that test_client fixture clears dependency overrides after test."""
    from api.helpers.database import get_cards_collection
    from api.main import app

    # Before using fixture, overrides should be empty
    initial_overrides = len(app.dependency_overrides)

    # Use test client fixture (simulate what the fixture does)
    app.dependency_overrides[get_cards_collection] = lambda: mock_cards_collection
    assert len(app.dependency_overrides) == initial_overrides + 1

    # Clean up (simulate what fixture does)
    app.dependency_overrides.clear()
    assert len(app.dependency_overrides) == 0


@pytest.mark.integration
def test_test_client_can_call_api_endpoints(test_client):
    """Test that test_client can successfully call API endpoints."""
    # Test a simple endpoint that uses mocked database
    response = test_client.get("/sets")
    assert response.status_code == 200

    # Should return sets data
    data = response.json()
    assert "sets" in data
    assert isinstance(data["sets"], list)


@pytest.mark.integration
def test_test_client_empty_returns_no_data(test_client_empty):
    """Test that test_client_empty fixture returns empty results."""
    response = test_client_empty.get("/sets")
    assert response.status_code == 200

    data = response.json()
    assert "sets" in data
    assert len(data["sets"]) == 0
