from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Clarity Grid Chatbot")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "answer": ""})

@app.post("/")
async def chat(request: Request, user_query: str = Form(...)):
    # For now, just echo the question
    answer = f"You asked: '{user_query}'. Full AI functionality will be added next!"
    return templates.TemplateResponse("index.html", {"request": request, "answer": answer, "query": user_query})

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