import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
import streamlit as st
from typing import Sequence
from st_pages import Page, show_pages
# st.set_page_config(page_title='Project Gurukul', page_icon="🕉️", layout="centered")
# add_page_title('Project Gurukul')
# Specify what pages should be shown in the sidebar, and what their titles and icons
# should be
show_pages(
    [
        Page("website/app.py", "Gurukul", "🕉️"),
        Page("website/pages/forum.py", "Forum", ":books:"),
    ]
)
from projectgurukul import corelib
from projectgurukul.corelib import (get_query_engines, get_empty_response, get_router_query_engine) 
from pages.forum import post_thread

CURRENT_QUERY_ENGINE = 'curr_query_engine'
DEBUG = False

@st.cache_resource
def load_data(scripture):
    return get_query_engines(scripture=scripture, is_offline=False)

@st.cache_resource
def load_router_query_engine(scriptures):
    return get_router_query_engine(scriptures=scriptures , is_offline=False)

def get_source_str():
    return str.lower(st.session_state['source'][0])


def update_source_query_engine():
    if st.session_state['source']:
        print ("st.session_state['source']", st.session_state['source'])
        if type(st.session_state['source']) == list  and len(st.session_state['source'])>1:
            st.session_state[CURRENT_QUERY_ENGINE] = load_router_query_engine(scriptures=st.session_state['source'])
            print("loading multi index query engine")
        else:
            print("loading single index query engine")
            st.session_state[CURRENT_QUERY_ENGINE] = load_data(get_source_str())
    else:
        st.session_state[CURRENT_QUERY_ENGINE] = None

with st.sidebar:
    # Multiselect 
    options = st.multiselect(
    label='Select Sources of Vedic Scripture',
    key='source',
    default=['gita', 'ramayana'], 
    on_change=update_source_query_engine,
    options = ['gita', 'ramayana'])

update_source_query_engine()

st.title("🕉️ Project Gurukul")
st.caption("🚀 Select one or more sources from the side bar and ask me anything from the selected scripture.")
st.caption(f"📖 Currently fetching answers from {','.join(st.session_state['source'])}")
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about life ?"}]

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
                response = query_engine.query(prompt)
        msg = response.response
        
        scripture_info = corelib.SCRIPTURE_MAPPING[get_source_str()]
    
        sourcestr = (f"\n\nReferences:\n---\n")
        for i, source in enumerate(response.source_nodes):
            scripture_info = corelib.get_scripture_from_source_metadata(source.node.metadata)
            sourcestr += f"\n\n[{i+1}]: {scripture_info.get_reference_string(source.node.metadata)}\n\n"

        msg = msg + sourcestr 
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.write(msg)

#post to forum button
if 'messages' in st.session_state and len(st.session_state.messages)>1:
    post_to_forum = st.button("Post To Forum")
    if post_to_forum:
        question = st.session_state.messages[-2]
        answer = st.session_state.messages[-1]
        post_thread(question, answer)
        st.toast(":green[**Posted your question and answer to forum.**]")
        st.session_state['forum_scroll_section']="q-how-can-one-obtain-divine-qualities"
        st.switch_page("pages/forum.py")

#clear button to clear context 
if 'messages' in st.session_state and len(st.session_state.messages)>1:
    clear_button_clicked = st.button("Clear")
    if clear_button_clicked:
        del st.session_state.messages
        st.rerun() 
