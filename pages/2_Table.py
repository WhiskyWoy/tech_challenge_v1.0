import streamlit as st
import pandas as pd
import lorem

if 'fact_table' not in st.session_state:
   st.session_state.fact_table = pd.DataFrame()


st.set_page_config(layout="wide")

# Using "with" notation
with st.sidebar:
    download = st.download_button("Download pdf", "Good Job!")
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

    st.table(load_data())
else:
    st.title("Table of Facts")
    st.table(st.session_state.fact_table)


