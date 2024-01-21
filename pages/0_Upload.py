# Importing libraries
import streamlit as st
import pandas as pd
import backend
import os
import ui
import time
# Configuring the default settings of the page
st.set_page_config(
    page_title="Upload",
    page_icon="⚖️",
    layout="wide",
)

ui.add_logo()

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

st.markdown("Laden Sie zunächst den Schriftsatz des Klägers und den Schriftsatz des Beklagten hoch. Achten Sie darauf, die Schriftsätze in dem korrekten Feld hochzuladen.")
cola2, cola3, cola4 = st.columns([0.15,0.05,0.7])
cola2.write("Und wähle eine GPT Version aus:")

if 'gpt_4' not in st.session_state:
    st.session_state.gpt_4 = None

if cola3.button("GPT-4"):
    st.session_state.gpt_4 = True
    st.success("GPT-4 wurde ausgewählt.")
if cola4.button("GPT-3"):
    st.session_state.gpt_4 = False
    st.success("GPT-3 wurde ausgewählt.")

password = st.text_input("Bitte gebe das Passwort ein", type="password")

uploaded = False

colb1, colb2, _= st.columns([0.225,0.225,0.55])
# Allowing users to upload multiple files
#read pdf as bytes
with open("pdfs/brief_plaintiff.pdf", "rb") as f:
        colb1.download_button(
        "Beispiel-PDF des Klägers Herunterladen",
        data=f.read(),
        file_name='brief_plaintiff.pdf',
        mime='application/pdf'
        )
with open("pdfs/brief_defendant.pdf", "rb") as f:
        colb2.download_button(
        "Beispiel-PDF des Klägers Herunterladen",
        data=f.read(),
        file_name='brief_defendant.pdf',
        mime='application/pdf'
        )
upload_plaintiff = st.file_uploader("Kläger Schriftsatz")
upload_defendant = st.file_uploader("Beklagter Schriftsatz")

if upload_plaintiff and upload_defendant:
    upload_button = st.button("Hochladen")
    if upload_button:
        if st.session_state.gpt_4 == None:
            st.error("Bitte wähle eine GPT Version aus.")
        else:
            if password == st.secrets["PASSWORD"]:
                uploaded = True
                message0 = st.success("Beide Dokumente wurden erfolgreich hochgeladen!")
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
                message1 = st.info("Zusammenfassung wird erstellt...")
                backend.generate_summary()
                message0.empty()
                message1.empty()
                message0 = st.success("Zusammenfassung erfolgreich erstellt!")
                message1.info("Bitte warte mit dem auswählen einer Funktion, bis die Verarbeitung abgeschlossen ist.")
                message2 = st.info("Tabelle wird erstellt...")
                backend.find_commonalities_and_differences()
                message0.empty()
                message2.empty()
                message0 = st.success("Tabelle erfolgreich erstellt!")
                message = st.info("Vergleich der Schriftsätze wird erstellt...")
                if not st.session_state.gpt_4:
                    message3 = st.info("Jasmin brauch eine kurze Pause, der Vergleich kommt in 30 Sekunden (too many requests as GPT-3.5 Turbo is limited at 3 actions per minute)")
                    time.sleep(30)
                backend.compare_pdfs()
                message0.empty()
                message1.empty()
                message3.empty()
                message0 = st.success("Vergleich der Schriftsätze erfolgreich erstellt!")
                backend.create_pdf()
                message1 = st.success("Wähle eine der vier Funktionen von Jasmin aus")
                st.sidebar.success("Wähle eine Option aus der Sidebar aus.")
                st.text("")
                st.text("")
                st.text("")

                # Display images in two columns
                col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 0.2, 1, 0.2, 1, 0.2, 1])

                col1.image("pictures/Bild1.jpg", use_column_width=True)
                col3.image("pictures/Bild2.jpg", use_column_width=True)
                col5.image("pictures/Bild3.jpg", use_column_width=True)
                col7.image("pictures/Bild4.jpg", use_column_width=True)

                if col1.button("Zusammenfassung", use_container_width=True):
                    st.switch_page("pages/1_Zusammenfassung.py")
                if col3.button("Tabelle an Fakten", use_container_width=True):
                    st.switch_page("pages/2_Tabelle.py")
                if col5.button("Direkter Schriftsatz Vergleich", use_container_width=True):
                    st.switch_page("pages/3_Schriftsätze.py")
                if col7.button("Chat mit Jasmin", use_container_width=True):
                    st.switch_page("pages/4_Jasmin.py")
                
            else:
                st.error("Falsches Passwort!")

