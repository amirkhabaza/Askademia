# db/index_setup.py
"""
Run once on an empty cluster or anytime you want to (re-)create the
Atlas Vector Search index for the TA-bot project.
"""
import sys
from pymongo.operations import SearchIndexModel        # needs PyMongo ≥ 4.6
from mongo_client import get_db

DB_NAME        = "Classroom-qna"
COLL_NAME      = "syllabus_chunks"
INDEX_NAME     = "syllabus_emb"
EMBEDDING_SIZE = 768            # Gemini returns 768-D vectors

def ensure_collection():
    db = get_db()
    if COLL_NAME not in db.list_collection_names():
        db.create_collection(COLL_NAME)                # empty stub
    return db[COLL_NAME]

def ensure_vector_index(coll):
    # ——— definition per Atlas docs ———
    vector_def = {
        "fields": [
            {
                "type":        "vector",
                "path":        "embedding",
                "numDimensions": EMBEDDING_SIZE,
                "similarity":  "cosine"
            }
        ]
    }

    model = SearchIndexModel(
        name       = INDEX_NAME,
        definition = vector_def,
        type       = "vectorSearch"
    )
    coll.create_search_index(model=model)              # async build on Atlas

def main():
    coll = ensure_collection()
    ensure_vector_index(coll)
    print("✔ Vector index creation requested. Check Atlas UI for status.")

if __name__ == "__main__":
    sys.exit(main())
