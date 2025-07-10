import streamlit as st
from langchain_community.vectorstores import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama

# --- Configuration ---
DB_PATH = "chroma_db"

# --- App Setup ---
st.set_page_config(page_title="Professional RAG Chatbot", page_icon="🤖")
st.title("Professional RAG Chatbot")
st.write("Ask any question about your documents, and I'll provide an answer based on the knowledge base.")

# --- Load the Knowledge Base ---
@st.cache_resource
def load_retriever():
    """Loads the ChromaDB retriever from the persisted directory."""
    try:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        return vectorstore.as_retriever()
    except Exception as e:
        st.error(f"Failed to load the knowledge base. Have you run ingest.py first? Error: {e}")
        return None

retriever = load_retriever()

# --- Initialize Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("What is your question?"):
    if not retriever:
        st.warning("Retriever not loaded. Please ensure the knowledge base is created correctly.")
    else:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # --- Generate AI Response ---
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            # 1. Retrieve relevant context
            relevant_docs = retriever.get_relevant_documents(prompt)
            context_str = "\n\n".join([doc.page_content for doc in relevant_docs])

            # 2. Create the prompt for the LLM
            formatted_prompt = f"""
            You are a helpful assistant. Answer the user's question based ONLY on the following context. If the answer is not in the context, say you don't know.

            [CONTEXT]
            {context_str}
            [/CONTEXT]

            Question: {prompt}
            """

            # 3. Stream the response from the LLM
            llm = ChatOllama(model="llama3.1:8b", temperature=0)
            try:
                for chunk in llm.stream(formatted_prompt):
                    full_response += chunk
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"An error occurred with the AI model: {e}")
                full_response = "Sorry, I encountered an error."

        # Add AI response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
