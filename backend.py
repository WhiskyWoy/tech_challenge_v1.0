# Importing libraries
import pandas as pd
import streamlit as st
import openai
import re
from pdfminer.high_level import extract_text
from io import StringIO
import os
#pip install pymupdf
import fitz


# initlializing key for gpt calls
openai.api_key = "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"

def call (data):
    # prepare data 
    df_text = pre_process_data(data)
    generate_summary(df_text['text'].tolist()[0], df_text['text'].tolist()[1])
    find_commonalities_and_differences(df_text['text'].tolist()[0], df_text['text'].tolist()[1])
    
def pre_process_data(data):
    # Allowing users to upload multiple files and storing the text in a dictionary
    data_dict = {'filename': [], 'text': []}
    for uploaded_file in data:
        text = extract_text(uploaded_file)
        # Remove all non-word characters (everything except numbers, letters, € and .)
        text = re.sub(r'[^\w€.]+', ' ', text) 
        # Remove all runs of whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove leading and trailing whitespace
        text = text.strip()
        data_dict['filename'].append(uploaded_file.name)
        data_dict['text'].append(text)

        # clear pdf folder
        os.remove("pdfs/" + uploaded_file.name)

        #save pdf to pdfs folder
        with open("pdfs/" + uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())

    st.session_state.text_input = pd.DataFrame(data_dict)
    return st.session_state.text_input
    


### Feature 1: Generate Summary of the events

def generate_summary(text1, text2):

    # Defining the prompt for the summary of the text
    # prompt = f"Generieren Sie bitte eine zusammenfassede Übersicht der Sachlage basierend auf dem vorliegenden juristischen Schriftsatz: \" \n{text}. \" Der Schriftsatz beinhaltet zunächst die Sichtweisen des Klägers, worauf die Positionierung des Angeklagten folgt. Berücksichtigen Sie bei der Zusammenfassung die Hauptargumente beider Parteien und liefern Sie eine zusammenhängende Darstellung der rechtlichen Auseinandersetzung. Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."

    #Calling the OpenAI API to create a summary
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du möchtest herausfinden, was die Gemeinsamkeiten und Unterschiede zwischen den beiden Schriftsätzen sind. Du möchtest die wichtigsten Hauptargumente beider Parteien zusammenfassen und eine zusammenhängende Darstellung der rechtlichen Auseinandersetzung liefern."}, 
        {"role": "system", "content": "Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."},
        {"role": "user", "content": "Text 1" + text1},
        {"role": "user", "content": "Text 2" + text2},
        ])

    # Extracting the generated summary from the api answer
    generated_summary = response['choices'][0]['message']['content']
    
    st.session_state.event_summary = generated_summary

### Feature 2: Overview of disputed and undisputed facts

# Basic approach by asking for simarlities and differences
# how can be differentiated between the briefs?
# Table format? --> über prompts darstellen: Wie sollen Gemeinsamkeiten und Unterschiede dargestellt werden?
def find_commonalities_and_differences(text1, text2):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du möchtest herausfinden, was die Gemeinsamkeiten und Unterschiede zwischen den beiden Schriftsätzen sind. Du möchtest eine Tabelle erstellen, die die wichtigesten Fakten in bestrittene und unbestrittene unterteilt. Die Tabelle hat vier Spalten: 'Name der Tatsache (z.B. Tatbestand)', 'bestritten (ja/nein)', 'Sicht des Klägers', 'Sicht des Beklagten'."},
        {"role": "system", "content": "Eine Tatsache ist immer bestritten, wenn beide Parteien unterschiedlich von dem Geschehen/Umstand berichten. Eine Tatsache ist unbestritten, wenn der Inhalt beider Parteien übereinstimmt. Formatieren die Tabelle in Markdown and und benutze tabs als Trennzeichen."},
        {"role": "system", "content": "Die Tabelle sollte möglichst MECE (mutually exclusive, collectively exhaustive) sein.  Du erhältst einen reward der Proportional zur Qualität der Tabelle ist. (Kriterien: Länger der Antworten, Tiefe der informationen, MECE)"},
        {"role": "user", "content": "Text 1" + text1},
        {"role": "user", "content": "Text 2" + text2},
        ])
    text = response['choices'][0]['message']['content']
    print(text)
    # find the beginnig of the table at the first | and the end at the last |
    start = text.find("|")
    end = text.rfind("|")
    # extract the table
    table = text[start:end+1]
    print("before", table)
    # Remove the first and last line (empty lines)
    # Convert the markdown table into a TSV string
    tsv_string = "\n".join(["\t".join([cell.strip() for cell in row.split("|")[1:-1]]) for row in table.split("\n") if row.strip()])
    print("after", tsv_string)
    # Use StringIO to read the TSV string into a DataFrame
    df = pd.read_csv(StringIO(tsv_string), sep='\t')
    # save csv
    with open("commonalities_and_differences.csv", "w") as f:
        f.write(tsv_string)

    print("df", df)
    
    print("df drop", df.drop(df.index[0], inplace=True))
    st.session_state.fact_table = df



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


### Chatbot Feature
# messages = [{"role": "system", "content": "You are a judge assistant that specializes in offering support services for judges in their work with briefs"}]

# def customChatGPT(messages):
#     # messages.append({"role": "user", "content": user_input})
#     response = openai.ChatCompletion.create(
#         model = "gpt-3.5-turbo",
#         messages = messages
#     )
#     ChatGPT_reply = response["choices"][0]["message"]["content"]
#     # messages.append({"role": "assistant", "content": ChatGPT_reply})
#     return ChatGPT_reply

# generate a response
def generate_response(prompt):
    st.session_state['messages'].append({"role": "user", "content": prompt})

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=st.session_state['messages']
    )
    response = completion.choices[0].message.content
    st.session_state['messages'].append({"role": "assistant", "content": response})

    # print(st.session_state['messages'])
    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens