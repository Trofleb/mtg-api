from typing import Optional

import streamlit as st
from requests import get


@st.cache_data
def search_cards(
    text: str,
    cursor: Optional[str] = None,
    selected_sets: Optional[list[str]] = None,
    colors: Optional[list[str]] = None,
    color_operator: str = "or",
    cmc_min: Optional[int] = None,
    cmc_max: Optional[int] = None,
    types: Optional[list[str]] = None,
    rarities: Optional[list[str]] = None,
) -> dict:
    """Search for MTG cards with optional filters.

    Args:
        text: Search text
        cursor: Pagination cursor
        selected_sets: List of set names to filter by
        colors: List of colors (W, U, B, R, G)
        color_operator: How to apply color filter ("or", "and", "exactly")
        cmc_min: Minimum converted mana cost
        cmc_max: Maximum converted mana cost
        types: List of card types to filter by
        rarities: List of rarities to filter by

    Returns:
        Dict with 'cards', 'cursor', and 'has_more' keys
    """
    filter_params = {}
    if selected_sets:
        filter_params["sets"] = selected_sets
    if colors:
        filter_params["colors"] = colors
        filter_params["color_operator"] = color_operator
    if cmc_min is not None:
        filter_params["cmc_min"] = cmc_min
    if cmc_max is not None:
        filter_params["cmc_max"] = cmc_max
    if types:
        filter_params["types"] = types
    if rarities:
        filter_params["rarities"] = rarities

    try:
        response = get(
            f"http://api:8000/cards/search/{text}",
            params={"cursor": cursor},
            json=filter_params if filter_params else None,
            timeout=30,
        )
        response.raise_for_status()
        cards = response.json()

        if "cards" not in cards:
            print(f"Unexpected response: {cards}")
            return {"cards": [], "cursor": None, "has_more": False}

        return cards
    except Exception as e:
        print(f"Error searching cards: {e}")
        return {"cards": [], "cursor": None, "has_more": False, "error": str(e)}


@st.cache_data
def all_sets() -> list[str]:
    return get("http://api:8000/sets").json()["sets"]
