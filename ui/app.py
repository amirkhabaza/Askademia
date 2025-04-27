import sys
import os
import streamlit as st
import asyncio
import threading
import time

# Add project root to sys.path to allow sibling imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import student agent components (assuming structure allows)
try:
    from src.student_agent import student_agent, send_query_to_ta
    # Make sure student_agent is initialized BEFORE importing here
except ImportError as e:
    st.error(f\"Failed to import Student Agent components: {e}\\nEnsure src/student_agent.py exists and can be imported.\")
    st.stop() # Stop execution if agent cannot be imported

# --- Streamlit App Configuration ---
st.set_page_config(page_title=\"Askademia TA Bot\", layout=\"wide\")
st.title(\"🎓 Askademia TA Bot\")
st.caption(\"Ask me questions about your course material!\")

# --- Agent Management --- 

# Function to run the agent in a separate thread
def run_agent_loop(agent):
    try:
        agent.run() # This blocks until agent stops
    except Exception as e:
        print(f\"Error running agent loop: {e}\")
        # Handle error appropriately, maybe try restarting or signal UI

# Check if agent is already running in this session
if 'agent_thread' not in st.session_state:
    st.session_state.agent_thread = None
if 'agent_running' not in st.session_state:
    st.session_state.agent_running = False

# Start the agent if not already running
if not st.session_state.agent_running:
    print(\"Starting Student Agent thread...\")
    # Ensure a unique event loop for the thread if needed (often required with uagents/asyncio)
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    st.session_state.agent_thread = threading.Thread(target=run_agent_loop, args=(student_agent,), daemon=True)
    st.session_state.agent_thread.start()
    # Give agent a moment to start up
    time.sleep(2) # Adjust as needed
    # Check if agent is alive (basic check, might need more robust health check)
    if st.session_state.agent_thread.is_alive():
        st.session_state.agent_running = True
        print(\"Student Agent thread started.\")
        # Initialize agent storage if needed on first run
        student_agent.storage.set(\"response_ready\", True) # Start ready
        student_agent.storage.set(\"last_response\", None)
    else:
        st.error(\"Failed to start Student Agent thread! Check logs.\")
        st.session_state.agent_running = False # Ensure it's marked as not running

# --- Chat Interface Logic ---

# Initialize chat history
if \"messages\" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message[\"role\"]):
        st.markdown(message[\"content\"])

# --- Handling User Input --- 
if prompt := st.chat_input(\"Ask about the course..."): 
    # Add user message to chat history
    st.session_state.messages.append({\"role\": \"user\", \"content\": prompt})
    # Display user message in chat message container
    with st.chat_message(\"user\"):
        st.markdown(prompt)

    # --- Send Query to Agent --- 
    if st.session_state.agent_running:
        with st.spinner(\"Asking the TA Bot...\"):
            # Call the async function using agent's context (or loop)
            # Running async code from sync Streamlit requires care.
            # We can use agent's own loop if available or run_in_executor.
            # Simplest for thread model: run via agent's context if possible
            # This assumes student_agent instance is directly usable here.
            try:
                # We need to schedule the async task onto the agent's running event loop
                # One way: Use asyncio.run_coroutine_threadsafe if loop accessible
                # Simpler but potentially problematic: direct await (might not work correctly with Streamlit's execution)
                # Let's try scheduling via agent's context if possible
                # Need to ensure the context is valid here - usually within agent handlers.
                # Direct call might block streamlit, instead use storage as signal?
                
                # **Revised approach: Use storage as signal, agent loop picks it up**
                # We modify student_agent to poll a 'query_to_send' storage key
                # For now, let's *simulate* the async call difficulties.
                # We will use a placeholder for direct async call, which needs fixing
                # TODO: Implement robust way to call send_query_to_ta from Streamlit thread
                
                # Trigger the send function (Needs robust implementation)
                # A simple flag/storage based approach might be better:
                student_agent.storage.set(\"query_to_send\", prompt)
                
                # --- Wait for Agent Response --- 
                response_content = None
                start_time = time.time()
                timeout_seconds = 30 # Max wait time for a response
                while time.time() - start_time < timeout_seconds:
                    if student_agent.storage.get(\"response_ready\"):
                        response_data = student_agent.storage.get(\"last_response\")
                        if response_data:
                            response_content = response_data.get(\"content\")
                            # Clear the ready flag after processing
                            student_agent.storage.set(\"response_ready\", False)
                            student_agent.storage.set(\"last_response\", None)
                        break # Exit wait loop
                    time.sleep(0.5) # Check periodically
                
                if response_content is None:
                    response_content = \"Sorry, I didn't get a response from the TA Bot in time.\"

            except Exception as e:
                 st.error(f\"Error interacting with agent: {e}\")
                 response_content = f\"Error: {e}\" 

        # Display assistant response in chat message container
        with st.chat_message(\"assistant\"):
            st.markdown(response_content)
        # Add assistant response to chat history
        st.session_state.messages.append({\"role\": \"assistant\", \"content\": response_content})
        
    else:
        st.error(\"Student Agent is not running. Cannot send query.\") 