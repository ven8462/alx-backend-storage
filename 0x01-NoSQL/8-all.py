#!/usr/bin/env python3
""" pymongo + NoSQL module """

from pymongo import MongoClient


def list_all(mongo_collection):
    """list all documents in a collection"""
    return ([] if mongo_collection.count_documents({}) == 0 else
            list(mongo_collection.find()))


if __name__ == "__main__":
    client = MongoClient('mongodb://127.0.0.1:27017')
    school_collection = client.my_db.school
    schools = list_all(school_collection)
    for school in schools:
        print("[{}] {}".format(school.get('_id'), school.get('name')))
