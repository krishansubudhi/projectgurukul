import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
import streamlit as st
from st_pages import Page, show_pages
from website.footer import footer_html
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

from projectgurukul.corelib import (get_query_engines, get_empty_response, get_fusion_query_engine_trained_model, get_fusion_query_engine, get_router_query_engine) 
from website.pages.forum import post_thread, get_random_threads


CURRENT_QUERY_ENGINE = 'curr_query_engine'
DEBUG = False

@st.cache_resource
def load_query_engine(scriptures):
    return get_fusion_query_engine_trained_model(scriptures=scriptures , is_offline=False, data_dir="data")

def get_source_str():
    return str.lower(st.session_state['source'][0])

def update_source_query_engine():
    if st.session_state['source']:
        # print ("st.session_state['source']", st.session_state['source'])
        st.session_state[CURRENT_QUERY_ENGINE] = load_query_engine(scriptures=st.session_state['source'])
    else:
        st.session_state[CURRENT_QUERY_ENGINE] = None

@st.cache_data(max_entries=50, show_spinner=False)
def get_response(prompt:str) -> str:
    # TODO: User chat engine. Query engine does not take context.
    # https://docs.llamaindex.ai/en/stable/api_reference/query/chat_engines.html
    query_engine = st.session_state[CURRENT_QUERY_ENGINE]
    if DEBUG:
        response =  get_empty_response()
    else:
        response = query_engine.query(prompt)
    msg = response.response
    scripture_info = corelib.SCRIPTURE_MAPPING[get_source_str()]
    sourcestr = (f"\n\nReferences:\n---\n")
    for i, source in enumerate(response.source_nodes):
        scripture_info = corelib.get_scripture_from_source_metadata(source.node.metadata)
        sourcestr += f"\n\n[{i+1}]: {scripture_info.get_reference_string(source.node.metadata)}\n\n"
    msg = msg + sourcestr 
    return msg

def clear_state_messages():
    del st.session_state.messages

def post_to_forum(i):
    question = st.session_state.messages[i - 1]
    answer = st.session_state.messages[i]
    print(question)
    print(answer)
    post_thread(question, answer)
    st.toast(":green[**Posted your question and answer to forum.**]")
    st.session_state['forum_scroll_section']="q-how-can-one-obtain-divine-qualities"
    st.switch_page("pages/forum.py")

def generate_response(container, prompt):
    if not CURRENT_QUERY_ENGINE in st.session_state or  not st.session_state[CURRENT_QUERY_ENGINE]:
        container.info("Please select a source from the sidebar.")
        container.stop()
    else:
        with container.chat_message("assistant"):
            with st.spinner("Breathe in, breathe out, you're getting there 🧘‍♂️"):
                response_msg = get_response(prompt) 
                st.session_state.messages.append({"role": "assistant", "content": response_msg})
                st.write(response_msg)
            

with st.sidebar:
    # Multiselect 
    options = st.multiselect(
    label='Select Sources of Vedic Scripture',
    key='source',
    default=['gita', 'ramayana'], 
    on_change=update_source_query_engine,
    options = ['gita', 'ramayana'])

    st.markdown(footer_html, unsafe_allow_html=True)

update_source_query_engine()

st.title("🕉️ Project Gurukul")
st.caption("🚀 Select one or more sources from the side bar and ask me anything from the selected scripture.")
st.caption(f"📖 Currently fetching answers from {','.join(st.session_state['source'])}")

suggestion_children = st.container()
chat_container = st.container()

def suggestion_clicked(question , answer):
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    chat_container.chat_message("user").write(question)
    chat_container.chat_message("assistant").write(answer)
    # generate_response(chat_container, question)

def render():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Ask me anything about life ?"}]

    if len(st.session_state["messages"]) < 2:
        suggestion_children.write("Suggestions💡:")
        random_threads = get_random_threads()
        for thread in random_threads:
            suggestion_children.button(label=thread.question['content'], on_click=suggestion_clicked, type="primary", args=(thread.question['content'], thread.answer['content']),key = thread._id.int)
    for i, msg in enumerate(st.session_state.messages):
        with st.container():
            with chat_container.chat_message(msg["role"]):
                st.write(msg["content"])
                if i!=0 and i % 2 == 0:
                    #post to forum button
                    st.button("Post To Forum", on_click=post_to_forum, key ="post_to_forum_" + str(i), args = (i,))
    #clear button to clear context 
    if len(st.session_state.messages) > 1:
        st.button("Clear All 🗑", on_click=clear_state_messages)
    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_container.chat_message('user').write(prompt)
        generate_response(chat_container, prompt)
        message_len = len(st.session_state.messages)
        #post to forum button
        st.button("Post To Forum", on_click=post_to_forum, key ="post_to_forum_" + str(message_len - 1), args = (message_len-1,))
render()

