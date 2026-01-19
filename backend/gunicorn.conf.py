# gunicorn.conf.py
timeout = 120      # 2 minutes (prevents worker timeout)
workers = 1        # Single worker for free tier
keepalive = 5      # Keep connections alive
