import streamlit as st

st.set_page_config(
    page_title="MTG Deck list",
    page_icon="👋",
)

st.title("MTG Deck list")

deck_list = st.text_area("Deck list")
