# File: send_vision_question.py
import asyncio
from uagents import Agent, Context
from models import Question # Make sure models.py is accessible and updated

# Replace with the actual address of your running StudentAgent
STUDENT_AGENT_ADDRESS = "agent1qf0fyw5akprk7gz9262r5pcd37xjzmuq38lkknajqk7syahzs2xhvhllqt7" # From your logs

# --- Configuration for Vision Question ---
# Replace with a publicly accessible image URL
TEST_IMAGE_URL = "https://storage.googleapis.com/generativeai-downloads/images/scones.jpg"
TEST_QUESTION_TEXT = "What is shown in this image?"
# -----------------------------------------

# Use a different port for this test agent if running simultaneously with others
test_vision_sender = Agent(
    name="test_vision_sender",
    port=8004, # Changed port
    endpoint=['http://localhost:8004/submit']
)

@test_vision_sender.on_event("startup")
async def send_question(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address is {ctx.agent.address}')
    ctx.logger.info(f"Sending vision question to {STUDENT_AGENT_ADDRESS}")
    try:
        await ctx.send(
            STUDENT_AGENT_ADDRESS,
            Question(
                text=TEST_QUESTION_TEXT,
                student_id="test_vision_user_001",
                image_url=TEST_IMAGE_URL # Include the image URL
            )
        )
        ctx.logger.info("Vision question sent.")
    except Exception as e:
        ctx.logger.error(f"Failed to send message: {e}")
    # Optional: Stop the test agent after sending
    # await asyncio.sleep(2.0)
    # ctx.stop()

if __name__ == "__main__":
    test_vision_sender.run() 