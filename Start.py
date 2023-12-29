# Importing libraries
import streamlit as st
from pdfminer.high_level import extract_text
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
    st.session_state.text_input = pd.DataFrame()

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
"""
)

# Allowing users to upload multiple files and storing the text in a dictionary
data_dict = {'filename': [], 'text': []}
uploaded_files = st.file_uploader("Choose a Text file", accept_multiple_files=True)
for uploaded_file in uploaded_files:
    text_data = extract_text(uploaded_file)
    #bytes_data = uploaded_file.read()
    #st.write("filename:", uploaded_file.name)
    #st.write(text_data)
    #append to dataframe
    data_dict['filename'].append(uploaded_file.name)
    data_dict['text'].append(text_data)
    
# In the case of a successful upload passing the data dictionary to the backend
uploaded = st.button('Upload', key='up')
if uploaded and len(uploaded_files) > 0:
    st.success('Uploaded successfully, proccessing...')
    backend.call(data_dict)
    st.success('Processed successfully, please select a feature above.')
    st.sidebar.success("Select a feature above.")
elif uploaded and len(uploaded_files) == 0:
    st.error('Please upload a file first.')
