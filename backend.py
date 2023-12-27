import pandas as pd
import time
import streamlit as st
import openai

st.title("Jasmin - Your Digital Judge Assistant")

openai.api_key = "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"

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
prompt = st.chat_input("How can I help you?")
if prompt:
    #Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("Jasmin"):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model = st.session_state["openai_model"],
            messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream = True,
        ):
            full_response += response.choices[0].delta.get("content", "")
            message_placeholder.markdown(full_response + "| ")
        message_placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "Jasmin", "content": full_response})        

### Aus youtube Tutorial
# messages = []
# system_msg = input("What type of chatbot would you like to create?\n")
# messages.append({"role": "system", "content": system_msg})

# print("Your new assistant is ready")
# while input != "quit()":
#     message = input()
#     messages.append({"role": "user", "content": message})
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=messages)
#     reply = response["choices"] [0] ["message"] ["content"]
#     messages.append({"role": "assistant", "content": reply})
#     print ("\n" + reply + "\n")

# von Zeno - wichtig?
# def call (data):
#     df = pd.DataFrame(data)
#     #sleep for 5 seconds
#     time.sleep(5)
#     st.session_state.df = df

