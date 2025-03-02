from typing import Optional
from pydantic import AnyUrl, BaseModel
from pymongo import MongoClient
from unidecode import unidecode
from api.helpers.cards_mongo import CARD_PROJECTION, AGGREGATE_CARD
from common.constants import (
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE,
)

from fastapi.routing import APIRouter

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
def read_root(
    name: str,
    lang: str = "en",
    set: str = None,
    num: str = None,
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
def read_root(
    text: str,
    lang: str = "en",
    cursor: str = None,
    page_count=10,
    card_filter: CardFilter = None,
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
