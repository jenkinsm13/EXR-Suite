"""
Files router for directory operations and file management
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
import tkinter as tk
from tkinter import filedialog
import os

from api.models import (
    DirectoryListing, FileInfo, SearchRequest, SearchResponse,
    NavigationRequest, NavigationResponse, DriveInfo, SuccessResponse
)
from utils.file_utils import FileManager

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize file manager
file_manager = FileManager()

@router.post("/select-directory", response_model=NavigationResponse)
async def select_directory():
    """
    Open a directory selection dialog and navigate to the selected directory
    
    Returns:
        Navigation response with the selected directory listing
    """
    try:
        # Create a hidden root window for the file dialog
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Open directory selection dialog
        selected_path = filedialog.askdirectory(
            title="Select Directory",
            initialdir=os.path.expanduser("~")  # Start from user's home directory
        )
        
        # Destroy the root window
        root.destroy()
        
        if not selected_path:
            raise HTTPException(status_code=400, detail="No directory selected")
        
        # Navigate to the selected directory
        new_path = file_manager.navigate_to_directory(selected_path)
        directory_listing = file_manager.list_directory()
        
        return NavigationResponse(
            current_path=new_path,
            parent_path=file_manager.get_parent_directory(),
            directory_listing=DirectoryListing(**directory_listing)
        )
        
    except Exception as e:
        logger.error(f"Error selecting directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/directory", response_model=DirectoryListing)
async def list_directory(path: str = Query("", description="Directory path to list")):
    """
    List contents of a directory
    
    Args:
        path: Directory path (relative or absolute)
        
    Returns:
        Directory listing with files and subdirectories
    """
    try:
        result = file_manager.list_directory(path)
        return DirectoryListing(**result)
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file-info", response_model=FileInfo)
async def get_file_info(file_path: str = Query(..., description="Path to the file")):
    """
    Get detailed information about a file
    
    Args:
        file_path: Path to the file
        
    Returns:
        File information including size, dates, and type
    """
    try:
        result = file_manager.get_file_info(file_path)
        return FileInfo(**result)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error getting file info for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/navigate", response_model=NavigationResponse)
async def navigate_to_directory(request: NavigationRequest):
    """
    Navigate to a directory
    
    Args:
        request: Navigation request with target path
        
    Returns:
        Navigation response with new directory listing
    """
    try:
        new_path = file_manager.navigate_to_directory(request.path)
        directory_listing = file_manager.list_directory()
        
        return NavigationResponse(
            current_path=new_path,
            parent_path=file_manager.get_parent_directory(),
            directory_listing=DirectoryListing(**directory_listing)
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Directory not found: {request.path}")
    except NotADirectoryError:
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")
    except Exception as e:
        logger.error(f"Error navigating to directory {request.path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parent", response_model=NavigationResponse)
async def get_parent_directory():
    """
    Get parent directory listing
    
    Returns:
        Parent directory listing
    """
    try:
        parent_path = file_manager.get_parent_directory()
        directory_listing = file_manager.list_directory(parent_path)
        
        return NavigationResponse(
            current_path=parent_path,
            parent_path=file_manager.get_parent_directory(),
            directory_listing=DirectoryListing(**directory_listing)
        )
    except Exception as e:
        logger.error(f"Error getting parent directory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=SearchResponse)
async def search_files(request: SearchRequest):
    """
    Search for files in a directory
    
    Args:
        request: Search request with query and options
        
    Returns:
        Search results with matching files
    """
    try:
        results = file_manager.search_files(request.query, request.directory)
        
        # Convert to FileInfo models
        file_infos = [FileInfo(**result) for result in results]
        
        return SearchResponse(
            query=request.query,
            results=file_infos,
            total_results=len(file_infos),
            search_directory=request.directory or file_manager.current_directory
        )
    except Exception as e:
        logger.error(f"Error searching files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/drives", response_model=DriveInfo)
async def get_drive_letters():
    """
    Get available drive letters (Windows only)
    
    Returns:
        List of available drives
    """
    try:
        drives = file_manager.get_drive_letters()
        current_drive = file_manager.current_directory[:2] + "\\" if file_manager.current_directory else ""
        
        return DriveInfo(
            drives=drives,
            current_drive=current_drive
        )
    except Exception as e:
        logger.error(f"Error getting drive letters: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recent", response_model=List[str])
async def get_recent_directories():
    """
    Get list of recently accessed directories
    
    Returns:
        List of recent directory paths
    """
    try:
        return file_manager.get_recent_directories()
    except Exception as e:
        logger.error(f"Error getting recent directories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-directory", response_model=SuccessResponse)
async def create_directory(name: str = Query(..., description="Directory name")):
    """
    Create a new directory in the current location
    
    Args:
        name: Name of the directory to create
        
    Returns:
        Success response
    """
    try:
        new_dir_path = file_manager.create_directory(name)
        return SuccessResponse(
            message=f"Directory created successfully: {new_dir_path}",
            data={"path": new_dir_path}
        )
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Directory already exists: {name}")
    except Exception as e:
        logger.error(f"Error creating directory {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete-file", response_model=SuccessResponse)
async def delete_file(file_path: str = Query(..., description="Path to file to delete")):
    """
    Delete a file
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        Success response
    """
    try:
        file_manager.delete_file(file_path)
        return SuccessResponse(message=f"File deleted successfully: {file_path}")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/copy-file", response_model=SuccessResponse)
async def copy_file(
    source_path: str = Query(..., description="Source file path"),
    destination_path: str = Query(..., description="Destination file path")
):
    """
    Copy a file
    
    Args:
        source_path: Source file path
        destination_path: Destination file path
        
    Returns:
        Success response
    """
    try:
        file_manager.copy_file(source_path, destination_path)
        return SuccessResponse(
            message=f"File copied successfully from {source_path} to {destination_path}"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Source file not found: {source_path}")
    except Exception as e:
        logger.error(f"Error copying file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-path")
async def get_current_path():
    """
    Get current working directory
    
    Returns:
        Current directory path
    """
    try:
        return {"current_path": file_manager.current_directory}
    except Exception as e:
        logger.error(f"Error getting current path: {e}")
        raise HTTPException(status_code=500, detail=str(e))
