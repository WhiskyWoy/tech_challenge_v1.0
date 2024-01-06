# Importing libraries
import streamlit as st
import pandas as pd
import backend

# Configuring the default settings of the page
st.set_page_config(
    page_title="Start Page",
    page_icon="👋",
    layout="wide",
)

# Ensuring the information storage across sessions
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame()

# Formatting of the page
st.write("# Welcome to Jasmin, your AI Judge Assistant! 👋")

st.sidebar.write("Upload your document and then select a feature above.")

st.markdown(
    """
    Jasmin is an AI assistant built specifically for
    helping judges in preparing for court hearings in civil cases.
    Key features include:
    - **Fact extraction** from both parties' briefs
    - **Case summary** generation
    - **Briefs** comparisons side by side
    - **Interactive communication** with Jasmin
"""
)

# Allowing users to upload multiple files
uploaded_files = st.file_uploader("Choose a Text file", accept_multiple_files=True)
    
# In the case of a successful upload passing the data dictionary to the backend
uploaded = st.button('Upload', key='up')
if uploaded and len(uploaded_files) > 0:
    st.success('Uploaded successfully, proccessing...')
    backend.call(uploaded_files)
    st.success('Processed successfully, please select a feature above.')
    st.sidebar.success("Select a feature above.")
elif uploaded and len(uploaded_files) == 0:
    st.error('Please upload a file first.')
