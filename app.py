from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import numpy as np
import faiss
import google.generativeai as genai

app = FastAPI(title="Clarity Grid Chatbot")
templates = Jinja2Templates(directory="templates")

# Configure Gemini AI
api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
genai.configure(api_key=api_key)

# Load FAISS index and metadata
try:
    index = faiss.read_index("faiss_index.idx")
    with open("metadata.json", "r", encoding="utf-8") as f:
        texts = json.load(f)
    RAG_AVAILABLE = True
    print(f"✅ RAG system loaded: {len(texts)} documents indexed")
except Exception as e:
    RAG_AVAILABLE = False
    index = None
    texts = []
    print(f"⚠️ RAG system not available: {e}")

def generate_ai_answer(query):
    """Generate answer using Gemini AI with RAG (if available)"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # Try to retrieve relevant documents
        retrieved_docs = retrieve_documents(query)
        
        if retrieved_docs and RAG_AVAILABLE:
            # RAG mode: Use retrieved documents as context
            context = "\n\n".join(retrieved_docs)
            prompt = f"""Based on the following context about electrical grids, answer the question accurately and helpfully:

Context:
{context}

Question: {query}

Please provide a clear, informative answer based on the context provided. If the context doesn't contain relevant information, use your general knowledge about electrical grids."""
        else:
            # Fallback mode: General AI response
            prompt = f"""You are a helpful assistant for electrical grid information. 
            Answer the following question about electrical grids, power systems, or related topics:
            
            Question: {query}
            
            If the question is not related to electrical grids or power systems, politely redirect to grid-related topics."""
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(temperature=0.2)
        )
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def retrieve_documents(query, k=3):
    """Retrieve relevant documents using FAISS similarity search"""
    if not RAG_AVAILABLE:
        return []
    
    try:
        # Get query embedding
        query_resp = genai.embed_content(
            model="models/text-embedding-004",
            content=query
        )
        query_vec = np.array(query_resp['embedding']).astype("float32").reshape(1, -1)
        
        # Search FAISS index
        distances, indices = index.search(query_vec, k)
        return [texts[i] for i in indices[0]]
    except Exception as e:
        print(f"Error in document retrieval: {e}")
        return []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/")
async def chat(request: Request, user_query: str = Form(...)):
    try:
        answer = generate_ai_answer(user_query)
        return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": user_query})
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        return templates.TemplateResponse("index.html", {"request": request, "answer": error_msg, "query": user_query})

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "rag_available": RAG_AVAILABLE,
        "documents_indexed": len(texts) if RAG_AVAILABLE else 0
    }

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    return """
    <!DOCTYPE html>
    <html>
        <head><title>Clarity Grid Chatbot</title></head>
        <body style="font-family: Arial; margin: 40px;">
            <h1>🤖 Clarity Grid Chatbot</h1>
            <p>✅ Deployment successful!</p>
            <p>The full RAG functionality will be added once basic deployment works.</p>
        </body>
    </html>
    """