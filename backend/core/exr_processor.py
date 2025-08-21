"""
Core EXR processing module using OpenEXR library
Handles file reading, writing, metadata extraction, and image processing
"""

import OpenEXR
import numpy as np
from typing import Dict, Tuple, Optional, Any
import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EXRProcessor:
    """Main class for EXR file processing operations"""
    
    def __init__(self):
        self.supported_extensions = {'.exr'}
        self.cache = {}  # Simple in-memory cache for processed images
    
    def is_exr_file(self, file_path: str) -> bool:
        """Check if file is a valid EXR file"""
        try:
            return OpenEXR.isOpenExrFile(file_path)
        except Exception as e:
            logger.error(f"Error checking EXR file: {e}")
            return False
    
    def read_exr_file(self, file_path: str) -> Tuple[Dict[str, np.ndarray], Dict[str, Any]]:
        """
        Read EXR file and return image data and metadata
        
        Args:
            file_path: Path to the EXR file
            
        Returns:
            Tuple of (image_data, metadata)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.is_exr_file(file_path):
            raise ValueError(f"File is not a valid EXR file: {file_path}")
        
        try:
            exr_file = OpenEXR.InputFile(file_path)
            header = exr_file.header()
            
            # Extract comprehensive metadata
            metadata = self._extract_metadata(header)
            
            # Read image data
            image_data = self._read_image_data(exr_file, header)
            
            exr_file.close()
            
            # Cache the result
            self.cache[file_path] = {
                'image_data': image_data,
                'metadata': metadata,
                'header': header
            }
            
            return image_data, metadata
            
        except Exception as e:
            logger.error(f"Error reading EXR file {file_path}: {e}")
            raise
    
    def _extract_metadata(self, header) -> Dict[str, Any]:
        """Extract all available metadata from EXR header"""
        metadata = {}
        
        # Basic header information
        metadata['channels'] = list(header['channels'].keys())
        metadata['dataWindow'] = str(header['dataWindow'])
        metadata['displayWindow'] = str(header['displayWindow'])
        
        # Standard metadata fields
        standard_fields = [
            'pixelAspectRatio', 'screenWindowCenter', 'screenWindowWidth',
            'lineOrder', 'compression', 'chunkCount', 'tiles', 'envmap',
            'adoptedNeutral', 'renderingTransform', 'lookModTransform',
            'whiteLuminance', 'chromaticities', 'whitePoint', 'primaries',
            'acesImageContainerFlag', 'multiView', 'worldToCamera',
            'worldToNDC', 'deepImageState', 'tiledesc', 'name', 'type',
            'version', 'maxSamplesPerPixel', 'dwaCompressionLevel',
            'idManifest', 'tileDescription', 'multiPart', 'view', 'owner',
            'comments', 'capDate', 'utcOffset', 'longitude', 'latitude',
            'altitude', 'focus', 'expTime', 'aperture', 'isoSpeed',
            'keyCode', 'timeCode', 'wrapmodes', 'framesPerSecond'
        ]
        
        for field in standard_fields:
            try:
                if field in header:
                    metadata[field] = str(header[field])
            except Exception as e:
                logger.debug(f"Could not extract field {field}: {e}")
        
        # Extract channel information
        metadata['channel_info'] = {}
        for channel_name, channel in header['channels'].items():
            try:
                metadata['channel_info'][channel_name] = {
                    'type': str(type(channel.type)),
                    'xSampling': getattr(channel, 'xSampling', 1),
                    'ySampling': getattr(channel, 'ySampling', 1)
                }
            except Exception as e:
                logger.debug(f"Could not extract channel info for {channel_name}: {e}")
        
        return metadata
    
    def _read_image_data(self, exr_file, header) -> Dict[str, np.ndarray]:
        """Read image data from EXR file"""
        channels = list(header['channels'].keys())
        data_window = header['dataWindow']
        
        # Calculate dimensions
        width = data_window.max.x - data_window.min.x + 1
        height = data_window.max.y - data_window.min.y + 1
        
        # Read all channels
        image_data = {}
        for channel in channels:
            try:
                channel_data = exr_file.channel(channel)
                # Convert to numpy array with proper dtype
                channel_type = header['channels'][channel].type
                
                # Fix: Use the .v attribute to get the actual value for comparison
                if hasattr(channel_type, 'v'):
                    pixel_type_value = channel_type.v
                else:
                    # Fallback: convert to string and compare
                    pixel_type_value = str(channel_type)
                
                if pixel_type_value == OpenEXR.FLOAT:
                    dtype = np.float32
                elif pixel_type_value == OpenEXR.HALF:
                    dtype = np.float16
                elif pixel_type_value == OpenEXR.UINT:
                    dtype = np.uint32
                else:
                    dtype = np.float32  # Default to float32
                
                image_data[channel] = np.frombuffer(channel_data, dtype=dtype).reshape(height, width)
                
            except Exception as e:
                logger.error(f"Error reading channel {channel}: {e}")
                raise
        
        return image_data
    
    def write_exr_file(self, file_path: str, image_data: Dict[str, np.ndarray], 
                       metadata: Dict[str, Any], original_header=None) -> None:
        """
        Write image data to EXR file with metadata preservation
        
        Args:
            file_path: Output file path
            image_data: Dictionary of channel data
            metadata: Metadata to include
            original_header: Original header to preserve (optional)
        """
        try:
            if original_header:
                header = original_header.copy()
            else:
                # Create new header
                height, width = next(iter(image_data.values())).shape
                header = OpenEXR.Header(width, height)
                
                # Set channels
                header['channels'] = {}
                for channel_name in image_data.keys():
                    header['channels'][channel_name] = OpenEXR.Channel(OpenEXR.FLOAT)
            
            # Create output file
            exr_file = OpenEXR.OutputFile(file_path, header)
            
            # Prepare data for writing
            data_to_write = {}
            for channel_name, channel_data in image_data.items():
                # Ensure data is float32 for writing
                if channel_data.dtype != np.float32:
                    channel_data = channel_data.astype(np.float32)
                data_to_write[channel_name] = channel_data.tobytes()
            
            # Write pixels
            exr_file.writePixels(data_to_write)
            exr_file.close()
            
            logger.info(f"Successfully wrote EXR file: {file_path}")
            
        except Exception as e:
            logger.error(f"Error writing EXR file {file_path}: {e}")
            raise
    
    def get_thumbnail(self, file_path: str, size: int = 200) -> np.ndarray:
        """Generate thumbnail for display - full image, memory efficient"""
        try:
            # Read the full EXR file but process it efficiently
            image_data, _ = self.read_exr_file(file_path)
            
            # Use first RGB channel or first available channel
            if 'R' in image_data and 'G' in image_data and 'B' in image_data:
                # RGB image - stack efficiently
                thumbnail = np.stack([
                    image_data['R'],
                    image_data['G'], 
                    image_data['B']
                ], axis=-1)
            else:
                # Single channel or other format
                first_channel = next(iter(image_data.values()))
                thumbnail = np.stack([first_channel] * 3, axis=-1)
            
            # Resize thumbnail to target size - this is where memory usage happens
            thumbnail = self._resize_image_efficient(thumbnail, size, size)
            
            # Normalize to 0-1 range for display
            thumbnail = self._normalize_image(thumbnail)
            
            return thumbnail
            
        except Exception as e:
            logger.error(f"Error generating thumbnail for {file_path}: {e}")
            raise

    def _resize_image_efficient(self, image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Memory-efficient image resizing for large images"""
        current_height, current_width = image.shape[:2]
        
        # If the image is already smaller than target, return as is
        if current_height <= target_height and current_width <= target_width:
            return image
        
        # For very large images, use a multi-step downsampling approach
        # This prevents memory issues by processing in smaller chunks
        
        # Calculate the scale factor
        scale_x = target_width / current_width
        scale_y = target_height / current_height
        scale = min(scale_x, scale_y)
        
        # If scaling down significantly, use multi-step approach
        if scale < 0.5:
            # Multi-step downsampling to avoid memory issues
            current_img = image.copy()
            
            while current_img.shape[0] > target_height * 2 or current_img.shape[1] > target_width * 2:
                # Downsample by factor of 2 each step
                new_height = current_img.shape[0] // 2
                new_width = current_img.shape[1] // 2
                
                if len(current_img.shape) == 3:
                    # RGB image - downsample each channel
                    downsampled = np.zeros((new_height, new_width, 3), dtype=current_img.dtype)
                    for c in range(3):
                        downsampled[:, :, c] = self._downsample_channel_2x(current_img[:, :, c])
                else:
                    # Single channel
                    downsampled = self._downsample_channel_2x(current_img)
                
                # Replace current image and free memory
                del current_img
                current_img = downsampled
                
                # Force garbage collection
                import gc
                gc.collect()
            
            # Final resize to exact target size
            result = self._resize_image(current_img, target_width, target_height)
            del current_img
            return result
        else:
            # For smaller scale changes, use regular resize
            return self._resize_image(image, target_width, target_height)

    def _downsample_channel_2x(self, channel: np.ndarray) -> np.ndarray:
        """Downsample a channel by factor of 2 using simple averaging"""
        height, width = channel.shape
        new_height = height // 2
        new_width = width // 2
        
        # Use simple 2x2 block averaging
        downsampled = np.zeros((new_height, new_width), dtype=channel.dtype)
        
        for y in range(new_height):
            for x in range(new_width):
                # Extract 2x2 block
                y1, y2 = y * 2, min((y + 1) * 2, height)
                x1, x2 = x * 2, min((x + 1) * 2, width)
                
                # Calculate average of the block
                block = channel[y1:y2, x1:x2]
                downsampled[y, x] = np.mean(block)
        
        return downsampled
    
    def _resize_image(self, image: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
        """Simple resize using numpy (for thumbnails)"""
        current_height, current_width = image.shape[:2]
        
        # Simple nearest neighbor resize
        y_indices = np.linspace(0, current_height - 1, target_height, dtype=int)
        x_indices = np.linspace(0, current_width - 1, target_width, dtype=int)
        
        if len(image.shape) == 3:
            return image[y_indices][:, x_indices]
        else:
            return image[y_indices][:, x_indices]
    
    def _normalize_image(self, image: np.ndarray) -> np.ndarray:
        """Normalize image to 0-1 range"""
        min_val = image.min()
        max_val = image.max()
        
        if max_val > min_val:
            return (image - min_val) / (max_val - min_val)
        else:
            return image
    
    def apply_adjustments(self, image_data: Dict[str, np.ndarray], 
                         adjustments: Dict[str, float]) -> Dict[str, np.ndarray]:
        """
        Apply image adjustments to the image data
        
        Args:
            image_data: Original image data
            adjustments: Dictionary of adjustment parameters
            
        Returns:
            Adjusted image data
        """
        adjusted_data = {}
        
        # Copy original data
        for channel_name, channel_data in image_data.items():
            adjusted_data[channel_name] = channel_data.copy()
        
        # Apply exposure adjustment
        if 'exposure' in adjustments:
            exposure_value = adjustments['exposure']
            for channel_name, channel_data in adjusted_data.items():
                adjusted_data[channel_name] = np.clip(
                    channel_data * (2 ** exposure_value),
                    0.0,
                    np.finfo(np.float32).max
                )
        
        # Apply contrast adjustment
        if 'contrast' in adjustments:
            contrast_value = adjustments['contrast']
            for channel_name, channel_data in adjusted_data.items():
                # Normalize to 0-1 range first
                min_val = channel_data.min()
                max_val = channel_data.max()
                if max_val > min_val:
                    normalized = (channel_data - min_val) / (max_val - min_val)
                    # Apply contrast using power function
                    adjusted = np.power(normalized, contrast_value)
                    # Scale back to original range
                    adjusted_data[channel_name] = adjusted * (max_val - min_val) + min_val
        
        # Apply color balance
        if 'red_scale' in adjustments or 'green_scale' in adjustments or 'blue_scale' in adjustments:
            scales = {
                'R': adjustments.get('red_scale', 1.0),
                'G': adjustments.get('green_scale', 1.0),
                'B': adjustments.get('blue_scale', 1.0)
            }
            
            for channel_name, channel_data in adjusted_data.items():
                if channel_name in scales:
                    adjusted_data[channel_name] = np.clip(
                        channel_data * scales[channel_name],
                        0.0,
                        np.finfo(np.float32).max
                    )
        
        # Apply brightness adjustment
        if 'brightness' in adjustments:
            brightness_value = adjustments['brightness']
            for channel_name, channel_data in adjusted_data.items():
                adjusted_data[channel_name] = np.clip(
                    channel_data + brightness_value,
                    0.0,
                    np.finfo(np.float32).max
                )
        
        # Apply saturation adjustment
        if 'saturation' in adjustments and len(adjusted_data) >= 3:
            saturation_value = adjustments['saturation']
            if 'R' in adjusted_data and 'G' in adjusted_data and 'B' in adjusted_data:
                # Convert to luminance
                luminance = 0.299 * adjusted_data['R'] + 0.587 * adjusted_data['G'] + 0.114 * adjusted_data['B']
                
                # Apply saturation
                for channel in ['R', 'G', 'B']:
                    adjusted_data[channel] = np.clip(
                        luminance + saturation_value * (adjusted_data[channel] - luminance),
                        0.0,
                        np.finfo(np.float32).max
                    )
        
        return adjusted_data
    
    def clear_cache(self):
        """Clear the image cache"""
        self.cache.clear()
        logger.info("Image cache cleared")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the cache"""
        return {
            'cached_files': len(self.cache),
            'cache_keys': list(self.cache.keys())
        }
