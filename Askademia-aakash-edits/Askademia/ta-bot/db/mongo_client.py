import os, pymongo
_client = None

def get_db():
    global _client
    if not _client:
        _client = pymongo.MongoClient(os.getenv("MONGODB_URI"))
    return _client["Classroom-qna"]          # single DB

print(get_db().list_collection_names())
