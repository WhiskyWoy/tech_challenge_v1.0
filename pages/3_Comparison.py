import streamlit as st
import pandas as pd
import lorem
import pybase64

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

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
    download = st.download_button("Download pdf", "Good Job!")
    textsize = st.slider("Text size", 1, 10, 2)
    
col1, col2 = st.columns(2)

if st.session_state.df.empty:
    st.title("You need to upload briefs first")

else:
    st.title("Comparison of both briefs")
    col1.header("Plaintiff")
    displayPDF(st.session_state.df['filename'].iloc[0], col1)
    col2.header("Defendant")
    displayPDF(st.session_state.df['filename'].iloc[1], col2)