import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# --- Configuration ---
DATA_PATH = "data/"
DB_PATH = "chroma_db"

# --- Helper Functions ---

def load_documents(data_path):
    """Loads all PDF documents from the specified data path."""
    print(f"Loading documents from {data_path}...")
    documents = []
    for filename in os.listdir(data_path):
        if filename.endswith('.pdf'):
            file_path = os.path.join(data_path, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
    print(f"Loaded {len(documents)} document(s).")
    return documents

def split_documents(documents):
    """Splits the loaded documents into smaller chunks for processing."""
    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    texts = text_splitter.split_documents(documents)
    print(f"Created {len(texts)} text chunks.")
    return texts

def create_vector_store(texts, db_path):
    """Creates and persists a Chroma vector store from the text chunks."""
    print("Initializing embeddings model...")
    # Use a local model through Ollama for embeddings
    embeddings = OllamaEmbeddings(model="nomic-embed-text")

    print(f"Creating and persisting vector store at {db_path}...")
    # Create the vector store and persist it to disk
    vectorstore = Chroma.from_documents(
        documents=texts, 
        embedding=embeddings, 
        persist_directory=db_path
    )
    print("Vector store created successfully.")
    return vectorstore

# --- Main Execution ---

if __name__ == "__main__":
    # 1. Load the documents
    documents = load_documents(DATA_PATH)

    if not documents:
        print("No PDF documents found. Please add a PDF to the 'data' directory.")
    else:
        # 2. Split the documents into chunks
        texts = split_documents(documents)

        # 3. Create and persist the vector store
        create_vector_store(texts, DB_PATH)

        print("\n--- Ingestion Complete ---")
        print(f"Your knowledge base is ready and stored in the '{DB_PATH}' directory.")
