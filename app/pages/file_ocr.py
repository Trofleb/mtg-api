import streamlit as st
from requests import get

st.set_page_config(
    page_title="Magic the Gathening cards",
    page_icon="👋",
)


file = st.file_uploader("Upload a file to OCR", type=["png", "jpg", "jpeg", "pdf"])

if not file:
    st.stop()
    st.info("Please upload a file to OCR.")


def get_ocr(file):
    response = get("http://api:8000/ocr", files={"file": file})
    return response.json()["text"]


text = get_ocr(file) if file else None

st.markdown(text)
