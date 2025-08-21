"""
Background thumbnail worker for generating thumbnails without blocking the UI
"""

import threading
import queue
import time
import logging
from typing import Dict, Optional, Callable
from pathlib import Path
import os
import hashlib

from .exr_processor import EXRProcessor
from utils.image_converter import ImageConverter

logger = logging.getLogger(__name__)

class ThumbnailWorker:
    """Background worker for generating thumbnails"""
    
    def __init__(self, max_workers: int = 2, cache_dir: str = None):
        self.max_workers = max_workers
        self.workers = []
        self.task_queue = queue.Queue()
        self.result_cache = {}  # In-memory cache for current session
        self.callbacks = {}
        self.running = False
        self.exr_processor = EXRProcessor()
        self.image_converter = ImageConverter()
        
        # Set up persistent disk cache
        if cache_dir is None:
            # Default to a .thumbnails folder in the user's home directory
            cache_dir = os.path.expanduser("~/.exr_suite/thumbnails")
        
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def start(self):
        """Start the background workers"""
        if self.running:
            return
            
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
        logger.info(f"Started {self.max_workers} thumbnail workers")
    
    def stop(self):
        """Stop the background workers"""
        self.running = False
        # Add None to queue to signal workers to stop
        for _ in self.workers:
            self.task_queue.put(None)
        
        for worker in self.workers:
            worker.join(timeout=1.0)
        
        self.workers.clear()
        logger.info("Stopped thumbnail workers")
    
    def _worker_loop(self):
        """Main worker loop"""
        logger.info(f"Worker thread {threading.current_thread().name} started")
        processed_count = 0
        
        while self.running:
            try:
                # Use a shorter timeout to be more responsive
                task = self.task_queue.get(timeout=0.1)
                if task is None:  # Stop signal
                    logger.info(f"Worker thread {threading.current_thread().name} received stop signal")
                    break
                    
                file_path, size, callback = task
                logger.debug(f"Worker processing: {file_path}")
                
                try:
                    self._process_thumbnail(file_path, size, callback)
                    processed_count += 1
                    
                    # Clean up cache every 10 processed thumbnails
                    if processed_count % 10 == 0:
                        self.limit_cache_size(max_size=30)
                        # Force garbage collection
                        import gc
                        gc.collect()
                    
                    # Clean up disk cache every 50 processed thumbnails
                    if processed_count % 50 == 0:
                        self.cleanup_disk_cache(max_age_hours=12)
                        
                except Exception as e:
                    logger.error(f"Error processing thumbnail {file_path}: {e}")
                    # Still call callback with None to signal error
                    if callback:
                        try:
                            callback(None)
                        except Exception as callback_error:
                            logger.error(f"Error in callback: {callback_error}")
                finally:
                    # Always mark task as done, even if it failed
                    self.task_queue.task_done()
                    
            except queue.Empty:
                # Continue loop when timeout occurs
                continue
            except Exception as e:
                logger.error(f"Unexpected error in worker loop: {e}")
                # Don't break the loop on unexpected errors
                continue
        
        logger.info(f"Worker thread {threading.current_thread().name} stopped")
    
    def _get_cache_path(self, file_path: str, size: int) -> Path:
        """Generate cache file path for a thumbnail"""
        # Create a hash of the file path to avoid filesystem issues
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.cache_dir / f"{file_hash}_{size}.png"
    
    def _is_cache_valid(self, file_path: str, cache_path: Path) -> bool:
        """Check if cached thumbnail is still valid (file hasn't changed)"""
        if not cache_path.exists():
            return False
        
        # Check if the source file is newer than the cache
        source_mtime = os.path.getmtime(file_path)
        cache_mtime = os.path.getmtime(cache_path)
        
        return cache_mtime > source_mtime
    
    def _load_from_disk_cache(self, file_path: str, size: int) -> Optional[bytes]:
        """Load thumbnail from disk cache if valid"""
        cache_path = self._get_cache_path(file_path, size)
        
        if self._is_cache_valid(file_path, cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Failed to load cached thumbnail {cache_path}: {e}")
        
        return None
    
    def _save_to_disk_cache(self, file_path: str, size: int, thumbnail_bytes: bytes):
        """Save thumbnail to disk cache"""
        cache_path = self._get_cache_path(file_path, size)
        
        try:
            with open(cache_path, 'wb') as f:
                f.write(thumbnail_bytes)
            logger.debug(f"Saved thumbnail to disk cache: {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save thumbnail to disk cache {cache_path}: {e}")

    def _process_thumbnail(self, file_path: str, size: int, callback: Optional[Callable]):
        """Process a single thumbnail task"""
        try:
            # Check if already cached in memory
            cache_key = f"{file_path}_{size}"
            if cache_key in self.result_cache:
                logger.debug(f"Thumbnail already in memory cache: {file_path}")
                if callback:
                    callback(self.result_cache[cache_key])
                return
            
            # Check disk cache first
            cached_bytes = self._load_from_disk_cache(file_path, size)
            if cached_bytes:
                logger.debug(f"Thumbnail loaded from disk cache: {file_path}")
                # Load into memory cache and return
                self.result_cache[cache_key] = cached_bytes
                if callback:
                    callback(cached_bytes)
                return
            
            # Generate thumbnail
            logger.info(f"Generating thumbnail for: {file_path}")
            
            try:
                # Read EXR file and create thumbnail
                image_data, _ = self.exr_processor.read_exr_file(file_path)
                
                # Convert to PIL image
                pil_image = self.image_converter.exr_to_pil(image_data, 'RGB')
                
                # Resize for thumbnail
                pil_image.thumbnail((size, size), resample=3)  # 3 = LANCZOS
                
                # Convert to bytes
                import io
                img_buffer = io.BytesIO()
                pil_image.save(img_buffer, format='PNG', optimize=True)
                img_bytes = img_buffer.getvalue()
                
                # Cache in memory and on disk
                self.result_cache[cache_key] = img_bytes
                self._save_to_disk_cache(file_path, size, img_bytes)
                
                # Limit cache size to prevent memory leaks
                self.limit_cache_size(max_size=50)
                
                logger.info(f"Thumbnail generated successfully: {file_path}")
                
                # Clean up PIL image and buffer
                pil_image.close()
                img_buffer.close()
                
                # Call callback if provided
                if callback:
                    callback(img_bytes)
                    
            except Exception as e:
                logger.error(f"Error in thumbnail generation: {e}")
                # Clean up any partial data
                if 'image_data' in locals():
                    del image_data
                if 'pil_image' in locals():
                    pil_image.close()
                if 'img_buffer' in locals():
                    img_buffer.close()
                raise
                
        except Exception as e:
            logger.error(f"Error generating thumbnail for {file_path}: {e}")
            if callback:
                callback(None)  # Signal error
    
    def request_thumbnail(self, file_path: str, size: int = 200, callback: Optional[Callable] = None):
        """Request a thumbnail to be generated in the background"""
        if not self.running:
            self.start()
        
        # Check cache first
        cache_key = f"{file_path}_{size}"
        if cache_key in self.result_cache:
            if callback:
                callback(self.result_cache[cache_key])
            return
        
        # Add to queue
        self.task_queue.put((file_path, size, callback))
    
    def get_cached_thumbnail(self, file_path: str, size: int = 200) -> Optional[bytes]:
        """Get cached thumbnail if available (from memory or disk)"""
        cache_key = f"{file_path}_{size}"
        
        # Check memory cache first
        if cache_key in self.result_cache:
            return self.result_cache[cache_key]
        
        # Check disk cache
        cached_bytes = self._load_from_disk_cache(file_path, size)
        if cached_bytes:
            # Load into memory cache for faster future access
            self.result_cache[cache_key] = cached_bytes
            return cached_bytes
        
        return None
    
    def clear_cache(self):
        """Clear the thumbnail cache"""
        self.result_cache.clear()
        logger.info("Thumbnail cache cleared")
    
    def limit_cache_size(self, max_size: int = 100):
        """Limit the memory cache size to prevent memory leaks"""
        if len(self.result_cache) > max_size:
            # Remove oldest entries (simple FIFO approach)
            keys_to_remove = list(self.result_cache.keys())[:len(self.result_cache) - max_size]
            for key in keys_to_remove:
                del self.result_cache[key]
            logger.info(f"Limited cache size: removed {len(keys_to_remove)} old entries")
    
    def cleanup_disk_cache(self, max_age_hours: int = 24):
        """Clean up old disk cache files to save disk space"""
        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            cache_files = list(self.cache_dir.glob("*.png"))
            removed_count = 0
            
            for cache_file in cache_files:
                try:
                    file_age = current_time - cache_file.stat().st_mtime
                    if file_age > max_age_seconds:
                        cache_file.unlink()
                        removed_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove old cache file {cache_file}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old disk cache files")
                
        except Exception as e:
            logger.warning(f"Error cleaning up disk cache: {e}")
    
    def get_cache_info(self) -> Dict:
        """Get cache information"""
        return {
            'cached_thumbnails': len(self.result_cache),
            'cache_keys': list(self.result_cache.keys()),
            'queue_size': self.task_queue.qsize(),
            'workers': len(self.workers)
        }

# Global thumbnail worker instance
thumbnail_worker = ThumbnailWorker()
