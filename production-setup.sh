#!/bin/bash

# Leonardo's RFQ Alchemy - Production Server Setup Script
# This script sets up the application for production deployment

set -e

echo "🏭 Leonardo's RFQ Alchemy - Production Server Setup"
echo "===================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root for initial setup"
    echo "   Run: sudo ./production-setup.sh"
    exit 1
fi

# Update system packages
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required system packages
echo "📦 Installing system dependencies..."
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nodejs \
    npm \
    ufw \
    curl \
    git

# Install PM2 globally
echo "📦 Installing PM2..."
npm install -g pm2

# Create application user
echo "👤 Creating application user..."
if ! id "rfq-alchemy" &>/dev/null; then
    useradd -r -s /bin/bash -d /opt/rfq-alchemy -m rfq-alchemy
fi

# Create application directories
echo "📁 Creating application directories..."
mkdir -p /opt/rfq-alchemy
mkdir -p /var/lib/rfq-alchemy/{uploads,chroma_proposal_db}
mkdir -p /var/log/rfq-alchemy

# Set proper ownership
chown -R rfq-alchemy:rfq-alchemy /opt/rfq-alchemy
chown -R rfq-alchemy:rfq-alchemy /var/lib/rfq-alchemy
chown -R rfq-alchemy:rfq-alchemy /var/log/rfq-alchemy

# Copy application files (assuming current directory contains the app)
echo "📋 Copying application files..."
cp -r . /opt/rfq-alchemy/
chown -R rfq-alchemy:rfq-alchemy /opt/rfq-alchemy

# Set up Python virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u rfq-alchemy python3 -m venv /opt/rfq-alchemy/venv
sudo -u rfq-alchemy /opt/rfq-alchemy/venv/bin/pip install --upgrade pip
sudo -u rfq-alchemy /opt/rfq-alchemy/venv/bin/pip install -r /opt/rfq-alchemy/requirements.txt
sudo -u rfq-alchemy /opt/rfq-alchemy/venv/bin/pip install gunicorn

# Install Node.js dependencies and build frontend
echo "🔨 Building frontend..."
cd /opt/rfq-alchemy/leonardos-rfq-alchemy-main
sudo -u rfq-alchemy npm ci --only=production
sudo -u rfq-alchemy npm run build
cd /opt/rfq-alchemy

# Set up environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f /opt/rfq-alchemy/.env ]; then
    cp /opt/rfq-alchemy/.env.production /opt/rfq-alchemy/.env
    echo "📝 Please edit /opt/rfq-alchemy/.env with your API keys and configuration"
fi

# Configure firewall
echo "🔥 Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 3002  # Frontend
ufw allow 8000  # Backend API

# Create systemd service
echo "⚙️  Creating systemd service..."
cp /opt/rfq-alchemy/rfq-alchemy.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable rfq-alchemy

echo "✅ Production setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit /opt/rfq-alchemy/.env with your API keys"
echo "2. Configure nginx reverse proxy (optional but recommended)"
echo "3. Set up SSL certificates"
echo "4. Start the service: systemctl start rfq-alchemy"
echo ""
echo "🚀 To deploy/start the application:"
echo "   cd /opt/rfq-alchemy"
echo "   sudo -u rfq-alchemy ./deploy.sh"
echo ""
echo "📊 To monitor the application:"
echo "   systemctl status rfq-alchemy"
echo "   sudo -u rfq-alchemy pm2 status"
echo "   sudo -u rfq-alchemy pm2 logs"
