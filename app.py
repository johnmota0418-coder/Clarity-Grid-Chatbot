from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json
import numpy as np
import faiss
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
import requests
import tempfile
from io import BytesIO

app = FastAPI(title="Clarity Grid Chatbot")
templates = Jinja2Templates(directory="templates")

# Configure Gemini AI
api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
genai.configure(api_key=api_key)

# Azure Blob Storage URLs
BLOB_BASE_URL = "https://itse9cac.blob.core.windows.net/public"
FAISS_INDEX_URL = f"{BLOB_BASE_URL}/free_electrical_grid_index.faiss"
METADATA_URL = f"{BLOB_BASE_URL}/free_electrical_grid_metadata.json"

def download_file_from_blob(url, local_path=None):
    """Download file from Azure Blob Storage"""
    try:
        print(f"📥 Downloading from {url}...")
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        if local_path:
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return local_path
        else:
            return BytesIO(response.content)
    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None

# Load FREE sentence transformer model for query embeddings
print("📥 Loading FREE embedding model for queries...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ FREE embedding model loaded")

# Load FAISS index and metadata from Azure Blob Storage
try:
    # Try to load from local files first (for development)
    if os.path.exists("free_electrical_grid_index.faiss") and os.path.exists("free_electrical_grid_metadata.json"):
        print("📂 Loading from local files...")
        index = faiss.read_index("free_electrical_grid_index.faiss")
        with open("free_electrical_grid_metadata.json", "r", encoding="utf-8") as f:
            texts = json.load(f)
    else:
        print("☁️ Loading from Azure Blob Storage...")
        # Download FAISS index to temporary file
        temp_faiss_path = tempfile.mktemp(suffix='.faiss')
        faiss_file = download_file_from_blob(FAISS_INDEX_URL, temp_faiss_path)
        if not faiss_file:
            raise Exception("Failed to download FAISS index")
        
        # Download metadata
        metadata_stream = download_file_from_blob(METADATA_URL)
        if not metadata_stream:
            raise Exception("Failed to download metadata")
        
        # Load FAISS index
        index = faiss.read_index(faiss_file)
        
        # Load metadata
        metadata_stream.seek(0)
        texts = json.load(metadata_stream)
        
        # Clean up temp file
        os.unlink(temp_faiss_path)
    
    RAG_AVAILABLE = True
    print(f"✅ FREE RAG system loaded: {len(texts)} electrical transmission lines indexed (FREE embeddings)")
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

def retrieve_documents(query, k=5):
    """Retrieve relevant documents using FAISS similarity search with FREE embeddings"""
    if not RAG_AVAILABLE:
        return []
    
    try:
        print(f"🔍 Searching for: {query}")
        
        # Get query embedding using same FREE model as data
        query_embedding = embedding_model.encode([query])
        query_vec = query_embedding.astype("float32")
        
        print(f"📊 Query vector shape: {query_vec.shape}")
        print(f"📊 Index total vectors: {index.ntotal}")
        
        # Search FAISS index
        distances, indices = index.search(query_vec, k)
        
        # Get relevant documents
        relevant_docs = []
        for i, idx in enumerate(indices[0]):
            if idx < len(texts):
                doc = texts[idx]
                distance = distances[0][i]
                print(f"  📄 Found: {doc['id']} (distance: {distance:.3f})")
                relevant_docs.append(doc['content'])
        
        print(f"✅ Retrieved {len(relevant_docs)} relevant documents")
        return relevant_docs
        
    except Exception as e:
        print(f"❌ Error in document retrieval: {e}")
        return []

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/")
async def chat(request: Request, query: str = Form(...)):
    print(f"📝 Received query: {query}")  # Debug log
    try:
        answer = generate_ai_answer(query)
        print(f"✅ Generated answer: {len(answer)} characters")  # Debug log
        return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": query})
    except Exception as e:
        error_msg = f"Error generating response: {str(e)}"
        print(f"❌ Error: {error_msg}")  # Debug log
        return templates.TemplateResponse("index.html", {"request": request, "answer": error_msg, "query": query})

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
        <head><title>FREE Electrical Grid Assistant - 84K+ Real Lines</title></head>
        <body style="font-family: Arial; margin: 40px;">
            <h1>🤖 Clarity Grid Chatbot</h1>
            <p>✅ Deployment successful!</p>
            <p>The full RAG functionality will be added once basic deployment works.</p>
        </body>
    </html>
    """