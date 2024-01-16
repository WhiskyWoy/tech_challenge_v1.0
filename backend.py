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
import ast
from fpdf import FPDF
import lorem
import matplotlib.pyplot as plt
from pandas.plotting import table
import textwrap
import PyPDF2


# initlializing key for gpt calls
openai.api_key = "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"

def call (data):
    # prepare data 
    pre_process_data(data)
    #generate_summary()
    #df_table = find_commonalities_and_differences()
    df_table = pd.read_csv("commonalities_and_differences_save.csv", sep='\t')
    df_table.drop(df_table.index[0], inplace=True)
    st.session_state.fact_table = df_table
    # read event summary txt#
    with open("event_summary.txt", "r") as f:
        st.session_state.event_summary = f.read()
    highlight_pdf(df_table, True)
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

    # save as txt
    with open("event_summary.txt", "w") as f:
        f.write(generated_summary)

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

    return df


# read out pdfs (double work, should be removed in the end)
def read_pdf(pdf_path):
    pdf = fitz.open(pdf_path)

    full_text = ""

    for page_number in range(pdf.page_count):
        page = pdf[page_number]
        text = page.get_text()
        full_text += text

    pdf.close()

    return full_text


### Feature 3: Compare documents by highlighting the briefs
# input: text to be highlighted (as list), plaintiff/ defendant as context
def highlight_pdf(df, dryrun):

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

    if dryrun is True:

        # highlight plaintiff
        pdfIn_plaintiff = fitz.open("pdfs/brief_plaintiff.pdf")

        for page in pdfIn_plaintiff:

            list_plaintiff = ["Der Kläger hat das Motorrad am 8. März 1972 gekauft und erworben. Er ist Eigentü",
                              "mer des Motorrads.",
                              "Der Beklagte ist Besitzer des Fahrzeugs. Mit Schreiben vom 3. Juli 2021 wurde der Beklagte zur Herausgabe des Fahrzeugs aufgefordert.",
                              "n.a.",
                              "Wie der Beklagte vorprozessual mitgeteilt hat, wurde dieser Fuchsschwanz am 21. Mai 2021 beim Vorbeifahren durch den Radfahrer Matthias Hoster schuldhaft beschädigt.",
                              "Der Beklagte schuldet nach § 985 BGB Herausgabe des Motorrads. Zum Besitz ist er nicht berechtigt.",
                              "Da der Beklagte den Betrag von 70,- € aufgrund der Beschädigung des Fuchs",
                              "schwanzes erhalten hat, ist er zur Zahlung dieses Betrages an den Kläger verpflich",
                              "tet."]

            # find coordinates of text that should be highlighted
            text_instances = [page.search_for(text) for text in list_plaintiff]

            j = 0
            k = [0, 0, 1, 2, 3, 4, 5, 5, 5]
            # iterate through each instance for highlighting
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors(stroke=highlight_colors[k[j]])
                # annot.set_info(title=context[k])
                annot.update()
                j += 1

        # Saving the PDF Output
        pdfIn_plaintiff.save("pdfs/brief_plaintiff_highlighted.pdf")
        print("PDF Plaintiff stored")

        # highlight defendant
        pdfIn_defendant = fitz.open("pdfs/brief_defendant.pdf")

        for page in pdfIn_defendant:

            list_defendant = [
                "Der Beklagte ist Besitzer des Motorrads. Es wird jedoch ausdrücklich bestritten, dass der Kläger Eigentü",
                "mer ist.", "Von diesem erwarb der Beklagte das Motorrad mit dem angebundenen Fuchs",
                "schwanz am 10. April 2021 redlich für 600,- € zum Zwecke der Restaurierung. Auch die Zulassungsbescheinigung Teil II wurde ihm übergeben.",
                "Das Motorrad war vor der Restaurierung nicht verkehrstüchtig, trotz seines Alters waren offensichtlich seit längerem keine Teile erneuert worden. Auch der äußere Zu",
                "stand war reparaturbedürftig.", "n.a.",
                "Die Klage ist abzuweisen, weil der Kläger nicht Eigentümer des Motorrads ist.", "n.a."]

            # find coordinates of text that should be highlighted
            text_instances = [page.search_for(text) for text in list_defendant]

            j = 0
            k = [0, 0, 1, 1, 2, 2, 3, 4, 5]
            # iterate through each instance for highlighting
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors(stroke=highlight_colors[k[j]])
                # annot.set_info(title=context[k])
                annot.update()
                j += 1

        # Saving the PDF Output
        pdfIn_defendant.save("pdfs/brief_defendant_highlighted.pdf")
        print("PDF Defendant stored")

    else:
        # get text form (need to be sure to have the correct document)
        full_text_plaintiff = read_pdf("pdfs/brief_plaintiff.pdf")
        full_text_defendant = read_pdf("pdfs/brief_defendant.pdf")

        # list_contexts = df.iloc[1:, 0].tolist()
        list_facts_plaintiff = df.iloc[1:, 2].tolist()
        list_facts_defendant = df.iloc[1:, 3].tolist()

        string_facts_plaintiff = ''.join(map(str, list_facts_plaintiff))
        string_facts_defendant = ''.join(map(str, list_facts_defendant))

        # find the original plaintiff text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
                {"role": "system",
                 "content": "Du erhältst einen originalen Schriftsatz von einem Kläger sowie eine Liste mit Stichpunkten, welche einen Fakt innerhalb des Dokuments beschreiben. Du möchtest die Textstellen im originalen Dokument suchen, welche von dem jeweiligenn Stichpunkt beschrieben wird."},
                {"role": "system",
                 "content": "Gibt bitte dir originale Textstellen in einer einzigen Liste zurück und zwar in der gleichen Reihenfolge wie die Stichpunkte. Bitte nimm keine ganzen Absätze, sondern nur kurze originale Textstücke. Achte Beispiel: ['Originaltext1', 'Originaltext2', ...]."},
                {"role": "user", "content": full_text_plaintiff},
                {"role": "user", "content": string_facts_plaintiff},
            ])
        text_plaintiff = response['choices'][0]['message']['content']

        print("ChatGPT plaintiff")
        print(text_plaintiff)

        # Find the position of '[' and ']'
        start_index = text_plaintiff.find('[')
        end_index = text_plaintiff.find(']')

        # Extract the substring containing the list representation
        list_representation = text_plaintiff[start_index:end_index + 1]

        try:
            list_plaintiff = ast.literal_eval(list_representation)
        except (ValueError, SyntaxError) as e:
            print(f"Error: {e}")



        # find the original defendant text
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system",
                 "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
                {"role": "system",
                 "content": "Du erhältst einen originalen Schriftsatz von einem Kläger sowie eine Liste mit Stichpunkten, welche einen Fakt innerhalb des Dokuments beschreiben. Du möchtest die Textstellen im originalen Dokument suchen, welche von dem jeweiligenn Stichpunkt beschrieben wird."},
                {"role": "system",
                 "content": "Gibt bitte dir originale Textstellen in einer einzigen Liste zurück und zwar in der gleichen Reihenfolge wie die Stichpunkte. Bitte nimm keine ganzen Absätze, sondern nur kurze originale Textstücke. Beispiel: ['Originaltext1', 'Originaltext2', ...]."},
                {"role": "user", "content": full_text_defendant},
                {"role": "user", "content": string_facts_defendant},
            ])
        text_defendant = response['choices'][0]['message']['content']

        # Find the position of '[' and ']'
        start_index = text_defendant.find('[')
        end_index = text_defendant.find(']')

        # Extract the substring containing the list representation
        list_representation = text_defendant[start_index:end_index + 1]

        try:
            list_defendant = ast.literal_eval(list_representation)
        except (ValueError, SyntaxError) as e:
            print(f"Error: {e}")

        # highlight plaintiff
        pdfIn_plaintiff = fitz.open("pdfs/brief_plaintiff.pdf")

        for page in pdfIn_plaintiff:

            # find coordinates of text that should be highlighted
            text_instances = [page.search_for(text) for text in list_plaintiff]

            i = 0
            # iterate through each instance for highlighting
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors(stroke=highlight_colors[i])
                # annot.set_info(title=list_contexts[i])
                annot.update()
                i += 1

        # Saving the PDF Output
        pdfIn_plaintiff.save("pdfs/brief_plaintiff_highlighted.pdf")
        print("PDF Plaintiff stored")

        # highlight defendant
        pdfIn_defendant = fitz.open("pdfs/brief_defendant.pdf")

        for page in pdfIn_defendant:

            # find coordinates of text that should be highlighted
            text_instances = [page.search_for(text) for text in list_defendant]

            i = 0
            # iterate through each instance for highlighting
            for inst in text_instances:
                annot = page.add_highlight_annot(inst)
                annot.set_colors(stroke=highlight_colors[i])
                # annot.set_info(title=list_contexts[i])
                annot.update()
                i += 1

        # Saving the PDF Output
        pdfIn_defendant.save("pdfs/brief_defendant_highlighted.pdf")
        print("PDF Defendant stored")


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
    pdf.set_font('DejaVu', 'B', 14)

    pdf.cell(200, 10, txt="Zusammenfassung", ln=1, align="C")
    pdf.set_font('DejaVu', '', 10)
    pdf.cell(200, 10, txt=" ", ln=1, align="C")
    #pdf.multi_cell(200, 10, txt=text.tolist()[0], ln=1, align="L")
    pdf.multi_cell(175, 5, txt=text, align="L")
    #pdf.cell(200, 10, txt=" ", ln=1, align="C")
    #pdf.cell(200, 10, txt=" ", ln=1, align="C")
    #pdf.cell(200, 10, txt=" ", ln=1, align="C")
    #pdf.set_font('DejaVu', 'B', 14)
    #pdf.cell(200, 10, txt="Tabelle der wichtigsten Fakten", ln=1, align="C")
    #pdf.set_font('DejaVu', '', 14)
    #pdf.cell(200, 10, txt=" ", ln=1, align="C")

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
    plt.savefig('mytable.png')

    #new page
    pdf.add_page(orientation='L')

    

    pdf.image('mytable.png', x = 0, y = 0, w = 300, h = 200)

    pdf.output("output.pdf")

    merger = PyPDF2.PdfMerger()
    # List of PDF files to merge
    pdf_files = ["output.pdf", "pdfs/brief_plaintiff_highlighted.pdf", "pdfs/brief_defendant_highlighted.pdf"]

    # Loop through the PDF files and add each one to the merger
    for pdf_file in pdf_files:
        with open(pdf_file, "rb") as fileobj:
            merger.append(fileobj)

    # Write the merged PDF to a new file
    with open("merged.pdf", "wb") as outfile:
        merger.write(outfile)

    #read pdf as bytes
    with open("merged.pdf", "rb") as f:
        st.session_state.pdf = f.read()
        
    # Save the PDF to a bytes object
    #pdf_out = io.BytesIO()
    #pdf.output(dest='S')
    #pdf_data = pdf_out.getvalue()
    #st.session_state.pdf = pdf.output(dest='S').encode('latin-1')

