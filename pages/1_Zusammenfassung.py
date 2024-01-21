# Importing libraries
import streamlit as st
import pandas as pd
import lorem
import sys
sys.path.append("..")
import ui


# Ensuring the information storage across sessions
if 'event_summary' not in st.session_state:
    st.session_state.event_summary = None
if 'pdf' not in st.session_state:
    st.session_state.pdf = b""
    
if st.session_state.event_summary == None:
    ui.add_logo()
    st.title("Zusammenfassung der Schriftsätze ⚖️")
    st.error("Bitte laden Sie zunächst Schriftsätze hoch, um sich die Zusammenfassung ausgeben lassen zu können.")

else:
    ui.add_logo()
    st.title("Zusammenfassung der Schriftsätze ⚖️")
    st.write(st.session_state.event_summary)
    with st.sidebar:
        # download output.pdf file
        st.download_button(
            "PDF Herunterladen",
            data=st.session_state.pdf,
            file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
            mime='application/pdf'
        )
