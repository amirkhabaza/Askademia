import sys
import os
import asyncio

# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import logging
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Import shared models and config
from src.models import StudentQuery, TAResponse, ErrorResponse
import config

# --- Agent Configuration (from config.py) ---
AGENT_NAME = config.STUDENT_AGENT_NAME
AGENT_SEED = config.STUDENT_AGENT_SEED
AGENT_PORT = config.STUDENT_AGENT_PORT
AGENT_ENDPOINT = config.STUDENT_AGENT_ENDPOINT

# Get TA agent address from config or environment (assuming TA address is known)
# In a real scenario, you might use discovery (Almanac)
TA_AGENT_ADDRESS = os.getenv("TA_AGENT_ADDRESS") 
if not TA_AGENT_ADDRESS:
    # Attempt to get it from a running TA agent instance (less reliable for deployment)
    # This requires the TA agent to be running with the default seed when this starts
    # A better approach is setting TA_AGENT_ADDRESS in .env or discovering via Almanac
    from uagents.resolver import Resolver
    from uagents.crypto import Identity
    print("Warning: TA_AGENT_ADDRESS not found in environment. Trying to resolve from default TA seed.")
    try:
        resolver = Resolver()
        # Assuming TA uses the seed from config
        ta_identity = Identity.from_seed(config.TA_AGENT_SEED, 0)
        TA_AGENT_ADDRESS = ta_identity.address
        print(f"Resolved TA Agent Address: {TA_AGENT_ADDRESS}")
    except Exception as e:
        print(f"Error resolving TA agent address: {e}. Please set TA_AGENT_ADDRESS environment variable.")
        TA_AGENT_ADDRESS = None # Ensure it's None if resolution fails


# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(AGENT_NAME)

# Initialize Agent
student_agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT,
    endpoint=AGENT_ENDPOINT,
)

# fund_agent_if_low(student_agent.wallet.address())

# --- Message Handlers ---
# Store the latest response received for the UI to potentially access
# Note: This simple storage might have race conditions if multiple UIs/queries overlap
# A more robust solution might involve request IDs and callbacks or a message queue.

@student_agent.on_message(model=TAResponse)
async def handle_ta_response(ctx: Context, sender: str, msg: TAResponse):
    logger.info(f"Received response from TA {sender}: {msg.answer[:100]}...")
    # Store the answer in agent's context storage
    ctx.storage.set("last_response", {"type": "success", "content": msg.answer})
    ctx.storage.set("response_ready", True)

@student_agent.on_message(model=ErrorResponse)
async def handle_error_response(ctx: Context, sender: str, msg: ErrorResponse):
    logger.error(f"Received error from TA {sender}: {msg.error}")
    # Store the error in agent's context storage
    ctx.storage.set("last_response", {"type": "error", "content": msg.error})
    ctx.storage.set("response_ready", True)

# --- Function for UI to Call --- 
# This function will be called (somehow) by the Streamlit UI
async def send_query_to_ta(ctx: Context, query_text: str):
    if not TA_AGENT_ADDRESS:
        logger.error("Cannot send query: TA Agent Address is not configured or resolved.")
        ctx.storage.set("last_response", {"type": "error", "content": "TA Agent address unknown."})
        ctx.storage.set("response_ready", True)
        return
        
    logger.info(f"Sending query to TA ({TA_AGENT_ADDRESS}): '{query_text}'")
    ctx.storage.set("response_ready", False) # Mark response as not ready
    ctx.storage.set("last_response", None)    # Clear previous response
    try:
        await ctx.send(TA_AGENT_ADDRESS, StudentQuery(query=query_text))
    except Exception as e:
        logger.error(f"Error sending query to TA: {e}")
        ctx.storage.set("last_response", {"type": "error", "content": f"Failed to send query: {e}"})
        ctx.storage.set("response_ready", True)

# Example of how UI *might* trigger this (Actual integration TBD in app.py)
# This requires the agent event loop to be running.
# @student_agent.on_interval(period=10.0) # Example trigger, NOT for final UI
# async def example_interval_send(ctx: Context):
#      if not ctx.storage.get("response_ready"): # Avoid sending if waiting
#          await send_query_to_ta(ctx, "Example interval query: What is the grading policy?")

# --- Main Execution (for standalone testing) ---
if __name__ == "__main__":
    logger.info(f"Student Agent Name: {AGENT_NAME}")
    logger.info(f"Student Agent Address: {student_agent.address}")
    logger.info(f"Student Agent Endpoint: {student_agent.endpoint}")
    if TA_AGENT_ADDRESS:
        logger.info(f"Target TA Agent Address: {TA_AGENT_ADDRESS}")
    else:
        logger.warning("TA Agent Address is not set. Agent will run but cannot send queries.")
    student_agent.run()
