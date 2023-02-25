import requests
import streamlit as st

api_url = "http://api:8000/expand_sentence"

st.title("Sentence Expander")
sentence = st.text_input("Enter a sentence:")

if sentence:
    response = requests.get(api_url, params={"sentence": sentence})

    if response.status_code == 200:
        expanded_sentence = response.json()["expanded_sentence"]

        st.write("Expanded sentence:")
        st.write(expanded_sentence)
    else:
        st.write("Error: Failed to expand sentence. Please try again.")
