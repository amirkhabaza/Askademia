import os
from dotenv import load_dotenv
from pymongo import MongoClient
from uagents import Agent, Context, Model

load_dotenv()
db = MongoClient(os.getenv("MONGODB_URI")).askademia

class Escalation(Model):
    student_id: str
    question: str

agent = Agent(name="EscalationAgent", seed="seed3")

@agent.on_message(model=Escalation)
async def on_escalation(ctx: Context, msg: Escalation):
    db.escalations.insert_one({
        "student_id": msg.student_id,
        "question": msg.question,
        "status": "pending"
    })
    await ctx.send(msg, {"ack": "Escalated to TA."})

if __name__=="__main__":
    agent.run()