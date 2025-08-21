"""
Image conversion utilities for converting EXR data to displayable formats
"""

import numpy as np
from PIL import Image
import io
import base64
from typing import Dict, Tuple, Optional, Union, Any
import logging

logger = logging.getLogger(__name__)

class ImageConverter:
    """Converts EXR image data to various display formats"""
    
    def __init__(self):
        self.supported_output_formats = {'PNG', 'JPEG', 'TIFF'}
        self.default_quality = 95
    
    def exr_to_pil(self, image_data: Dict[str, np.ndarray], 
                output_format: str = 'RGB') -> Image.Image:
        """
        Convert EXR image data to PIL Image
        
        Args:
            image_data: Dictionary of channel data
            output_format: Output format ('RGB', 'RGBA', 'L' for grayscale)
            
        Returns:
            PIL Image object
        """
        try:
            if not image_data:
                raise ValueError("No image data provided")
            
            # Get image dimensions
            first_channel = next(iter(image_data.values()))
            height, width = first_channel.shape
            
            logger.debug(f"Converting EXR to PIL: {output_format}, {width}x{height}, channels: {list(image_data.keys())}")
            
            if output_format == 'RGB':
                # Create RGB image
                if 'R' in image_data and 'G' in image_data and 'B' in image_data:
                    # Standard RGB
                    logger.debug("Using standard RGB channels")
                    r_channel = self._normalize_channel(image_data['R'])
                    g_channel = self._normalize_channel(image_data['G'])
                    b_channel = self._normalize_channel(image_data['B'])
                    
                    # Stack channels
                    rgb_array = np.stack([r_channel, g_channel, b_channel], axis=-1)
                    
                elif len(image_data) == 1:
                    # Single channel, convert to grayscale then RGB
                    logger.debug("Converting single channel to RGB")
                    single_channel = self._normalize_channel(next(iter(image_data.values())))
                    rgb_array = np.stack([single_channel] * 3, axis=-1)
                    
                else:
                    # Multiple channels, use first three
                    logger.debug(f"Using first three channels: {list(image_data.keys())[:3]}")
                    channels = list(image_data.values())[:3]
                    normalized_channels = [self._normalize_channel(ch) for ch in channels]
                    
                    # Pad with zeros if less than 3 channels
                    while len(normalized_channels) < 3:
                        normalized_channels.append(np.zeros_like(normalized_channels[0]))
                    
                    rgb_array = np.stack(normalized_channels, axis=-1)
                
                # Convert to uint8
                rgb_array = (rgb_array * 255).astype(np.uint8)
                
                logger.debug(f"RGB array shape: {rgb_array.shape}, dtype: {rgb_array.dtype}")
                return Image.fromarray(rgb_array, 'RGB')
                
            elif output_format == 'RGBA':
                # Create RGBA image
                if 'R' in image_data and 'G' in image_data and 'B' in image_data:
                    r_channel = self._normalize_channel(image_data['R'])
                    g_channel = self._normalize_channel(image_data['G'])
                    b_channel = self._normalize_channel(image_data['B'])
                    
                    # Create alpha channel (use luminance or constant)
                    if 'A' in image_data:
                        a_channel = self._normalize_channel(image_data['A'])
                    else:
                        # Create alpha from luminance
                        a_channel = 0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel
                    
                    rgba_array = np.stack([r_channel, g_channel, b_channel, a_channel], axis=-1)
                    rgba_array = (rgba_array * 255).astype(np.uint8)
                    
                    return Image.fromarray(rgba_array, 'RGBA')
                    
                else:
                    # Fallback to RGB
                    return self.exr_to_pil(image_data, 'RGB')
                    
            elif output_format == 'L':
                # Create grayscale image
                if 'R' in image_data and 'G' in image_data and 'B' in image_data:
                    # Convert RGB to grayscale using luminance
                    r_channel = self._normalize_channel(image_data['R'])
                    g_channel = self._normalize_channel(image_data['G'])
                    b_channel = self._normalize_channel(image_data['B'])
                    
                    gray_channel = 0.299 * r_channel + 0.587 * g_channel + 0.114 * b_channel
                    
                elif len(image_data) == 1:
                    # Single channel
                    gray_channel = self._normalize_channel(next(iter(image_data.values())))
                    
                else:
                    # Use first channel
                    gray_channel = self._normalize_channel(next(iter(image_data.values())))
                
                gray_array = (gray_channel * 255).astype(np.uint8)
                return Image.fromarray(gray_array, 'L')
                
            else:
                raise ValueError(f"Unsupported output format: {output_format}")
                    
        except Exception as e:
            logger.error(f"Error converting EXR to PIL: {e}")
            logger.error(f"Image data keys: {list(image_data.keys()) if image_data else 'None'}")
            if image_data:
                for key, value in image_data.items():
                    logger.error(f"Channel {key}: shape={value.shape}, dtype={value.dtype}, min={value.min()}, max={value.max()}")
            raise
    
    def exr_to_base64(self, image_data: Dict[str, np.ndarray], 
                      output_format: str = 'PNG', 
                      quality: int = None) -> str:
        """
        Convert EXR image data to base64 string
        
        Args:
            image_data: Dictionary of channel data
            output_format: Output format ('PNG', 'JPEG')
            quality: JPEG quality (1-100, only for JPEG)
            
        Returns:
            Base64 encoded string
        """
        try:
            # Convert to PIL Image
            pil_image = self.exr_to_pil(image_data, 'RGB')
            
            # Convert to base64
            buffer = io.BytesIO()
            
            if output_format.upper() == 'JPEG':
                if quality is None:
                    quality = self.default_quality
                pil_image.save(buffer, format='JPEG', quality=quality)
            else:
                pil_image.save(buffer, format='PNG')
            
            buffer.seek(0)
            image_bytes = buffer.getvalue()
            
            # Encode to base64
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            
            # Add data URL prefix
            mime_type = 'image/jpeg' if output_format.upper() == 'JPEG' else 'image/png'
            data_url = f"data:{mime_type};base64,{base64_string}"
            
            return data_url
            
        except Exception as e:
            logger.error(f"Error converting EXR to base64: {e}")
            raise
    
    def exr_to_bytes(self, image_data: Dict[str, np.ndarray], 
                     output_format: str = 'PNG', 
                     quality: int = None) -> bytes:
        """
        Convert EXR image data to bytes
        
        Args:
            image_data: Dictionary of channel data
            output_format: Output format ('PNG', 'JPEG')
            quality: JPEG quality (1-100, only for JPEG)
            
        Returns:
            Image bytes
        """
        try:
            # Convert to PIL Image
            pil_image = self.exr_to_pil(image_data, 'RGB')
            
            # Convert to bytes
            buffer = io.BytesIO()
            
            if output_format.upper() == 'JPEG':
                if quality is None:
                    quality = self.default_quality
                pil_image.save(buffer, format='JPEG', quality=quality)
            else:
                pil_image.save(buffer, format='PNG')
            
            buffer.seek(0)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error converting EXR to bytes: {e}")
            raise
    
    def create_thumbnail(self, image_data: Dict[str, np.ndarray], 
                        size: Tuple[int, int] = (200, 200),
                        output_format: str = 'PNG') -> bytes:
        """
        Create a thumbnail from EXR image data
        
        Args:
            image_data: Dictionary of channel data
            size: Thumbnail size (width, height)
            output_format: Output format
            
        Returns:
            Thumbnail bytes
        """
        try:
            # Convert to PIL Image
            pil_image = self.exr_to_pil(image_data, 'RGB')
            
            # Resize image
            pil_image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convert to bytes
            buffer = io.BytesIO()
            pil_image.save(buffer, format=output_format)
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            raise
    
    def _normalize_channel(self, channel_data: np.ndarray) -> np.ndarray:
        """
        Normalize channel data to 0-1 range
        
        Args:
            channel_data: Input channel data
            
        Returns:
            Normalized channel data
        """
        try:
            min_val = np.min(channel_data)
            max_val = np.max(channel_data)
            
            if max_val > min_val:
                normalized = (channel_data - min_val) / (max_val - min_val)
            else:
                normalized = channel_data - min_val
            
            # Clip to 0-1 range
            return np.clip(normalized, 0.0, 1.0)
            
        except Exception as e:
            logger.error(f"Error normalizing channel: {e}")
            raise
    
    def apply_tone_mapping(self, image_data: Dict[str, np.ndarray], 
                          method: str = 'reinhard') -> Dict[str, np.ndarray]:
        """
        Apply tone mapping to HDR image data
        
        Args:
            image_data: Dictionary of channel data
            method: Tone mapping method ('reinhard', 'gamma', 'linear')
            
        Returns:
            Tone mapped image data
        """
        try:
            if method == 'reinhard':
                return self._reinhard_tone_mapping(image_data)
            elif method == 'gamma':
                return self._gamma_tone_mapping(image_data, gamma=2.2)
            elif method == 'linear':
                return self._linear_tone_mapping(image_data)
            else:
                raise ValueError(f"Unsupported tone mapping method: {method}")
                
        except Exception as e:
            logger.error(f"Error applying tone mapping: {e}")
            raise
    
    def _reinhard_tone_mapping(self, image_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Apply Reinhard tone mapping"""
        try:
            mapped_data = {}
            
            for channel_name, channel_data in image_data.items():
                # Reinhard tone mapping formula
                mapped = channel_data / (1 + channel_data)
                mapped_data[channel_name] = mapped
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"Error in Reinhard tone mapping: {e}")
            raise
    
    def _gamma_tone_mapping(self, image_data: Dict[str, np.ndarray], 
                           gamma: float = 2.2) -> Dict[str, np.ndarray]:
        """Apply gamma correction"""
        try:
            mapped_data = {}
            
            for channel_name, channel_data in image_data.items():
                # Apply gamma correction
                mapped = np.power(channel_data, 1.0 / gamma)
                mapped_data[channel_name] = mapped
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"Error in gamma tone mapping: {e}")
            raise
    
    def _linear_tone_mapping(self, image_data: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """Apply linear tone mapping (simple normalization)"""
        try:
            mapped_data = {}
            
            for channel_name, channel_data in image_data.items():
                # Linear normalization
                min_val = np.min(channel_data)
                max_val = np.max(channel_data)
                
                if max_val > min_val:
                    mapped = (channel_data - min_val) / (max_val - min_val)
                else:
                    mapped = channel_data - min_val
                
                mapped_data[channel_name] = mapped
            
            return mapped_data
            
        except Exception as e:
            logger.error(f"Error in linear tone mapping: {e}")
            raise
    
    def get_image_stats(self, image_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
        """
        Get statistical information about the image data
        
        Args:
            image_data: Dictionary of channel data
            
        Returns:
            Dictionary containing image statistics
        """
        try:
            stats = {}
            
            for channel_name, channel_data in image_data.items():
                channel_stats = {
                    'min': float(np.min(channel_data)),
                    'max': float(np.max(channel_data)),
                    'mean': float(np.mean(channel_data)),
                    'std': float(np.std(channel_data)),
                    'shape': channel_data.shape,
                    'dtype': str(channel_data.dtype)
                }
                stats[channel_name] = channel_stats
            
            # Overall stats
            all_values = np.concatenate([ch.flatten() for ch in image_data.values()])
            stats['overall'] = {
                'min': float(np.min(all_values)),
                'max': float(np.max(all_values)),
                'mean': float(np.mean(all_values)),
                'std': float(np.std(all_values)),
                'total_pixels': int(len(all_values))
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting image stats: {e}")
            raise
