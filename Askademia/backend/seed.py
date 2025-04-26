import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
db = MongoClient(os.getenv("MONGODB_URI")).askademia

# Remove old test student, then insert fresh
db.students.delete_one({"_id": "student1"})
db.students.insert_one({
    "_id": "student1",
    "name": "Test Student",
    "weakTopics": ["algebra", "calculus"]
})
print("✅ Seeded student1")