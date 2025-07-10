module.exports = {
  apps: [
    {
      name: 'rfq-alchemy-backend',
      script: 'python',
      args: '-m gunicorn backend.main:app uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000',
      cwd: process.cwd(),
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        PYTHONPATH: process.cwd(),
        DEBUG: 'False'
      },
      watch: false,
    },
    {
      name: 'rfq-alchemy-frontend',
      script: "./build/index.js",
      watch: false,
      env: {
        NODE_ENV: "development",
        PORT: 3002
      },
      env_production: {
        NODE_ENV: "production",
        PORT: 3002
      }
    }
  ]
};
