from pydantic import AnyUrl, BaseModel
from pymongo import MongoClient
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


@router.get("/cards/search/{text}")
def read_root(text: str, lang: str = "en", cursor: str = None, page_count=10):
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
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "id": 1,
                        "name": 1,
                        "oracle_id": 1,
                        "lang": 1,
                        "oracle_text": 1,
                        "set_name": 1,
                        # "frame": 1,
                        # "reserved": 1,
                        # "full_art": 1,
                        # "textless": 1,
                        "artist": 1,
                        # "booster": 1,
                        # "attraction_lights": 1,
                        "layout": 1,
                        # "story_spotlight": 1,
                        # "artist_ids": 1,
                        # "border_color": 1,
                        # "card_back_id": 1,
                        # "collector_number": 1,
                        # "content_warning": 1,
                        # "digital": 1,
                        # "finishes": 1,
                        "flavor_name": 1,
                        "flavor_text": 1,
                        # "frame_effects": 1,
                        "games": 1,
                        # "highres_image": 1,
                        # "illustration_id": 1,
                        # "image_status": 1,
                        # "image_uris": 1,
                        # "oversized": 1,
                        # "prices": 1,
                        # "printed_name": 1,
                        # "printed_text": 1,
                        # "printed_type_line": 1,
                        "promo": 1,
                        # "promo_types": 1,
                        # "purchase_uris": 1,
                        "rarity": 1,
                        "related_uris": 1,
                        "released_at": 1,
                        "reprint": 1,
                        # "scryfall_set_uri": 1,
                        "set_name": 1,
                        # "set_search_uri": 1,
                        # "set_type": 1,
                        # "set_uri": 1,
                        "set": 1,
                        # "set_id": 1,
                        # "textless": 1,
                        "variation": 1,
                        "variation_of": 1,
                        "security_stamp": 1,
                        "watermark": 1,
                        # "preview_previewed_at": 1,
                        # "preview_source_uri": 1,
                        # "preview_source": 1,
                        "thumbnail": "$image_uris.small",
                        "image": "$image_uris.large",
                        "imageXL": "$image_uris.png",
                        "score": {"$meta": "textScore"},
                    }
                },
                {
                    "$group": {
                        "_id": "$oracle_id",
                        "name": {"$first": "$name"},
                        "card_text": {"$first": "$oracle_text"},
                        "card_count": {"$sum": 1},
                        "cards": {"$addToSet": "$$ROOT"},
                        "score": {"$max": {"$meta": "textScore"}},
                        "edhrec_rank": {"$max": "$edhrec_rank"},
                        "penny_rank": {"$max": "$penny_rank"},
                        "thumbnail": {"$first": "$thumbnail"},
                    }
                },
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

    print(result)
    return result
