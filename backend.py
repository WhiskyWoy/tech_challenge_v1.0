import pandas as pd
import time
import streamlit as st
import openai

### simple chat bot

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

### Feature 1: Generate Summary of the events (https://medium.com/@AIandInsights/text-summarization-8c47f8c115a8#:~:text=Here%E2%80%99s%20an%20example%20function%20that%20uses%20OpenAI%E2%80%99s%20GPT-3,text%3A%20def%20generate_summary%20%28text%29%3A%20input_chunks%20%3D%20split_text%20%28text%29)

# Preprocessing data into smaller chunks to ensure correct format
def split_text(text):
    max_chunk_size = 2048
    chunks = []
    current_chunk = ""
    for sentence in text.split("."):
        if len(current_chunk) + len(sentence) < max_chunk_size:
            current_chunk += sentence + "."
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + "."
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Generating a summary for every extracted chunk
def generate_summary(text):
    input_chunks = split_text(text)
    output_chunks = []
    for chunk in input_chunks:
        response = openai.Completion.create(
            engine="davinci",
            prompt=(f"Please summarize the following text:\n{chunk}\n\nSummary:"),
            temperature=0.5,
            max_tokens=1024,
            n = 1,
            stop=None
        )
        summary = response.choices[0].text.strip()
        output_chunks.append(summary)
    return " ".join(output_chunks)

# Slighly different approach
def generate_summary(input):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  
            prompt=input
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

### Feature 2: Overview of disputed and undisputed facts

# Basic approach by asking for simarlities and differences
def find_commonalities_and_differences(text1, text2):
    try:
        prompt = f"Find similarities and differences between the following two documents:\n\nText 1: {text1}\n\nText 2: {text2}\n\n:"
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {str(e)}"

### Feature 3: Compare documents by highlighting the briefs


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

def call (data):
    df = pd.DataFrame(data)
    #sleep for 5 seconds
    time.sleep(5)
    st.session_state.df = df

