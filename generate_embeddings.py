import json
import faiss
import numpy as np
import google.generativeai as genai

# Initialize Gemini client
genai.configure(api_key="AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")

# Paths
input_file = r"C:\Users\johnj\Plan-1\data_preprocessed.jsonl"
index_file = r"C:\Users\johnj\Plan-1\faiss_index.idx"
metadata_file = r"C:\Users\johnj\Plan-1\metadata.json"

# Load preprocessed data
texts = []
with open(input_file, "r", encoding="utf-8") as f:
    for line in f:
        obj = json.loads(line)
        texts.append(obj["text"])

# Generate embeddings
embeddings = []
for text in texts:
    response = genai.embed_content(
        model="models/text-embedding-004",
        content=text
    )
    embeddings.append(response['embedding'])

# Convert to numpy array
embeddings_np = np.array(embeddings).astype("float32")

# Create FAISS index
dimension = len(embeddings_np[0])
index = faiss.IndexFlatL2(dimension)  # L2 distance
index.add(embeddings_np)

# Save FAISS index
faiss.write_index(index, index_file)

# Save metadata (to map FAISS indices back to texts)
with open(metadata_file, "w", encoding="utf-8") as f:
    json.dump(texts, f, indent=2)

print(f"Saved {len(texts)} embeddings to FAISS index and metadata file.")
