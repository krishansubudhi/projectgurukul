import streamlit as st

from uuid import uuid4
from datetime import datetime
from streamlit_disqus import st_disqus
from website.footer import footer_html
from website import mongo_utils, constants
from streamlit_components import social_share_widget
# st.set_page_config(page_title='Gurukul Forum', page_icon=":books:", layout="centered")

if 'question' not in st.session_state:
    st.set_page_config(page_title='Gurukul Forum', page_icon=":books:", layout="centered")
else:
    print("session state contains question.")
    st.set_page_config(page_title=st.session_state["question"], page_icon="❓", layout="centered")

def render_forum():
    mongo_client = mongo_utils.get_mongo_client()
    with st.sidebar:
        st.markdown(footer_html, unsafe_allow_html=True)
    threads = mongo_utils.read_forum_data(mongo_client)
    with st.container(border=False):
        for thread in threads:
            with st.container(border=True):
                show_thread(mongo_client, thread)

def show_thread(mongo_client, thread: mongo_utils.ForumThread):
    st.markdown("*{}*".format(thread.post_date.date()))
    st.markdown("## Q: {}".format(thread.question['content']))
    st.markdown("### A: {} ".format(thread.answer['content']))
    url = f"{constants.SITE_BASE_URL}/forum?thread_id={thread._id}"
    st.markdown(f" 🔗 Post [link]({url})")
    result = social_share_widget(thread.question['content'], thread.answer["content"][:500]+"...", url)
    if result == "copy":
        st.toast("copied share text to clipboard.")

    comment_box = st.expander("💬 Open comments")
                # st_disqus(shortname="gurukul-streamlit-app", identifier=thread._id.int, url="https://gurukul.streamlit.app/forum#" + str(thread._id.int), title=thread.question)
                # Show comments
    comment_box.write("**Comments:**")
    for comment_dict in thread.comments:
        comment = mongo_utils.Comment(**comment_dict)
        comment_box.markdown("{} - {}> {}".format(comment.userid,
                                comment.post_date, comment.comment))
    with st.form("comment_box" + str(thread._id), clear_on_submit=True, border=True):
        comment_text = st.text_input("Enter comment here")
        submitted = st.form_submit_button(
                        ":green[Post Comment]")
        if submitted:
            if comment_text == "":
                st.toast(":red[☝️ Your comment cannot be empty.]")
            else:
                comment = mongo_utils.Comment(
                                _id=uuid4(), comment=comment_text, post_date=datetime.now(), userid="test_user")
                if mongo_utils.add_comment_to_forum(mongo_client, thread, comment):
                    comment_box.write(
                                    "{} - {}> {}".format(comment.userid, comment.post_date, comment.comment))
                    st.toast(":green[☝️ Your comment was successfully posted.]")


all_params = st.query_params.to_dict()
# print(all_params)
if 'thread_id' not in all_params:
    st.title("📝 Gurukul Forum")
    render_forum()
else:
    mongo_client = mongo_utils.get_mongo_client()
    thread = mongo_utils.find_thread_by_id(mongo_client, all_params["thread_id"])
    if thread:
        rerun = False
        if "question" not in st.session_state:
            rerun = True
        st.session_state["question"] = thread.question["content"]
        if rerun:
            st.rerun()
        
        show_thread(mongo_client, thread)
    else:
        st.error(f"No post found with id {all_params['thread_id']}")
    
    st.link_button("All posts", f"{constants.SITE_BASE_URL}/forum")
