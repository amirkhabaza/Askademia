import sys
import os
# Add project root to sys.path to allow sibling imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.mongo_client import get_db
from embeddings.embedder import embed

# Constants
DB_NAME = "Classroom-qna"  # Should match index_setup.py
COLL_NAME = "syllabus_chunks" # Should match index_setup.py and loader.py
INDEX_NAME = "syllabus_emb"   # Should match index_setup.py
NUM_CANDIDATES = 100         # Atlas Search parameter (higher means more initial docs considered)
LIMIT = 5                    # Number of relevant chunks to return

def retrieve_context(user_query: str) -> str:
    """
    Embeds the user query and performs a vector search in MongoDB 
    to retrieve relevant document chunks.
    Returns a formatted string containing the context.
    """
    try:
        db = get_db() # Get database object
        coll = db[COLL_NAME]

        # 1. Embed the user query
        query_embedding = embed(user_query)

        # 2. Perform Vector Search
        # Note: Ensure your Atlas Search index (syllabus_emb) is built and active
        search_stage = {
            "$vectorSearch": {
                "index": INDEX_NAME,
                "path": "embedding", # Field containing the vectors
                "queryVector": query_embedding,
                "numCandidates": NUM_CANDIDATES,
                "limit": LIMIT
            }
        }

        # Optional: Add a projection stage to only return necessary fields
        projection_stage = {
            "$project": {
                "_id": 0,           # Exclude the default _id field
                "chunk": 1,         # Include the text chunk
                "score": {"$meta": "vectorSearchScore"} # Include the search score
            }
        }

        pipeline = [search_stage, projection_stage]
        
        results = list(coll.aggregate(pipeline))

        # 3. Format the results into a context string
        if not results:
            return "No relevant context found in the course material."

        # Use newline character directly
        context_str = "\n---\n".join([f"Chunk (Score: {res['score']:.4f}):\n{res['chunk']}" for res in results])
        return context_str

    except Exception as e:
        # Basic error handling, consider adding logging
        print(f"Error during context retrieval: {e}")
        return "Error retrieving context from the database."

# Example Usage (optional, for testing)
if __name__ == '__main__':
    test_query = "Summarize the main points of Lecture 3." 
    print(f"Retrieving context for query: '{test_query}'")
    context = retrieve_context(test_query)
    # Use newline character directly
    print(f"\nRetrieved Context:\n{context}") 