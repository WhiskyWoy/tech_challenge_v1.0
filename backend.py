# Importing libraries
import pandas as pd
import time
import streamlit as st
import openai

# initlializing key for gpt calls
openai.api_key = "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"

### Feature 1: Generate Summary of the events (https://medium.com/@AIandInsights/text-summarization-8c47f8c115a8#:~:text=Here%E2%80%99s%20an%20example%20function%20that%20uses%20OpenAI%E2%80%99s%20GPT-3,text%3A%20def%20generate_summary%20%28text%29%3A%20input_chunks%20%3D%20split_text%20%28text%29)

# Preprocessing data into smaller chunks to ensure correct format
# Markdown text
# summary geht über Inhalte beider texte
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
# how can be differentiated between the briefs?
# Table format? --> über prompts darstellen: Wie sollen Gemeinsamkeiten und Unterschiede dargestellt werden?
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
# text der reingeht, geht auch wieder raus
# markierung der gemeinsamkeiten und unterschiede
# welche Möglichkeiten gibt es, um pdf zu markieren?
# Text ausgeben, der mit Markdown formatiert ist

def call (data):
    df = pd.DataFrame(data)
    #sleep for 5 seconds
    time.sleep(5)
    st.session_state.df = df

