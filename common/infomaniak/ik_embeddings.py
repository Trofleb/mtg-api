import os
from time import sleep

import requests
from langchain_core.embeddings import Embeddings

TOKEN = os.environ.get("IK_API_KEY", "NOKEY")
PRODUCT_ID = os.environ.get("IK_PRODUCT_ID", "NOPRODID")
URL = f"https://api.infomaniak.com/1/ai/{PRODUCT_ID}/openai/v1"


class RateLimited(Exception):
    pass


def fetch_embeddings(*args, **kwargs):
    req = requests.request(*args, **kwargs)

    if req.status_code == 429:
        raise RateLimited(f"Rate limit exceeded: {req.reason}\n{req.text}")
    if not req.ok:
        raise Exception(
            f"Request failed with status code {req.status_code}: {req.reason}\n{req.text}"
        )

    return req.json()


class IKEmbeddings(Embeddings):
    EMBED_URL = f"{URL}/embeddings"

    def __init__(self, model="mini_lm_l12_v2"):
        self.model = model

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        data = {"input": texts, "model": self.model, "mode": "index"}
        headers = {
            "Authorization": f"Bearer {TOKEN}",
        }
        batch_size = 100
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            data["input"] = batch_texts

            try:
                result = fetch_embeddings(
                    "POST", url=self.EMBED_URL, json=data, headers=headers
                )
            except RateLimited:
                sleep(60)
                result = fetch_embeddings(
                    "POST", url=self.EMBED_URL, json=data, headers=headers
                )

            embeddings.extend([embedding["embedding"] for embedding in result["data"]])

        return embeddings

    def embed_query(self, text: str) -> list[float]:
        data = {"input": [text], "model": self.model, "mode": "index"}
        headers = {
            "Authorization": f"Bearer {TOKEN}",
            "mode": "query",
        }
        req = requests.request("POST", url=self.EMBED_URL, json=data, headers=headers)
        result = req.json()
        return [embedding["embedding"] for embedding in result["data"]][0]
