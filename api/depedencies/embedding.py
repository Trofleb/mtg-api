import os
from typing import Annotated

import meilisearch
from fastapi import Depends


def get_meilisearch_client():
    return meilisearch.Client(
        url=os.environ.get("MEILI_HTTP_ADDR", "http://localhost:7700"),
        api_key=os.environ.get("MEILI_API_KEY", "NOKEY"),
    )


MeilisearchClient = Annotated[meilisearch.Client, Depends(get_meilisearch_client)]
