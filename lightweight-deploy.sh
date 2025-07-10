#!/bin/bash

# Leonardo's RFQ Alchemy - Lightweight Production Deployment
# Optimized for small servers (1GB RAM)

set -e

echo "🚀 Leonardo's RFQ Alchemy - Lightweight Deployment"
echo "=================================================="

# Check available memory
MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
MEMORY_MB=$((MEMORY_KB / 1024))
echo "💾 Available memory: ${MEMORY_MB}MB"

if [ $MEMORY_MB -lt 1500 ]; then
    echo "⚠️  Low memory detected. Using optimized installation..."
    USE_SWAP=true
else
    USE_SWAP=false
fi

# Create swap file if needed for low memory systems
if [ "$USE_SWAP" = true ]; then
    echo "💾 Creating temporary swap file for installation..."
    if [ ! -f /swapfile ]; then
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo "✅ Swap file created"
    fi
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p chroma_proposal_db

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment and upgrade pip
echo "📦 Setting up virtual environment..."
source venv/bin/activate
pip install --upgrade pip

# Install only essential Python packages first
echo "📦 Installing essential Python packages..."
pip install --no-cache-dir \
    fastapi \
    uvicorn \
    gunicorn \
    python-dotenv \
    python-multipart \
    pydantic \
    pydantic-settings

# Install packages in smaller batches to avoid memory issues
echo "📦 Installing core dependencies (batch 1/3)..."
pip install --no-cache-dir \
    langchain \
    langchain-core \
    langchain-openai \
    langchain-groq \
    openai \
    groq

echo "📦 Installing vector database dependencies (batch 2/3)..."
pip install --no-cache-dir \
    chromadb \
    langchain-chroma

echo "📦 Installing PDF processing dependencies (batch 3/3)..."
pip install --no-cache-dir \
    PyPDF2 \
    pdfplumber \
    aiofiles

# Build frontend
echo "🔨 Building frontend..."
cd leonardos-rfq-alchemy-main

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm ci --only=production --no-audit --no-fund
fi

# Build the frontend
echo "🏗️  Building React application..."
npm run build

cd ..

# Create minimal ecosystem config for low-resource deployment
echo "⚙️  Creating optimized PM2 configuration..."
cat > ecosystem.minimal.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'rfq-alchemy-backend',
      script: './venv/bin/python',
      args: '-m uvicorn backend.main:app --host 0.0.0.0 --port 8000',
      cwd: process.cwd(),
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: process.cwd(),
        DEBUG: 'False'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '800M',
      min_uptime: '10s',
      max_restarts: 5,
      restart_delay: 4000,
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_file: './logs/backend-combined.log',
      time: true
    },
    {
      name: 'rfq-alchemy-frontend',
      script: 'npm',
      args: 'run preview -- --host 0.0.0.0 --port 3002',
      cwd: process.cwd() + '/leonardos-rfq-alchemy-main',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production'
      },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
      max_memory_restart: '200M',
      min_uptime: '10s',
      max_restarts: 5,
      restart_delay: 4000,
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_file: './logs/frontend-combined.log',
      time: true
    }
  ]
};
EOF

# Stop any existing PM2 processes
echo "🛑 Stopping existing PM2 processes..."
pm2 delete all 2>/dev/null || echo "No existing processes to stop"

# Start services with minimal config
echo "🚀 Starting services with PM2..."
pm2 start ecosystem.minimal.js

# Save PM2 configuration
echo "💾 Saving PM2 configuration..."
pm2 save

# Remove swap file if we created it
if [ "$USE_SWAP" = true ] && [ -f /swapfile ]; then
    echo "🧹 Cleaning up temporary swap file..."
    swapoff /swapfile
    rm /swapfile
fi

# Show status
echo "✅ Lightweight deployment complete!"
echo ""
echo "📊 PM2 Status:"
pm2 status

echo ""
echo "🌐 Services are now running:"
echo "  Frontend: http://localhost:3002"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "💡 This is a minimal deployment optimized for low-memory servers"
echo "   Some advanced features may require additional packages"
echo ""
echo "📝 Management commands:"
echo "  pm2 status    - Show process status"
echo "  pm2 logs      - Show all logs"
echo "  pm2 restart all - Restart services"
