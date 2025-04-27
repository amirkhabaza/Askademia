import sys
import os
# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.rag_handler import retrieve_context
from src.gemini_handler import generate_response
from prompts.ta_system_prompts import TA_SYSTEM_PROMPT

def main():
    # --- Simulate User Input ---
    # Try different queries relevant to your Syllabus.pdf
    user_query = "What is the professor's email address?"
    # user_query = "What topics are covered in week 3?"
    # user_query = "What is the professor's email address?"

    print(f"Testing RAG Pipeline with query: '{user_query}'")
    print("-" * 30)

    # 1. Retrieve Context
    print("Retrieving context...")
    context = retrieve_context(user_query)
    print(f"Retrieved Context:\n{context}")
    print("-" * 30)

    # Check if context retrieval failed
    if context == "Error retrieving context from the database." or context == "No relevant context found in the course material.":
        print("Aborting generation due to context retrieval issue.")
        return

    # 2. Generate Response
    print("Generating response...")
    final_response = generate_response(
        system_prompt=TA_SYSTEM_PROMPT, 
        user_query=user_query, 
        context=context
    )
    # Use newline character directly
    print(f"\nGenerated Final Response:\n{final_response}")
    print("-" * 30)

if __name__ == "__main__":
    main() 