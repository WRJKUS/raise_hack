# Leonardo's RFQ Alchemy - Production Deployment Guide

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# 1. Run the production setup script (as root)
sudo ./production-setup.sh

# 2. Configure environment variables
sudo nano /opt/rfq-alchemy/.env

# 3. Deploy the application
cd /opt/rfq-alchemy
sudo -u rfq-alchemy ./deploy.sh
```

### Option 2: Manual Deployment
```bash
# 1. Create logs directory
mkdir -p logs

# 2. Build frontend
cd leonardos-rfq-alchemy-main
npm ci --only=production
npm run build
cd ..

# 3. Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## Production Configuration

### Environment Variables (.env)
```bash
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Production Settings
DEBUG=False
NODE_ENV=production

# Paths (adjust for your server)
CHROMA_PERSIST_DIRECTORY=/var/lib/rfq-alchemy/chroma_proposal_db
UPLOAD_DIRECTORY=/var/lib/rfq-alchemy/uploads
```

### PM2 Configuration Features
- **Gunicorn**: Uses 4 worker processes for better performance
- **Auto-restart**: Processes restart on failure
- **Logging**: Comprehensive logging to `/logs/` directory
- **Memory limits**: Automatic restart if memory usage exceeds limits
- **Production mode**: Optimized for production environment

### Services
- **Frontend**: Runs on port 3002 (built static files)
- **Backend**: Runs on port 8000 (Gunicorn + Uvicorn workers)

## Security Considerations

### Firewall Configuration
```bash
ufw enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 3002  # Frontend
ufw allow 8000  # Backend API
```

### Nginx Reverse Proxy (Recommended)
```bash
# Copy nginx configuration
sudo cp nginx.conf.template /etc/nginx/sites-available/rfq-alchemy
sudo ln -s /etc/nginx/sites-available/rfq-alchemy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL/TLS Setup
```bash
# Using Let's Encrypt (recommended)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring and Management

### PM2 Commands
```bash
pm2 status                    # Show process status
pm2 logs                      # Show all logs
pm2 logs rfq-alchemy-backend  # Backend logs only
pm2 logs rfq-alchemy-frontend # Frontend logs only
pm2 restart all               # Restart all processes
pm2 reload all                # Zero-downtime reload
pm2 stop all                  # Stop all processes
pm2 delete all                # Remove all processes
pm2 monit                     # Real-time monitoring
```

### System Service (Optional)
```bash
# Enable systemd service for auto-start on boot
sudo systemctl enable rfq-alchemy
sudo systemctl start rfq-alchemy
sudo systemctl status rfq-alchemy
```

### Log Files
- PM2 logs: `./logs/`
- Gunicorn access logs: `./logs/backend-access.log`
- Gunicorn error logs: `./logs/backend-error.log`
- System logs: `/var/log/rfq-alchemy/`

## Performance Optimization

### Backend (Gunicorn)
- 4 worker processes (adjust based on CPU cores)
- Uvicorn workers for async support
- Memory monitoring and auto-restart

### Frontend (Vite)
- Production build with optimizations
- Static file serving
- Gzip compression (via nginx)

### Database
- Persistent Chroma vector database
- Optimized for production workloads

## Troubleshooting

### Common Issues
1. **Port conflicts**: Ensure ports 3002 and 8000 are available
2. **Permission errors**: Check file ownership and permissions
3. **API key errors**: Verify environment variables are set
4. **Memory issues**: Monitor with `pm2 monit`

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend accessibility
curl http://localhost:3002

# PM2 status
pm2 status
```

### Logs Analysis
```bash
# Real-time logs
pm2 logs --lines 100

# Error logs only
pm2 logs --err

# Specific service logs
pm2 logs rfq-alchemy-backend --lines 50
```

## Backup and Maintenance

### Important Directories
- `/var/lib/rfq-alchemy/chroma_proposal_db/` - Vector database
- `/var/lib/rfq-alchemy/uploads/` - Uploaded files
- `/opt/rfq-alchemy/.env` - Configuration

### Regular Maintenance
```bash
# Update dependencies
pip install -r requirements.txt --upgrade
npm update

# Restart services
pm2 restart all

# Clean old logs
pm2 flush
```

## Access Points

After successful deployment:
- **Frontend**: http://your-domain.com:3002 (or via nginx proxy)
- **Backend API**: http://your-domain.com:8000
- **API Documentation**: http://your-domain.com:8000/api/docs
- **PM2 Web Interface**: `pm2 web` (optional)
