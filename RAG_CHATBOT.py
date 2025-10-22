import json
import numpy as np
import faiss
import google.generativeai as genai

# -------------------------------
# Initialize Gemini client
# -------------------------------
genai.configure(api_key="AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")

# -------------------------------
# Load FAISS index and metadata
# -------------------------------
index_file = r"C:\Users\johnj\Plan-1\faiss_index.idx"
metadata_file = r"C:\Users\johnj\Plan-1\metadata.json"

index = faiss.read_index(index_file)

with open(metadata_file, "r", encoding="utf-8") as f:
    texts = json.load(f)

# -------------------------------
# Function to get top-k relevant features
# -------------------------------
def retrieve(query, k=3):
    # Get query embedding from Gemini
    query_resp = genai.embed_content(
        model="models/text-embedding-004",
        content=query
    )
    query_vec = np.array(query_resp['embedding']).astype("float32").reshape(1, -1)
    
    # Search FAISS
    distances, indices = index.search(query_vec, k)
    results = [texts[i] for i in indices[0]]
    return results

# -------------------------------
# Function to generate answer using Gemini
# -------------------------------
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

# -------------------------------
# Example usage
# -------------------------------
question = "Which lines are in service in Alabama?"
answer = generate_answer(question)
print("Answer:\n", answer)
