import os
from dotenv import load_dotenv
from pymongo import MongoClient
from uagents import Agent, Context, Model

load_dotenv()
db = MongoClient(os.getenv("MONGODB_URI")).askademia
ASI_KEY = os.getenv("ASI_ONE_KEY")

class QuizRequest(Model):
    student_id: str

agent = Agent(name="QuizAgent", seed="seed2", llm_api_key=ASI_KEY)

@agent.on_message(model=QuizRequest)
async def on_quiz(ctx: Context, msg: QuizRequest):
    student = db.students.find_one({"_id": msg.student_id})
    topics  = student.get("weakTopics", [])
    prompt  = f"Generate 5 practice questions on: {', '.join(topics)}"
    resp    = await ctx.llm.complete(prompt)
    qs      = [q.strip() for q in resp.choices[0].text.split("\n") if q.strip()]
    db.quizzes.insert_one({"student_id": msg.student_id, "questions": qs})
    await ctx.send(msg, {"quiz": qs})

if __name__=="__main__":
    agent.run()