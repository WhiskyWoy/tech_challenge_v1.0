import pandas as pd
import time
import streamlit as st

def call (data):
    df = pd.DataFrame(data)
    #sleep for 5 seconds
    time.sleep(5)
    st.session_state.df = df

