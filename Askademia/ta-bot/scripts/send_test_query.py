import sys
import os
import asyncio
import argparse
# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

# Import the message models and config
from src.models import StudentQuery, TAResponse, ErrorResponse
import config

# --- Configuration (from config.py) ---
TA_AGENT_ADDRESS = None # We will get this from the running agent instance later

# Query to send (keep allowing override here)
QUERY_TEXT = "What is the policy on late submissions?"
# QUERY_TEXT = "How is the final grade calculated?"

SENDER_NAME = config.STUDENT_AGENT_NAME
SENDER_SEED = config.STUDENT_AGENT_SEED

# --- Agent Setup ---
# Initialize sender agent using config
sender_agent = Agent(
    name=config.STUDENT_AGENT_NAME,
    seed=config.STUDENT_AGENT_SEED,
    port=config.STUDENT_AGENT_PORT,
    endpoint=config.STUDENT_AGENT_ENDPOINT
)

# fund_agent_if_low(sender_agent.wallet.address())

# --- Response Handlers ---
@sender_agent.on_message(model=TAResponse)
async def handle_ta_response(ctx: Context, sender: str, msg: TAResponse):
    ctx.logger.info(f"Received response from {sender}: {msg.answer}")
    # Consider shutting down after response
    # await asyncio.sleep(1.0) # Give time for logs to flush
    # ctx.stop()

@sender_agent.on_message(model=ErrorResponse)
async def handle_error_response(ctx: Context, sender: str, msg: ErrorResponse):
    ctx.logger.error(f"Received error from {sender}: {msg.error}")
    # ctx.stop()

# --- Get TA Address and Send Query ---
# We need the actual address of the *running* TA agent.
# The config holds its *intended* seed/name, but the address is generated.
# For testing, the easiest way is still to pass it as an argument or copy-paste.
# We'll add an argument parser for this.

async def send_query_to_address(ctx: Context, target_address: str):
    ctx.logger.info(f"Sending query to TA Agent {target_address}: '{QUERY_TEXT}'")
    await ctx.send(target_address, StudentQuery(query=QUERY_TEXT))

# --- Main Execution with Argument Parsing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a test query to the TA agent.")
    parser.add_argument("ta_address", type=str, help="The address of the running TA agent.")
    args = parser.parse_args()

    TA_AGENT_ADDRESS = args.ta_address

    # Define the startup behavior *after* getting the address
    @sender_agent.on_event("startup")
    async def startup_event(ctx: Context):
        await send_query_to_address(ctx, TA_AGENT_ADDRESS)

    print(f"Running Test Sender Agent '{SENDER_NAME}'")
    print(f"Target TA Agent: {TA_AGENT_ADDRESS}")
    print(f"Query: '{QUERY_TEXT}'")
    sender_agent.run() 