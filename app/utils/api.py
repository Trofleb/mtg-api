from typing import Optional

import streamlit as st
from requests import get

from common.scyfall_models import PrintedCard


@st.cache_data
def search_cards(
    text: str, cursor: Optional[str] = None, selected_sets: Optional[list[str]] = None
) -> list[PrintedCard]:
    cards = get(
        f"http://api:8000/cards/search/{text}",
        params={"cursor": cursor},
        json={"sets": selected_sets},
    ).json()

    if "cards" not in cards:
        print(cards)

    return cards


@st.cache_data
def all_sets() -> list[str]:
    return get("http://api:8000/sets").json()["sets"]
