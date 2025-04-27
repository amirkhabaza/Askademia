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
TA_AGENT_ADDRESS = None # Set via command-line argument

# Default query if none is provided via command line
DEFAULT_QUERY_TEXT = "What is the professor's name?"

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
    ctx.logger.info(f"Sending query to TA Agent {target_address}: '{DEFAULT_QUERY_TEXT}'")
    await ctx.send(target_address, StudentQuery(query=DEFAULT_QUERY_TEXT))

# --- Main Execution with Argument Parsing ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send a test query to the TA agent.")
    parser.add_argument("ta_address", type=str, help="The address of the running TA agent.")
    parser.add_argument("--query", type=str, default=DEFAULT_QUERY_TEXT, 
                        help=f"The query text to send (default: '{DEFAULT_QUERY_TEXT}')")
    args = parser.parse_args()

    TA_AGENT_ADDRESS = args.ta_address
    query_to_send = args.query # Get the query from args

    # Define the startup behavior *after* getting the address and query
    @sender_agent.on_event("startup")
    async def startup_event(ctx: Context):
        ctx.logger.info(f"Sending query to TA Agent {TA_AGENT_ADDRESS}: '{query_to_send}'")
        # Send the query from the arguments
        await ctx.send(TA_AGENT_ADDRESS, StudentQuery(query=query_to_send))

    print(f"Running Test Sender Agent '{SENDER_NAME}'")
    print(f"Target TA Agent: {TA_AGENT_ADDRESS}")
    print(f"Query: '{query_to_send}'") # Print the actual query being sent
    sender_agent.run() 