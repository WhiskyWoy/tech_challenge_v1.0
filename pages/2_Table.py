import streamlit as st
import pandas as pd
import lorem
st.set_page_config(layout="wide")

# Using object notation
add_selectbox = st.sidebar.selectbox(
    "How would you like to be contacted?",
    ("Email", "Home phone", "Mobile phone")
)

# Using "with" notation
with st.sidebar:
    download = st.download_button("Download pdf", "Good Job!")
    textsize = st.slider("Text size", 1, 10, 2)
    

st.title("Hello Jasmin")
st.header("Jasmin's table of facts")
#st.write(lorem.text())
#st.markdown('<font size=10>lorem.text()</font>')


# Define the font size variable
font_size = textsize
print("print")

@st.cache
def text():
    return lorem.text()

# Use st.markdown with inline CSS to change the font size
#st.markdown(f'<div style="font-size: {font_size*10}px;">{text()}</div>', unsafe_allow_html=True)

@st.cache
def load_data():
    df = pd.read_excel("fact_table.xlsx")
    #use first column as index and drop it
    df.set_index(df.columns[0], inplace=True)
    return df

st.table(load_data())
