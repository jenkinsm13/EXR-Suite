"""
Metadata router for EXR metadata extraction and display
"""

from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
import logging
import os

from .models import MetadataResponse, SuccessResponse
from core.exr_processor import EXRProcessor

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize EXR processor
exr_processor = EXRProcessor()

@router.get("/{file_path:path}", response_model=MetadataResponse)
async def get_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get comprehensive metadata from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Complete metadata information
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Convert metadata to response model format
        response_data = {
            'file_path': file_path,
            'channels': metadata.get('channels', []),
            'data_window': metadata.get('dataWindow', ''),
            'display_window': metadata.get('displayWindow', ''),
            'channel_info': metadata.get('channel_info', {}),
            'pixel_aspect_ratio': metadata.get('pixelAspectRatio'),
            'screen_window_center': metadata.get('screenWindowCenter'),
            'screen_window_width': metadata.get('screenWindowWidth'),
            'line_order': metadata.get('lineOrder'),
            'compression': metadata.get('compression'),
            'chunk_count': metadata.get('chunkCount'),
            'tiles': metadata.get('tiles'),
            'envmap': metadata.get('envmap'),
            'adopted_neutral': metadata.get('adoptedNeutral'),
            'rendering_transform': metadata.get('renderingTransform'),
            'look_mod_transform': metadata.get('lookModTransform'),
            'white_luminance': metadata.get('whiteLuminance'),
            'chromaticities': metadata.get('chromaticities'),
            'white_point': metadata.get('whitePoint'),
            'primaries': metadata.get('primaries'),
            'aces_image_container_flag': metadata.get('acesImageContainerFlag'),
            'multi_view': metadata.get('multiView'),
            'world_to_camera': metadata.get('worldToCamera'),
            'world_to_ndc': metadata.get('worldToNDC'),
            'deep_image_state': metadata.get('deepImageState'),
            'tiledesc': metadata.get('tiledesc'),
            'name': metadata.get('name'),
            'type': metadata.get('type'),
            'version': metadata.get('version'),
            'max_samples_per_pixel': metadata.get('maxSamplesPerPixel'),
            'dwa_compression_level': metadata.get('dwaCompressionLevel'),
            'id_manifest': metadata.get('idManifest'),
            'tile_description': metadata.get('tileDescription'),
            'multi_part': metadata.get('multiPart'),
            'view': metadata.get('view'),
            'owner': metadata.get('owner'),
            'comments': metadata.get('comments'),
            'cap_date': metadata.get('capDate'),
            'utc_offset': metadata.get('utcOffset'),
            'longitude': metadata.get('longitude'),
            'latitude': metadata.get('latitude'),
            'altitude': metadata.get('altitude'),
            'focus': metadata.get('focus'),
            'exp_time': metadata.get('expTime'),
            'aperture': metadata.get('aperture'),
            'iso_speed': metadata.get('isoSpeed'),
            'key_code': metadata.get('keyCode'),
            'time_code': metadata.get('timeCode'),
            'wrapmodes': metadata.get('wrapmodes'),
            'frames_per_second': metadata.get('framesPerSecond')
        }
        
        return MetadataResponse(**response_data)
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{file_path:path}")
async def get_metadata_summary(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get a summary of key metadata from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Summary of key metadata fields
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Create summary with key fields
        summary = {
            'file_path': file_path,
            'basic_info': {
                'channels': metadata.get('channels', []),
                'data_window': metadata.get('dataWindow', ''),
                'display_window': metadata.get('displayWindow', ''),
                'compression': metadata.get('compression', ''),
                'line_order': metadata.get('lineOrder', '')
            },
            'color_info': {
                'pixel_aspect_ratio': metadata.get('pixelAspectRatio'),
                'screen_window_center': metadata.get('screenWindowCenter'),
                'screen_window_width': metadata.get('screenWindowWidth'),
                'chromaticities': metadata.get('chromaticities'),
                'white_point': metadata.get('whitePoint'),
                'primaries': metadata.get('primaries')
            },
            'technical_info': {
                'chunk_count': metadata.get('chunkCount'),
                'tiles': metadata.get('tiles'),
                'envmap': metadata.get('envmap'),
                'deep_image_state': metadata.get('deepImageState')
            },
            'camera_info': {
                'world_to_camera': metadata.get('worldToCamera'),
                'world_to_ndc': metadata.get('worldToNDC'),
                'focus': metadata.get('focus'),
                'exp_time': metadata.get('expTime'),
                'aperture': metadata.get('aperture'),
                'iso_speed': metadata.get('isoSpeed')
            },
            'metadata_count': len([v for v in metadata.values() if v is not None])
        }
        
        return summary
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting metadata summary from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels/{file_path:path}")
async def get_channel_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get detailed channel information from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Detailed channel information
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Extract channel information
        channels = metadata.get('channels', [])
        channel_info = metadata.get('channel_info', {})
        
        # Build detailed channel data
        detailed_channels = []
        for channel_name in channels:
            channel_data = {
                'name': channel_name,
                'info': channel_info.get(channel_name, {}),
                'type': channel_info.get(channel_name, {}).get('type', 'Unknown'),
                'x_sampling': channel_info.get(channel_name, {}).get('xSampling', 1),
                'y_sampling': channel_info.get(channel_name, {}).get('ySampling', 1)
            }
            detailed_channels.append(channel_data)
        
        return {
            'file_path': file_path,
            'total_channels': len(channels),
            'channels': detailed_channels
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting channel metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technical/{file_path:path}")
async def get_technical_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get technical metadata from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Technical metadata information
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Extract technical metadata
        technical_data = {
            'file_path': file_path,
            'compression': metadata.get('compression'),
            'line_order': metadata.get('lineOrder'),
            'chunk_count': metadata.get('chunkCount'),
            'tiles': metadata.get('tiles'),
            'envmap': metadata.get('envmap'),
            'deep_image_state': metadata.get('deepImageState'),
            'tiledesc': metadata.get('tiledesc'),
            'multi_part': metadata.get('multiPart'),
            'max_samples_per_pixel': metadata.get('maxSamplesPerPixel'),
            'dwa_compression_level': metadata.get('dwaCompressionLevel'),
            'id_manifest': metadata.get('idManifest'),
            'tile_description': metadata.get('tileDescription'),
            'version': metadata.get('version'),
            'type': metadata.get('type')
        }
        
        return technical_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting technical metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/color/{file_path:path}")
async def get_color_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get color-related metadata from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Color metadata information
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Extract color metadata
        color_data = {
            'file_path': file_path,
            'pixel_aspect_ratio': metadata.get('pixelAspectRatio'),
            'screen_window_center': metadata.get('screenWindowCenter'),
            'screen_window_width': metadata.get('screenWindowWidth'),
            'chromaticities': metadata.get('chromaticities'),
            'white_point': metadata.get('whitePoint'),
            'primaries': metadata.get('primaries'),
            'white_luminance': metadata.get('whiteLuminance'),
            'aces_image_container_flag': metadata.get('acesImageContainerFlag'),
            'adopted_neutral': metadata.get('adoptedNeutral'),
            'rendering_transform': metadata.get('renderingTransform'),
            'look_mod_transform': metadata.get('lookModTransform')
        }
        
        return color_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting color metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/camera/{file_path:path}")
async def get_camera_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get camera-related metadata from an EXR file
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Camera metadata information
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        # Extract camera metadata
        camera_data = {
            'file_path': file_path,
            'world_to_camera': metadata.get('worldToCamera'),
            'world_to_ndc': metadata.get('worldToNDC'),
            'focus': metadata.get('focus'),
            'exp_time': metadata.get('expTime'),
            'aperture': metadata.get('aperture'),
            'iso_speed': metadata.get('isoSpeed'),
            'key_code': metadata.get('keyCode'),
            'time_code': metadata.get('timeCode'),
            'longitude': metadata.get('longitude'),
            'latitude': metadata.get('latitude'),
            'altitude': metadata.get('altitude'),
            'cap_date': metadata.get('capDate'),
            'utc_offset': metadata.get('utcOffset')
        }
        
        return camera_data
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting camera metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/raw/{file_path:path}")
async def get_raw_metadata(file_path: str = Path(..., description="Path to the EXR file")):
    """
    Get raw metadata from an EXR file (all available fields)
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Raw metadata dictionary
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and extract metadata
        _, metadata = exr_processor.read_exr_file(file_path)
        
        return {
            'file_path': file_path,
            'raw_metadata': metadata,
            'metadata_count': len(metadata),
            'available_fields': list(metadata.keys())
        }
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error extracting raw metadata from {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
