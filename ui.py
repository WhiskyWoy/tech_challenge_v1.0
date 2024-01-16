import streamlit as st

def add_logo():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                background-image: url(https://i.imgur.com/u7OERnp.png);
                background-repeat: no-repeat;
                padding-top: 20px;
                background-position: 20px 20px;
            }
            [data-testid="stSidebarNav"]::before {
                content: "Jasmin";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 80px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )