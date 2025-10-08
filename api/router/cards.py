from typing import Optional

from fastapi import HTTPException
from fastapi.routing import APIRouter
from pydantic import AnyUrl, BaseModel
from pymongo import MongoClient
from unidecode import unidecode

from api.helpers.cards_mongo import AGGREGATE_CARD, CARD_PROJECTION
from common.constants import (
    DATABASE,
    DATABASE_HOST,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)
from common.scyfall_models import PrintedCard

router = APIRouter()

client = MongoClient(
    f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
)

db = client[DATABASE]
collection = db["cards"]


class Card(PrintedCard):
    thumbnail: AnyUrl
    image: AnyUrl
    imageXL: AnyUrl


class OracleCard:
    id: str
    name: str
    card_text: str
    set_count: int
    thumbnail: str
    card_count: str
    edhrec_rank: int
    penny_rank: int
    cards: list[Card]


class CardFilter(BaseModel):
    sets: Optional[list[str]] = None


@router.get("/cards/{name}")
def search_card_by_name(
    name: str,
    lang: str = "en",
    set: Optional[str] = None,
):
    search_name = unidecode(name).lower()
    results = [
        card
        for card in collection.aggregate(
            [
                {
                    "$match": {
                        "name_search": {
                            "$regex": f"^{search_name}",
                        },
                    }
                },
                {"$project": CARD_PROJECTION},
                {"$sort": {"released_at": -1}},
                {
                    "$match": {
                        "lang": {"$eq": lang},
                        "layout": {
                            "$nin": ["art_series"],
                        },
                        "set": ({"$eq": set.lower()} if set else {"$exists": True}),
                    }
                },
                {"$group": AGGREGATE_CARD},
            ]
        )
    ]

    if len(results) == 0:
        return None

    return results[0]


@router.get("/cards/search/{text}")
def search_card_by_text(
    text: str,
    lang: str = "en",
    cursor: Optional[str] = None,
    page_count=10,
    card_filter: Optional[CardFilter] = None,
):
    results = [
        card
        for card in collection.aggregate(
            [
                {
                    "$match": {
                        "$text": {
                            "$search": text,
                            "$caseSensitive": False,
                            "$diacriticSensitive": False,
                        },
                        "lang": {"$eq": lang},
                        "set_name": (
                            {"$in": card_filter.sets}
                            if card_filter and card_filter.sets
                            else {"$exists": True}
                        ),
                    }
                },
                {"$project": {"score": 1, **CARD_PROJECTION}},
                {"$group": {"score": {"$max": "$score"}, **AGGREGATE_CARD}},
                {"$sort": {"score": -1}},
                (
                    {
                        "$match": {
                            "score": {
                                "$lt": float(cursor),
                            }
                        }
                    }
                    if cursor
                    else {
                        "$match": {
                            "_id": {
                                "$exists": True,
                            }
                        }
                    }
                ),
                {
                    "$limit": page_count + 1,
                },
            ]
        )
    ]

    result = {
        "cards": results[:page_count],
        "cursor": str(results[-2]["score"]) if len(results) > page_count else None,
        "has_more": len(results) > page_count,
    }

    return result


@router.get("/cards/id/{scryfall_id}")
def get_card_by_scryfall_id(scryfall_id: str):
    """Get a specific MTG card printing by Scryfall ID.

    Args:
        scryfall_id: Unique Scryfall UUID for a specific card printing

    Returns:
        Card data including image_uris and all metadata

    Raises:
        HTTPException: 404 if card not found
    """

    # Query MongoDB for card by Scryfall ID
    card = collection.find_one({"id": scryfall_id}, CARD_PROJECTION)

    if card is None:
        raise HTTPException(
            status_code=404, detail=f"Card with ID {scryfall_id} not found"
        )

    return card


@router.get("/cards/oracle/{oracle_id}")
def get_cards_by_oracle_id(oracle_id: str):
    """Get all printings of a card by Oracle ID.

    Args:
        oracle_id: Oracle UUID representing the card concept (non-unique)

    Returns:
        List of all card printings sharing this oracle_id

    Raises:
        HTTPException: 404 if no cards found with this oracle_id
    """

    # Query MongoDB for all cards with this Oracle ID
    cards = list(
        collection.find({"oracle_id": oracle_id}, CARD_PROJECTION).sort(
            "released_at", -1
        )
    )

    if not cards:
        raise HTTPException(
            status_code=404, detail=f"No cards found with Oracle ID {oracle_id}"
        )

    return cards
