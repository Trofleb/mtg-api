import os
from typing import Annotated
from fastapi import Depends
from fastapi.responses import StreamingResponse
from fastapi.routing import APIRouter
from langchain_community.vectorstores import Meilisearch
from api.depedencies.embedding import MeilisearchClient
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from common.infomaniak.ik_embeddings import IKEmbeddings
from common.infomaniak.ik_llm import manual_chat_call

router = APIRouter(prefix="/mtg")

DND_MODEL = os.environ.get("MODEL", "bge_multilingual_gemma2")
DND_DIMENSIONS = int(os.environ.get("DIMENSIONS", 3584))


def mtg_store(client: MeilisearchClient):
    embedders = {"custom": {"source": "userProvided", "dimensions": DND_DIMENSIONS}}
    model = IKEmbeddings(model=DND_MODEL)

    return Meilisearch(
        client=client,
        embedding=model,
        index_name=f"mtg_rules_{DND_MODEL}",
        embedders=embedders,
    )


MTGStore = Annotated[Meilisearch, Depends(mtg_store)]


@router.get("/ruling/{question}", response_class=StreamingResponse)
def read_root(question: str, mtg_store: MTGStore, paragraph_counts: int = 20):
    paragraphs = mtg_store.similarity_search(
        query=question,
        embedder_name="custom",
        k=paragraph_counts,
    )

    stream_answer = manual_chat_call(
        messages=[
            SystemMessage(
                content=(
                    "Vous êtes un Juge du jeu de carte Magic: The Gathering. Vous aidez un joueur "
                    "avec une question sur les règles, gardez vos réponse courtes et clair pour ne pas ralentir le jeu."
                )
            ),
            HumanMessage(
                content=f"Veuillez répondre à la question suivante : {question}"
            ),
            HumanMessage(
                content=f"""
                    Voici les {paragraph_counts} meilleurs résultats des règles liés à la question :
                    ---
                    {"---".join([f"{result.metadata}: {result.page_content}" for result in paragraphs])}
                """
            ),
        ]
    )

    return StreamingResponse(stream_answer)
