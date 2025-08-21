"""
Images router for image operations, thumbnails, and previews
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional
import logging
import io

from .models import ThumbnailRequest, PreviewRequest, ImageStats, SuccessResponse
from core.exr_processor import EXRProcessor
from core.thumbnail_worker import thumbnail_worker
from utils.image_converter import ImageConverter

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize processors
exr_processor = EXRProcessor()
image_converter = ImageConverter()

@router.get("/thumbnail/{file_path:path}")
async def get_thumbnail(
    file_path: str,
    size: int = Query(200, ge=50, le=800, description="Thumbnail size in pixels"),
    format: str = Query("PNG", description="Output format")
):
    """
    Get thumbnail image for display (uses background worker for performance)
    
    Args:
        file_path: Path to the EXR file
        size: Thumbnail size in pixels
        format: Output format (PNG or JPEG)
        
    Returns:
        Thumbnail image as bytes
    """
    try:
        # Validate format
        if format.upper() not in ['PNG', 'JPEG']:
            raise HTTPException(status_code=400, detail="Format must be PNG or JPEG")
        
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Check if thumbnail is already cached
        cached_thumbnail = thumbnail_worker.get_cached_thumbnail(file_path, size)
        if cached_thumbnail:
            # Set response headers
            mime_type = 'image/jpeg' if format.upper() == 'JPEG' else 'image/png'
            headers = {
                'Content-Type': mime_type,
                'Content-Length': str(len(cached_thumbnail)),
                'Cache-Control': 'public, max-age=3600'  # Cache for 1 hour
            }
            
            return Response(
                content=cached_thumbnail,
                media_type=mime_type,
                headers=headers
            )
        
        # If not cached, generate thumbnail using background worker
        # For now, generate synchronously but in the future this could be async
        thumbnail_bytes = await _generate_thumbnail_sync(file_path, size, format.upper())
        
        # Set response headers
        mime_type = 'image/jpeg' if format.upper() == 'JPEG' else 'image/png'
        headers = {
            'Content-Type': mime_type,
            'Content-Length': str(len(thumbnail_bytes)),
            'Cache-Control': 'public, max-age=3600'  # Cache for 1 hour
        }
        
        return Response(
            content=thumbnail_bytes,
            media_type=mime_type,
            headers=headers
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error generating thumbnail for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def _generate_thumbnail_sync(file_path: str, size: int, format: str) -> bytes:
    """Generate thumbnail synchronously (temporary until we implement proper async)"""
    try:
        # Read EXR file and create thumbnail
        image_data, _ = exr_processor.read_exr_file(file_path)
        thumbnail_bytes = image_converter.create_thumbnail(
            image_data, 
            size=(size, size), 
            output_format=format
        )
        
        # Cache the result
        thumbnail_worker.result_cache[f"{file_path}_{size}"] = thumbnail_bytes
        
        return thumbnail_bytes
        
    except Exception as e:
        logger.error(f"Error in thumbnail generation: {e}")
        raise

@router.get("/preview/{file_path:path}")
async def get_preview(
    file_path: str,
    format: str = Query("PNG", description="Output format"),
    quality: Optional[int] = Query(None, ge=1, le=100, description="JPEG quality")
):
    """
    Get preview image for editing
    
    Args:
        file_path: Path to the EXR file
        format: Output format (PNG or JPEG)
        quality: JPEG quality (1-100, only for JPEG)
        
    Returns:
        Preview image as bytes
    """
    try:
        # Validate format
        if format.upper() not in ['PNG', 'JPEG']:
            raise HTTPException(status_code=400, detail="Format must be PNG or JPEG")
        
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and convert to preview
        image_data, _ = exr_processor.read_exr_file(file_path)
        preview_bytes = image_converter.exr_to_bytes(
            image_data,
            output_format=format.upper(),
            quality=quality
        )
        
        # Set response headers
        mime_type = 'image/jpeg' if format.upper() == 'JPEG' else 'image/png'
        headers = {
            'Content-Type': mime_type,
            'Content-Length': str(len(preview_bytes)),
            'Cache-Control': 'public, max-age=1800'  # Cache for 30 minutes
        }
        
        return Response(
            content=preview_bytes,
            media_type=mime_type,
            headers=headers
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error generating preview for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preview-with-adjustments")
async def get_preview_with_adjustments(request: PreviewRequest):
    """
    Get preview image with applied adjustments
    
    Args:
        request: Preview request with adjustments
        
    Returns:
        Preview image as bytes
    """
    try:
        logger.info(f"Processing preview request for: {request.file_path}")
        logger.info(f"Adjustments: {request.adjustments}")
        
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(request.file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file
        logger.info("Reading EXR file...")
        image_data, _ = exr_processor.read_exr_file(request.file_path)
        logger.info(f"EXR file read successfully. Channels: {list(image_data.keys())}")
        logger.info(f"Channel shapes: {[(k, v.shape, v.dtype) for k, v in image_data.items()]}")
        
        # Apply adjustments if provided
        if request.adjustments:
            logger.info("Applying adjustments...")
            
            # Convert adjustments to dict format expected by processor
            adjustments_dict = {}
            if request.adjustments.exposure is not None:
                adjustments_dict['exposure'] = request.adjustments.exposure
            if request.adjustments.contrast is not None:
                adjustments_dict['contrast'] = request.adjustments.contrast
            if request.adjustments.brightness is not None:
                adjustments_dict['brightness'] = request.adjustments.brightness
            if request.adjustments.saturation is not None:
                adjustments_dict['saturation'] = request.adjustments.saturation
            if request.adjustments.red_scale is not None:
                adjustments_dict['red_scale'] = request.adjustments.red_scale
            if request.adjustments.green_scale is not None:
                adjustments_dict['green_scale'] = request.adjustments.green_scale
            if request.adjustments.blue_scale is not None:
                adjustments_dict['blue_scale'] = request.adjustments.blue_scale
            
            logger.info(f"Adjustments dict: {adjustments_dict}")
            
            # Apply tone mapping if specified
            if request.adjustments.tone_mapping:
                logger.info(f"Applying tone mapping: {request.adjustments.tone_mapping}")
                try:
                    image_data = image_converter.apply_tone_mapping(
                        image_data, 
                        method=request.adjustments.tone_mapping
                    )
                    logger.info("Tone mapping applied successfully")
                except Exception as e:
                    logger.error(f"Error applying tone mapping: {e}")
                    raise
            
            # Apply other adjustments
            if adjustments_dict:
                logger.info("Applying other adjustments...")
                try:
                    image_data = exr_processor.apply_adjustments(image_data, adjustments_dict)
                    logger.info("Adjustments applied successfully")
                except Exception as e:
                    logger.error(f"Error applying adjustments: {e}")
                    raise
        
        # Convert to preview format
        logger.info("Converting to preview format...")
        try:
            # Convert directly to bytes using the proper method
            preview_bytes = image_converter.exr_to_bytes(
                image_data,
                output_format=request.format.upper(),
                quality=request.quality
            )
            logger.info(f"Conversion to bytes successful. Size: {len(preview_bytes)} bytes")
            
        except Exception as e:
            logger.error(f"Error converting to preview format: {e}")
            raise
        
        # Set response headers
        mime_type = 'image/jpeg' if request.format.upper() == 'JPEG' else 'image/png'
        headers = {
            'Content-Type': mime_type,
            'Content-Length': str(len(preview_bytes)),
            'Cache-Control': 'no-cache'  # Don't cache adjusted previews
        }
        
        logger.info("Preview generation completed successfully")
        return Response(
            content=preview_bytes,
            media_type=mime_type,
            headers=headers
        )
        
    except FileNotFoundError:
        logger.error(f"File not found: {request.file_path}")
        raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
    except Exception as e:
        logger.error(f"Error generating adjusted preview for {request.file_path}: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats/{file_path:path}", response_model=ImageStats)
async def get_image_stats(file_path: str):
    """
    Get statistical information about an EXR image
    
    Args:
        file_path: Path to the EXR file
        
    Returns:
        Image statistics including min, max, mean, std for each channel
    """
    try:
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file
        image_data, _ = exr_processor.read_exr_file(file_path)
        
        # Get image statistics
        stats = image_converter.get_image_stats(image_data)
        
        return ImageStats(
            file_path=file_path,
            stats=stats
        )
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error getting image stats for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/base64/{file_path:path}")
async def get_image_base64(
    file_path: str,
    format: str = Query("PNG", description="Output format"),
    quality: Optional[int] = Query(None, ge=1, le=100, description="JPEG quality")
):
    """
    Get image as base64 data URL
    
    Args:
        file_path: Path to the EXR file
        format: Output format (PNG or JPEG)
        quality: JPEG quality (1-100, only for JPEG)
        
    Returns:
        Base64 encoded image as data URL
    """
    try:
        # Validate format
        if format.upper() not in ['PNG', 'JPEG']:
            raise HTTPException(status_code=400, detail="Format must be PNG or JPEG")
        
        # Check if file exists and is EXR
        if not exr_processor.is_exr_file(file_path):
            raise HTTPException(status_code=400, detail="File is not a valid EXR file")
        
        # Read EXR file and convert to base64
        image_data, _ = exr_processor.read_exr_file(file_path)
        base64_url = image_converter.exr_to_base64(
            image_data,
            output_format=format.upper(),
            quality=quality
        )
        
        return {"data_url": base64_url}
        
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error converting image to base64 for {file_path}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/clear-cache", response_model=SuccessResponse)
async def clear_image_cache():
    """
    Clear the image cache
    
    Returns:
        Success response
    """
    try:
        exr_processor.clear_cache()
        return SuccessResponse(message="Image cache cleared successfully")
    except Exception as e:
        logger.error(f"Error clearing image cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache-info")
async def get_cache_info():
    """
    Get information about the image cache
    
    Returns:
        Cache information
    """
    try:
        cache_info = exr_processor.get_cache_info()
        return cache_info
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
