import streamlit as st
from requests import post
from streamlit.runtime.uploaded_file_manager import UploadedFile

st.set_page_config(
    page_title="Magic the Gathening cards",
    page_icon="👋",
)


file = st.file_uploader("Upload a file to OCR", type=["png", "jpg", "jpeg", "pdf"])

if not file:
    st.stop()
    st.info("Please upload a file to OCR.")


def get_ocr(file: UploadedFile):
    response = post(
        "http://api:8000/ocr", files={"file": (file.name, file.read(), file.type)}
    )
    if response.status_code != 200:
        st.error(
            f"Failed to OCR file: {response.reason}(status code: {response.status_code}): {response.text}"
        )
        return "Error"
    return response.json()["text"]


text = get_ocr(file) if file else None

st.markdown(text)
