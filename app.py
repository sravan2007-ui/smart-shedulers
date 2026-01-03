#!/usr/bin/env python3
"""
Redirect script to run the main Flask application from the backend directory.
This file exists to handle cases where app.py is called from the root directory.
"""

import os
import sys

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Change to the backend directory
os.chdir(backend_dir)

# Import and run the main application
from app import app, init_db

if __name__ == '__main__':
    # Initialize database if needed
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5001)
