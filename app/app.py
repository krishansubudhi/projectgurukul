import streamlit as st
import starter
import openai


CURRENT_QUERY_ENGINE = 'curr_query_engine'

@st.cache_resource
def load_data(scripture):
    return starter.get_query_engines(scripture=scripture, is_offline=False, similarity_top_k=3)

st.set_page_config(page_title='Project Gurukul', page_icon="🕉️", layout="centered", initial_sidebar_state="collapsed")

def update_source_query_engine():
    st.session_state[CURRENT_QUERY_ENGINE] = load_data(str.lower(st.session_state['source'][0]))

def set_open_api_key():
    openai_api_key = st.session_state['chatbot_api_key']
    openai.api_key = openai_api_key
    print(st.session_state['chatbot_api_key'])
    if not CURRENT_QUERY_ENGINE in st.session_state:
        update_source_query_engine()

with st.sidebar:
    # Multiselect 
    options = st.multiselect(
    label='Select Source of Vedic Scripture',
    key='source',
    default="Gita", 
    on_change=update_source_query_engine,
    options = ['Gita', 'Ramayana', 'Mahabharata', 'Rig Veda'])
    #OPEN API KEY 
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password", on_change=set_open_api_key)

st.title("🕉️ Project Gurukul")
st.caption("🚀 Select a source from the side bar and ask me anything from the selected scripture.")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about life ?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not CURRENT_QUERY_ENGINE in st.session_state:
        st.info("Please select a source from the sidebar and provide you openai API key")
        st.stop()
    query_engine = st.session_state[CURRENT_QUERY_ENGINE]
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.spinner(f"Collecting knowledge and distilling it for you."):
        # fetch response
        response = query_engine.query(prompt + starter.SYSTEM_PROMPT)
        msg = response.response
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.chat_message("assistant").write(msg)