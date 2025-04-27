import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError("GEMINI_API_KEY must be set in the environment variables or .env file")

genai.configure(api_key=API_KEY)

# Configuration for the generation
generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

# Safety settings - adjust as needed
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

# Initialize the model
# Use a model suitable for chat, like gemini-1.5-flash or gemini-pro
model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

def generate_response(system_prompt: str, user_query: str, context: str) -> str:
    """
    Generates a response using the Gemini model based on system prompt, user query, and context.
    """
    try:
        # Constructing the prompt for the model
        # You might refine this structure based on Gemini's best practices
        full_prompt = f"""{system_prompt}

Context from course material:
---
{context}
---

Student Query: {user_query}

Response:"""

        response = model.generate_content(full_prompt)
        # Safely access the text part, handling potential issues
        if response.parts:
            return response.text
        else:
            # Handle cases where the response might be blocked or empty
            # You might want to inspect response.prompt_feedback here
            print("Warning: Gemini response was empty or blocked.")
            return "I could not generate a response based on the provided information."

    except Exception as e:
        # Basic error handling, consider adding logging
        print(f"Error during Gemini API call: {e}")
        return "Sorry, I encountered an error trying to generate a response."

# Example Usage (optional, for testing)
if __name__ == '__main__':
    test_prompt = "You are a helpful assistant."
    test_query = "What is the main topic?"
    test_context = "This document discusses the importance of vector databases."
    reply = generate_response(test_prompt, test_query, test_context)
    print(f"Generated Reply:\n{reply}") 