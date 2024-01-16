# Importing libraries
import streamlit as st
import pandas as pd
import backend
import os

# Configuring the default settings of the page
st.set_page_config(
    page_title="Startseite",
    page_icon="⚖️",
    layout="wide",
)

# Formatting of the page
st.write("# Jasmin heißt Sie willkommen, Ihre AI-Assistentin! ⚖️")

st.sidebar.write("Laden Sie Ihre Dokumente hoch und wählen Sie dann eine Funktion aus.")

st.markdown(
    """
    Jasmin ist eine KI-Assistentin, die speziell dafür entwickelt wurde,
    Richtern bei der Vorbereitung auf Gerichtsverhandlungen in Zivilsachen zu helfen.
    Zu den Hauptfunktionen gehören:
    - **Zusammenfassung:** steigen Sie schnell in den Fall ein
    - **Übersicht der Fakten:** analysieren Sie die wichtigsten Fakten des Falls
    - **Vergleich:** betrachten Sie die gekennzeichneten Schriftsätze nebeneinander
    - **Interaktive Kommunikation:** fragen Sie Jasmin Ihre Fragen zum Fall
"""
)

# Allowing users to upload multiple files
upload_plaintiff = st.file_uploader("Kläger Schriftsatz")
upload_defendant = st.file_uploader("Beklagter Schriftsatz")

if upload_plaintiff and upload_defendant:
    upload_button = st.button("Hochladen")
    if upload_button:
        st.success("Beide Dokumente wurden erfolgreich hochgeladen!")
        st.success("Verarbeitung läuft...")
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
        st.success("Verarbeitung erfolgreich! Wähle eine Option aus der Sidebar aus.")
        st.sidebar.success("Wähle eine Option aus der Sidebar aus.")
