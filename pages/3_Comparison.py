import streamlit as st
import pandas as pd
import lorem
import pybase64

if 'text_input' not in st.session_state:
    st.session_state.text_input = pd.DataFrame()

st.set_page_config(layout="wide")

def displayPDF(file, col):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = pybase64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    col.markdown(pdf_display, unsafe_allow_html=True)

# Using "with" notation
with st.sidebar:
    #download output.pdf file
    st.download_button(
    "Download PDF",
    data=st.session_state.pdf,
    file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
    mime='application/pdf'
)
    textsize = st.slider("Text size", 1, 10, 2)
    

if st.session_state.text_input.empty:
    st.title("You need to upload briefs first")

else:
    st.title("Comparison of both briefs")
    col1, col2 = st.columns(2)
    col1.header("Plaintiff")
    # open pdf from pdf folder
    displayPDF("pdfs/brief_plaintiff.pdf", col1)
    col2.header("Defendant")
    displayPDF("pdfs/brief_defendant.pdf", col2)