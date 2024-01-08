# Importing libraries
import pandas as pd
import streamlit as st
import openai
import re
from pdfminer.high_level import extract_text
from io import StringIO
import io
import os
#pip install pymupdf
import fitz
from fpdf import FPDF
import lorem
import matplotlib.pyplot as plt
from pandas.plotting import table
import textwrap


# initlializing key for gpt calls
openai.api_key = "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"

def call (data):
    # prepare data 
    pre_process_data(data)
    #generate_summary()
    find_commonalities_and_differences()
    create_pdf()
    
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

    st.session_state.text_df = pd.DataFrame(data_dict)
    st.session_state.text1 = st.session_state.text_df['text'].tolist()[0]
    st.session_state.text2 = st.session_state.text_df['text'].tolist()[1]
    


### Feature 1: Generate Summary of the events

def generate_summary():

    #Calling the OpenAI API to create a summary
    response = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du möchtest herausfinden, was die Gemeinsamkeiten und Unterschiede zwischen den beiden Schriftsätzen sind. Du möchtest die wichtigsten Hauptargumente beider Parteien zusammenfassen und eine zusammenhängende Darstellung der rechtlichen Auseinandersetzung liefern."}, 
        {"role": "system", "content": "Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."},
        {"role": "user", "content": "Text 1" + st.session_state.text1},
        {"role": "user", "content": "Text 2" + st.session_state.text2},
        ])

    # Extracting the generated summary from the api answer
    generated_summary = response['choices'][0]['message']['content']
    
    st.session_state.event_summary = generated_summary

### Feature 2: Overview of disputed and undisputed facts

# Basic approach by asking for simarlities and differences
# how can be differentiated between the briefs?
# Table format? --> über prompts darstellen: Wie sollen Gemeinsamkeiten und Unterschiede dargestellt werden?
def find_commonalities_and_differences():
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du möchtest herausfinden, was die Gemeinsamkeiten und Unterschiede zwischen den beiden Schriftsätzen sind. Du möchtest eine Tabelle erstellen, die die wichtigesten Fakten in bestrittene und unbestrittene unterteilt. Die Tabelle hat vier Spalten: 'Name der Tatsache (z.B. Tatbestand)', 'bestritten (ja/nein)', 'Sicht des Klägers', 'Sicht des Beklagten'."},
        {"role": "system", "content": "Eine Tatsache ist immer bestritten, wenn beide Parteien unterschiedlich von dem Geschehen/Umstand berichten. Eine Tatsache ist unbestritten, wenn der Inhalt beider Parteien übereinstimmt. Formatieren die Tabelle in Markdown and und benutze tabs als Trennzeichen."},
        {"role": "system", "content": "Die Tabelle sollte möglichst vollständig sein.  Du erhältst einen reward der Proportional zur Qualität der Tabelle ist. (Kriterien: Länger der Antworten, Tiefe der informationen, MECE). Sei bitte ausführlich und genau."},
        {"role": "user", "content": "Text 1" + st.session_state.text1},
        {"role": "user", "content": "Text 2" + st.session_state.text2},
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

def create_pdf():
    text = st.session_state.event_summary
    df = st.session_state.fact_table 
    #df = pd.read_excel("fact_table.xlsx")
    #use first column as index and drop it
    #df.set_index(df.columns[0], inplace=True)
    #text = lorem.text()

    #pdf.set_font("Arial", size=12)
    def add_line_breaks(text):
        return '\n'.join(textwrap.wrap(text, width=50))

    # Apply the function to each cell in the DataFrame
    df = df.applymap(add_line_breaks)

    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', 'B', 16)

    pdf.cell(200, 10, txt="Event Summary", ln=1, align="C")
    pdf.set_font('DejaVu', '', 12)
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    #pdf.multi_cell(200, 10, txt=text.tolist()[0], ln=1, align="L")
    pdf.multi_cell(150, 10, txt=text, align="L")
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(200, 10, txt="Table of Facts", ln=1, align="C")
    pdf.set_font('DejaVu', '', 14)
    pdf.cell(200, 10, txt=" ", ln=1, align="C")

    fig, ax = plt.subplots(figsize=(20, 10)) # set size frame
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_frame_on(False)  # no visible frame
    tabla = table(ax, df, loc='center', cellLoc='center')  # where df is your data frame
    tabla.auto_set_font_size(True) # Activate set fontsize manually
    #tabla.set_fontsize(10) # if ++fontsize is necessary ++colWidths
    tabla.scale(1.2, 4) # Table size
    plt.savefig('mytable.png')

    #new page
    pdf.add_page(orientation='L')

    pdf.image('mytable.png', x = 0, y = 0, w = 300, h = 200)
  
    #pdf.output("output.pdf")

    
    # Save the PDF to a bytes object
    #pdf_out = io.BytesIO()
    #pdf.output(dest='S')
    #pdf_data = pdf_out.getvalue()
    st.session_state.pdf = pdf.output(dest='S').encode('latin-1')

