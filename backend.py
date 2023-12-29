# Importing libraries
import pandas as pd
import time
import streamlit as st
import openai
import re
import fitz


# initlializing key for gpt calls
openai.api_key = "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"

### Feature 1: Generate Summary of the events

def generate_summary(df):

    # Create the text for summary
    text = " ".join(df['text'].tolist())
    # Remove all non-word characters (everything except numbers and letters)
    text = re.sub(r'\W+', ' ', text)

    # Remove all runs of whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove leading and trailing whitespace
    text = text.strip()

    # Defining the prompt for the summary of the text
    prompt = f"Generieren Sie bitte eine zusammenfassede Übersicht der Sachlage basierend auf dem vorliegenden juristischen Schriftsatz: \" \n{text}. \" Der Schriftsatz beinhaltet jeweils die Sichtweisen des Klägers und des Angeklagten. Berücksichtigen Sie bei der Zusammenfassung die Hauptargumente beider Parteien und liefern Sie eine zusammenhängende Darstellung der rechtlichen Auseinandersetzung. Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."

    #Calling the OpenAI API to create a summary
    response = openai.Completion.create(
        engine = "text-davinci-003",
        prompt=prompt,
        max_tokens=500 # can be adjusted
    )

    # Extracting the generated summary from the api answer
    generated_summary = response.choices[0].text.strip()

    #create a new df
    df2= pd.DataFrame({'text': [text], 'summary': [generated_summary]})

    st.session_state.event_summary = df2

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
# input: text to be highlighted (as list), plaintiff/ defendant as context
def highlight_pdf(highlighted_text, context):

    if context == "plaintiff":
        pdf = "brief_plaintiff.pdf"
    else:
        pdf = "brief_defendant.pdf"

    pdfIn = fitz.open(pdf)

    # highlighted_text = ["Das Motorrad war vor der Restaurierung nicht verkehrstüchtig, trotz seines Alters waren "
    #                    "offensichtlich seit längerem keine Teile erneuert worden.",
    #                    "Der Beklagte erfuhr erstmals bei einem Gespräch mit Herrn Grünbaum am 5. Juni 2021, dass "
    #                    "dieser das Motorrad von einer unbekannten Person erworben hatte und dass dieses zuvor dem
    #                    Sohn des Klägers gestohlen worden war."]

    for page in pdfIn:

        # find coordinates of text that should be highlighted
        text_instances = [page.search_for(text) for text in highlighted_text]

        # set list of colors for highlighting
        highlight_colors = [
            (1, 0, 0),  # Red
            (0, 1, 0),  # Green
            (0, 0, 1),  # Blue
            (1, 1, 0),  # Yellow
            (1, 0, 1),  # Magenta
            (0, 1, 1),  # Cyan
            (0.5, 0, 0),  # Maroon
            (0, 0.5, 0),  # Olive
            (0, 0, 0.5),  # Navy
            (0.5, 0.5, 0),  # Olive Green
            (0.5, 0, 0.5),  # Purple
            (0, 0.5, 0.5),  # Teal
            (0.8, 0.4, 0),  # Dark Orange
            (0.8, 0, 0.4),  # Dark Reddish Pink
            (0.4, 0.8, 0),  # Dark Lime Green
            (0, 0.8, 0.4),  # Dark Mint Green
            (0.4, 0, 0.8),  # Dark Indigo
            (0, 0.4, 0.8),  # Dark Sky Blue
            (0.7, 0.7, 0.7),  # Light Gray
            (0.4, 0.4, 0.4),  # Medium Gray
            (0.9, 0.9, 0),  # Pale Yellow
            (0, 0.9, 0.9),  # Light Cyan
            (0.9, 0, 0.9),  # Pink
            (0.7, 0.7, 0.9),  # Light Purple
            (0.9, 0.7, 0.7),  # Light Salmon
        ]
        # iterate through each instance for highlighting
        i = 0
        for inst in text_instances:
            annot = page.add_highlight_annot(inst)
            annot.set_colors(stroke=highlight_colors[i])
            annot.update()
            i += 1

    # Saving the PDF Output
    pdfIn.save("brief_" + context + "_highlighted.pdf")


def call (data):
    df = pd.DataFrame(data)
<<<<<<< HEAD
    #sleep for 5 seconds
    time.sleep(5)
    st.session_state.df = df
=======
    st.session_state.text_input = df
    generate_summary(df)

>>>>>>> origin/main
