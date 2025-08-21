#!/usr/bin/env python3
"""
EXR Editing Suite - Desktop Application
Main entry point for the desktop application using pywebview
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.app import create_desktop_window

def main():
    """Main entry point for the desktop application"""
    print("Starting EXR Editing Suite...")
    
    # Create and run the desktop window (backend startup is handled inside)
    create_desktop_window()

if __name__ == "__main__":
    main()
