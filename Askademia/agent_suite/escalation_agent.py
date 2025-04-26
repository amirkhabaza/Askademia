import asyncio
# Use the new google-genai library
from google import genai
from google.genai import types

from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

import config
from models import AmbiguousQuestion, EscalationInfo # Import necessary models

# Instantiate the client globally
client = genai.Client(api_key=config.GEMINI_API_KEY)
gemini_model_name = 'gemini-2.5-pro-exp-03-25' # Use the specified 2.5 pro model

escalation_agent = Agent(
    name=config.ESCALATION_AGENT_NAME,
    port=config.ESCALATION_AGENT_PORT,
    endpoint=["http://localhost:{}/submit".format(config.ESCALATION_AGENT_PORT)],
    seed=config.ESCALATION_AGENT_NAME + " seed",
)

fund_agent_if_low(escalation_agent.wallet.address())

async def summarize_for_ta(question: AmbiguousQuestion) -> EscalationInfo:
    """Summarizes the ambiguous question context for the TA using Gemini."""
    prompt = f"""A student asked a question that the Student Agent found ambiguous.
    Reason for ambiguity: {question.reason}
    Original Question: {question.original_question}

    Please provide a very brief summary for a Teaching Assistant (TA) dashboard.
    Include the original question and the reason for ambiguity.
    """
    try:
        # Construct the request using the new types
        contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
        # Use the client to generate content
        response = client.models.generate_content(model=gemini_model_name, contents=contents)
        summary = response.text.strip()
    except Exception as e:
        summary = f"Error generating summary: {e}"

    return EscalationInfo(
        summary=summary,
        original_question=question.original_question
        # student_id could potentially be added if passed in AmbiguousQuestion
    )

escalation_proto = Protocol("EscalationProtocol")

@escalation_proto.on_message(model=AmbiguousQuestion)
async def handle_ambiguous_question(ctx: Context, sender: str, msg: AmbiguousQuestion):
    ctx.logger.info(f"Received ambiguous question from {sender}: '{msg.original_question}'")

    escalation_details = await summarize_for_ta(msg)

    ctx.logger.info("Sending summarized info to TA Dashboard (simulation)")
    ctx.logger.info(f"Summary: {escalation_details.summary}")
    ctx.logger.info(f"Original Question: {escalation_details.original_question}")

    # TODO: Implement actual sending to TA Dashboard API
    # try:
    #     async with httpx.AsyncClient() as client:
    #         await client.post("TA_DASHBOARD_ESCALATION_ENDPOINT", json=escalation_details.dict())
    #     ctx.logger.info("Successfully sent escalation info to TA Dashboard")
    # except Exception as e:
    #     ctx.logger.error(f"Failed to send escalation info to TA dashboard: {e}")
    pass

@escalation_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f'{config.ESCALATION_AGENT_NAME} started!')
    ctx.logger.info(f"Address: {ctx.agent.address}")
    # config.ESCALATION_AGENT_ADDRESS = ctx.agent.address

escalation_agent.include(escalation_proto)

if __name__ == "__main__":
    escalation_agent.run()
