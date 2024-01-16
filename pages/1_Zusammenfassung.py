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

with st.sidebar:
    #download output.pdf file
    st.download_button(
    "PDF Herunterladen",
    data=st.session_state.pdf,
    file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
    mime='application/pdf'
)
    
if st.session_state.event_summary == None:
    ui.add_logo()
    st.title("Es wurden noch keine Schriftsätze hochgeladen")
    # st.header("Example Summary:")
    # #st.write(lorem.text())
    # #st.markdown('<font size=10>lorem.text()</font>')


    # # Define the font size variable

    # @st.cache_data
    # def text():
    #     return lorem.text()

    # # Use st.markdown with inline CSS to change the font size
    # st.write(text())
else:
    ui.add_logo()
    st.title("Zusammenfassung der Schriftsätze ⚖️")
    st.write(st.session_state.event_summary)
