from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import google.generativeai as genai

app = FastAPI(title="Clarity Grid Chatbot")
templates = Jinja2Templates(directory="templates")

# Configure Gemini AI
api_key = os.getenv("GOOGLE_AI_API_KEY", "AIzaSyDu_A4_boYS532-NDub0lXnXKjFEXDB_jQ")
genai.configure(api_key=api_key)

def generate_ai_answer(query):
    """Generate answer using Gemini AI (without RAG for now)"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
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
    return {"status": "healthy"}

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