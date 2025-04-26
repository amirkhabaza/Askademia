# To run this code you need to install the following dependencies:
# pip install google-genai
import os
from dotenv import load_dotenv
import base64
from google import genai
from google.genai import types


GEMINI_KEY = os.getenv("GEMINI_API_KEY")


def generate():
    client = genai.Client(api_key=GEMINI_KEY)

    model = "gemini-2.5-pro-exp-03-25"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""Act as a Teaching Assistant. Please refer to Student's Weak Topics and Generate 5 Quiz Questions. Don't give the solution for students, instead help point them to the right answer"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()

