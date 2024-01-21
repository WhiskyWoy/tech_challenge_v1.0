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
import ast
from fpdf import FPDF
import matplotlib.pyplot as plt
from pandas.plotting import table
import textwrap
import PyPDF2
import time


def set_api_key():
    if st.session_state.gpt_4:
        openai.api_key = st.secrets["OPENAI_GPT4_API_KEY"]
        st.session_state.model = "gpt-4-1106-preview"
    else:
        st.session_state.model = "gpt-3.5-turbo"
        openai.api_key = st.secrets["OPENAI_GPT3_API_KEY"]


def call(data):
    set_api_key()
    pre_process_data(data)

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
        if os.path.exists("pdfs/" + uploaded_file.name):
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
        model=st.session_state.model,
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
        model=st.session_state.model,
        messages=[
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du möchtest herausfinden, was die Gemeinsamkeiten und Unterschiede zwischen den beiden Schriftsätzen sind. Du möchtest eine Tabelle erstellen, die die wichtigesten Fakten in bestrittene und unbestrittene unterteilt. Die Tabelle hat vier Spalten: 'Name der Tatsache (z.B. Tatbestand)', 'bestritten (ja/nein)', 'Sicht des Klägers', 'Sicht des Beklagten'."},
        {"role": "system", "content": "Eine Tatsache ist immer bestritten, wenn beide Parteien unterschiedlich von dem Geschehen/Umstand berichten. Eine Tatsache ist unbestritten, wenn der Inhalt beider Parteien übereinstimmt. Formatieren die Tabelle in Markdown and und benutze tabs als Trennzeichen."},
        {"role": "system", "content": "Die Tabelle sollte möglichst vollständig sein.  Du erhältst einen reward der Proportional zur Qualität der Tabelle ist. (Kriterien: Länger der Antworten, Tiefe der informationen, MECE). Sei bitte ausführlich und genau."},
        {"role": "user", "content": "Text 1" + st.session_state.text1},
        {"role": "user", "content": "Text 2" + st.session_state.text2},
        ])
    text = response['choices'][0]['message']['content']
    # find the beginnig of the table at the first | and the end at the last |
    start = text.find("|")
    end = text.rfind("|")
    # extract the table
    table = text[start:end+1]
    # Convert the markdown table into a TSV string
    tsv_string = "\n".join(["\t".join([cell.strip() for cell in row.split("|")[1:-1]]) for row in table.split("\n") if row.strip()])
    # Use StringIO to read the TSV string into a DataFrame
    df = pd.read_csv(StringIO(tsv_string), sep='\t')

    st.session_state.fact_table = df

    return df


# read out pdfs
def read_pdf(pdf_path):
    pdf = fitz.open(pdf_path)
    full_text = ""
    for page_number in range(pdf.page_count):
        page = pdf[page_number]
        text = page.get_text()
        full_text += text

    pdf.close()

    return full_text

