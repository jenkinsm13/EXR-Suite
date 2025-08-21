"""
Main FastAPI application for EXR Editing Suite
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
import logging
import os

from api.files_router import router as files_router
from api.images_router import router as images_router
from api.editing_router import router as editing_router
from api.metadata_router import router as metadata_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="EXR Editing Suite API",
    description="High-performance EXR editing suite with OpenEXR integration",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(images_router, prefix="/api/images", tags=["images"])
app.include_router(editing_router, prefix="/api/editing", tags=["editing"])
app.include_router(metadata_router, prefix="/api/metadata", tags=["metadata"])

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "EXR Editing Suite API",
        "version": "1.0.0"
    }

# Root endpoint - serve frontend
@app.get("/")
async def root():
    """Serve the frontend application"""
    from fastapi.responses import FileResponse
    import os
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return FileResponse(os.path.join(static_dir, "index.html"))

# Catch-all route for frontend assets
@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    """Catch-all route for frontend assets and routing"""
    from fastapi.responses import FileResponse
    import os
    
    # Don't handle API routes
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    file_path = os.path.join(static_dir, full_path)
    
    # If file exists, serve it
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    
    # Otherwise serve the frontend index.html for client-side routing
    return FileResponse(os.path.join(static_dir, "index.html"))

# API info endpoint
@app.get("/api/info")
async def api_info():
    """API information endpoint"""
    return {
        "message": "EXR Editing Suite API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }



if __name__ == "__main__":
    # Get configuration from environment variables
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8001"))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"Starting EXR Editing Suite API on {host}:{port}")
    logger.info(f"Reload mode: {reload}")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
