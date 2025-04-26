import asyncio
# Use the new google-genai library
from google import genai
from google.genai import types
import httpx # Added for fetching image URLs

from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

import config
from models import Question, Answer, PerformanceData, AmbiguousQuestion, EscalationInfo, Quiz # Import necessary models

# Instantiate the client globally
client = genai.Client(api_key=config.GEMINI_API_KEY)
gemini_model_name = 'gemini-2.5-pro-exp-03-25' # Use the specified 2.5 pro model

student_agent = Agent(
    name=config.STUDENT_AGENT_NAME,
    port=config.STUDENT_AGENT_PORT,
    endpoint=["http://localhost:{}/submit".format(config.STUDENT_AGENT_PORT)],
    seed=config.STUDENT_AGENT_NAME + " seed", # Optional but good for reproducible addresses
)

fund_agent_if_low(student_agent.wallet.address())

# Pass ctx for logging within the function
async def analyze_question(ctx: Context, question_text: str, image_url: str | None = None) -> dict:
    """Analyzes question clarity (and image context if provided) and generates answer using Gemini."""
    prompt = f"""Analyze the following student question, potentially referring to the provided image.
    1. Is the question clear and answerable directly (considering the image if provided)? (Answer YES or NO)
    2. If YES, provide a concise answer.
    3. If NO, briefly explain why it's ambiguous.

    Question: {question_text}

    Response format:
    Clarity: [YES/NO]
    Answer/Reason: [Your answer or explanation]
    """
    try:
        parts = [types.Part.from_text(text=prompt)]

        if image_url:
            ctx.logger.info(f"Fetching image from URL: {image_url}") # Added logging for image fetch
            try:
                # Rename local variable to avoid shadowing global Gemini client
                async with httpx.AsyncClient() as http_client:
                    response = await http_client.get(image_url, timeout=10.0) # Added timeout
                    response.raise_for_status() # Raise HTTP errors
                    image_data = response.content
                    mime_type = response.headers.get('content-type', 'image/jpeg') # Default mime type if not found
                    parts.append(types.Part.from_data(data=image_data, mime_type=mime_type))
            except httpx.RequestError as exc:
                 ctx.logger.error(f"HTTP Exception for {exc.request.url} - {exc}")
                 return {"clear": False, "detail": f"Error fetching image: {exc}"}
            except Exception as img_exc: # Catch other potential errors during image processing
                ctx.logger.error(f"Error processing image from {image_url}: {img_exc}")
                return {"clear": False, "detail": f"Error processing image: {img_exc}"}

        contents = [types.Content(role="user", parts=parts)]

        response = client.models.generate_content(model=gemini_model_name, contents=contents)

        # Basic parsing (improve with regex or more robust parsing if needed)
        lines = response.text.strip().split('\n')
        clarity_line = next((line for line in lines if line.startswith('Clarity:')), "Clarity: NO")
        answer_reason_line = next((line for line in lines if line.startswith('Answer/Reason:')), "Answer/Reason: Could not process")

        is_clear = "YES" in clarity_line
        detail = answer_reason_line.split(':', 1)[1].strip()

        return {"clear": is_clear, "detail": detail}
    except Exception as e:
        # Log the specific error for better debugging
        ctx.logger.error(f"Error during Gemini API call or parsing: {e}", exc_info=True)
        return {"clear": False, "detail": f"Error analyzing question: {e}"}

student_proto = Protocol("StudentProtocol")

@student_proto.on_message(model=Question)
async def handle_question(ctx: Context, sender: str, msg: Question):
    log_message = f"Received question from {msg.student_id}: '{msg.text}'"
    if msg.image_url:
        log_message += f" with image: {msg.image_url}"
    ctx.logger.info(log_message)

    # Pass ctx, text and image_url to the analysis function
    analysis = await analyze_question(ctx, msg.text, msg.image_url)

    if analysis["clear"]:
        answer_text = analysis["detail"]
        ctx.logger.info(f"Sending answer: {answer_text}")
        # In a real system, you'd send this back to the student source
        # For now, just log it. await ctx.send(sender, Answer(text=answer_text))
        pass # Placeholder for sending answer back to student interface
    else:
        reason = analysis["detail"]
        ctx.logger.warning(f"Question ambiguous: {reason}. Escalating.")
        if not config.ESCALATION_AGENT_ADDRESS:
            ctx.logger.error("Escalation Agent address not configured.")
            return
        await ctx.send(
            config.ESCALATION_AGENT_ADDRESS,
            AmbiguousQuestion(original_question=msg.text, reason=reason) # Consider adding image_url here too if needed
        )

@student_proto.on_message(model=PerformanceData)
async def handle_performance_data(ctx: Context, sender: str, msg: PerformanceData):
    ctx.logger.info(f"Received performance data for student {msg.student_id} on quiz {msg.quiz_id}: Score {msg.score}")
    # TODO: Store performance data, potentially update TA Dashboard
    # Example: Send data to TA dashboard (replace with actual API call)
    # try:
    #     async with httpx.AsyncClient() as client:
    #         await client.post("TA_DASHBOARD_API_ENDPOINT", json=msg.dict())
    # except Exception as e:
    #     ctx.logger.error(f"Failed to send performance data to TA dashboard: {e}")
    pass

# Example of how Student Agent might initiate a Quiz
@student_proto.on_interval(period=3600.0) # Example: Trigger every hour
async def maybe_send_quiz(ctx: Context):
    # Logic to decide if/when to send a quiz
    send_quiz_now = False # Replace with actual logic
    if send_quiz_now and config.QUIZ_AGENT_ADDRESS:
        ctx.logger.info("Requesting quiz generation or distribution...")
        # This interaction needs refinement - does Student Agent *request* a quiz?
        # Or does Quiz Agent proactively send quizzes? Assuming Quiz Agent sends for now.
        # Maybe Student Agent sends a trigger message?
        # await ctx.send(config.QUIZ_AGENT_ADDRESS, RequestQuiz(...))
        pass

@student_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f'{config.STUDENT_AGENT_NAME} started!')
    ctx.logger.info(f"Address: {ctx.agent.address}")
    # Set the address in config if needed (for testing/dynamic setup)
    # config.STUDENT_AGENT_ADDRESS = ctx.agent.address

student_agent.include(student_proto)

if __name__ == "__main__":
    student_agent.run()
