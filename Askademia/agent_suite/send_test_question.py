# File: send_test_question.py
from uagents import Agent, Context
from models import Question # Make sure models.py is accessible

# Replace with the actual address of your running StudentAgent
STUDENT_AGENT_ADDRESS = "agent1qf0fyw5akprk7gz9262r5pcd37xjzmuq38lkknajqk7syahzs2xhvhllqt7" # From your logs

test_sender = Agent(name="test_sender",
                    port = 8003,
                    endpoint = ['http://localhost:8003/submit'])

@test_sender.on_event("startup")
async def send_question(ctx: Context):
    ctx.logger.info(f'My name is {ctx.agent.name} and my address  is {ctx.agent.address}')
    ctx.logger.info(f"Sending test question to {STUDENT_AGENT_ADDRESS}")
    try:
        await ctx.send(
            STUDENT_AGENT_ADDRESS,
            Question(text="What is the meaning of life?", student_id="test_user_001")
        )
        ctx.logger.info("Question sent.")
    except Exception as e:
        ctx.logger.error(f"Failed to send message: {e}")
    # Optional: Stop the test agent after sending
    # await asyncio.sleep(2.0)
    # ctx.stop()


if __name__ == "__main__":
    test_sender.run()
