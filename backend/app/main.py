import os
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
import sys
import io
from pathlib import Path
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Safe Unicode handling for Windows without breaking uvicorn's stdout
if sys.platform == "win32" and hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass  # If reconfigure isn't available, skip silently

# Import services
from app.services.sanitizer import QuerySanitizer
from app.services.classifier import QueryClassifier
from app.services.composer import AnswerComposer
from app.services.validator import ResponseValidator
from app.services.refusal import RefusalHandler
from app.retrieval.vector_store import VectorStore
from app.retrieval.llm_assistant import LLMAssistant
from app.ingest import run_ingestion

app = FastAPI(title="Mutual Fund Chatbot API")

# Add CORS middleware to allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://mutual-fund-chatbot-pmcl.vercel.app",
        "https://mutual-fund-chatbot-pmcl-kajolchawla98s-projects.vercel.app",
    ],
    allow_origin_regex=r"https://mutual-fund-chatbot-pmcl.*\.vercel\.app",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize singletons
sanitizer = QuerySanitizer()
classifier = QueryClassifier()
composer = AnswerComposer()
validator = ResponseValidator()
refusal_handler = RefusalHandler()
llm_assistant = LLMAssistant()

# Vector store is created fresh per request to avoid stale cache after ingestion
def get_vector_store():
    """Always return a fresh VectorStore so new ingestion data is visible."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chroma_db")
    return VectorStore(persist_directory=db_path)

def auto_ingest_if_empty():
    """Run ingestion in background if the vector store has no data."""
    try:
        vs = get_vector_store()
        results = vs.search("HDFC", top_k=1)
        if not results:
            print("[STARTUP] Vector store is empty. Triggering background ingestion...")
            import threading
            t = threading.Thread(target=run_ingestion, daemon=True)
            t.start()
        else:
            print(f"[STARTUP] Vector store has data ({len(results)} results). Skipping ingestion.")
    except Exception as e:
        print(f"[STARTUP] Could not check vector store: {e}. Triggering ingestion...")
        import threading
        t = threading.Thread(target=run_ingestion, daemon=True)
        t.start()

@app.on_event("startup")
async def startup_event():
    auto_ingest_if_empty()

# Rate limiting dictionary (very simple for demo purposes)
request_log = {}

# API Contracts
class ChatQueryRequest(BaseModel):
    session_id: str
    user_message: str

class ChatQueryResponse(BaseModel):
    answer_text: str
    citation_url: Optional[str] = None
    last_updated_date: Optional[str] = None
    refusal_flag: bool

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip not in request_log:
        request_log[client_ip] = []
        
    # Remove older requests (keep 1 min window)
    request_log[client_ip] = [t for t in request_log[client_ip] if current_time - t < 60]
    
    if len(request_log[client_ip]) > 20: # Max 20 reqs/min
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=429, content={"detail": "Too many requests"})
        
    request_log[client_ip].append(current_time)
    response = await call_next(request)
    return response

@app.post("/chat/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    # Phase 8: Privacy Sanitization
    sanitized_query = sanitizer.sanitize(request.user_message)
    
    # Phase 4: Intent Classification
    intent = classifier.classify_intent(sanitized_query)
    
    if intent != "FACTUAL":
        # Phase 6: Refusal Flow
        refusal_msg = refusal_handler.handle_refusal(intent, sanitized_query)
        last_updated = refusal_msg.split("Last updated from sources: ")[-1] if "Last updated" in refusal_msg else None
        
        return ChatQueryResponse(
            answer_text=refusal_msg,
            refusal_flag=True,
            last_updated_date=last_updated
        )
        
    # Phase 3: Retrieval
    # 1. LLM Query Rewrite
    optimized_query = llm_assistant.rewrite_query(sanitized_query)
    print(f"[DEBUG] Original query: {sanitized_query}")
    print(f"[DEBUG] Optimized query: {optimized_query}")
    
    # 2. Vector Search
    vs = get_vector_store()
    retrieved_chunks = vs.search(optimized_query, top_k=3)
    print(f"[DEBUG] Retrieved {len(retrieved_chunks)} chunks")
    for i, chunk in enumerate(retrieved_chunks):
        print(f"[DEBUG]   Chunk {i}: distance={chunk.get('distance')}, text={chunk['text'][:100]}...")
    
    if not retrieved_chunks:
        return ChatQueryResponse(
            answer_text=(
                "The specific information is not available in our current data. "
                "However, I can help you with information on these funds: "
                "HDFC Mid-Cap, ICICI Bluechip, Motilal Oswal Small Cap"
            ),
            refusal_flag=False,
            citation_url=None,
            last_updated_date=None
        )

    # Phase 5: Generation
    raw_answer = composer.compose_answer(sanitized_query, retrieved_chunks)
    print(f"[DEBUG] Raw LLM answer: {raw_answer}")
    
    # Phase 5: Post-Processor Validation
    primary_url = retrieved_chunks[0].get("metadata", {}).get("url")
    validation_result = validator.validate(raw_answer, original_url=primary_url)
    print(f"[DEBUG] Validation result: valid={validation_result['is_valid']}, reasons={validation_result.get('reasons', [])}")
    
    final_text = validation_result["final_text"]
    last_updated = final_text.split("Last updated from sources: ")[-1] if "Last updated" in final_text else None
    is_not_available = "The specific information is not available" in final_text
    
    return ChatQueryResponse(
        answer_text=final_text,
        citation_url=primary_url if (validation_result["is_valid"] and not is_not_available) else None,
        last_updated_date=last_updated,
        refusal_flag=False
    )

@app.post("/ingest/run")
async def trigger_ingest():
    try:
        run_ingestion()
        return {"status": "success", "message": "Ingestion completed successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Mutual Fund Chatbot API"}
