# Askademia TA Bot

This project implements a Teaching Assistant (TA) chatbot powered by Fetch.ai agents (`uagents`), Google Gemini, and a Retrieval-Augmented Generation (RAG) pipeline using MongoDB Atlas Vector Search.

## Description

The goal is to create an AI agent that can answer student questions about course content. The agent uses course documents (like syllabi, lecture notes, etc.) as its knowledge base. When a student asks a question, the system finds the most relevant parts of the documents and uses Gemini to generate an answer based *only* on that information.

## Features

*   **RAG Pipeline:** Retrieves relevant context from course documents stored in MongoDB before generating an answer.
*   **Gemini Integration:** Uses Google Gemini for both text embedding (`text-embedding-004`) and chat generation (`gemini-1.5-flash`).
*   **Fetch.ai Agent:** Built using the `uagents` library (Fetch.ai V2), allowing for potential future expansion into a multi-agent system.
*   **PDF Document Loading:** Includes a script to load, chunk, embed, and store content from PDF documents.
*   **Configurable:** Uses a `.env` file for secrets and `config.py` for agent settings.

## Technology Stack

*   **Language:** Python 3
*   **AI Agent Framework:** Fetch.ai `uagents`
*   **LLM & Embeddings:** Google Gemini API (`google-generativeai`)
*   **Vector Database:** MongoDB Atlas with Vector Search
*   **PDF Parsing:** PyMuPDF (`pymupdf`)
*   **Database Driver:** `pymongo`
*   **Configuration:** `python-dotenv`
*   **Other:** `tiktoken` (for text chunking)

## Setup

1.  **Clone the Repository:**
    ```bash
    git clone <your-repo-url>
    cd Askademia/ta-bot 
    ```

2.  **Create Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # macOS/Linux
    # or
    .\venv\Scripts\activate # Windows
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**
    *   Create a file named `.env` in the `Askademia/ta-bot` directory.
    *   Add your secrets:
        ```dotenv
        # Required: Get from Google AI Studio or GCP
        GEMINI_API_KEY=YOUR_GEMINI_API_KEY
        
        # Required: Get from MongoDB Atlas connection string
        MONGO_URI=mongodb+srv://<user>:<password>@<cluster-url>/...?retryWrites=true&w=majority
        
        # Optional: Define custom seeds for agent addresses (otherwise defaults are used)
        # TA_AGENT_SEED=a_very_secret_phrase_for_the_ta_agent
        # STUDENT_AGENT_SEED=a_different_secret_phrase_for_the_student
        ```

5.  **Set up MongoDB Atlas:**
    *   Ensure you have a MongoDB Atlas cluster.
    *   The `MONGO_URI` should point to it.
    *   Run the index setup script **once** to create the database (`Classroom-qna`), collection (`syllabus_chunks`), and the Atlas Vector Search index (`syllabus_emb`):
        ```bash
        python db/index_setup.py
        ```
    *   Wait for the index to finish building in the Atlas UI before loading data.

## Data Loading

1.  **Place Documents:** Put your course documents (currently supports PDFs) into a directory, for example, `Askademia/ta-bot/embeddings/`.
2.  **Run Loader Script:** Execute the loader script, providing the path to your documents and an optional course ID. It will chunk, embed, and insert the content into MongoDB.
    
    *Example: Ingest all PDFs from the `embeddings` folder with course ID 'CMPE295B':*
    ```bash
    python embeddings/loader.py embeddings/*.pdf CMPE295B
    ```
    *Example: Ingest only `Syllabus.pdf` with the default course ID ('GEN'):*
    ```bash
    python embeddings/loader.py embeddings/Syllabus.pdf
    ```
    **(Repeat this step whenever you add or update documents)**

## Running the Application

The system consists of (at least) two agents: the TA Agent and a script to send it queries.

1.  **Run the TA Agent:**
    *   Open a terminal, navigate to `Askademia/ta-bot`, and activate the virtual environment.
    *   Start the TA agent:
        ```bash
        python src/ta_agent.py
        ```
    *   It will print its configuration, including its **Agent Address** (e.g., `agent1...`). **Copy this address.** Keep this terminal running.

2.  **Send a Test Query:**
    *   Open a **second** terminal, navigate to `Askademia/ta-bot`, and activate the virtual environment.
    *   Run the test sender script, providing the TA agent's address as a command-line argument:
        ```bash
        python scripts/send_test_query.py <PASTE_TA_AGENT_ADDRESS_HERE>
        ```
    *   Observe the logs in both terminals. The second terminal should print the TA agent's response.

## Configuration Files

*   `.env`: Stores secrets (API keys, DB URI, optional agent seeds).
*   `config.py`: Loads `.env` variables and defines agent names, ports, and default endpoints.

## Directory Structure

```
Askademia/ta-bot/
├── .env                # API Keys, DB URI, Agent Seeds (Create this file)
├── config.py           # Agent/App configuration
├── requirements.txt    # Python dependencies
├── db/                 # Database related scripts
│   ├── index_setup.py  # Creates MongoDB collection and vector index
│   └── mongo_client.py # MongoDB connection utility
├── embeddings/         # Document processing and embedding
│   ├── Syllabus.pdf    # Example document (Add your course files here)
│   ├── chunk_utils.py  # Text chunking logic
│   ├── embedder.py     # Gemini embedding function
│   └── loader.py       # Loads, chunks, embeds, and stores documents
├── prompts/            # System prompts for the LLM
│   └── ta_system_prompts.py
├── scripts/            # Utility and testing scripts
│   ├── send_test_query.py # Sends a query to the running TA agent
│   └── test_rag_pipeline.py # Tests the RAG pipeline locally
├── src/                # Core source code
│   ├── gemini_handler.py # Handles interaction with Gemini Chat API
│   ├── models.py       # Pydantic models for agent messages
│   ├── rag_handler.py  # Handles context retrieval from MongoDB
│   └── ta_agent.py     # The main Fetch.ai TA agent
├── ui/                 # Placeholder for User Interface (Next Step)
├── utils/              # Utility functions (e.g., logging - currently basic)
└── README.md           # This file
```

## Next Steps / Future Work

*   **User Interface:** Implement a user-friendly interface (e.g., using Streamlit, Gradio, or Flask/React) in the `ui/` directory.
*   **Student Agent:** Develop a persistent `Student Agent` (`src/student_agent.py`) to manage UI interaction and communication.
*   **Improved Error Handling:** Add more robust error handling throughout the pipeline.
*   **Logging:** Implement structured logging using `utils/logging_conf.py`.
*   **Conversation History:** Add support for maintaining conversation context.
*   **Support More File Types:** Extend `embeddings/loader.py` to handle `.txt`, `.md`, `.docx`, etc.
*   **Agent Discovery:** Utilize Fetch.ai Almanac for dynamic agent discovery instead of passing addresses manually.
