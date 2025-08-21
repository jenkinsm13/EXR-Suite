"""
Editing router for image adjustments and saving operations
"""

from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import logging
import os
from pathlib import Path

from .models import (
    ImageAdjustments, SaveRequest, SuccessResponse, 
    ImageStats, ErrorResponse
)
from core.exr_processor import EXRProcessor
from utils.image_converter import ImageConverter

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize processors
exr_processor = EXRProcessor()
image_converter = ImageConverter()

@router.post("/adjust", response_model=ImageStats)
async def adjust_image(
    file_path: str = Body(..., description="Path to the EXR file"),
    adjustments: ImageAdjustments = Body(..., description="Image adjustment parameters")
):
    """
    Apply image adjustments and return preview statistics
    
    Args:
        file_path: Path to the EXR file
        adjustments: Image adjustment parameters
        
    Returns:
        Image statistics after adjustments
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file
        image_data, metadata = exr_processor.read_exr_file(file_path)
        
        # Convert adjustments to dict format
        adjustments_dict = {}
        if adjustments.exposure is not None:
            adjustments_dict['exposure'] = adjustments.exposure
        if adjustments.contrast is not None:
            adjustments_dict['contrast'] = adjustments.contrast
        if adjustments.brightness is not None:
            adjustments_dict['brightness'] = adjustments.brightness
        if adjustments.saturation is not None:
            adjustments_dict['saturation'] = adjustments.saturation
        if adjustments.red_scale is not None:
            adjustments_dict['red_scale'] = adjustments.red_scale
        if adjustments.green_scale is not None:
            adjustments_dict['green_scale'] = adjustments.green_scale
        if adjustments.blue_scale is not None:
            adjustments_dict['blue_scale'] = adjustments.blue_scale
        
        # Apply tone mapping if specified
        if adjustments.tone_mapping:
            image_data = image_converter.apply_tone_mapping(
                image_data, 
                method=adjustments.tone_mapping
            )
        
        # Apply other adjustments
        if adjustments_dict:
            image_data = exr_processor.apply_adjustments(image_data, adjustments_dict)
        
        # Get image statistics
        stats = image_converter.get_image_stats(image_data)
        
        # Store adjusted image in cache for potential saving
        cache_key = f"{file_path}_adjusted"
        exr_processor.cache[cache_key] = {
            'image_data': image_data,
            'metadata': metadata,
            'adjustments': adjustments_dict
        }
        
        return ImageStats(
            file_path=file_path,
            stats=stats
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error applying adjustments to {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save", response_model=SuccessResponse)
async def save_image(request: SaveRequest):
    """
    Save edited image to EXR file
    
    Args:
        request: Save request with file path and options
        
    Returns:
        Success response
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(request.file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Determine output file path
        if request.save_as_new:
            if not request.new_filename:
                raise HTTPException(status_code=400, detail="New filename is required when saving as new file")
            
            # Create new filename with .exr extension if not provided
            if not request.new_filename.lower().endswith('.exr'):
                request.new_filename += '.exr'
            
            # Create output path in same directory as original
            original_dir = os.path.dirname(request.file_path)
            output_path = os.path.join(original_dir, request.new_filename)
            
            # Check if output file already exists
            if os.path.exists(output_path):
                raise HTTPException(status_code=409, detail=f"Output file already exists: {output_path}")
        else:
            # Overwrite original file
            output_path = request.file_path
        
        # Check if we have adjusted image in cache
        cache_key = f"{request.file_path}_adjusted"
        if cache_key in exr_processor.cache:
            # Use adjusted image from cache
            cached_data = exr_processor.cache[cache_key]
            image_data = cached_data['image_data']
            metadata = cached_data['metadata']
            
            # Get original header for metadata preservation
            original_header = None
            if request.file_path in exr_processor.cache:
                original_header = exr_processor.cache[request.file_path]['header']
            
            # Write adjusted image
            exr_processor.write_exr_file(
                output_path, 
                image_data, 
                metadata, 
                original_header
            )
            
            # Clear adjusted image from cache
            del exr_processor.cache[cache_key]
            
            action = "saved as new file" if request.save_as_new else "overwritten"
            return SuccessResponse(
                message=f"Image {action} successfully: {output_path}",
                data={"output_path": output_path}
            )
        else:
            # No adjustments applied, just copy original
            if request.save_as_new:
                import shutil
                shutil.copy2(request.file_path, output_path)
                action = "copied as new file"
            else:
                action = "no changes to save"
            
            return SuccessResponse(
                message=f"Image {action}: {output_path}",
                data={"output_path": output_path}
            )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied writing to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving image {request.file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-with-adjustments", response_model=SuccessResponse)
async def save_with_adjustments(
    file_path: str = Body(..., description="Path to the EXR file"),
    adjustments: ImageAdjustments = Body(..., description="Image adjustment parameters"),
    save_as_new: bool = Body(False, description="Save as new file instead of overwriting"),
    new_filename: Optional[str] = Body(None, description="New filename (required if save_as_new is True)")
):
    """
    Apply adjustments and save image in one operation
    
    Args:
        file_path: Path to the EXR file
        adjustments: Image adjustment parameters
        save_as_new: Save as new file instead of overwriting
        new_filename: New filename (required if save_as_new is True)
        
    Returns:
        Success response
    """
    try:
        # Validate new filename if saving as new
        if save_as_new and not new_filename:
            raise HTTPException(status_code=400, detail="New filename is required when saving as new file")
        
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file
        image_data, metadata = exr_processor.read_exr_file(file_path)
        
        # Convert adjustments to dict format
        adjustments_dict = {}
        if adjustments.exposure is not None:
            adjustments_dict['exposure'] = adjustments.exposure
        if adjustments.contrast is not None:
            adjustments_dict['contrast'] = adjustments.contrast
        if adjustments.brightness is not None:
            adjustments_dict['brightness'] = adjustments.brightness
        if adjustments.saturation is not None:
            adjustments_dict['saturation'] = adjustments.saturation
        if adjustments.red_scale is not None:
            adjustments_dict['red_scale'] = adjustments.red_scale
        if adjustments.green_scale is not None:
            adjustments_dict['green_scale'] = adjustments.green_scale
        if adjustments.blue_scale is not None:
            adjustments_dict['blue_scale'] = adjustments.blue_scale
        
        # Apply tone mapping if specified
        if adjustments.tone_mapping:
            image_data = image_converter.apply_tone_mapping(
                image_data, 
                method=adjustments.tone_mapping
            )
        
        # Apply other adjustments
        if adjustments_dict:
            image_data = exr_processor.apply_adjustments(image_data, adjustments_dict)
        
        # Determine output file path
        if save_as_new:
            # Create new filename with .exr extension if not provided
            if not new_filename.lower().endswith('.exr'):
                new_filename += '.exr'
            
            # Create output path in same directory as original
            original_dir = os.path.dirname(file_path)
            output_path = os.path.join(original_dir, new_filename)
            
            # Check if output file already exists
            if os.path.exists(output_path):
                raise HTTPException(status_code=409, detail=f"Output file already exists: {output_path}")
        else:
            # Overwrite original file
            output_path = file_path
        
        # Get original header for metadata preservation
        original_header = None
        if file_path in exr_processor.cache:
            original_header = exr_processor.cache[file_path]['header']
        
        # Write adjusted image
        exr_processor.write_exr_file(
            output_path, 
            image_data, 
            metadata, 
            original_header
        )
        
        action = "saved as new file" if save_as_new else "overwritten"
        return SuccessResponse(
            message=f"Image with adjustments {action} successfully: {output_path}",
            data={
                "output_path": output_path,
                "adjustments_applied": adjustments_dict
            }
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except PermissionError:
        raise HTTPException(status_code=403, detail=f"Permission denied writing to: {output_path}")
    except Exception as e:
        logger.error(f"Error saving image with adjustments {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/preview-adjustments/{file_path:path}")
async def preview_adjustments(
    file_path: str,
    exposure: Optional[float] = None,
    contrast: Optional[float] = None,
    brightness: Optional[float] = None,
    saturation: Optional[float] = None,
    red_scale: Optional[float] = None,
    green_scale: Optional[float] = None,
    blue_scale: Optional[float] = None,
    tone_mapping: Optional[str] = None
):
    """
    Get preview of adjustments without saving
    
    Args:
        file_path: Path to the EXR file
        exposure: Exposure adjustment
        contrast: Contrast adjustment
        brightness: Brightness adjustment
        saturation: Saturation adjustment
        red_scale: Red channel scale
        green_scale: Green channel scale
        blue_scale: Blue channel scale
        tone_mapping: Tone mapping method
        
    Returns:
        Preview image with adjustments applied
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file
        image_data, _ = exr_processor.read_exr_file(file_path)
        
        # Build adjustments dict
        adjustments_dict = {}
        if exposure is not None:
            adjustments_dict['exposure'] = exposure
        if contrast is not None:
            adjustments_dict['contrast'] = contrast
        if brightness is not None:
            adjustments_dict['brightness'] = brightness
        if saturation is not None:
            adjustments_dict['saturation'] = saturation
        if red_scale is not None:
            adjustments_dict['red_scale'] = red_scale
        if green_scale is not None:
            adjustments_dict['green_scale'] = green_scale
        if blue_scale is not None:
            adjustments_dict['blue_scale'] = blue_scale
        
        # Apply tone mapping if specified
        if tone_mapping:
            if tone_mapping not in ['reinhard', 'gamma', 'linear']:
                raise HTTPException(status_code=400, detail="Invalid tone mapping method")
            image_data = image_converter.apply_tone_mapping(image_data, method=tone_mapping)
        
        # Apply other adjustments
        if adjustments_dict:
            image_data = exr_processor.apply_adjustments(image_data, adjustments_dict)
        
        # Convert to preview format
        preview_bytes = image_converter.exr_to_bytes(image_data, output_format='PNG')
        
        # Return preview image
        from fastapi.responses import Response
        return Response(
            content=preview_bytes,
            media_type='image/png',
            headers={'Cache-Control': 'no-cache'}
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error generating adjustment preview for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/adjustment-presets")
async def get_adjustment_presets():
    """
    Get predefined adjustment presets
    
    Returns:
        Dictionary of adjustment presets
    """
    presets = {
        "cinematic": {
            "exposure": 0.5,
            "contrast": 1.2,
            "saturation": 0.8,
            "tone_mapping": "reinhard"
        },
        "vintage": {
            "exposure": -0.3,
            "contrast": 1.4,
            "saturation": 0.6,
            "red_scale": 1.1,
            "blue_scale": 0.9
        },
        "bright": {
            "exposure": 1.0,
            "contrast": 0.8,
            "brightness": 0.2
        },
        "dark": {
            "exposure": -1.0,
            "contrast": 1.3,
            "brightness": -0.2
        },
        "high_contrast": {
            "exposure": 0.0,
            "contrast": 2.0,
            "saturation": 1.2
        }
    }
    
    return {"presets": presets}
