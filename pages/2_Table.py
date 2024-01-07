import streamlit as st
import pandas as pd
import lorem

if 'fact_table' not in st.session_state:
   st.session_state.fact_table = pd.DataFrame()


st.set_page_config(layout="wide")

# Using "with" notation
# Using "with" notation
with st.sidebar:
    #download output.pdf file
    st.download_button(
    "Download PDF",
    data=st.session_state.pdf,
    file_name='Ganzheitliche Übersicht der Schriftsätze.pdf',
    mime='application/pdf'
)
    textsize = st.slider("Text size", 1, 10, 2)
    


if st.session_state.fact_table.empty:
    st.title("You need to upload briefs first")
    st.header("Example table of facts")
    #st.write(lorem.text())
    #st.markdown('<font size=10>lorem.text()</font>')


    # Define the font size variable
    font_size = textsize
    print("reload 2")

    @st.cache_data
    def text():
        return lorem.text()

    # Use st.markdown with inline CSS to change the font size
    #st.markdown(f'<div style="font-size: {font_size*10}px;">{text()}</div>', unsafe_allow_html=True)

    @st.cache_data
    def load_data():
        df = pd.read_excel("fact_table.xlsx")
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
    st.title("Table of Facts")
    df = st.session_state.fact_table
    print(df)
    #make headline bold with styler
    df.style.set_properties(**{'font-weight': 'bold'}, subset=['Headline'])

    st.dataframe(df)


