import streamlit as st
import pandas as pd
from backend import customChatGPT


st.set_page_config(layout="wide")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# # Initialize chat history
if "messages" not in st.session_state:
     st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Benutzereingabe abfragen
user_input = st.text_input("You:", "")

# Benutzerfrage verarbeiten und Antwort erhalten
if st.button("Send"):
    if user_input.strip() != "":
        st.session_state.messages.append({"role": "user", "content": user_input})
        reply = customChatGPT(st.session_state.messages)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.text_area("Chatbot:", value='\n'.join([f"{message['role'].capitalize()}: {message['content']}" for message in st.session_state.messages]), height=300, key="chat_output", max_chars=None, on_change=None, args=None, kwargs=None)

    else:
        st.warning("Please insert a question.")

# # Chat-Historie anzeigen
# if st.checkbox("Viewing chat history"):
#     for message in st.session_state.messages:
#         role = message["role"]
#         content = message["content"]
#         st.text(f"{role.capitalize()}: {content}")

with st.sidebar:
    download = st.download_button("Download pdf", "Good Job!")
    textsize = st.slider("Text size", 1, 10, 2)