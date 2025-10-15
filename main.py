#!/usr/bin/env python3
"""
Main entry point for the Music Streaming API
Railpack will automatically detect and run this with uvicorn
"""
from streaming_improved import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)