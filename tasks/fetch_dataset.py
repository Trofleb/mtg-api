import json
import logging
import os
from datetime import datetime
from urllib.request import urlretrieve

from pymongo import InsertOne, MongoClient, UpdateOne
from requests import get
from tqdm import tqdm
from unidecode import unidecode

from tasks.indexes import INDEX_BASE, TEXT_INDEX, TEXT_INDEX_OPTION
from tasks.obj_utils import yield_differences

DOWNLOAD_FILENAME = "latest_cards.json"
API_URL = "https://api.scryfall.com/bulk-data"

DATABASE = os.getenv("DATABASE", "mtg")
DATABASE_HOST = os.getenv("DATABASE_HOSTNAME", "mtg")
DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "root")

HUEY_LOGGER = logging.getLogger("huey")


def read_file(file_path: str):
    with open(file_path) as file:
        return json.loads(file.read())


class ProgressBar:
    def __init__(self):
        self.progress = 0

    def progress_hook(self, blocknum, blocksize, totalsize):
        progress_update = (
            blocknum * blocksize / totalsize * 100
            if totalsize != -1
            else blocknum * blocksize / 3e9 * 100
        )

        if progress_update - self.progress > 1:
            self.progress = progress_update
            HUEY_LOGGER.info(f"Downloading {progress_update:.2f}%")


def load_dataset():
    result = get(API_URL)
    bulk_data = result.json()["data"]
    all_cards = next(filter(lambda x: x["type"] == "all_cards", bulk_data), None)
    raw_cards_uri = all_cards["download_uri"]

    progress_bar = ProgressBar()
    urlretrieve(
        raw_cards_uri,
        DOWNLOAD_FILENAME,
        reporthook=progress_bar.progress_hook,
    )

    return datetime.fromisoformat(all_cards["updated_at"]), read_file(DOWNLOAD_FILENAME)


def get_dbs():
    client = MongoClient(
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
    )
    db = client[DATABASE]
    card_collection = db["cards"]

    base_indexes = card_collection.create_indexes(INDEX_BASE)
    text_index = card_collection.create_indexes(TEXT_INDEX, **TEXT_INDEX_OPTION)
    HUEY_LOGGER.info(f"Indexes validated: {len(base_indexes)}, {len(text_index)}")
    card_stocks_daily = db["card_stocks_daily"]
    edhrec_daily = db["edhrec_daily"]

    return card_collection, card_stocks_daily, edhrec_daily


def update_cards_db():
    HUEY_LOGGER.info("Loading dataset")
    date, cards = load_dataset()
    card_collection, card_stocks_daily, edhrec_daily = get_dbs()

    batch_updates = []
    price_updates = []
    edhrec_update = []

    sorted_cards = sorted(cards, key=lambda x: x["id"])
    sorted_existing = card_collection.find().sort("id", 1)
    next_existing = next(sorted_existing, None)

    for card in tqdm(sorted_cards):
        card_id = card["id"]
        card["name_search"] = unidecode(card["name"]).lower()

        if card.get("_id"):
            HUEY_LOGGER.warning(f"Card should not have an _id, {card}")
            break

        prices = {
            price_key: (
                card["prices"][price_key]
                if not card["prices"][price_key]
                else float(card["prices"][price_key])
            )
            for price_key in card["prices"]
        }
        price_updates.append(
            InsertOne({"date": date, "card_id": card_id, "prices": prices})
        )
        edhrec_update.append(
            InsertOne(
                {
                    "date": date,
                    "card_id": card_id,
                    "edhrec_rank": card.get("edhrec_rank", None),
                }
            )
        )

        del card["prices"]
        if "edhrec_rank" in card:
            del card["edhrec_rank"]

        if not next_existing or next_existing["id"] != card_id:
            batch_updates.append(InsertOne(card))
            continue

        db_id = next_existing["_id"]
        del next_existing["_id"]

        update = {}
        for key, before, after in yield_differences(next_existing, card):
            update[key] = after

        if update:
            batch_updates.append(UpdateOne({"_id": db_id}, {"$set": update}))

        next_existing = next(sorted_existing, None)

        if batch_updates:
            HUEY_LOGGER.info(f"Batch updates: {len(batch_updates)}")
            card_collection.bulk_write(batch_updates)

        if price_updates:
            HUEY_LOGGER.info(f"Price updates: {len(price_updates)}")
            card_stocks_daily.bulk_write(price_updates)

        if edhrec_update:
            HUEY_LOGGER.info(f"Edhrec updates: {len(edhrec_update)}")
            edhrec_daily.bulk_write(edhrec_update)
