"""Database dependency injection for FastAPI.

This module provides dependency injection functions for MongoDB connections,
enabling easy mocking in tests via app.dependency_overrides.
"""

from typing import Annotated

from fastapi import Depends
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from common.constants import (
    DATABASE,
    DATABASE_HOST,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)


def get_mongo_client() -> MongoClient:
    """Get MongoDB client instance.

    Returns:
        MongoClient: Configured MongoDB client connection.
    """
    return MongoClient(
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
    )


def get_database(client: MongoClient = Depends(get_mongo_client)) -> Database:
    """Get MongoDB database instance.

    Args:
        client: MongoDB client from dependency injection.

    Returns:
        Database: MongoDB database instance.
    """
    return client[DATABASE]


def get_cards_collection(db: Database = Depends(get_database)) -> Collection:
    """Get cards collection from MongoDB.

    Args:
        db: MongoDB database from dependency injection.

    Returns:
        Collection: MongoDB cards collection.
    """
    return db["cards"]


# Type annotations for use in route handlers
MongoDatabase = Annotated[Database, Depends(get_database)]
CardsCollection = Annotated[Collection, Depends(get_cards_collection)]
