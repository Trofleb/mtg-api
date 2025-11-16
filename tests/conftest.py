"""Shared pytest fixtures for all tests.

This module provides common fixtures for integration testing with mocked
MongoDB collections and FastAPI TestClient with dependency overrides.
"""

import pytest
from fastapi.testclient import TestClient

from api.helpers.database import get_cards_collection
from api.main import app
from tests.fixtures.sample_cards import get_all_sample_cards
from tests.mocks.mongodb import MockMongoCollection


@pytest.fixture
def mock_cards_collection():
    """Mock MongoDB collection pre-loaded with sample cards.

    Returns:
        MockMongoCollection instance with test card data.
    """
    return MockMongoCollection(get_all_sample_cards())


@pytest.fixture
def empty_collection():
    """Empty MongoDB collection for testing empty states.

    Returns:
        MockMongoCollection instance with no documents.
    """
    return MockMongoCollection([])


@pytest.fixture
def test_client(mock_cards_collection):
    """FastAPI TestClient with mocked MongoDB collection.

    This fixture overrides the database dependency to use the mock
    collection instead of connecting to a real MongoDB instance.

    Args:
        mock_cards_collection: Fixture providing mock collection.

    Yields:
        TestClient instance with overridden dependencies.
    """
    # Override the dependency to return our mock collection
    app.dependency_overrides[get_cards_collection] = lambda: mock_cards_collection

    # Create test client
    yield TestClient(app)

    # Clear overrides after test completes
    app.dependency_overrides.clear()


@pytest.fixture
def test_client_empty(empty_collection):
    """FastAPI TestClient with empty MongoDB collection.

    Useful for testing endpoints with no data.

    Args:
        empty_collection: Fixture providing empty collection.

    Yields:
        TestClient instance with empty collection.
    """
    app.dependency_overrides[get_cards_collection] = lambda: empty_collection
    yield TestClient(app)
    app.dependency_overrides.clear()
