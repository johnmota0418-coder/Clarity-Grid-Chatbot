from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Clarity Grid Chatbot")

@app.get("/")
async def root():
    return {"message": "Hello! Clarity Grid Chatbot is running!", "status": "success"}

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