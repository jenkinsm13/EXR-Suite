"""
File utilities for directory operations and file management
"""

import os
import os.path
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class FileManager:
    """Manages file operations and directory navigation"""
    
    def __init__(self):
        self.supported_extensions = {'.exr'}
        self.current_directory = os.getcwd()
    
    def list_directory(self, path: str = "") -> Dict[str, Any]:
        """
        List contents of a directory
        
        Args:
            path: Directory path (relative or absolute)
            
        Returns:
            Dictionary containing directory information
        """
        try:
            # Resolve path
            if not path:
                target_path = self.current_directory
            elif os.path.isabs(path):
                target_path = path
            else:
                target_path = os.path.join(self.current_directory, path)
            
            # Ensure path exists and is a directory
            if not os.path.exists(target_path):
                raise FileNotFoundError(f"Directory not found: {target_path}")
            
            if not os.path.isdir(target_path):
                raise NotADirectoryError(f"Path is not a directory: {target_path}")
            
            # Get directory contents
            items = []
            directories = []
            files = []
            
            try:
                with os.scandir(target_path) as entries:
                    for entry in entries:
                        # Skip hidden files and folders (starting with . or _)
                        if entry.name.startswith('.') or entry.name.startswith('_'):
                            continue
                            
                        try:
                            item_info = {
                                'name': entry.name,
                                'path': entry.path,
                                'is_dir': entry.is_dir(),
                                'is_file': entry.is_file(),
                                'size': 0,
                                'modified': None
                            }
                            
                            if entry.is_file():
                                # Get file size
                                try:
                                    stat = entry.stat()
                                    item_info['size'] = stat.st_size
                                    item_info['modified'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                                    
                                    # Check if it's an EXR file
                                    if Path(entry.name).suffix.lower() in self.supported_extensions:
                                        item_info['is_exr'] = True
                                        files.append(item_info)
                                    else:
                                        item_info['is_exr'] = False
                                        files.append(item_info)
                                        
                                except OSError as e:
                                    logger.warning(f"Could not get file info for {entry.path}: {e}")
                                    item_info['is_exr'] = False
                                    files.append(item_info)
                            
                            elif entry.is_dir():
                                directories.append(item_info)
                                
                        except OSError as e:
                            logger.warning(f"Could not access {entry.path}: {e}")
                            continue
                            
            except PermissionError as e:
                logger.error(f"Permission denied accessing directory {target_path}: {e}")
                raise
            
            # Sort items
            directories.sort(key=lambda x: x['name'].lower())
            files.sort(key=lambda x: x['name'].lower())
            
            # Combine all items
            items = directories + files
            
            return {
                'current_path': target_path,
                'parent_path': str(Path(target_path).parent),
                'items': items,
                'directory_count': len(directories),
                'file_count': len(files),
                'exr_count': len([f for f in files if f.get('is_exr', False)]),
                'total_size': sum(f.get('size', 0) for f in files)
            }
            
        except Exception as e:
            logger.error(f"Error listing directory {path}: {e}")
            raise
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed information about a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Path is not a file: {file_path}")
            
            # Get file statistics
            stat = os.stat(file_path)
            file_info = {
                'name': os.path.basename(file_path),
                'path': file_path,
                'size': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'is_exr': Path(file_path).suffix.lower() in self.supported_extensions,
                'extension': Path(file_path).suffix.lower(),
                'directory': os.path.dirname(file_path)
            }
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise
    
    def navigate_to_directory(self, path: str) -> str:
        """
        Navigate to a directory and return its contents
        
        Args:
            path: Directory path to navigate to
            
        Returns:
            Absolute path of the new directory
        """
        try:
            # Resolve path
            if os.path.isabs(path):
                target_path = path
            else:
                target_path = os.path.join(self.current_directory, path)
            
            # Ensure path exists and is a directory
            if not os.path.exists(target_path):
                raise FileNotFoundError(f"Directory not found: {target_path}")
            
            if not os.path.isdir(target_path):
                raise NotADirectoryError(f"Path is not a directory: {target_path}")
            
            # Update current directory
            self.current_directory = os.path.abspath(target_path)
            
            return self.current_directory
            
        except Exception as e:
            logger.error(f"Error navigating to directory {path}: {e}")
            raise
    
    def get_parent_directory(self) -> str:
        """Get the parent directory of the current directory"""
        try:
            parent = os.path.dirname(self.current_directory)
            if parent == self.current_directory:
                # We're at the root
                return self.current_directory
            return parent
        except Exception as e:
            logger.error(f"Error getting parent directory: {e}")
            return self.current_directory
    
    def search_files(self, query: str, directory: str = None) -> List[Dict[str, Any]]:
        """
        Search for files in a directory
        
        Args:
            query: Search query (filename pattern)
            directory: Directory to search in (defaults to current)
            
        Returns:
            List of matching files
        """
        try:
            search_dir = directory if directory else self.current_directory
            
            if not os.path.exists(search_dir):
                raise FileNotFoundError(f"Directory not found: {search_dir}")
            
            if not os.path.isdir(search_dir):
                raise NotADirectoryError(f"Path is not a directory: {search_dir}")
            
            matching_files = []
            
            for root, dirs, files in os.walk(search_dir):
                for file in files:
                    if query.lower() in file.lower():
                        file_path = os.path.join(root, file)
                        try:
                            file_info = self.get_file_info(file_path)
                            matching_files.append(file_info)
                        except Exception as e:
                            logger.warning(f"Could not get info for {file_path}: {e}")
                            continue
            
            return matching_files
            
        except Exception as e:
            logger.error(f"Error searching files: {e}")
            raise
    
    def create_directory(self, name: str, parent_directory: str = None) -> str:
        """
        Create a new directory
        
        Args:
            name: Name of the directory to create
            parent_directory: Parent directory (defaults to current)
            
        Returns:
            Path of the created directory
        """
        try:
            parent = parent_directory if parent_directory else self.current_directory
            new_dir_path = os.path.join(parent, name)
            
            if os.path.exists(new_dir_path):
                raise FileExistsError(f"Directory already exists: {new_dir_path}")
            
            os.makedirs(new_dir_path, exist_ok=False)
            logger.info(f"Created directory: {new_dir_path}")
            
            return new_dir_path
            
        except Exception as e:
            logger.error(f"Error creating directory {name}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file
        
        Args:
            file_path: Path to the file to delete
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"Path is not a file: {file_path}")
            
            os.remove(file_path)
            logger.info(f"Deleted file: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise
    
    def copy_file(self, source_path: str, destination_path: str) -> bool:
        """
        Copy a file
        
        Args:
            source_path: Source file path
            destination_path: Destination file path
            
        Returns:
            True if successful
        """
        try:
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            if not os.path.isfile(source_path):
                raise FileNotFoundError(f"Source path is not a file: {source_path}")
            
            # Ensure destination directory exists
            dest_dir = os.path.dirname(destination_path)
            if dest_dir and not os.path.exists(dest_dir):
                os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file
            import shutil
            shutil.copy2(source_path, destination_path)
            logger.info(f"Copied file from {source_path} to {destination_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error copying file: {e}")
            raise
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def get_drive_letters(self) -> List[str]:
        """Get available drive letters on Windows"""
        try:
            drives = []
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
            return drives
        except Exception as e:
            logger.error(f"Error getting drive letters: {e}")
            return []
    
    def get_recent_directories(self) -> List[str]:
        """Get list of recently accessed directories"""
        # This could be enhanced with persistent storage
        return [self.current_directory]
