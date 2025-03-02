from typing import Annotated
from fastapi import Depends
from langchain_community.vectorstores import Meilisearch
import meilisearch
import os

from common.infomaniak.ik_embeddings import IKEmbeddings


def get_meilisearch_client():
    return meilisearch.Client(
        url=os.environ.get("MEILI_HTTP_ADDR", "http://localhost:7700"),
        api_key=os.environ.get("MEILI_API_KEY", "x"),
    )


MeilisearchClient = Annotated[meilisearch.Client, Depends(get_meilisearch_client)]
