import logging
import os
from datetime import datetime
from urllib.request import urlretrieve

import ijson
from pymongo import InsertOne, MongoClient, UpdateOne
from requests import get
from unidecode import unidecode

from tasks.obj_utils import yield_differences

DOWNLOAD_FILENAME = "latest_cards.json"
API_URL = "https://api.scryfall.com/bulk-data"

DATABASE = os.getenv("DATABASE", "mtg")
DATABASE_HOST = os.getenv("DATABASE_HOSTNAME", "mtg")
DATABASE_PORT = os.getenv("DATABASE_PORT", "27017")
DATABASE_USER = os.getenv("DATABASE_USER", "root")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD", "root")

HUEY_LOGGER = logging.getLogger("huey")


def get_dbs():
    client = MongoClient(
        f"mongodb://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}"
    )
    db = client[DATABASE]
    card_collection = db["cards"]

    # base_indexes = card_collection.create_indexes(INDEX_BASE)
    # text_index = card_collection.create_indexes(TEXT_INDEX, **TEXT_INDEX_OPTION)
    # HUEY_LOGGER.info(f"Indexes validated: {len(base_indexes)}, {len(text_index)}")
    card_stocks_daily = db["card_stocks_daily"]
    edhrec_daily = db["edhrec_daily"]

    return card_collection, card_stocks_daily, edhrec_daily


class ProgressBar:
    def __init__(self, text, total=None):
        self.progress = 0
        self.total = total
        self.text = text

    def progress_hook_index(self, index):
        progress_update = (index / self.total * 100) if self.total else index

        step = 1 if self.total else (progress_update // 100)
        if progress_update - self.progress > step:
            self.progress = progress_update
            HUEY_LOGGER.info(
                f"{self.text} {progress_update:.2f}{'%' if self.total else '#'}"
            )

    def progress_hook_urlretrieve(self, blocknum, blocksize, totalsize):
        progress_update = (
            blocknum * blocksize / totalsize * 100
            if totalsize != -1
            else blocknum * blocksize / 3e9 * 100
        )

        if progress_update - self.progress > 1:
            self.progress = progress_update
            HUEY_LOGGER.info(f"{self.text} {progress_update:.2f}%")


def i_fetch_dataset():
    card_collection, card_stocks_daily, edhrec_daily = get_dbs()

    result = get(API_URL)
    bulk_data = result.json()["data"]
    all_cards = next(filter(lambda x: x["type"] == "all_cards", bulk_data), None)
    raw_cards_uri = all_cards["download_uri"]
    last_update_datetime = datetime.fromisoformat(all_cards["updated_at"])

    pb_download = ProgressBar("Download file")  # 500k cards
    urlretrieve(
        raw_cards_uri,
        DOWNLOAD_FILENAME,
        reporthook=pb_download.progress_hook_urlretrieve,
    )

    with open(DOWNLOAD_FILENAME, "rb") as f:
        HUEY_LOGGER.info("Processing cards")
        cards = ijson.items(f, "item", use_float=True)
        pb_cards = ProgressBar("Process cards", 500000)  # 500k cards
        for index, card in enumerate(cards):
            pb_cards.progress_hook_index(index)
            card_id = card["id"]
            card["name_search"] = unidecode(card["name"]).lower()

            prices = {
                price_key: (
                    card["prices"][price_key]
                    if not card["prices"][price_key]
                    else float(card["prices"][price_key])
                )
                for price_key in card["prices"]
            }
            card_stocks_daily.bulk_write(
                [
                    InsertOne(
                        {
                            "date": last_update_datetime,
                            "card_id": card_id,
                            "prices": prices,
                        }
                    )
                ]
            )
            edhrec_daily.bulk_write(
                [
                    InsertOne(
                        {
                            "date": last_update_datetime,
                            "card_id": card_id,
                            "edhrec_rank": card.get("edhrec_rank", None),
                        }
                    )
                ]
            )

            del card["prices"]
            if "edhrec_rank" in card:
                del card["edhrec_rank"]

            next_existing = card_collection.find_one({"id": card_id})
            if not next_existing:
                card_collection.insert_one(card)
                continue

            db_id = next_existing["_id"]
            del next_existing["_id"]

            update = {}
            for key, before, after in yield_differences(next_existing, card):
                update[key] = after

            if update:
                card_collection.bulk_write(
                    [UpdateOne({"_id": db_id}, {"$set": update})]
                )
