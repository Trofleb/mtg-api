from functools import reduce
from typing import Optional

import streamlit as st
import streamlit_shadcn_ui as ui
from requests import get

st.set_page_config(
    page_title="Magic the Gathening cards",
    page_icon="👋",
)


st.info(
    "Card info comes from the [Scryfall API](https://scryfall.com/docs/api). Thank you so much for all the data !"
)

st.title("Magic the Gathering cards")


st.warning("This is a work in progress, please don't share the link yet.")
st.stop()


@st.cache_data
def search_cards(text: str, cursor: Optional[str] = None) -> list[str]:
    cards = get(
        f"http://api:8000/cards/search/{text}", params={"cursor": cursor}
    ).json()

    return cards


def reduce_count(acc, value):
    acc[value] = acc.get(value, 0) + 1
    return acc


@st.cache_data
def get_sets(oracle_card):
    return reduce(reduce_count, [card["set_name"] for card in oracle_card["cards"]], {})


@st.cache_data
def get_set_cards(oracle_card, selected_set):
    return [
        card
        for card in oracle_card["cards"]
        if not selected_set or card["set_name"] == selected_set[0]
    ]


search_text = st.text_input("Search", "Black Lotus")

if (
    "cards" not in st.session_state
    or "current_search" not in st.session_state
    or "cursor" not in st.session_state
    or "to_load" not in st.session_state
):
    st.session_state["current_search"] = None
    st.session_state["cards"] = None
    st.session_state["cursor"] = None
    st.session_state["to_load"] = None

if search_text:
    if search_text != st.session_state["current_search"]:
        results = search_cards(search_text, None)
        st.session_state["current_search"] = search_text
        st.session_state["cards"] = results["cards"]
        st.session_state["cursor"] = results["cursor"]
    elif st.session_state["to_load"]:
        results = search_cards(search_text, st.session_state["cursor"])
        st.session_state["cards"].extend(results["cards"])
        st.session_state["cursor"] = results["cursor"]
        st.session_state["to_load"] = None

if not st.session_state["cards"]:
    st.write("No cards found")
    st.stop()

for oracle_card in st.session_state["cards"]:
    name, sets = st.columns([2, 2])
    with name:
        # st.write(oracle_card)
        st.write(oracle_card["name"])
        ui.metric_card(
            content=oracle_card["card_count"],
            title="Version count",
            key=rf"version-count-{oracle_card['name']}",
        )
    with sets:
        # select set
        sets = get_sets(oracle_card)
        selected_set = st.selectbox(
            "Select set",
            list(sets.items()),
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=rf"select-set-{oracle_card['name']}",
            index=None,
        )
        # Set cards
        set_cards = get_set_cards(oracle_card, selected_set)
        langs = reduce(reduce_count, [card["lang"] for card in set_cards], {})
        selected_lang = st.selectbox(
            "Select language",
            list(langs.items()),
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=rf"select-lang-{oracle_card['name']}",
            index=None,
        )
        # Lang cards
        lang_cards = [
            card
            for card in set_cards
            if not selected_lang or card["lang"] == selected_lang[0]
        ]
        years = reduce(
            reduce_count, [card["released_at"][:4] for card in lang_cards], {}
        )
        selected_year = st.selectbox(
            "Select year",
            list(years.items()),
            format_func=lambda x: f"{x[0]} ({x[1]})",
            key=rf"select-year-{oracle_card['name']}",
            index=None,
        )
        # Year cards
        year_cards = [
            card
            for card in lang_cards
            if not selected_year or card["released_at"][:4] == selected_year[0]
        ]

    year_cards_thumbnail = [
        year_card["thumbnail"] for year_card in year_cards if year_card.get("thumbnail")
    ]
    if (
        not selected_year
        and not selected_set
        and not selected_lang
        and oracle_card["thumbnail"]
    ):
        st.image(oracle_card["thumbnail"])
    elif len(year_cards_thumbnail) > 0:
        st.image(year_cards_thumbnail)
    else:
        st.info("No image available")

if st.session_state["cursor"]:
    if st.button("Load more"):
        st.session_state["to_load"] = st.session_state["cursor"]
