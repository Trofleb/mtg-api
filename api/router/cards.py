from typing import Optional

from fastapi import HTTPException
from fastapi.routing import APIRouter
from pydantic import AnyUrl, BaseModel
from unidecode import unidecode

from api.helpers.cards_mongo import AGGREGATE_CARD, CARD_PROJECTION
from api.helpers.database import CardsCollection
from common.scyfall_models import PrintedCard

router = APIRouter()


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
    colors: Optional[list[str]] = None  # WUBRG filter
    color_operator: Optional[str] = "or"  # "or", "and", "exactly"
    cmc_min: Optional[int] = None
    cmc_max: Optional[int] = None
    types: Optional[list[str]] = None  # creature, instant, sorcery, etc.
    rarities: Optional[list[str]] = None  # common, uncommon, rare, mythic


@router.get("/cards/{name}")
def search_card_by_name(
    name: str,
    collection: CardsCollection,
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
    collection: CardsCollection,
    lang: str = "en",
    cursor: Optional[str] = None,
    page_count=10,
    card_filter: Optional[CardFilter] = None,
):
    # Build match conditions
    match_conditions = {
        "$text": {
            "$search": text,
            "$caseSensitive": False,
            "$diacriticSensitive": False,
        },
        "lang": {"$eq": lang},
    }

    # Add set filter
    if card_filter and card_filter.sets:
        match_conditions["set_name"] = {"$in": card_filter.sets}

    # Add color filter
    if card_filter and card_filter.colors:
        if card_filter.color_operator == "exactly":
            # Exactly these colors (no more, no less)
            match_conditions["colors"] = {"$size": len(card_filter.colors)}
            match_conditions["colors"] = {"$all": card_filter.colors}
        elif card_filter.color_operator == "and":
            # Contains all these colors (may have more)
            match_conditions["colors"] = {"$all": card_filter.colors}
        else:  # "or" - default
            # Contains any of these colors
            match_conditions["colors"] = {"$in": card_filter.colors}

    # Add CMC filter
    if card_filter and (
        card_filter.cmc_min is not None or card_filter.cmc_max is not None
    ):
        cmc_filter = {}
        if card_filter.cmc_min is not None:
            cmc_filter["$gte"] = card_filter.cmc_min
        if card_filter.cmc_max is not None:
            cmc_filter["$lte"] = card_filter.cmc_max
        match_conditions["cmc"] = cmc_filter

    # Add type filter (checks if type_line contains any of the specified types)
    if card_filter and card_filter.types:
        # Case-insensitive regex for type matching
        type_patterns = [
            {"type_line": {"$regex": t, "$options": "i"}} for t in card_filter.types
        ]
        match_conditions["$or"] = type_patterns

    # Add rarity filter
    if card_filter and card_filter.rarities:
        match_conditions["rarity"] = {"$in": card_filter.rarities}

    results = [
        card
        for card in collection.aggregate(
            [
                {"$match": match_conditions},
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
def get_card_by_scryfall_id(scryfall_id: str, collection: CardsCollection):
    """Get a specific MTG card printing by Scryfall ID.

    Args:
        scryfall_id: Unique Scryfall UUID for a specific card printing
        collection: MongoDB cards collection (injected dependency)

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
def get_cards_by_oracle_id(oracle_id: str, collection: CardsCollection):
    """Get all printings of a card by Oracle ID.

    Args:
        oracle_id: Oracle UUID representing the card concept (non-unique)
        collection: MongoDB cards collection (injected dependency)

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
