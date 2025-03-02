import requests
import streamlit as st

st.title("Question sur les règles de DnD!")

st.write(
    "Ceci est une simple application web pour prédire la réponse à une question basée sur les règles de Donjons et Dragons."
)

question = st.text_input("Posez votre question ici:")

if not question:
    st.stop()


@st.cache_resource
def stream_answer(question):
    api_url = f"http://api:8000/dnd/ruling/{question}"
    response = requests.get(api_url, stream=True)
    yield from (chunk.decode() for chunk in response.iter_content(chunk_size=1024))


st.write("Voici la réponse à votre question:")
st.write_stream(stream_answer(question))
