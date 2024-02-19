import sys
sys.path.append(".")
import dotenv
dotenv.load_dotenv(".env")
from website import constants
from projectgurukul.corelib import (get_query_engines, get_empty_response,
                                    get_fusion_query_engine_trained_model, get_fusion_query_engine, get_router_query_engine)
from website import mongo_utils
from projectgurukul import corelib
import streamlit.components.v1 as components
from website.footer import footer_html
from st_pages import Page, show_pages
import streamlit as st

from streamlit_components import social_share_widget


st.set_page_config(page_title='Project Gurukul',
                   page_icon="🕉️", layout="centered")



CURRENT_QUERY_ENGINE = 'curr_query_engine'
DEBUG = False
mongo_client = mongo_utils.get_mongo_client()


@st.cache_resource
def load_query_engine(scriptures):
    return get_fusion_query_engine_trained_model(scriptures=scriptures, is_offline=True, data_dir="data")


def get_source_str():
    return str.lower(st.session_state['source'][0])


def update_source_query_engine():
    if st.session_state['source']:
        # print ("st.session_state['source']", st.session_state['source'])
        st.session_state[CURRENT_QUERY_ENGINE] = load_query_engine(
            scriptures=st.session_state['source'])
    else:
        st.session_state[CURRENT_QUERY_ENGINE] = None


@st.cache_data(max_entries=50, show_spinner=False)
def get_response(prompt: str) -> str:
    # TODO: User chat engine. Query engine does not take context.
    # https://docs.llamaindex.ai/en/stable/api_reference/query/chat_engines.html
    query_engine = st.session_state[CURRENT_QUERY_ENGINE]
    if DEBUG:
        response = get_empty_response()
    else:
        response = query_engine.query(prompt)
    msg = response.response
    scripture_info = corelib.SCRIPTURE_MAPPING[get_source_str()]
    sourcestr = (f"\n\n**References:**\n\n")
    for i, source in enumerate(response.source_nodes):
        scripture_info = corelib.get_scripture_from_source_metadata(
            source.node.metadata)
        sourcestr += f"\n\n[{i+1}]: {scripture_info.get_reference_string(source.node.metadata)}\n\n"
    msg = msg + sourcestr
    return msg


def clear_state_messages():
    del st.session_state.messages


def generate_response(container, prompt):
    if not CURRENT_QUERY_ENGINE in st.session_state or not st.session_state[CURRENT_QUERY_ENGINE]:
        container.info("Please select a source from the sidebar.")
        container.stop()
    else:
        with container.chat_message("assistant"):
            with st.spinner("Breathe in, breathe out, you're getting there 🧘‍♂️"):
                response_msg = get_response(prompt)
                st.session_state.messages.append(
                    {"role": "assistant", "content": response_msg})
                st.write(response_msg)
                i = len(st.session_state.messages)-1
                question = st.session_state.messages[i - 1]
                answer = st.session_state.messages[i]
                # post to forum button
                if st.button("Share", key=f"share_{i}", type = "primary"):
                    share(question, answer)


with st.sidebar:
    # Multiselect
    options = st.multiselect(
        label='Select Sources of Vedic Scripture',
        key='source',
        default=['gita', 'ramayana'],
        on_change=update_source_query_engine,
        options=['gita', 'ramayana','mahabharata'])

    st.markdown(footer_html, unsafe_allow_html=True)

update_source_query_engine()

st.image("website/images/gurukul2.jpeg")
st.title("🕉️ Project Gurukul")
st.caption("🚀 Select one or more sources from the side bar and ask me anything from the selected scripture.")
st.caption(
    f"📖 Currently fetching answers from {','.join(st.session_state['source'])}")

suggestion_children = st.container()
chat_container = st.container()


def suggestion_clicked(question, answer):
    print("suggestion: ",question)
    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer})
    chat_container.chat_message("user").write(question)
    chat_container.chat_message("assistant").write(answer)
    # generate_response(chat_container, question)

def share(question, answer):
    with st.spinner("Creating share URL 🔗 "):
        thread_id = mongo_utils.post_thread(mongo_client, question, answer)

    url = f"{constants.SITE_BASE_URL}/forum?thread_id={thread_id}"
    st.markdown(f" 🔗 Share [link]({url}) created successfully.")
    result = social_share_widget(question['content'], answer["content"][:500]+"...", url)
    if result == "copy": # Not working. As this function does not execute during rerun.
        st.toast("Text copied to clipboard.")

    # st.toast(":green[**Posted your question and answer to forum.**]")


def render():
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Ask me anything about life ?"}]

    if len(st.session_state["messages"]) < 2:
        suggestion_children.write("Suggestions💡:")
        random_threads = mongo_utils.get_random_threads(mongo_client)
        for thread in random_threads:
            suggestion_children.button(label=thread.question['content'], on_click=suggestion_clicked, type="secondary", args=(
                thread.question['content'], thread.answer['content']), key=thread._id.int)
    for i, msg in enumerate(st.session_state.messages):
        with st.container():
            with chat_container.chat_message(msg["role"]):
                st.write(msg["content"])
                if i >= 2 and st.session_state.messages[i]['role'] == "assistant" and st.session_state.messages[i-1]['role'] == "user":
                    # post to forum button
                    question = st.session_state.messages[i - 1]
                    answer = st.session_state.messages[i]
                    if st.button("Share", key=f"share_{i}", type = "primary"):
                        share(question, answer)
    # clear button to clear context
    if len(st.session_state.messages) > 1:
        st.button("Clear All 🗑", on_click=clear_state_messages)
    if prompt := st.chat_input():
        print("Question: ", prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        chat_container.chat_message('user').write(prompt)
        generate_response(chat_container, prompt)


render()
