import os, requests
from dotenv import load_dotenv
from pymongo import MongoClient
from uagents import Agent, Context, Model

load_dotenv()
db = MongoClient(os.getenv("MONGODB_URI")).askademia
ASI_KEY   = os.getenv("ASI_ONE_KEY")
VISION_KEY = os.getenv("GEMINI_KEY")

class Question(Model):
    text: str
    student_id: str
    image_url: str = None

async def ocr(url):
    res = requests.post(
        f"https://vision.googleapis.com/v1/images:annotate?key={VISION_KEY}",
        json={"requests":[{"image":{"source":{"imageUri":url}},"features":[{"type":"TEXT_DETECTION"}]}]}
    ).json()
    return res["responses"][0]["fullTextAnnotation"]["text"]

agent = Agent(name="StudentAgent", seed="seed1", llm_api_key=ASI_KEY)

@agent.on_message(model=Question)
async def on_question(ctx: Context, msg: Question):
    # OCR if needed
    text = msg.text if not msg.image_url else await ocr(msg.image_url)
    # Prompt ASI:One
    prompt = f"You are a tutor. Solve step-by-step:\nQuestion: {text}"
    resp   = await ctx.llm.complete(prompt)
    answer = resp.choices[0].text.strip()
    probs  = resp.choices[0].logprobs.token_logprobs
    conf   = sum(probs)/len(probs)
    status = "answered" if conf>=0.8 else "escalated"
    # Persist
    db.questions.insert_one({
        "student_id": msg.student_id,
        "question": text,
        "answer": answer,
        "confidence": conf,
        "status": status
    })
    # Reply
    outgoing = answer if status=="answered" else "Not confident—TA will follow up."
    await ctx.send(msg, {"answer": outgoing})

if __name__=="__main__":
    agent.run()