#!/usr/bin/env python3
"""
EXR Editing Suite - Desktop Application Module
Provides functions for starting the backend and creating the desktop window
"""

import webview
import threading
import uvicorn
import logging
import os
import sys
import time
import socket
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from .main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def find_available_port(start_port=8001, max_attempts=10):
    """Find an available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_attempts}")

def start_backend(port=None):
    """Start FastAPI backend in separate thread"""
    if port is None:
        port = find_available_port()
    
    try:
        logger.info(f"Starting FastAPI backend on port {port}...")
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=port, 
            log_level="info",
            access_log=False,  # Disable access logs in desktop mode
            reload=False  # Disable reload to prevent double startup
        )
    except Exception as e:
        logger.error(f"Error starting backend: {e}")
        raise

def create_desktop_window():
    """Create and start the pywebview desktop window"""
    try:
        # Find available port
        port = find_available_port()
        logger.info(f"Using port {port} for backend")
        
        # Start backend in separate thread
        backend_thread = threading.Thread(target=start_backend, args=(port,), daemon=True)
        backend_thread.start()
        
        # Wait a moment for backend to start
        time.sleep(2)
        
        # Create pywebview window
        logger.info("Creating desktop window...")
        webview.create_window(
            'EXR Editing Suite',
            f'http://127.0.0.1:{port}',
            width=1400,
            height=900,
            resizable=True,
            text_select=True,
            min_size=(800, 600),
            background_color='#1f2937',  # Dark background
            frameless=False,
            easy_drag=True,
            fullscreen=False
        )
        
        # Start the webview event loop
        webview.start(debug=False)
        
    except Exception as e:
        logger.error(f"Error creating desktop window: {e}")
        sys.exit(1)

if __name__ == "__main__":
    """Main entry point for desktop application"""
    try:
        logger.info("Starting EXR Editing Suite Desktop Application...")
        create_desktop_window()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
