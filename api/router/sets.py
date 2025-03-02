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


class Sets(BaseModel):
    sets: list[str]


@router.get("/sets")
def get_sets() -> Sets:
    sets = [
        card_set["_id"]
        for card_set in collection.aggregate(
            [
                {
                    "$group": {
                        "_id": "$set_name",
                    }
                },
                {"$sort": {"_id": -1}},
            ]
        )
    ]

    return {"sets": sets}
