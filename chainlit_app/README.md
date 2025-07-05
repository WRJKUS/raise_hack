# 🚀 LangGraph Proposal Analyzer

Welcome to the **LangGraph Proposal Analyzer** - an intelligent proposal comparison and analysis system powered by LangGraph workflows and Chroma vector database.

## ✨ Features

- **📄 Proposal Upload**: Upload multiple proposal documents for analysis
- **🤖 AI-Powered Analysis**: Comprehensive comparison using advanced LLM models
- **🔍 Vector Search**: Intelligent similarity search using Chroma vector database
- **💬 Interactive Q&A**: Ask questions about your proposals and get detailed answers
- **📊 Workflow Visualization**: Real-time workflow status and progress tracking
- **🎨 Modern UI**: Clean, responsive interface with custom styling

## 🚀 Quick Start

### Prerequisites

- **For Dev Container Setup** (Recommended):
  - Docker Desktop installed and running
  - Visual Studio Code with Dev Containers extension
  - Groq API key (for LLM)
  - OpenAI API key (for embeddings)

- **For Local Setup**:
  - Python 3.11 or higher
  - Groq API key (for LLM)
  - OpenAI API key (for embeddings)

## 🐳 Development Container Setup (Recommended)

The easiest way to get started is using the pre-configured development container that includes all necessary dependencies and tools.

### Step 1: Prerequisites for Dev Container

1. **Install Docker Desktop**
   - Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop/)
   - Ensure Docker is running before proceeding

