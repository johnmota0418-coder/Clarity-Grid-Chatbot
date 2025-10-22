# Clarity Grid RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with FastAPI, FAISS, and Google's Gemini AI for intelligent question answering about electrical grid data.

## Features

- **RAG Architecture**: Combines document retrieval with generative AI for accurate, context-aware responses
- **FAISS Vector Search**: Fast similarity search using Facebook AI Similarity Search
- **Google Gemini Integration**: Powered by Google's latest Gemini AI model
- **FastAPI Web Interface**: Modern, fast web framework with automatic API documentation
- **Responsive Design**: Clean web interface for easy interaction

## Setup

### Prerequisites

- Python 3.8+
- Google AI API Key (get one from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. Clone the repository:
```bash
git clone https://github.com/johnmota0418-coder/Clarity-Grid-Chatbot.git
cd Clarity-Grid-Chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google AI API key in `app.py`:
```python
genai.configure(api_key="YOUR_API_KEY_HERE")
```

4. Generate embeddings (if not already done):
```bash
python generate_embeddings.py
```

5. Run the application:
```bash
uvicorn app:app --reload
```

The application will be available at `http://localhost:8000`

## Docker Deployment

### Build and run with Docker:

```bash
# Build the image
docker build -t clarity-grid-chatbot .

# Run the container
docker run -p 8000:8000 clarity-grid-chatbot
```

## Cloud Deployment Options

### 1. Railway
- Push your code to GitHub
- Connect your repository to Railway
- Set environment variables
- Deploy automatically

### 2. Render
- Connect your GitHub repository
- Select "Web Service"
- Set build and start commands
- Deploy

### 3. Google Cloud Run
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/[PROJECT-ID]/clarity-grid-chatbot

# Deploy to Cloud Run
gcloud run deploy --image gcr.io/[PROJECT-ID]/clarity-grid-chatbot --platform managed
```

### 4. AWS App Runner
- Use the Dockerfile for containerized deployment
- Connect your GitHub repository
- Configure auto-deployment

## Environment Variables

For production deployment, set these environment variables:

- `GOOGLE_AI_API_KEY`: Your Google AI API key
- `PORT`: Port number (default: 8000)

## Project Structure

```
├── app.py                 # Main FastAPI application
├── generate_embeddings.py # Script to generate FAISS embeddings
├── RAG_CHATBOT.py        # Standalone chatbot script
├── data.json             # Raw data file
├── data_preprocessed.jsonl # Preprocessed data
├── faiss_index.idx       # FAISS vector index
├── metadata.json         # Document metadata
├── templates/
│   └── index.html        # Web interface template
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── README.md           # This file
```

## Usage

1. Open your browser to `http://localhost:8000`
2. Enter your question about electrical grid data
3. The system will:
   - Find relevant documents using FAISS similarity search
   - Generate a contextual response using Gemini AI
   - Display the answer in the web interface

## API Documentation

FastAPI automatically generates API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## License

MIT License - see LICENSE file for details