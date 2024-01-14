import streamlit as st
import starter
import os


@st.cache_resource
def load_data():
    scripture = str.lower(st.session_state['source'][0])
    return starter.get_query_engines(scripture=scripture, is_offline=False, similarity_top_k=3)

st.set_page_config(page_title='Project Gurukul', page_icon="🕉️", layout="centered", initial_sidebar_state="collapsed")

def set_open_api_key():
    openai_api_key = st.session_state['chatbot_api_key']
    os.environ['OPENAI_API_KEY'] = openai_api_key

with st.sidebar:
    def update_source_query_engine():
        print(st.session_state['source'])
        #TODO update the query engine here based on the values in the st.session_state['source']
    options = st.multiselect(
    label='Select Source of Vedic Scripture',
    key='source',
    default="Gita", 
    on_change=update_source_query_engine,
    options = ['Gita', 'Ramayana', 'Mahabharata', 'Rig Veda'])
    openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password", on_change=set_open_api_key)

query_engine = load_data()

st.title("🕉️ Project Gurukul")
st.caption("🚀 Select a source from the side bar and ask me anything from the selected scripture.")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about life ?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not query_engine:
        st.info("Please select a source from the sidebar and provide you open ai API key")
        st.stop()
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    # fetch response\
    response = query_engine.query(prompt + starter.SYSTEM_PROMPT)
    msg = response.response
    st.session_state.messages.append({"role": "assistant", "content": msg})
    st.chat_message("assistant").write(msg)