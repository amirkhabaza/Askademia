import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

# --- General --- 
# Database connection string (loaded from .env)
MONGO_URI = os.getenv("MONGO_URI")
# Gemini API Key (loaded from .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- TA Agent Configuration ---
TA_AGENT_NAME = "askademia_ta_agent"
# It's better practice to load sensitive seeds from environment variables
TA_AGENT_SEED = os.getenv("TA_AGENT_SEED", "askademia_ta_default_dev_seed") 
TA_AGENT_PORT = 8001 # Default port for the TA agent
TA_AGENT_ENDPOINT = f"http://localhost:{TA_AGENT_PORT}/submit" # Default local endpoint
# You might want to make the endpoint configurable via environment variables too:
# TA_AGENT_ENDPOINT = os.getenv("TA_AGENT_ENDPOINT", f"http://localhost:{TA_AGENT_PORT}/submit")

# --- Test Student Agent Configuration ---
STUDENT_AGENT_NAME = "test_student_agent"
STUDENT_AGENT_SEED = os.getenv("STUDENT_AGENT_SEED", "test_student_default_dev_seed")
STUDENT_AGENT_PORT = 8002 # Default port for the student agent if it needs one
STUDENT_AGENT_ENDPOINT = f"http://localhost:{STUDENT_AGENT_PORT}/submit"

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_API_TOKEN = os.getenv("CANVAS_API_TOKEN")

CANVAS_COURSE_IDS = {
    "SP25: DATA-201 Sec 22 - Database Tech for DA": "1606393", # Replace with your actual Course Name: Course ID mapping
    # "ANOTHER_COURSE": "987654" 
} 