import sys
import os

# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from pymongo.errors import ConnectionFailure

# Import DB utility and configuration
try:
    from db.mongo_client import get_db
    import config
except ImportError as e:
    print(f"Error importing necessary modules: {e}")
    print("Please ensure db/mongo_client.py and config.py exist and are correct.")
    sys.exit(1)

def check_documents():
    """
    Connects to MongoDB and lists the distinct filenames found in the collection.
    """
    try:
        db = get_db() # Get database object
        # Use collection name from config if available, otherwise default
        collection_name = getattr(config, 'COLL_NAME', 'syllabus_chunks') 
        coll = db[collection_name]

        print(f"Checking collection '{db.name}.{collection_name}' for distinct document filenames...")

        # Find distinct values in the 'file' field
        distinct_files = coll.distinct("file")

        if not distinct_files:
            print("No documents found in the collection (based on the 'file' field).")
        else:
            print("\nFound the following document filenames in the database:")
            for filename in sorted(distinct_files):
                print(f"- {filename}")
            print(f"\nTotal distinct files found: {len(distinct_files)}")

    except ConnectionFailure:
        print("Error: Could not connect to MongoDB.")
        print("Please ensure MongoDB is running and the MONGO_URI in your .env file is correct.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_documents() 