2. **Install VS Code and Dev Containers Extension**
   - Install [Visual Studio Code](https://code.visualstudio.com/)
   - Install the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

3. **Get Your API Keys**
   - **Groq API Key**: Visit [Groq Console](https://console.groq.com/) to create an account and generate an API key
   - **OpenAI API Key**: Visit [OpenAI Platform](https://platform.openai.com/) to create an account and generate an API key

### Step 2: Open Project in Dev Container

1. **Clone and Open Repository**
   ```bash
   git clone <repository-url>
   cd langgraph
   ```

2. **Open in VS Code**
   ```bash
   code .
   ```

3. **Reopen in Container**
   - VS Code should detect the `.devcontainer` configuration
   - Click "Reopen in Container" when prompted, or
   - Use Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`) → "Dev Containers: Reopen in Container"

4. **Wait for Container Build**
   - The first time will take a few minutes to build the container
   - Subsequent opens will be much faster

### Step 3: Configure API Keys in Dev Container

The API keys are configured in `.devcontainer/devcontainer.json` for the development container setup. However, once inside the dev container, you have several options to set up your API keys:

#### Option A: Configure in devcontainer.json (Recommended for Dev Container)
The API keys are set in `.devcontainer/devcontainer.json` as environment variables that are automatically loaded when the container starts. This provides a persistent and secure way to manage API keys in the development environment.

#### Option B: Set Environment Variables (Session-based)
```bash
# Set API keys for current session
export GROQ_API_KEY="your_groq_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"

# Verify they're set
echo $GROQ_API_KEY
echo $OPENAI_API_KEY
```

#### Option C: Add to Shell Profile (Persistent)
```bash
# Add to your shell profile for persistence
echo 'export GROQ_API_KEY="your_groq_api_key_here"' >> ~/.bashrc
echo 'export OPENAI_API_KEY="your_openai_api_key_here"' >> ~/.bashrc

# Reload shell configuration
source ~/.bashrc
```

#### Option D: Create .env File (Alternative)
```bash
# Navigate to chainlit_app directory
cd chainlit_app

# Create .env file with API keys
cat > .env << EOF
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
GROQ_MODEL=llama-3.1-8b-instant
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_proposal_db
CHROMA_COLLECTION_NAME=proposal_collection

# Application Configuration
APP_NAME=LangGraph Proposal Analyzer
APP_DESCRIPTION=An intelligent proposal comparison and analysis system powered by LangGraph workflows
MAX_FILE_SIZE_MB=10
SESSION_TIMEOUT=3600

# UI Configuration
ENABLE_TELEMETRY=true
SHOW_PROMPT_PLAYGROUND=true
DEFAULT_THEME=light

# Development Configuration
DEBUG=false
LOG_LEVEL=INFO
EOF
```

### Step 4: Run the Application in Dev Container

```bash
# Navigate to chainlit_app directory (if not already there)
cd chainlit_app

# Install dependencies (usually pre-installed in dev container)
pip install -r requirements.txt

# Run the application
python run.py
```

The application will be available at `http://localhost:8000`

### Step 5: Verify Setup

1. **Check API Keys**
   ```bash
   # Test if API keys are accessible
   python -c "import os; print('GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')"
   python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
   ```

2. **Test Application**
   - Open `http://localhost:8000` in your browser
   - Try the demo functionality to ensure everything works

## 💻 Local Installation (Alternative)

If you prefer not to use the dev container, you can set up the environment locally:

### Local Setup Steps

1. **Clone or navigate to the chainlit_app directory**
   ```bash
   cd chainlit_app
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   The API keys are configured in `.devcontainer/devcontainer.json`. You can either:
   - Copy the devcontainer.json.example to .devcontainer/devcontainer.json and set the API keys there
   - Or create a .env file in the chainlit_app directory with your API keys

4. **Run the application**
   ```bash
   python run.py
   ```

   Or manually:
   ```bash
   chainlit run app.py -w --port 8000
   ```

5. **Open your browser**
   Navigate to `http://localhost:8000`

## 🔧 Configuration

### Environment Variables

The application uses environment variables for configuration. These can be set in multiple ways:

1. **Using .env file** (Recommended - see dev container setup above)
2. **System environment variables**
3. **Shell session variables**

#### Complete .env File Template

```env
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Model Configuration
GROQ_MODEL=llama-3.1-8b-instant
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# Vector Database Configuration
CHROMA_PERSIST_DIRECTORY=./chroma_proposal_db
CHROMA_COLLECTION_NAME=proposal_collection

# Application Configuration
APP_NAME=LangGraph Proposal Analyzer
APP_DESCRIPTION=An intelligent proposal comparison and analysis system powered by LangGraph workflows
MAX_FILE_SIZE_MB=10
SESSION_TIMEOUT=3600

# UI Configuration
ENABLE_TELEMETRY=true
SHOW_PROMPT_PLAYGROUND=true
DEFAULT_THEME=light

# Development Configuration
DEBUG=false
LOG_LEVEL=INFO

# Optional: Literal AI Configuration (for advanced analytics)
LITERAL_AI_URL=
LITERAL_AI_API_KEY=
```

### API Keys Setup

**Note**: For development container setup, API keys are configured in `.devcontainer/devcontainer.json`.

1. **Groq API Key**:
   - Visit [Groq Console](https://console.groq.com/)
   - Create an account and generate an API key
   - Add to your `.env` file, set as environment variable, or configure in `.devcontainer/devcontainer.json`

2. **OpenAI API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/)
   - Create an account and generate an API key
   - Add to your `.env` file, set as environment variable, or configure in `.devcontainer/devcontainer.json`

### Dev Container Benefits

When using the dev container setup:
- ✅ **Consistent Environment**: Same Python version, dependencies, and tools for all developers
- ✅ **Pre-configured**: All necessary packages and extensions pre-installed
- ✅ **Isolated**: No conflicts with your local Python environment
- ✅ **Portable**: Works the same on Windows, macOS, and Linux
- ✅ **Quick Setup**: Get started in minutes, not hours

## 🛠️ How It Works

### 1. **Setup Phase**
- Upload your proposal documents or use demo data
- Documents are processed and embedded into a Chroma vector store
- Vector database is initialized for efficient similarity search

### 2. **Analysis Phase**
- AI analyzes all proposals comprehensively
- Generates detailed comparison reports
- Identifies key differences, strengths, and recommendations

### 3. **Interactive Phase**
- Ask specific questions about the proposals
- Get contextual answers based on vector similarity search
- Explore different aspects of your proposals

## 🎯 Usage Guide

### Getting Started

1. **Launch the Application**
   - **Dev Container**: Follow the dev container setup above, then run `python run.py`
   - **Local Setup**: Install dependencies and run `python run.py` or use Chainlit directly
   - Open `http://localhost:8000` in your browser

2. **Choose Your Option**
   - **Demo**: Try with sample proposals
   - **Upload**: Add your own proposal documents
   - **Help**: View available commands

3. **Upload Proposals** (if not using demo)
   - Click "Upload Files" or type `upload`
   - Select your proposal documents
   - Wait for processing to complete

4. **Review Analysis**
   - Read the comprehensive analysis report
   - Note key findings and recommendations

5. **Ask Questions**
   - Use natural language to ask about proposals
   - Try the suggested questions or ask your own
   - Get detailed, contextual responses

### Example Workflow

```
1. Start app → 2. Upload proposals → 3. Review analysis → 4. Ask questions
```

## 💡 Example Questions

### Budget Analysis
- "Which proposal has the highest budget?"
- "What's the total cost of all proposals?"
- "Compare the cost-effectiveness of each proposal"

### Timeline Comparison
- "Which proposal has the shortest timeline?"
- "Compare the delivery schedules"
- "What are the project milestones?"

### Technical Analysis
- "What are the key technical differences?"
- "Which proposal uses the most advanced technology?"
- "What are the technical requirements?"

### Risk Assessment
- "What are the main risks in each proposal?"
- "Which proposal carries the least risk?"
- "What mitigation strategies are proposed?"

## 🔧 Technical Architecture

### Core Components

- **LangGraph Workflows**: Structured, stateful processing
- **Chroma Vector Database**: Efficient similarity search and retrieval
- **Groq LLM**: Fast language model inference
- **OpenAI Embeddings**: High-quality text embeddings
- **Chainlit UI**: Interactive web interface

### Workflow Nodes

1. **Setup Node**: Processes proposals and creates vector store
2. **Comparison Node**: Generates comprehensive analysis
3. **Interactive Node**: Handles user questions and responses
4. **Decision Node**: Manages workflow flow control

### Data Flow

```
Proposals → Vector Store → Analysis → Interactive Q&A
```

## 📋 Supported File Types

- **📄 PDF documents** (.pdf) - **Recommended format**
  - Full text extraction from all pages
  - Handles complex layouts and formatting
  - Best compatibility with proposal documents
- **📝 Text files** (.txt) - Plain text format
- **📄 Word documents** (.docx) - Microsoft Word format
- **📝 Markdown files** (.md) - Markdown format

**File Requirements:**
- Maximum size: 10MB per file
- PDF files are automatically processed for text extraction
- Include budget and timeline information for better analysis
- Multiple files can be uploaded simultaneously

## 🎨 User Interface

### Main Features

- **Action Buttons**: Quick access to common functions
- **Workflow Status**: Visual progress indicators
- **Proposal Cards**: Clean document summaries
- **Interactive Chat**: Natural language interface
- **Question Suggestions**: Pre-built query options

### Commands

- `demo` - Load sample proposals
- `upload` - Upload your documents
- `status` - Check workflow status
- `help` - Show available commands

## 🔍 Troubleshooting

### Dev Container Issues

**1. Container Won't Start**
```
Error: Failed to start dev container
```
**Solution:**
- Ensure Docker Desktop is running
- Check Docker has sufficient resources allocated
- Try rebuilding the container: Command Palette → "Dev Containers: Rebuild Container"

**2. Port Already in Use**
```
Error: Port 8000 is already in use
```
**Solution:**
- Stop other applications using port 8000
- Or modify the port in `run.py` or use: `chainlit run app.py -w --port 8001`

**3. API Keys Not Found in Container**
```
Error: API key not found
```
**Solution:**
- Verify `.env` file exists in `chainlit_app` directory
- Check environment variables: `echo $GROQ_API_KEY`
- Recreate `.env` file following the dev container setup steps

### Common Application Issues

**1. API Key Errors**
```
Error: Invalid API key
```
**Solution:**
- Check your `.env` file and ensure API keys are correct
- Verify API keys work by testing them directly with the providers
- Ensure no extra spaces or quotes in the API keys

**2. File Upload Issues**
```
Error: File processing failed
```
**Solution:**
- Check file format (PDF, TXT, DOCX, MD)
- Ensure file size is under 10MB
- Verify file encoding (UTF-8 recommended)
- Try with a simple text file first

**3. Vector Store Errors**
```
Error: Vector store not initialized
```
**Solution:**
- Restart the workflow by uploading proposals again
- Clear the Chroma database: `rm -rf chainlit_app/chroma_proposal_db`
- Restart the application

**4. Memory Issues**
```
Error: Out of memory
```
**Solution:**
- Reduce file sizes
- Process fewer files at once
- Restart the application
- In dev container: increase Docker memory allocation

### Debug Mode

Enable debug mode by setting in your `.env`:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🚀 Advanced Usage

### Custom Configuration

Edit `.chainlit/config.toml` to customize:
- UI theme and colors
- Session timeout
- File upload limits
- Feature toggles

### Extending Functionality

The application is built with modularity in mind:
- Add new workflow nodes
- Integrate additional LLM providers
- Customize analysis templates
- Add new file format support

## 📊 Performance Tips

### Optimization

1. **File Preparation**
   - Use text files when possible (faster processing)
   - Include structured information (budgets, timelines)
   - Remove unnecessary formatting

2. **Question Formulation**
   - Be specific in your questions
   - Reference proposal names when possible
   - Ask one question at a time for best results

3. **Session Management**
   - Use the same session for related questions
   - Check workflow status if experiencing issues
   - Restart if needed for fresh analysis

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest black flake8
   ```
3. Run tests:
   ```bash
   pytest
   ```
4. Format code:
   ```bash
   black app.py
   ```

### Project Structure

```
chainlit_app/
├── app.py                 # Main application
├── run.py                 # Startup script
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
├── README.md             # Documentation
├── .chainlit/
│   └── config.toml       # Chainlit configuration
└── public/
    └── style.css         # Custom styling
```

## 📝 License

This project is part of the LangGraph codebase. Please refer to the main repository for license information.

## 🆘 Support

### Getting Help

1. **Check Documentation**: Review this README and inline help
2. **Use Help Command**: Type `help` in the application
3. **Check Logs**: Enable debug mode for detailed logging
4. **Restart Application**: Often resolves temporary issues

### Common Solutions

- **Slow Performance**: Reduce file sizes, check internet connection
- **Analysis Errors**: Verify API keys, check file formats
- **UI Issues**: Clear browser cache, try different browser
- **Upload Problems**: Check file permissions, verify formats

---

## 🎉 Ready to Get Started?

### Quick Start with Dev Container (Recommended)
1. **Open in VS Code** and reopen in dev container
2. **Set up API keys** using the .env file method
3. **Run the application** with `python run.py`
4. **Upload proposals** or try the demo
5. **Start analyzing** and asking questions!

### Alternative Local Setup
1. **Set up your environment** with Python 3.11+ and API keys
2. **Install dependencies** using pip
3. **Configure environment** variables or .env file
4. **Run the application** with `python run.py`
5. **Upload proposals** or try the demo
6. **Start analyzing** and asking questions!

**Happy analyzing!** 🚀📊
