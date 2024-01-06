import streamlit as st
import pandas as pd

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.set_page_config(layout="wide")

# Benutzereingabe abfragen
user_input = st.text_input("You:", "")

# Benutzerfrage verarbeiten und Antwort erhalten
if st.button("Send"):
    if user_input.strip() != "":
        reply = st.session_state.customChatGPT(user_input)
        st.text_area("Chatbot:", value=reply, height=100, key="chat_output")
    else:
        st.warning("Please insert a question.")

# Chat-Historie anzeigen
if st.checkbox("Viewing chat history"):
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        st.text(f"{role.capitalize()}: {content}")

with st.sidebar:
    download = st.download_button("Download pdf", "Good Job!")
    textsize = st.slider("Text size", 1, 10, 2)