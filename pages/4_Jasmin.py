# Inspiration can be found here: https://github.com/marshmellow77/streamlit-chatgpt-ui/blob/main/app.py
# The corresponding explanations could be found here: https://towardsdatascience.com/build-your-own-chatgpt-like-app-with-streamlit-20d940417389 

import streamlit as st
from backend import generate_response
from streamlit_chat import message

# Setting page title and header
st.set_page_config(page_title="Jasmin")
st.markdown("<h1 style='text-align: center;'>Jasmin - Die Richterassistentin</h1>", unsafe_allow_html=True)

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du sollst die Schriftsätze lesen bei Fragen dich auf den Inhalt der Schriftsätze beziehen."},
        {"role": "system", "content": "Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."},
        {"role": "user", "content": "Text 1" + st.session_state.text1},
        {"role": "user", "content": "Text 2" + st.session_state.text2},
    ]
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

counter_placeholder = st.sidebar.empty()
#counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.button("Neustart der Konversation", key="Neustart")

# reset everything
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "Du bist eine Richterassistentin namens Jasmin. Deine Aufgabe ist es, den Richter zu unterstützen, um ihn effizienter bei der Vorbereitung einer Gerichtsverhandlung zu machen."},
        {"role": "system", "content": "Du erhältst zwei Schriftsätze vom Kläger und vom Beklagten. Du sollst die Schriftsätze lesen bei Fragen dich auf den Inhalt der Schriftsätze beziehen."},
        {"role": "system", "content": "Bitte fassen Sie den Inhalt der Schriftsätze in einer prägnanten, verständlichen Form zusammen."},
        {"role": "user", "content": "Text 1" + st.session_state.text1},
        {"role": "user", "content": "Text 2" + st.session_state.text2},
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    #counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("Sie:", key='input', height=100)
        submit_button = st.form_submit_button(label='Senden')
        
    if submit_button and user_input:
        output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['total_tokens'].append(total_tokens)

        # from https://openai.com/pricing#language-models
        cost = total_tokens * 0.002 / 1000
        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))
            #st.write(
                #f"Number of tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            #counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

### Old version
# st.set_page_config(layout="wide")

# if "openai_model" not in st.session_state:
#     st.session_state["openai_model"] = "gpt-3.5-turbo"

# # # Initialize chat history
# if "messages" not in st.session_state:
#      st.session_state.messages = []

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # Benutzereingabe abfragen
# user_input = st.text_input("You:", "")

# # Benutzerfrage verarbeiten und Antwort erhalten
# if st.button("Send"):
#     if user_input.strip() != "":
#         st.session_state.messages.append({"role": "user", "content": user_input})
#         reply = customChatGPT(st.session_state.messages)
#         st.session_state.messages.append({"role": "assistant", "content": reply})
#         user_input = st.text_input("You:", value="", key="user_input_new")
#     else:
#         st.warning("Please insert a question.")

# with st.sidebar:
#     download = st.download_button("Download pdf", "Good Job!")
#     textsize = st.slider("Text size", 1, 10, 2)