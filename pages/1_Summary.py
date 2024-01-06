# Importing libraries
import streamlit as st
import pandas as pd
import lorem

# Ensuring the information storage across sessions
if 'event_summary' not in st.session_state:
    st.session_state.event_summary = pd.DataFrame()

# Using "with" notation
with st.sidebar:
    download = st.download_button("Download pdf", "Good Job!")
    textsize = st.slider("Text size", 1, 10, 2)
    
if st.session_state.event_summary.empty:
    st.title("You need to upload briefs first")
    st.header("Example Summary:")
    #st.write(lorem.text())
    #st.markdown('<font size=10>lorem.text()</font>')


    # Define the font size variable
    font_size = textsize
    print("reload 1")

    @st.cache_data
    def text():
        return lorem.text()

    # Use st.markdown with inline CSS to change the font size
    st.markdown(f'<div style="font-size: {font_size*10}px;">{text()}</div>', unsafe_allow_html=True)
else:
    st.title("Event Summary")
    st.write(st.session_state.event_summary["summary"].iloc[0])
