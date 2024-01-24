import pymongo
from dataclasses import dataclass, asdict
from datetime import datetime
from uuid import uuid4, UUID
import streamlit as st


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


# Initialize connection.
@st.cache_resource
def get_mongo_client():
    return pymongo.MongoClient(st.secrets['MONGO_DB_CONNECTION_URL'], uuidRepresentation='standard')

def find_thread_by_id(client, id: str):
    threads_collection = client.test.threads
    thread_dict = threads_collection.find_one({"_id": UUID(id)})
    if thread_dict:
        return ForumThread(**thread_dict)

def post_thread(client: pymongo.MongoClient, question: str, answer: str):
    threads_collection = client.test.threads

    # TODO: Use find_many . same qn can be for multiple combination of sources
    existing_thread = threads_collection.find_one({"question": question})

    if existing_thread:
        # Thread with the same question exists
        if existing_thread["answer"] != answer:
            # Answer is different, update the post_date
            threads_collection.update_one({"_id": existing_thread["_id"]}, {
                                          "$set": {"post_date": datetime.now()}})
        return existing_thread["_id"]
    else:
        # Thread doesn't exist, insert a new one
        st.toast("Created new forum thread.")
        new_id = uuid4()
        add_thread_to_forum(client, ForumThread(_id=new_id, question=question, answer=answer, comments=[], post_date=datetime.now()))
        return new_id


def add_thread_to_forum(client: pymongo.MongoClient, thread: ForumThread):
    threads_collection = client.test.threads
    threads_collection.insert_one(asdict(thread))


def add_comment_to_forum(client: pymongo.MongoClient, thread: ForumThread, comment: Comment):
    threads_collection = client.test.threads
    thread.comments.append(comment)
    return threads_collection.find_one_and_update(filter={'_id': thread._id}, update={
        '$push': {'comments': asdict(comment)}}, upsert=True)

# Pull data from the collection.
# Uses st.cache_data to only rerun when the query changes or after ttl


@st.cache_data(ttl=10)
def read_forum_data(_client: pymongo.MongoClient, ):
    items = _client.test.threads.find().sort('post_date', pymongo.DESCENDING)
    items = list(items)  # make hashable for st.cache_data
    threads = [ForumThread(**item) for item in items]
    return threads


def get_random_threads(client: pymongo.MongoClient, ):
    items = client.test.threads.aggregate([{"$sample": {"size": 3}}])
    return [ForumThread(**item) for item in items]
