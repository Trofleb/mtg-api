import streamlit as st

st.set_page_config(
    page_title="Magic the Gathening cards",
    page_icon="👋",
)

st.info(
    "Card info comes from the [Scryfall API](https://scryfall.com/docs/api). Thank you so much for all the data !"
)

# @st.cache_data
# def read_file(file_path: str) -> DataFrame:
#     with open(file_path) as file:
#         return DataFrame(json.loads(file.read()))


# mtg_db = read_file("/data/all-cards-20250119102215.json")

# st.dataframe(mtg_db)
