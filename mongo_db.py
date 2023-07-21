import pymongo
from pymongo import errors
from datetime import datetime
from dateutil.relativedelta import relativedelta
from calendar import month_name
from typing import Dict
import logging
logger = logging.getLogger(__name__)


# connect to the database
logger.info("Connection to database...")
client = pymongo.MongoClient()  # localhost:27017
logger.info("Successfully connected to MongoDB")
articles_db = client.articles

article_collections = {}


def get_article_collection(coll_name):
    global article_collections, articles_db
    if coll_name not in article_collections:
        if coll_name not in articles_db.list_collection_names():
            logger.info(f"Collection '{coll_name}' not found... going to create and set index")
            articles_db.create_collection(coll_name)
            coll = articles_db[coll_name]
            # set the title as a unique index
            coll.create_index([("title", pymongo.ASCENDING)], unique=True)
        article_collections[coll_name] = articles_db[coll_name]
    return article_collections[coll_name]


def find(coll_name, search_criteria=None):
    coll = get_article_collection(coll_name)
    if search_criteria:
        return coll.find(search_criteria)
    return coll.find()


def select_for_backup(coll_name):
    coll = get_article_collection(coll_name)
    return coll.find(projection={"_id": 0})


def get_count(coll_name):
    coll = get_article_collection(coll_name)
    return coll.count_documents({})


def is_empty(coll_name):
    return get_count(coll_name) == 0


def group_by_month(coll_name):
    coll = get_article_collection(coll_name)
    oldest = coll.find().sort("published", 1).limit(1)[0]["published"]
    newest = get_latest_article_date(coll_name)
    start_month = datetime(oldest.year, oldest.month, 1, 0, 0, 0)
    start_next_month = start_month + relativedelta(months=1)
    ret = []  # List of tuple of year, month, list of map (documents)
    ret.append((start_month.year,
                start_month.month,
                [doc for doc in coll.find({"published": {"$gte": start_month, "$lt": start_next_month}})]))
    while start_next_month < newest:
        start_month = start_next_month
        start_next_month = start_month + relativedelta(months=1)
        ret.append((start_month.year,
                    start_month.month,
                    [doc for doc in coll.find({"published": {"$gte": start_month, "$lt": start_next_month}})]))
    return ret


def group_by_section(coll_name) -> Dict[str, Dict]:
    coll = get_article_collection(coll_name)
    grouped = {}
    for doc in coll.find().sort("section", 1):
        if doc["section"] in grouped:
            grouped[doc["section"]].append(doc)
        else:
            grouped[doc["section"]] = [doc]
    return grouped


def get_latest_article_date(coll_name):
    coll = get_article_collection(coll_name)
    return coll.find().sort("published", -1).limit(1)[0]["published"]


def insert_many(coll_name, docs):
    if not docs: return
    coll = get_article_collection(coll_name)
    try:
        result = coll.insert_many(docs, ordered=False)
        print(f"insert_many: Bulk operation success: {result}")
        logger.info(f"Bulk operation success: {result}")

    except errors.BulkWriteError as err:
        print(f"insert_many: Bulk operation finished with errors: {err.args}")
        logger.info(f"Bulk operation finished with errors: {err.args}")


def update(coll_name, doc):
    coll = get_article_collection(coll_name)
    coll.update_one({"_id": doc["_id"]}, {"$set": doc})


def delete_one(coll_name, doc):
    coll = get_article_collection(coll_name)
    coll.delete_one(doc)


if __name__ == "__main__":
    for year, month, docs in group_by_month("twenty_minutes"):
        print(f"{month_name[month]} {year}: {len(docs)} documents")
