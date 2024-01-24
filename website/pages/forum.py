import streamlit as st
import pymongo
from dataclasses import dataclass, asdict
from uuid import uuid4
from datetime import datetime
from streamlit_disqus import st_disqus
from website.footer import footer_html

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
    threads_collection = client.test.threads

    existing_thread = threads_collection.find_one({"question": question})

    if existing_thread:
        # Thread with the same question exists
        if existing_thread["answer"] != answer:
            # Answer is different, update the post_date
            threads_collection.update_one({"_id": existing_thread["_id"]}, {"$set": {"post_date": datetime.now()}})
        # else: answer is the same, or update_if_exists is False, do nothing
    else:
        # Thread doesn't exist, insert a new one
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
    items = client.test.threads.find().sort('post_date',pymongo.DESCENDING)
    items = list(items)  # make hashable for st.cache_data
    threads = [ForumThread(**item) for item in items]
    return threads

def get_random_threads():
    items = client.test.threads.aggregate([{ "$sample": { "size": 3 } }])
    return [ForumThread(**item) for item in items]

def render_forum():
    with st.sidebar:
        st.markdown(footer_html, unsafe_allow_html=True)
    threads = read_forum_data()
    with st.container(border=False):
        for thread in threads:
            with st.container(border=True):
                st.markdown("*{}*".format(thread.post_date.date()))
                st.markdown("## Q: {}".format(thread.question['content']))
                st.markdown("### A: {} ".format(thread.answer['content']))
                comment_box = st.expander("💬 Open comments")
                # st_disqus(shortname="gurukul-streamlit-app", identifier=thread._id.int, url="https://gurukul.streamlit.app/forum#" + str(thread._id.int), title=thread.question)
                # Show comments
                comment_box.write("**Comments:**")
                for comment_dict in thread.comments:
                    comment = Comment(**comment_dict)
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
                            comment = Comment(
                                _id=uuid4(), comment=comment_text, post_date=datetime.now(), userid="test_user")
                            if add_comment_to_forum(thread, comment):
                                comment_box.write(
                                    "{} - {}> {}".format(comment.userid, comment.post_date, comment.comment))
                                st.toast(":green[☝️ Your comment was successfully posted.]")


set_rendering_on()

if 'forum_render' in st.session_state:
    st.title("📝 Gurukul Forum")
    render_forum()
