import asyncio
# Use the new google-genai library
from google import genai
from google.genai import types

from uagents import Agent, Context, Model, Protocol
from uagents.setup import fund_agent_if_low

import config
from models import Quiz, QuizSubmission, PerformanceData # Import necessary models

# Instantiate the client globally
client = genai.Client(api_key=config.GEMINI_API_KEY)
gemini_model_name = 'gemini-2.5-pro-exp-03-25' # Use the specified 2.5 pro model

quiz_agent = Agent(
    name=config.QUIZ_AGENT_NAME,
    port=config.QUIZ_AGENT_PORT,
    endpoint=["http://localhost:{}/submit".format(config.QUIZ_AGENT_PORT)],
    seed=config.QUIZ_AGENT_NAME + " seed",
)

fund_agent_if_low(quiz_agent.wallet.address())

# Placeholder for quiz content store
ACTIVE_QUIZZES = {}

async def evaluate_submission(submission: QuizSubmission) -> PerformanceData:
    """Evaluates a quiz submission. Can use Gemini for complex answers."""
    # Basic evaluation logic (replace with actual logic or Gemini call)
    # This example assumes simple multiple choice or keyword matching
    # For more complex evaluation (e.g., free text), use Gemini:
    # prompt = f"Evaluate the student's answers: {submission.answers} for the quiz questions: {ACTIVE_QUIZZES[submission.quiz_id].questions}. Provide a score (0-100) and brief feedback."
    # contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    # response = client.models.generate_content(model=gemini_model_name, contents=contents)
    # score = parse_gemini_score(response.text)
    # feedback = parse_gemini_feedback(response.text)

    score = 85.0 # Placeholder score
    feedback = "Good job!" # Placeholder feedback

    return PerformanceData(
        student_id=submission.student_id,
        quiz_id=submission.quiz_id,
        score=score,
        feedback=feedback
    )

quiz_proto = Protocol("QuizProtocol")

@quiz_proto.on_message(model=QuizSubmission)
async def handle_submission(ctx: Context, sender: str, msg: QuizSubmission):
    ctx.logger.info(f"Received quiz submission for quiz {msg.quiz_id} from student {msg.student_id}")

    # TODO: Validate quiz ID (check if ACTIVE_QUIZZES has msg.quiz_id)

    performance = await evaluate_submission(msg)

    ctx.logger.info(f"Sending performance data to Student Agent for student {msg.student_id}")
    if not config.STUDENT_AGENT_ADDRESS:
            ctx.logger.error("Student Agent address not configured.")
            return
    await ctx.send(config.STUDENT_AGENT_ADDRESS, performance)

# Example: Quiz agent could periodically generate and send quizzes
# Or respond to requests from Student Agent
@quiz_proto.on_interval(period=7200.0) # Example: Every 2 hours
async def distribute_quiz(ctx: Context):
    # Logic to generate or select a quiz
    quiz_id = f"quiz_{int(asyncio.get_event_loop().time())}"
    new_quiz = Quiz(quiz_id=quiz_id, questions=["What is 1+1?", "Explain Fetch.ai Agents."])
    ACTIVE_QUIZZES[quiz_id] = new_quiz # Store quiz details

    # Logic to determine who receives the quiz (e.g., all students, specific group)
    # For now, just logs. In reality, might send to Student Agent or directly to student interfaces.
    ctx.logger.info(f"Generated quiz {quiz_id}. Ready for distribution.")
    # Example: Send to student agent to handle distribution logic
    # if config.STUDENT_AGENT_ADDRESS:
    #    await ctx.send(config.STUDENT_AGENT_ADDRESS, new_quiz)
    pass


@quiz_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f'{config.QUIZ_AGENT_NAME} started!')
    ctx.logger.info(f"Address: {ctx.agent.address}")
    # config.QUIZ_AGENT_ADDRESS = ctx.agent.address

quiz_agent.include(quiz_proto)

if __name__ == "__main__":
    quiz_agent.run()
