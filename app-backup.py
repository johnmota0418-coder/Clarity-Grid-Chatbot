import json
import numpy as np
import faiss
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import google.generativeai as genai

# --------------------------
# Initialize Gemini client
# --------------------------
api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
genai.configure(api_key=api_key)

# --------------------------
# Load FAISS index and metadata
# --------------------------
index_file = "faiss_index.idx"
metadata_file = "metadata.json"

index = faiss.read_index(index_file)
with open(metadata_file, "r", encoding="utf-8") as f:
    texts = json.load(f)

# --------------------------
# FastAPI & templates
# --------------------------
app = FastAPI(title="Clarity Grid RAG Chatbot", description="AI-powered electrical grid information chatbot")
templates = Jinja2Templates(directory="templates")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# --------------------------
# Retrieval function
# --------------------------
def retrieve(query, k=3):
    query_resp = genai.embed_content(
        model="models/text-embedding-004",
        content=query
    )
    query_vec = np.array(query_resp['embedding']).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_vec, k)
    return [texts[i] for i in indices[0]]

# --------------------------
# Generate answer
# --------------------------
def generate_answer(query):
    retrieved_texts = retrieve(query)
    context = "\n\n".join(retrieved_texts)
    prompt = f"Answer the question based on the following context:\n{context}\n\nQuestion: {query}"
    
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=0.2
        )
    )
    return response.text

# --------------------------
# Routes
# --------------------------
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Clarity Grid Chatbot is running"}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request, "answer": ""})
    except Exception as e:
        return HTMLResponse(f"<h1>Error loading template: {str(e)}</h1>", status_code=500)

@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_query: str = Form(...)):
    try:
        answer = generate_answer(user_query)
        return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": user_query})
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "answer": f"Error: {str(e)}", "query": user_query})

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
