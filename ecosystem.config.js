module.exports = {
  apps: [
    {
      name: 'rfq-alchemy-backend',
      script: 'python',
      args: '-m gunicorn backend.main:app -w 1 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --access-logfile ./logs/backend-access.log --error-logfile ./logs/backend-error.log',
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
      max_memory_restart: '2G',
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
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
      max_memory_restart: '1G',
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 4000,
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_file: './logs/frontend-combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
