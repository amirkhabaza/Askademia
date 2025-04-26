import os
from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file if it exists

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

# Agent Configurations
STUDENT_AGENT_PORT = 8000
STUDENT_AGENT_NAME = "StudentAgent"

QUIZ_AGENT_PORT = 8001
QUIZ_AGENT_NAME = "QuizAgent"

ESCALATION_AGENT_PORT = 8002
ESCALATION_AGENT_NAME = "EscalationAgent"

# Agent Addresses (Replace with actual addresses after startup)
# These will be printed to the console when each agent starts.
STUDENT_AGENT_ADDRESS = "agent1qf0fyw5akprk7gz9262r5pcd37xjzmuq38lkknajqk7syahzs2xhvhllqt7"
QUIZ_AGENT_ADDRESS = "agent1qtdn9lrrc02wmgu84q29lm879tlqxy5s0pjsak4jlnjlm2g3ulzx77unsyt"
# config.py
# ... other configurations ...

ESCALATION_AGENT_ADDRESS = "agent1qg66qg4juuhp5qv49j6ml9aye2294lmk9ln9j5m4fdeae5xctu2nyl3edjq"

# ... rest of the configurations ...