# get the original text from full text
def get_source(full_text, list_facts, context):

    if context == "plaintiff":
        role = "Du erhältst einen originalen Schriftsatz von einem Kläger sowie eine Liste mit Stichpunkten, welche einen Fakt innerhalb des Dokuments beschreiben. Du möchtest die Textstellen im originalen Dokument suchen, welche von dem jeweiligen Stichpunkt beschrieben wird."
    else:
        role = "Du erhältst einen originalen Schriftsatz von einem Beklagten sowie eine Liste mit Stichpunkten, welche einen Fakt innerhalb des Dokuments beschreiben. Du möchtest die Textstellen im originalen Dokument suchen, welche von dem jeweiligen Stichpunkt beschrieben wird."

    # find the original plaintiff text
    response = openai.ChatCompletion.create(
        model=st.session_state.model,
        messages=[
            {"role": "system",
                "content": "Du bist eine Richterassistentin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
            {"role": "system",
                "content": role},
            {"role": "system",
                "content": "Gib bitte die originale Textstellen in einer einzigen Liste zurück und zwar in der gleichen Reihenfolge wie die Stichpunkte. Bitte nimm keine ganzen Absätze, sondern nur kurze originale Textstücke. Beispiel: ['Originaltext1', 'Originaltext2', ...]."},
            {"role": "system",
                "content": "Es ist sehr wichtig, dass du die Formatierung ['Originaltext1', 'Originaltext2', ...] einhältst"},
            {"role": "system",
                "content": "Originaltext:"},
            {"role": "user",
                "content": full_text},
            {"role": "system",
                "content": "Liste mit Fakten:"},
            {"role": "user",
                "content": list_facts},
        ])
    answer = response['choices'][0]['message']['content']

    print(context, "Chatbot Antwort")
    print(answer)

    # Find the position of '[' and ']'
    start_index = answer.find('[')
    end_index = answer.find(']')

    # Extract the substring containing the list representation
    list_representation = answer[start_index:end_index + 1]

    try:
        list_answer = ast.literal_eval(list_representation)
    except (ValueError, SyntaxError) as e:
        print(f"Error: {e}")

    return list_answer


# use this function for highlighting. Takes the PDF Path, the list with original texts and the context ("plaintiff" or "defendant") as input
def highlight(path, list_source, context):

    # set list of colors for highlighting
    highlight_colors = [
        (0.8, 0.95, 0.8),  # Light Mint Green
        (0.95, 0.8, 0.8),  # Light Peach
        (0.8, 0.8, 0.95),  # Light Sky Blue
        (0.9, 0.95, 0.8),  # Pale Lime
        (0.8, 0.9, 0.95),  # Light Azure
        (0.95, 0.8, 0.95),  # Light Lavender
        (0.9, 0.8, 0.95),  # Light Mauve
        (0.95, 0.95, 0.8),  # Light Lemon
        (0.8, 0.95, 0.95),  # Light Cyan
        (0.95, 0.8, 0.8),  # Light Coral
        (0.8, 0.8, 0.8),  # Light Gray
        (0.95, 0.95, 0.95),  # Light Silver
        (0.9, 0.9, 0.8),  # Pale Yellow
        (0.8, 0.9, 0.9),  # Light Turquoise
        (0.9, 0.8, 0.9),  # Light Orchid
        (0.8, 0.9, 0.8),  # Light Sage
        (0.9, 0.8, 0.8),  # Light Salmon
        (0.8, 0.8, 0.9),  # Light Periwinkle
        (0.9, 0.9, 0.9),  # Light Ivory
        (0.95, 0.7, 0.7),  # Light Salmon (variation)
    ]

    pdfIn_pdf = fitz.open(path)

    for page in pdfIn_pdf:

        # find coordinates of text that should be highlighted
        try:
            text_instances = [page.search_for(text) for text in list_source]
        except:
            st.error("Es gab einen Fehler beim Hervorheben der Textstellen. Der Vergleich ist fehlerhaft oder konnte nicht erstellt werden. Versuchen Sie es erneut oder nutzen Sie GPT-4.")

        i = 0
        # iterate through each instance for highlighting
        for inst in text_instances:
            annot = page.add_highlight_annot(inst)
            annot.set_colors(stroke=highlight_colors[i])
            annot.update()
            i += 1

    # Save the PDF Output
    if context == "plaintiff":
        pdfIn_pdf.save("pdfs/brief_plaintiff_highlighted.pdf")
        print("PDF Plaintiff stored")
    else:
        pdfIn_pdf.save("pdfs/brief_defendant_highlighted.pdf")
        print("PDF Defendant stored")


### Feature 3: Compare documents by highlighting the briefs
def compare_pdfs():

    # get table of commonalities and differences
    df = st.session_state.fact_table

    # set paths
    path_plaintiff = "pdfs/brief_plaintiff.pdf"
    path_defendant = "pdfs/brief_defendant.pdf"

    # get full text from briefs
    full_text_plaintiff = read_pdf(path_plaintiff)
    full_text_defendant = read_pdf(path_defendant)

    # create a list of facts from the commonalities and differences table
    list_facts_plaintiff = df.iloc[1:, 2].tolist()
    list_facts_defendant = df.iloc[1:, 3].tolist()

    # create a string that can be read by the LLM
    string_facts_plaintiff = ''.join(map(str, list_facts_plaintiff))
    string_facts_defendant = ''.join(map(str, list_facts_defendant))

    # get list of original texts from LLM
    list_plaintiff = get_source(full_text_plaintiff, string_facts_plaintiff, "plaintiff")
    list_defendant = get_source(full_text_defendant, string_facts_defendant, "defendant")

    # highlight and save documents
    highlight(path_plaintiff, list_plaintiff, "plaintiff")
    highlight(path_defendant, list_defendant, "defendant")


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
    def add_line_breaks(text):
        return '\n'.join(textwrap.wrap(text, width=50))



    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSansCondensed.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)
    pdf.set_font('DejaVu', 'B', 14)

    pdf.cell(200, 10, txt="Zusammenfassung", ln=1, align="C")
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    pdf.multi_cell(175, 5, txt=text, align="L")

    try:
        df = df.applymap(add_line_breaks)
        fig, ax = plt.subplots(figsize=(24, 12)) # set size frame
        ax.xaxis.set_visible(False)  # hide the x axis
        ax.yaxis.set_visible(False)  # hide the y axis
        ax.set_frame_on(False)  # no visible frame
        # add title
        ax.set_title('Tabelle der wichtigsten Fakten', fontsize=24, color='black', position=(0.5, 1.0))
        tabla = table(ax, df, loc='center', cellLoc='center')  # where df is your data frame
        tabla.auto_set_font_size(True) # Activate set fontsize manually
        #tabla.set_fontsize(10) # if ++fontsize is necessary ++colWidths
        tabla.scale(1.2, 5.5) # Table size
        plt.savefig('pdfs/mytable.png')
        #new page
        pdf.add_page(orientation='L')
        pdf.image('pdfs/mytable.png', x = 0, y = 0, w = 300, h = 200)
    except:
        st.error("Die Tabelle hatte ein falsches Format, sie wird nicht in die PDF übernommen.")

    pdf.output("pdfs/output.pdf")

    merger = PyPDF2.PdfMerger()
    # List of PDF files to merge
    pdf_files = ["pdfs/output.pdf", "pdfs/brief_plaintiff_highlighted.pdf", "pdfs/brief_defendant_highlighted.pdf"]

    # Loop through the PDF files and add each one to the merger
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as fileobj:
            merger.append(fileobj)

    # Write the merged PDF to a new file
    with open("pdfs/merged.pdf", "wb") as outfile:
        merger.write(outfile)

    #read pdf as bytes
    with open("pdfs/merged.pdf", "rb") as f:
        st.session_state.pdf = f.read()
        
