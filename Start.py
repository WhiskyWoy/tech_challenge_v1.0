# Importing libraries
import streamlit as st
import pandas as pd
import backend
import os

# Configuring the default settings of the page
st.set_page_config(
    page_title="Start Page",
    page_icon="⚖️",
    layout="wide",
)

# Formatting of the page
st.write("# Welcome to Jasmin, your AI Judge Assistant! ⚖️")

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
upload_plaintiff = st.file_uploader("Upload plaintiff file")
upload_defendant = st.file_uploader("Upload defendant file")

if upload_plaintiff and upload_defendant:
    upload_button = st.button("Upload")
    if upload_button:
        st.success("Both documents successfully added!")
        uploaded_files = [upload_plaintiff, upload_defendant]
        # Define the paths for saving the files
        directory_plaintiff = "pdfs"
        directory_defendant = "pdfs"

        # Ensure the directories exist, create them if not
        os.makedirs(directory_plaintiff, exist_ok=True)
        os.makedirs(directory_defendant, exist_ok=True)

        # Construct the full file paths
        path_plaintiff = os.path.join(directory_plaintiff, "brief_plaintiff.pdf")
        path_defendant = os.path.join(directory_defendant, "brief_defendant.pdf")

        # Save the plaintiff file
        with open(path_plaintiff, "wb") as f_plaintiff:
            f_plaintiff.write(upload_plaintiff.getbuffer())

        # Save the defendant file
        with open(path_defendant, "wb") as f_defendant:
            f_defendant.write(upload_defendant.getbuffer())
        backend.call(uploaded_files)
        st.success("Processed successfully, please select a feature above.")
        st.sidebar.success("Select a feature above.")
