from fastapi.routing import APIRouter
from pydantic import BaseModel
from pymongo import MongoClient

from common.constants import (
    DATABASE,
    DATABASE_HOST,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)

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
