import streamlit as st

from utils.api import search_cards, all_sets


st.set_page_config(
    page_title="Magic the Gathening card search",
    page_icon="👋",
)


st.warning("This is a work in progress, please don't share the link yet.")
st.stop()

st.info(
    "Card info comes from the [Scryfall API](https://scryfall.com/docs/api). Thank you so much for all the data !"
)

st.title("Magic the Gathering cards")

search_text = st.text_input("Search", "Black Lotus")

with st.expander("Advanced search"):
    with st.form("Advanced search", border=False):
        set_list = all_sets()
        selected_sets = st.multiselect("Set", set_list)

        _, col = st.columns([4, 1])
        with col:
            submitted = st.form_submit_button(
                "Submit", type="primary", use_container_width=True
            )

if (
    "cards" not in st.session_state
    or "current_search" not in st.session_state
    or "cursor" not in st.session_state
):
    st.session_state["current_search"] = None
    st.session_state["cards"] = None
    st.session_state["cursor"] = None


if not search_text:
    st.stop()


if search_text != st.session_state["current_search"] or submitted:
    results = search_cards(search_text, None, selected_sets)
    st.session_state["current_search"] = search_text
    st.session_state["cards"] = results["cards"]
    st.session_state["cursor"] = results["cursor"]
else:
    results = search_cards(search_text, st.session_state["cursor"], selected_sets)
    st.session_state["cards"].extend(results["cards"])
    st.session_state["cursor"] = results["cursor"]

if not st.session_state["cards"]:
    if search_text:
        st.write("No cards found")
    else:
        st.write("Please search for a card")
    st.stop()


width = 3
cols = st.columns(width)
for i, oracle_card in enumerate(st.session_state["cards"]):
    col = cols[i % width]
    with col:
        st.html(
            f'<div style="text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">{oracle_card["name"]}</div>',
        )
        if oracle_card.get("thumbnail"):
            st.image(oracle_card["thumbnail"], use_container_width=True)
        elif oracle_card.get("faces_thumbnails"):
            thumbnail = oracle_card["faces_thumbnails"][0]
            st.image(thumbnail, use_container_width=True)
        else:
            st.image("./utils/Magic no image.png", use_container_width=True)


if st.session_state["cursor"]:
    _, col, _ = st.columns([2, 1, 2])
    with col:
        st.button("Load more")
