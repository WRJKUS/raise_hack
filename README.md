# Leonardo's RFQ Alchemy Platform

An AI-powered proposal comparison and analysis platform that integrates React frontend with FastAPI backend and LangGraph AI agents.

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + shadcn/ui
- **Backend**: FastAPI + Python
- **AI Engine**: LangGraph + LangChain + Groq/OpenAI
- **Vector Database**: Chroma
- **PDF Processing**: PyPDF2 + pdfplumber

## 🐳 Development Container Setup (Recommended)

For the easiest development experience, use the provided devcontainer configuration which includes all necessary tools and dependencies.

### Prerequisites

1. **Docker**: Install Docker Desktop
2. **VS Code**: Install Visual Studio Code with the Dev Containers extension
3. **API Keys**: You'll need the same API keys mentioned above

### Setup Steps

1. **Copy devcontainer configuration**:

   ```bash
   cp devcontainer.json.example .devcontainer/devcontainer.json
   ```

2. **Configure API Keys**: Edit `.devcontainer/devcontainer.json` and add your API keys:

   ```json
   "containerEnv": {
     "GROQ_API_KEY": "your_groq_api_key_here",
     "OPENAI_API_KEY": "your_openai_api_key_here"
   }
   ```

3. **Open in Dev Container**:
   - Open the project in VS Code
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Type "Dev Containers: Reopen in Container"
   - Select the command and wait for the container to build

### What's Included

The devcontainer provides:

- **Python 3.11** with all backend dependencies pre-installed
- **Node.js 18** with frontend dependencies pre-installed
- **VS Code extensions** for Python, TypeScript, Tailwind CSS, and more
- **Port forwarding** for backend (8000), frontend (8080), and Jupyter (8888)
- **Git and GitHub CLI** for version control
- **Automatic setup** that runs `pip install` and `npm install` on container creation

### Running the Application

Once the devcontainer is running:

1. **Start Backend** (in VS Code terminal):

   ```bash
   python start_backend.py
   ```

2. **Start Frontend** (in a new terminal):
   ```bash
   python start_frontend.py
   ```

The application will be available at the same URLs as the manual setup, with ports automatically forwarded from the container.

## 🎯 Features

### 1. Proposal Upload & Analysis

- Upload PDF proposal documents
- Automatic text extraction and processing
- AI-powered comparative analysis
- Scoring and ranking system

### 2. Interactive Chat Assistant

- Ask questions about uploaded proposals
- Context-aware responses using vector search
- Session-based conversation history
- Real-time proposal insights

### 3. LangGraph Workflow

- Multi-node AI workflow for proposal processing
- Vector store integration with Chroma
- Conditional workflow execution
- State management across conversation

## 📁 Project Structure

```
├── backend/                    # FastAPI backend
│   ├── core/                  # Configuration and settings
│   ├── models/                # Pydantic schemas
│   ├── routers/               # API endpoints
│   ├── services/              # Business logic
│   └── main.py               # FastAPI application
├── leonardos-rfq-alchemy-main/ # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── lib/              # API client and utilities
│   │   └── pages/            # Page components
├── requirements.txt           # Python dependencies
├── start_backend.py          # Backend startup script
├── start_frontend.py         # Frontend startup script
└── test_integration.py       # Integration tests
```

## 🔧 API Endpoints

### Proposals

- `POST /api/proposals/upload` - Upload proposal PDF
- `GET /api/proposals/list` - List all proposals
- `GET /api/proposals/{id}` - Get specific proposal
- `DELETE /api/proposals/{id}` - Delete proposal
- `GET /api/proposals/analysis/results` - Get analysis results

### Analysis

- `POST /api/analysis/start` - Start proposal analysis
- `GET /api/analysis/status/{session_id}` - Get analysis status
- `GET /api/analysis/result/{session_id}` - Get analysis result

### Chat

- `POST /api/chat/message` - Send chat message
- `GET /api/chat/history/{session_id}` - Get chat history
- `DELETE /api/chat/session/{session_id}` - Clear chat session

## 🧪 Testing

Run the integration test suite:

```bash
python test_integration.py
```

This will test:

- Backend health check
- File upload functionality
- Proposal analysis workflow
- Chat assistant responses
- API endpoint integration

## 🔍 Usage Workflow

1. **Upload Proposals**: Go to "Analysis Agent" tab and upload PDF proposals
2. **Start Analysis**: Click "Start AI Analysis" to process proposals
3. **Review Results**: View comparative analysis with scores and insights
4. **Ask Questions**: Use "Chat Assistant" to ask specific questions about proposals
5. **Get Insights**: Receive AI-powered responses with relevant proposal context

## ⚙️ Configuration

Key configuration options in `.env`:

```bash
# LLM Settings
DEFAULT_LLM_MODEL=llama-3.1-8b-instant
TEMPERATURE=0.1
MAX_TOKENS=4000

# Vector Database
EMBEDDING_MODEL=text-embedding-ada-002
CHROMA_PERSIST_DIRECTORY=./chroma_proposal_db

# File Upload
MAX_FILE_SIZE=10485760  # 10MB
UPLOAD_DIRECTORY=./uploads
```

## 🐛 Troubleshooting

### Backend Issues

- **API Keys**: Ensure GROQ_API_KEY and OPENAI_API_KEY are set
- **Dependencies**: Run `pip install -r requirements.txt`
- **Port Conflicts**: Backend runs on port 8000, frontend on 8080

### Frontend Issues

- **API Connection**: Check if backend is running at http://localhost:8000
- **CORS**: Backend is configured to allow frontend origin
- **Dependencies**: Run `npm install` in frontend directory

### Common Errors

- **"Vector store not initialized"**: Upload proposals before starting analysis
- **"No proposals available"**: Upload PDF files first
- **"API connection failed"**: Ensure backend server is running

## 🚀 Deployment

For production deployment:

1. **Backend**: Deploy FastAPI app using uvicorn/gunicorn
2. **Frontend**: Build with `npm run build` and serve static files
3. **Environment**: Set production API keys and configurations
4. **Database**: Use persistent storage for Chroma vector database

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Chroma Documentation](https://docs.trychroma.com/)
- [React Documentation](https://react.dev/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with `python test_integration.py`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
