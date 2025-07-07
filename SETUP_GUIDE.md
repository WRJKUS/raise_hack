# 🚀 Complete Setup Guide for Leonardo's RFQ Alchemy Platform

This guide will walk you through setting up the complete AI-powered proposal comparison platform from scratch.

## 📋 Prerequisites

### 1. System Requirements
- Python 3.11+
- Node.js 18+
- Git

### 2. API Keys Required
- **Groq API Key**: Get from [Groq Console](https://console.groq.com/)
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/)

## 🔧 Step-by-Step Setup

### Step 1: Environment Configuration

1. **Copy the environment template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your API keys**:
   ```bash
   # Required API Keys
   GROQ_API_KEY=your_groq_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here

   # Optional: Customize other settings
   DEFAULT_LLM_MODEL=llama-3.1-8b-instant
   TEMPERATURE=0.1
   MAX_TOKENS=4000
   ```

### Step 2: Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Test the workflow (optional)**:
   ```bash
   python test_workflow.py
   ```

3. **Start the backend server**:
   ```bash
   python start_backend.py
   ```

   You should see:
   ```
   ✅ Environment variables configured
   📦 Installing Python dependencies...
   ✅ Dependencies installed successfully
   📁 Created directory: uploads
   📁 Created directory: chroma_proposal_db
   🚀 Starting FastAPI server...
   📍 API will be available at: http://localhost:8000
   📖 API documentation at: http://localhost:8000/api/docs
   ```

### Step 3: Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd leonardos-rfq-alchemy-main
   ```

2. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   ```

   The frontend will be available at: http://localhost:8080

### Step 4: Verify Integration

1. **Run integration tests**:
   ```bash
   # From the root directory
   python test_integration.py
   ```

2. **Manual verification**:
   - Open http://localhost:8080 in your browser
   - Go to "Analysis Agent" tab
   - Upload a PDF proposal
   - Click "Start AI Analysis"
   - Go to "Chat Assistant" tab
   - Ask questions about your proposals

## 🎯 Usage Workflow

### 1. Upload Proposals
- Navigate to the "Analysis Agent" tab
- Click "Choose Files" and select PDF proposals
- Wait for upload confirmation

### 2. Start Analysis
- Click "Start AI Analysis" button
- Wait for the AI to process and analyze proposals
- Review the comparative analysis results

### 3. Interactive Chat
- Go to "Chat Assistant" tab
- Ask questions like:
  - "What is the average budget of the proposals?"
  - "Which proposal has the fastest timeline?"
  - "Compare the technical approaches"
  - "What are the main risks?"

### 4. Review Results
- Check the analysis scores and rankings
- Review strengths and concerns for each proposal
- Use insights for decision making

## 🔍 API Endpoints Reference

### Health Check
```bash
curl http://localhost:8000/api/health
```

### Upload Proposal
```bash
curl -X POST -F "file=@proposal.pdf" http://localhost:8000/api/proposals/upload
```

### Start Analysis
```bash
curl -X POST -H "Content-Type: application/json" -d "{}" http://localhost:8000/api/analysis/start
```

### Send Chat Message
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "What is the average budget?"}' \
  http://localhost:8000/api/chat/message
```

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
- **Check API keys**: Ensure GROQ_API_KEY and OPENAI_API_KEY are set
- **Check dependencies**: Run `pip install -r requirements.txt`
- **Check port**: Make sure port 8000 is not in use

#### Frontend Can't Connect
- **Backend running**: Verify backend is running at http://localhost:8000
- **CORS issues**: Backend is configured for localhost:8080
- **Check console**: Look for error messages in browser console

#### Upload Fails
- **File format**: Only PDF files are supported
- **File size**: Maximum 10MB per file
- **Permissions**: Check upload directory permissions

#### Analysis Fails
- **No proposals**: Upload proposals before starting analysis
- **API limits**: Check if you've hit API rate limits
- **Network**: Verify internet connection for API calls

### Error Messages

#### "Vector store not initialized"
- Upload proposals first, then start analysis

#### "No proposals available for analysis"
- Upload PDF files using the Analysis Agent tab

#### "Failed to process PDF"
- Ensure PDF is not corrupted or password-protected
- Try a different PDF file

#### "API connection failed"
- Check if backend server is running
- Verify API keys are correctly set

## 📊 Performance Tips

### For Better Analysis
- Upload high-quality, text-based PDFs
- Include proposals with clear structure
- Ensure proposals contain budget and timeline information

### For Faster Processing
- Upload smaller PDF files when possible
- Limit concurrent uploads
- Use specific questions in chat for better responses

## 🔒 Security Notes

- API keys are stored in environment variables
- Files are stored locally in the uploads directory
- Vector database is persisted locally
- No data is sent to external services except AI APIs

## 🚀 Production Deployment

### Backend Deployment
```bash
# Install all dependencies (including gunicorn for production)
pip install -r requirements.txt

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.main:app --bind 0.0.0.0:8000
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Serve static files with nginx or similar
```

### Environment Variables for Production
```bash
DEBUG=False
CHROMA_PERSIST_DIRECTORY=/app/data/chroma
UPLOAD_DIRECTORY=/app/data/uploads
```

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the logs in the terminal
3. Test with the integration script: `python test_integration.py`
4. Verify API keys are correctly set
5. Check that all dependencies are installed

## 🎉 Success Indicators

You'll know everything is working when:

- ✅ Backend starts without errors
- ✅ Frontend loads at http://localhost:8080
- ✅ You can upload PDF files
- ✅ Analysis completes successfully
- ✅ Chat assistant responds to questions
- ✅ Integration tests pass

Congratulations! Your AI-powered proposal comparison platform is ready to use! 🎊
