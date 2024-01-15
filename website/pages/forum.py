import streamlit as st
import pymongo
from dataclasses import dataclass, asdict
from uuid import uuid4
from datetime import datetime

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
    read_forum_data.clear()
    
def add_comment_to_forum(thread: ForumThread, comment: Comment):
    threads_collection = client.test.threads
    thread.comments.append(comment)
    threads_collection.find_one_and_update(thread)
    read_forum_data.clear()

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after 1 min.
@st.cache_data(ttl=60)
def read_forum_data():
    items = client.test.threads.find()
    items = list(items)  # make hashable for st.cache_data
    threads = [ForumThread(**item) for item in items]
    return threads

if 'forum_render' in st.session_state:
    st.title("📝 Gurukul Forum")
    threads = read_forum_data()
    with st.container(border=True):
        st.markdown("# All Threads")
        for thread in threads:
            with st.container(border=True):
                st.markdown("*{}*".format(thread.post_date.date()))
                st.markdown("## Q: {}".format(thread.question['content']))
                st.markdown("### A: {} ".format(thread.answer['content']))
                with st.expander("💬 Open comments"):
                    # Show comments
                    st.write("**Comments:**")
                    for comment in thread.comments:
                        st.markdown("{} - {}> {}".format(comment.userid, comment.post_date, comment.comment))
                    if len(thread.comments) > 0:
                        st.success("☝️ Your comment was successfully posted.")