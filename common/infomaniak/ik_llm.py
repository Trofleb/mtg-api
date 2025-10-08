import json
import logging
import os

from langchain_core.messages import BaseMessage, convert_to_openai_messages
from langchain_openai import ChatOpenAI
from requests import post

TOKEN = os.environ.get("IK_API_KEY", "NOKEY")
PRODUCT_ID = os.environ.get("IK_PRODUCT_ID", "NOPRODID")
URL = f"https://api.infomaniak.com/1/ai/{PRODUCT_ID}/openai"
MODEL = "llama3"


def get_ik_llm():
    return ChatOpenAI(
        api_key=TOKEN,
        base_url=URL,
        model=MODEL,
        temperature=0.6,
        top_p=0.95,
    )


def manual_chat_call(messages: list[BaseMessage], model=MODEL, token=TOKEN):
    req_messages = convert_to_openai_messages(messages)

    request = post(
        f"{URL}/chat/completions",
        json={"messages": req_messages, "model": model, "stream": True},
        headers={"Authorization": f"Bearer {token}"},
        stream=True,
    )

    for res in request.iter_content(chunk_size=2048):
        if b"[DONE]" in res:
            break

        try:
            json_res = json.loads(res[6:])
        except json.JSONDecodeError:
            logging.error(f"Failed to decode JSON: {res}")
            continue
        value = json_res["choices"][0]["delta"]["content"]

        if value:
            yield value
