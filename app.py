import json
import numpy as np
import faiss
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
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
app = FastAPI()
templates = Jinja2Templates(directory="templates")

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
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_query: str = Form(...)):
    answer = generate_answer(user_query)
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": user_query})
