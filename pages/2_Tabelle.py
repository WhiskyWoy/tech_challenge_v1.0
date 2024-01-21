import streamlit as st
import pandas as pd
import lorem
import ui

if 'fact_table' not in st.session_state:
   st.session_state.fact_table = pd.DataFrame()
if 'pdf' not in st.session_state:
    #empty binary data
    st.session_state.pdf = b""

st.set_page_config(layout="wide")

ui.add_logo()

if st.session_state.fact_table.empty:
    st.title("Tabelle mit den wichtigsten Fakten ⚖️")
    st.error("Bitte laden Sie zunächst Schriftsätze hoch, um die Tabellenübersicht einsehen zu können.")
else:
    st.title("Tabelle mit den wichtigsten Fakten ⚖️")
    df = st.session_state.fact_table
    #make headline bold with styler
    df.style.set_properties(**{'font-weight': 'bold'}, subset=['Headline'])

    st.dataframe(df)

    with st.sidebar:
        #download output.pdf file
        st.download_button(
        "PDF Herunterladen",
        data=st.session_state.pdf,
        file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
        mime='application/pdf'
    )


