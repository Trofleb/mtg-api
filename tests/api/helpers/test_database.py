"""Tests for database dependency injection module.

This module tests that the database dependency functions work correctly
and can be properly injected into FastAPI routes.
"""

from unittest.mock import MagicMock, patch

import pytest
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from api.helpers.database import get_cards_collection, get_database, get_mongo_client


@pytest.mark.unit
def test_get_mongo_client_returns_client():
    """Test that get_mongo_client returns a MongoDB client instance."""
    with patch("api.helpers.database.MongoClient") as mock_client:
        mock_instance = MagicMock(spec=MongoClient)
        mock_client.return_value = mock_instance

        client = get_mongo_client()

        assert client is mock_instance
        mock_client.assert_called_once()


@pytest.mark.unit
def test_get_database_returns_correct_database():
    """Test that get_database returns the correct database from client."""
    mock_client = MagicMock(spec=MongoClient)
    mock_database = MagicMock(spec=Database)
    mock_client.__getitem__.return_value = mock_database

    with patch("api.helpers.database.DATABASE", "test_db"):
        database = get_database(client=mock_client)

        assert database is mock_database
        mock_client.__getitem__.assert_called_once_with("test_db")


@pytest.mark.unit
def test_get_cards_collection_returns_correct_collection():
    """Test that get_cards_collection returns the cards collection."""
    mock_db = MagicMock(spec=Database)
    mock_collection = MagicMock(spec=Collection)
    mock_db.__getitem__.return_value = mock_collection

    collection = get_cards_collection(db=mock_db)

    assert collection is mock_collection
    mock_db.__getitem__.assert_called_once_with("cards")


@pytest.mark.unit
def test_dependency_injection_chain():
    """Test that the full dependency injection chain works together."""
    with patch("api.helpers.database.MongoClient") as mock_mongo_client:
        # Setup mock chain
        mock_client_instance = MagicMock(spec=MongoClient)
        mock_db_instance = MagicMock(spec=Database)
        mock_collection_instance = MagicMock(spec=Collection)

        mock_mongo_client.return_value = mock_client_instance
        mock_client_instance.__getitem__.return_value = mock_db_instance
        mock_db_instance.__getitem__.return_value = mock_collection_instance

        with patch("api.helpers.database.DATABASE", "test_db"):
            # Test full chain
            client = get_mongo_client()
            database = get_database(client=client)
            collection = get_cards_collection(db=database)

            # Verify chain worked
            assert client is mock_client_instance
            assert database is mock_db_instance
            assert collection is mock_collection_instance

            # Verify calls
            mock_mongo_client.assert_called_once()
            mock_client_instance.__getitem__.assert_called_once_with("test_db")
            mock_db_instance.__getitem__.assert_called_once_with("cards")
