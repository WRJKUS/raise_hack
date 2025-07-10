#!/bin/bash

# Leonardo's RFQ Alchemy - Production Deployment Script
# This script builds the frontend and starts both services with PM2

set -e  # Exit on any error

echo "🚀 Leonardo's RFQ Alchemy - Production Deployment"
echo "=================================================="

# Check if running as root (not recommended for production)
if [ "$EUID" -eq 0 ]; then
    echo "⚠️  Warning: Running as root is not recommended for production"
    echo "   Consider creating a dedicated user for the application"
fi

# Check if required environment variables are set
echo "🔍 Checking environment variables..."
if [ -z "$GROQ_API_KEY" ] && [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: No API keys found in environment"
    echo "   Make sure to set GROQ_API_KEY or OPENAI_API_KEY"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p chroma_proposal_db

# Set proper permissions
chmod 755 logs uploads chroma_proposal_db

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo "📦 Installing gunicorn for production..."
    pip install gunicorn
fi

# Navigate to frontend directory and build
echo "🔨 Building frontend for production..."
cd leonardos-rfq-alchemy-main

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm ci --only=production
fi

# Build the frontend
echo "🏗️  Building React application..."
npm run build

# Go back to project root
cd ..

# Stop any existing PM2 processes
echo "🛑 Stopping existing PM2 processes..."
pm2 delete all 2>/dev/null || echo "No existing processes to stop"

# Start services with PM2
echo "🚀 Starting services with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration for auto-restart on reboot
echo "💾 Saving PM2 configuration..."
pm2 save
pm2 startup

# Show status
echo "✅ Deployment complete!"
echo ""
echo "📊 PM2 Status:"
pm2 status

echo ""
echo "🌐 Services are now running:"
echo "  Frontend: http://localhost:3002"
echo "  Backend:  http://localhost:8000"
echo "  API Docs: http://localhost:8000/api/docs"
echo ""
echo "🔒 Security Notes:"
echo "  - Consider setting up a reverse proxy (nginx/apache)"
echo "  - Configure firewall rules"
echo "  - Set up SSL/TLS certificates"
echo "  - Review environment variables"
echo ""
echo "📝 Useful commands:"
echo "  pm2 status          - Show process status"
echo "  pm2 logs            - Show all logs"
echo "  pm2 logs rfq-alchemy-backend   - Show backend logs only"
echo "  pm2 logs rfq-alchemy-frontend  - Show frontend logs only"
echo "  pm2 restart all     - Restart all processes"
echo "  pm2 stop all        - Stop all processes"
echo "  pm2 delete all      - Delete all processes"
echo "  pm2 monit           - Monitor processes"
