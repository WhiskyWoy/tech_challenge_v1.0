import streamlit as st
import pandas as pd
import lorem

if 'fact_table' not in st.session_state:
   st.session_state.fact_table = pd.DataFrame()
if 'pdf' not in st.session_state:
    #empty binary data
    st.session_state.pdf = b""


st.set_page_config(layout="wide")

with st.sidebar:
    #download output.pdf file
    st.download_button(
    "PDF Herunterladen",
    data=st.session_state.pdf,
    file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
    mime='application/pdf'
)
    


if st.session_state.fact_table.empty:
    st.title("Es wurden noch keine Schriftsätze hochgeladen")
    st.header("Beispiel Tabelle:")
    #st.write(lorem.text())
    #st.markdown('<font size=10>lorem.text()</font>')


    @st.cache_data
    def text():
        return lorem.text()

    # Use st.markdown with inline CSS to change the font size
    #st.markdown(f'<div style="font-size: {font_size*10}px;">{text()}</div>', unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        df = pd.read_excel("test_data/fact_table.xlsx")
        #use first column as index and drop it
        df.set_index(df.columns[0], inplace=True)
        return df

    #st.table(load_data())
    df = load_data()
    print(df)
    #df.style.set_properties(**{'font-weight': 'bold'}, subset=['Headline'])
    df = df.style.set_properties(**{'font-weight': 'bold'}, subset=df.columns)
    #st.dataframe(df.style.set_properties(**{'font-weight': 'bold'}))
    st.dataframe(df)
else:
    st.title("Tabelle mit den wichtigsten Fakten ⚖️")
    df = st.session_state.fact_table
    print(df)
    #make headline bold with styler
    df.style.set_properties(**{'font-weight': 'bold'}, subset=['Headline'])

    st.dataframe(df)


