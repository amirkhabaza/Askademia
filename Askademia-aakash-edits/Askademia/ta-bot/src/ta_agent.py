import sys
import os
# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import logging
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low

# Import RAG components and models
from src.rag_handler import retrieve_context
from src.gemini_handler import generate_response
from prompts.ta_system_prompts import TA_SYSTEM_PROMPT
from src.models import StudentQuery, TAResponse, ErrorResponse

# Import configuration
import config

# --- Agent Configuration (from config.py) ---
AGENT_NAME = config.TA_AGENT_NAME
AGENT_SEED = config.TA_AGENT_SEED
AGENT_PORT = config.TA_AGENT_PORT
AGENT_ENDPOINT = config.TA_AGENT_ENDPOINT

# Initialize Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(AGENT_NAME)

# Initialize Agent
ta_agent = Agent(
    name=AGENT_NAME,
    seed=AGENT_SEED,
    port=AGENT_PORT, # Set the agent's port
    endpoint=AGENT_ENDPOINT # Set the agent's endpoint
)

# Fund agent on Testnet if needed (optional, for network interaction)
# fund_agent_if_low(ta_agent.wallet.address())

# --- Protocol Definition (Optional but good practice) ---
# You can define a protocol to structure interactions further
# For simplicity now, we'll handle messages directly
# ta_protocol = Protocol("TAInteraction")

# --- Message Handler ---
@ta_agent.on_message(model=StudentQuery)
async def handle_student_query(ctx: Context, sender: str, msg: StudentQuery):
    logger.info(f"Received query from {sender}: '{msg.query}'")

    # 1. Retrieve Context
    logger.info("Retrieving context...")
    context = retrieve_context(msg.query)
    
    # Handle retrieval errors
    if context.startswith("Error") or context.startswith("No relevant context"):
        logger.warning(f"Context retrieval issue: {context}")
        await ctx.send(sender, ErrorResponse(error=context))
        return
    
    logger.info(f"Retrieved context successfully. Snippet: {context[:100]}...")

    # 2. Generate Response
    logger.info("Generating response using Gemini...")
    final_response_text = generate_response(
        system_prompt=TA_SYSTEM_PROMPT,
        user_query=msg.query,
        context=context
    )

    # Handle generation errors (generate_response returns specific strings on error)
    if final_response_text.startswith("Sorry") or final_response_text.startswith("I could not"):
        logger.error(f"Gemini generation failed: {final_response_text}")
        await ctx.send(sender, ErrorResponse(error=final_response_text))
        return
    
    # 3. Send Response
    logger.info(f"Sending response to {sender}")
    await ctx.send(sender, TAResponse(answer=final_response_text))

# --- Run Logic (typically in a separate main.py) ---
# This part would usually be in a main script
if __name__ == "__main__":
    logger.info(f"TA Agent Name: {AGENT_NAME}")
    logger.info(f"TA Agent Address: {ta_agent.address}")
    logger.info(f"TA Agent Configured Endpoint: {AGENT_ENDPOINT}")
    logger.info(f"Starting TA Agent '{AGENT_NAME}' on port {AGENT_PORT}...")
    ta_agent.run() # This will block and run the agent