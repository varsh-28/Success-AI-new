from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import time

# --- Pydantic Models (Data Validation) ---
# This defines what the "request" from the frontend must look like
class ChatRequest(BaseModel):
    query: str

# This defines what the "response" to the frontend will look like
class ChatResponse(BaseModel):
    response: str
    context_source: str


# --- Mock Services (Replacing External Systems) ---
# We use 'async' to allow our server to handle many requests at once.

async def fetch_servicenow_context(query: str) -> str:
    """
    MOCK: This function replaces your Java context-service.
    In a real app, it would use 'httpx' to call the ServiceNow API.
    """
    print(f"Fetching context from ServiceNow for: {query}")
    # Simulate a network call
    await asyncio.sleep(0.5) 
    if "incident" in query.lower():
        return "Found 1 matching incident: INC12345 - 'Printer on fire'"
    return None

async def query_vector_db(query: str) -> str:
    """
    MOCK: This function replaces your vector DB call (HANA/Chroma).
    """
    print(f"Querying Vector DB for: {query}")
    # Simulate a DB lookup
    await asyncio.sleep(0.5) 
    return "Vector DB context: 'Printers are flammable. (Doc ID: 789)'"

async def call_llm(query: str, context: str) -> str:
    """
    MOCK: This function replaces your LLM (e.g., Gemini) call.
    """
    print("Calling LLM with combined prompt...")
    # Simulate the LLM "thinking"
    await asyncio.sleep(1)
    
    prompt = f"""
    Using this context: {context}
    Answer this query: {query}
    """
    
    # This is our "AI"
    return f"Mock AI Response: Yes, the printer is on fire. Context: {context}"


# --- FastAPI Application ---
app = FastAPI(
    title="SuccessAI Python Backend",
    description="The main API for the SuccessAI RAG chatbot."
)


@app.get("/")
def read_root():
    return {"message": "SuccessAI Backend is running!"}


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(request: ChatRequest):
    """
    This is the main chat endpoint that your Streamlit frontend will call.
    It performs the full RAG pipeline.
    """
    try:
        print(f"Received chat request: {request.query}")
        
        # 1. Fetch external context (replaces Java service)
        snow_context = await fetch_servicenow_context(request.query)
        
        # 2. Fetch knowledge context (your existing RAG logic)
        vector_context = await query_vector_db(request.query)
        
        # 3. Combine context
        final_context = ""
        context_source = ""
        
        if snow_context:
            final_context = snow_context
            context_source = "ServiceNow"
        else:
            final_context = vector_context
            context_source = "Vector DB"
            
        # 4. Generate AI response (your existing RAG logic)
        ai_response = await call_llm(request.query, final_context)
        
        # 5. Send the response back to the frontend
        return ChatResponse(
            response=ai_response,
            context_source=context_source
        )

    except Exception as e:
        print(f"Error in /chat endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# --- Need this for the `asyncio.sleep` calls to work ---
import asyncio
