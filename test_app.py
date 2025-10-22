from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="Clarity Grid Test")

@app.get("/")
async def root():
    return {"message": "Hello from Clarity Grid Chatbot!", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "port": os.getenv("PORT", "8000")}

@app.get("/test", response_class=HTMLResponse)
async def test_page():
    return """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Clarity Grid Chatbot Test</h1>
            <p>If you can see this, the deployment is working!</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)