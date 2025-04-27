import os
from dotenv import load_dotenv          # pip install python-dotenv
from google import genai                # pip install --upgrade google-genai


load_dotenv()

API_KEY = os.getenv("GEMINI_KEY") or os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_KEY or GEMINI_API_KEY must be set")

client = genai.Client(api_key=API_KEY)         # one client per process
EMBED_MODEL = "text-embedding-004"     # or text-embedding-005

def embed(text: str) -> list[float]:
    """
    Return a list[float] vector for *text* (length = 768 for this model).
    """
    resp = client.models.embed_content(model=EMBED_MODEL, contents=text)
    # SDK returns `.embedding` (single) or `.embeddings` (batch) – handle both
    return getattr(resp, "embedding", resp.embeddings[0].values)

vec = embed("hello")
print("dims:", len(vec))          # expect: 768
print("first 4:", vec[:4])