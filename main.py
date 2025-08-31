import uuid
from typing import Dict, List

# --- FastAPI and Pydantic Imports ---
from fastapi import FastAPI
from pydantic import BaseModel

# --- LangChain Imports ---
from langchain_community.vectorstores import Chroma
# from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.document_loaders import PyPDFLoader
# --- Environment Variables ---
from dotenv import load_dotenv
load_dotenv()

# --- Backend Application Setup ---
app = FastAPI(
    title="Conversational RAG Tutor API",
    description="An API for a conversational AI tutor with RAG capabilities.",
)

# --- Global Variables & In-memory Storage ---
# In a production environment, use a more robust storage like Redis or a database.
chat_histories: Dict[str, List] = {}
vectorstore = None
retriever = None
conversational_rag_chain = None

# --- Pydantic Models for API ---
class QueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    session_id: str
    query: str

class ChatResponse(BaseModel):
    text: str
    emotion: str # e.g., "happy", "thinking", "explaining"

# --- RAG Pipeline Setup ---
def setup_rag_pipeline():
    """Initializes the RAG pipeline, vector store, and conversational chain."""
    global vectorstore, retriever, conversational_rag_chain
    
    # 1. Load Documents from a source
    # loader = TextLoader("tutor_data.txt")
    loader = PyPDFLoader("python Machine Learning .pdf")
    docs = loader.load()

    # 2. Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    # 3. Create embeddings and store in ChromaDB
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

    # 4. Initialize LLM
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
    # llm =get_gpt_mini()

    # 5. Create the Retriever
    retriever = vectorstore.as_retriever()

    # 6. Create the Conversational RAG Chain
    # This prompt helps the LLM rephrase the user's question to be self-contained
    retriever_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user", "Given the above conversation, generate a search query to look up in order to get information relevant to the conversation.")
    ])
    
    history_aware_retriever = create_history_aware_retriever(llm, retriever, retriever_prompt)
    
    # This prompt instructs the LLM on how to answer, including the emotion
    system_prompt = (
        "You are an AI tutor. Use the retrieved context to answer questions. "
        "Your tone should be helpful and encouraging. Keep your answers concise. "
        "After your answer, specify an emotion from this list: "
        "[explaining, happy, thinking, neutral]. "
        "Format your entire response as a JSON object with two keys: 'answer' and 'emotion'.\n\n"
        "Context: {context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    conversational_rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    """Run setup tasks when the server starts."""
    print("Setting up RAG pipeline...")
    setup_rag_pipeline()
    print("Setup complete.")

@app.post("/query", response_model=ChatResponse)
async def handle_single_query(request: QueryRequest):
    """Handles a single, stateless query without conversation history."""
    import json
    # A simplified chain for single queries (no history)
    response = await conversational_rag_chain.ainvoke({
        "input": request.query,
        "chat_history": []
    })
    
    try:
        # The LLM output should be a JSON string, so we parse it
        result_json = json.loads(response["answer"])
        return ChatResponse(text=result_json.get("answer", ""), emotion=result_json.get("emotion", "neutral"))
    except json.JSONDecodeError:
        # Fallback if the LLM doesn't return valid JSON
        return ChatResponse(text=response["answer"], emotion="neutral")


@app.post("/chat", response_model=ChatResponse)
async def handle_chat_turn(request: ChatRequest):
    """Handles a multi-turn conversation with session history."""
    import json
    session_id = request.session_id
    query = request.query

    # Get or create chat history for the session
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    current_chat_history = chat_histories[session_id]

    # Invoke the conversational RAG chain
    response = await conversational_rag_chain.ainvoke({
        "input": query,
        "chat_history": current_chat_history
    })
    
    # Update chat history
    current_chat_history.extend([
        HumanMessage(content=query),
        AIMessage(content=response["answer"]) # We store the full JSON response in history
    ])
    # Limit history size to avoid overly large contexts
    chat_histories[session_id] = current_chat_history[-10:] 

    try:
        # Parse the JSON output from the LLM
        result_json = json.loads(response["answer"])
        return ChatResponse(text=result_json.get("answer", ""), emotion=result_json.get("emotion", "neutral"))
    except (json.JSONDecodeError, TypeError):
        # Fallback if the LLM response is not a valid JSON string
        return ChatResponse(text=response.get("answer", "I'm sorry, I had trouble processing that."), emotion="thinking")

# To run the server: uvicorn backend:app --reload