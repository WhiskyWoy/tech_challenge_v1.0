import streamlit as st
from backend import generate_response
from streamlit_chat import message
import ui

ui.add_logo()

st.markdown("<h1 style='text-align: center;'>Chat mit Jasmin - Die Richterassistentin</h1>", unsafe_allow_html=True)

if st.session_state.text_df.empty:
    st.title("Vergleich der Schriftsätze ⚖️")
    st.error("Bitte laden Sie zunächst Schriftsätze hoch, um die Schriftsätze vergleichen zu können.")
else:
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

