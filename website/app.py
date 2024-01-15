import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
import streamlit as st
from st_pages import Page, show_pages
st.set_page_config(page_title='Project Gurukul', page_icon="🕉️", layout="centered")
# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("website/app.py", "Home", "🕉️"),
        Page("website/pages/forum.py", "Forum", ":books:"),
    ]
)
from projectgurukul import corelib
from projectgurukul.corelib import (SYSTEM_PROMPT, get_query_engines, get_empty_response) 
from pages.forum import post_thread, set_rendering_on

CURRENT_QUERY_ENGINE = 'curr_query_engine'
DEBUG = False

@st.cache_resource
def load_data(scripture):
    return get_query_engines(scripture=scripture, is_offline=False)

def get_source_str():
    return str.lower(st.session_state['source'][0])


def update_source_query_engine():
    if st.session_state['source']: 
        st.session_state[CURRENT_QUERY_ENGINE] = load_data(get_source_str())
    else:
        st.session_state[CURRENT_QUERY_ENGINE] = None

with st.sidebar:
    # Multiselect 
    options = st.multiselect(
    label='Select Source of Vedic Scripture',
    key='source',
    default="Ramayana", 
    on_change=update_source_query_engine,
    options = ['Gita', 'Ramayana'])

update_source_query_engine()

st.title("🕉️ Project Gurukul")
st.caption("🚀 Select a source from the side bar and ask me anything from the selected scripture.")
st.caption(f"📖 Currently fetching answers from {','.join(st.session_state['source'])}")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about life ?"}]
set_rendering_on()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    if not CURRENT_QUERY_ENGINE in st.session_state or  not st.session_state[CURRENT_QUERY_ENGINE]:
        st.info("Please select a source from the sidebar.")
        st.stop()
    query_engine = st.session_state[CURRENT_QUERY_ENGINE]
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Breathe in, breathe out, you're getting there 🧘‍♂️"):
            # TODO: User chat engine. Query engine does not take context.
            # https://docs.llamaindex.ai/en/stable/api_reference/query/chat_engines.html
            if DEBUG:
                response = get_empty_response()
            else:
                response = query_engine.query(prompt + SYSTEM_PROMPT)
        msg = response.response
        
        scripture_info = corelib.SCRIPTURE_MAPPING[get_source_str()]
    
        sourcestr = (f"\n\nReferences:\n---\n{scripture_info.name}\n")
        for i, source in enumerate(response.source_nodes):
            relevant_metadata = ", ".join([f"{k} : {v}" for k,v in source.node.metadata.items() if k in scripture_info.metadatas_to_display])
            sourcestr += f"\n\n[{i+1}]: {relevant_metadata}\n\n" #+ f"{source.node.get_content()[:200]} '...'"
        msg = msg + sourcestr 
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.write(msg)

#post to forum button
if 'messages' in st.session_state and len(st.session_state.messages)>1:
    def disable(b):
        st.session_state["disabled_post_button"] = b
    post_to_forum = st.button("Post To Forum", on_click=disable, disabled=st.session_state.get("disabled_post_button", False), args=(True,))
    if post_to_forum:
        question = st.session_state.messages[-2]
        answer = st.session_state.messages[-1]
        post_thread(question, answer)
        st.toast(":green[**Posted your question and answer to forum.**]")

#clear button to clear context 
if 'messages' in st.session_state and len(st.session_state.messages)>1:
    clear_button_clicked = st.button("Clear")
    if clear_button_clicked:
        del st.session_state.messages
        st.rerun() 
