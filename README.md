# Professional RAG Chatbot with Local AI

A portfolio-ready Retrieval-Augmented Generation (RAG) chatbot that runs entirely on your local machine using Ollama and Streamlit. This project demonstrates a complete, end-to-end workflow for building a private, context-aware AI assistant that can answer questions about your own documents.

<!-- Placeholder for a GIF of the app in action -->
<!-- ![Chatbot Demo](./demo.gif) -->

## Overview

This application provides a user-friendly chat interface to interact with a knowledge base created from your personal PDF documents. It uses a RAG architecture to ensure that the AI's answers are grounded in the provided context, preventing hallucination and providing factual responses. The entire process, from data ingestion to answer generation, runs locally, ensuring your data remains private.

## Tech Stack

- **Frontend:** [Streamlit](https://streamlit.io/) - For building the interactive web UI.
- **LLM & Embeddings:** [Ollama](https://ollama.com/) - To run local large language models (like Llama 3.1) and embedding models.
- **Core Logic:** [LangChain](https://www.langchain.com/) - For orchestrating the RAG pipeline, including document loading, splitting, and vector store interaction.
- **Vector Database:** [ChromaDB](https://www.trychroma.com/) - For creating and storing persistent vector embeddings of the documents.
- **PDF Processing:** [PyPDF](https://pypi.org/project/pypdf/)

## Key Features

- **Local First:** All models and data are processed and stored on your local machine. No data ever leaves your computer.
- **RAG Architecture:** Ensures answers are accurate and based on the content of your documents.
- **Friendly UI:** A clean, intuitive chat interface built with Streamlit.
- **Easy Data Ingestion:** Simply place your PDFs in the `data` folder and run a single script to build the knowledge base.
- **Modular & Professional:** The code is structured professionally with a clear separation of concerns, a virtual environment, and version control.

## Project Structure

```
professional-rag-chatbot/
├── .gitignore
├── app.py             # The Streamlit frontend application
├── ingest.py          # Script to process PDFs and build the vector DB
├── requirements.txt   # Python dependencies
├── README.md          # You are here!
├── data/              # Folder for your source PDF documents
│   └── .gitkeep
└── venv/              # Python virtual environment
```

## Setup and Installation

Follow these steps to set up and run the project on your local machine.

### Prerequisites

1.  **Python 3.8+**
2.  **Ollama:** Make sure you have [Ollama installed](https://ollama.com/download) and running.

### Installation Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/atwine/professional_RAG_chatbot.git
    cd professional-rag-chatbot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the necessary Ollama models:**
    ```bash
    ollama pull llama3.1:8b
    ollama pull nomic-embed-text
    ```

## Usage

1.  **Add Your Documents:**
    - Place any PDF files you want to chat with into the `data/` directory.

2.  **Build the Knowledge Base:**
    - Run the ingestion script. This will process the PDFs, create embeddings, and save them to a local ChromaDB vector store.
    ```bash
    python ingest.py
    ```
    - You only need to run this once, or whenever you add, remove, or change documents in the `data/` folder.

3.  **Run the Chatbot Application:**
    - Start the Streamlit app.
    ```bash
    streamlit run app.py
    ```
    - Your browser should open to the chat interface, ready for your questions!

---

*This project was built with the assistance of Cascade, an agentic AI coding assistant.*
