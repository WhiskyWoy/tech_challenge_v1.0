# Importing libraries
import streamlit as st
import pandas as pd
import ui

# Configuring the default settings of the page
st.set_page_config(
    page_title="Landing Page",
    page_icon="⚖️",
    layout="wide",
)

ui.add_logo()

# Formatting of the page
st.write("# Landing Page for Jasmin, the AI Assistent ⚖️")

st.sidebar.write("Upload your documents and select a feature.")

col1, _, col2, _,  col3 = st.columns([0.3, 0.05, 0.3, 0.05, 0.3])

col1.header("Customer Need")
col1.write("Currently, judges are dealing with a large number of different legal cases. These include many pages which judges have to read and analyze. At the moment, judges cannot keep up with these cases, resulting in an average of 5 months duration of proceedings per case. Due to the lack of judges, every judge at a German local court has to deal with 521.9 cases per year on average.​")
col1.image("pictures/customer_need.png", use_column_width=True)

col2.header("Value Proposition")
col2.write("With Jasmin judges can upload cases as PDF and immediately receive a summary with the most important facts and a chronically structured storyline. Furthermore, they can interact, ask questions about the case, and highlight relevant parts. With this increase in productivity, the Ministry of Justice as the main customer can tackle its lack of judges and society benefits from better court access.​")
col2.image("pictures/value_proposition.png", use_column_width=True)

col3.header("Differentiation")
col3.write("The AI Judge assistant market is young and fragmented, lacking a clear market leader. With its unique selling points efficiency, accuracy and ease of use Jasmin stands out in efficiency and accuracy. With this competitive edge we plan to reach our SOM of M10€ annual recurring revenue in 2027 by getting a market share of 50% in Germany. The TAM of M600€ offers further growing opportunities abroad.  ​")
col3.image("pictures/differentiation.png", use_column_width=True)

col2.text("")
col2.text("")
col2.text("")
col2.text("")

st.markdown("""
<style>
.stButton>button {
    color: white;
    background-color: #242E57;
}
</style>
""", unsafe_allow_html=True)

if col2.button("Get Started", use_container_width=True):
    st.switch_page("pages/0_Upload.py")

