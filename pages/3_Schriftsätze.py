import streamlit as st
import pandas as pd
import lorem
import pybase64
import ui

if 'text_df' not in st.session_state:
    st.session_state.text_df = pd.DataFrame()
if 'pdf' not in st.session_state:
    st.session_state.pdf = b""

st.set_page_config(layout="wide")

def displayPDF(file, col):
    # Opening file from file path
    with open(file, "rb") as f:
        base64_pdf = pybase64.b64encode(f.read()).decode('utf-8')

    # Embedding PDF in HTML
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'

    # Displaying File
    col.markdown(pdf_display, unsafe_allow_html=True)

ui.add_logo()

if st.session_state.text_df.empty:
    st.title("Vergleich der Schriftsätze ⚖️")
    st.error("Bitte laden Sie zunächst Schriftsätze hoch, um die Schriftsätze vergleichen zu können.")

else:
    st.title("Vergleich der Schriftsätze ⚖️")
    col1, col2 = st.columns(2)
    col1.header("Kläger")
    # open pdf from pdf folder
    displayPDF("pdfs/brief_plaintiff_highlighted.pdf", col1)
    col2.header("Beklagter")
    displayPDF("pdfs/brief_defendant_highlighted.pdf", col2)
    with st.sidebar:
        # download output.pdf file
        st.download_button(
            "PDF Herunterladen",
            data=st.session_state.pdf,
            file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
            mime='application/pdf'
        )
