import streamlit as st
import pymongo
from dataclasses import dataclass, asdict
from uuid import uuid4
from datetime import datetime
from streamlit_disqus import st_disqus

@dataclass
class Comment:
    _id: uuid4
    userid: str
    comment: str
    post_date: datetime

@dataclass
class ForumThread:
    _id: uuid4
    post_date: datetime
    question: str
    answer: str
    comments: list[Comment]

def set_rendering_on():
    if 'forum_render' not in st.session_state:
        st.session_state['forum_render'] = True 

# Initialize connection.
@st.cache_resource
def init_connection():
    return pymongo.MongoClient(st.secrets['MONGO_DB_CONNECTION_URL'], uuidRepresentation='standard')

client = init_connection()

def post_thread(question:str, answer:str):
    add_thread_to_forum(ForumThread(_id = uuid4(), question=question, answer=answer, comments=[], post_date=datetime.now()))

def add_thread_to_forum(thread: ForumThread):
    threads_collection = client.test.threads
    threads_collection.insert_one(asdict(thread))

def add_comment_to_forum(thread: ForumThread, comment: Comment):
    threads_collection = client.test.threads
    thread.comments.append(comment)
    return threads_collection.find_one_and_update(filter={'_id': thread._id}, update={
                                           '$push': {'comments': asdict(comment)}}, upsert=True)

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after ttl 
@st.cache_data(ttl=10)
def read_forum_data():
    items = client.test.threads.find()
    items = list(items)  # make hashable for st.cache_data
    threads = [ForumThread(**item) for item in items]
    return threads

def render_forum():
    threads = read_forum_data()
    with st.container(border=True):
        st.markdown("# All Threads")
        for thread in threads:
            with st.container(border=True):
                st.markdown("*{}*".format(thread.post_date.date()))
                st.markdown("## Q: {}".format(thread.question['content']))
                st.markdown("### A: {} ".format(thread.answer['content']))
                comment_box = st.expander("💬 Open comments")
                st_disqus(shortname="gurukul.streamlit.app", url=thread._id.int)
                # # Show comments
                # comment_box.write("**Comments:**")
                # for comment_dict in thread.comments:
                #     comment = Comment(**comment_dict)
                #     comment_box.markdown("{} - {}> {}".format(comment.userid,
                #                 comment.post_date, comment.comment))
                # with st.form("comment_box" + str(thread._id), clear_on_submit=True, border=True):
                #     comment_text = st.text_input("Enter comment here")
                #     submitted = st.form_submit_button(
                #         ":green[Post Comment]")
                #     if submitted:
                #         if comment_text == "":
                #             st.toast(":red[☝️ Your comment cannot be empty.]")
                #         else:
                #             comment = Comment(
                #                 _id=uuid4(), comment=comment_text, post_date=datetime.now(), userid="test_user")
                #             if add_comment_to_forum(thread, comment):
                #                 comment_box.write(
                #                     "{} - {}> {}".format(comment.userid, comment.post_date, comment.comment))
                #                 st.toast(":green[☝️ Your comment was successfully posted.]")

if 'forum_render' in st.session_state:
    st.title("📝 Gurukul Forum")
    render_forum()

set_rendering_on()