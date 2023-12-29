# Importing libraries
import pandas as pd
import time
import streamlit as st
import openai

# initlializing key for gpt calls
openai.api_key = "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"

### Feature 1: Generate Summary of the events 

def generate_summary(data_dict):
    # Converting the dictionary in a pandas dataframe
    df = pd.DataFrame.from_dict(data_dict)

    # Create the text for summary
    text_to_summarize = " ".join(df['text'].tolist())

    # Defining the prompt for the summary of the text
    prompt = f"Generieren Sie bitte eine zusammenfassede Übersicht der Sachlage basierend auf dem vorliegenden 
    juristischen Schriftsatz \n{text_to_summarize}. Der Schriftsatz beinhaltet die Sichtweise des Klägers und des 
    Angeklagten. Berücksichtigen Sie bei der Zusammenfassung die Hauptargumente beider Parteien und liefern Sie eine 
    zusammenhängende Darstellung der rechtlichen Auseinandersetzung. Bitte fassen Sie den Inhalt der Schriftsätze 
    in einer prägnanten, verständlichen Form zusammen."

    # Calling the OpenAI API to create a summary
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=prompt,
      max_tokens=150  # can be adjusted
    )

    # Extracting the generated summary from the api answer 
    generated_summary = response.choices[0].text.strip()

    return generated_summary

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

