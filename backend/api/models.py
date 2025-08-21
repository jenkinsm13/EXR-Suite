"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any, Union
from enum import Enum
import os

class FileType(str, Enum):
    """File type enumeration"""
    DIRECTORY = "directory"
    FILE = "file"
    EXR = "exr"

class DirectoryItem(BaseModel):
    """Model for directory items"""
    name: str
    path: str
    is_dir: bool
    is_file: bool
    is_exr: bool = False
    size: int = 0
    size_human: str = ""
    modified: Optional[str] = None
    extension: str = ""

class DirectoryListing(BaseModel):
    """Model for directory listing response"""
    current_path: str
    parent_path: str
    items: List[DirectoryItem]
    directory_count: int
    file_count: int
    exr_count: int
    total_size: int

class FileInfo(BaseModel):
    """Model for file information"""
    name: str
    path: str
    size: int
    size_human: str
    modified: str
    created: str
    is_exr: bool
    extension: str
    directory: str

class ImageAdjustments(BaseModel):
    """Model for image adjustment parameters"""
    exposure: Optional[float] = Field(None, ge=-10.0, le=10.0, description="Exposure adjustment in stops")
    contrast: Optional[float] = Field(None, ge=0.1, le=5.0, description="Contrast adjustment")
    brightness: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Brightness adjustment")
    saturation: Optional[float] = Field(None, ge=0.0, le=3.0, description="Saturation adjustment")
    red_scale: Optional[float] = Field(None, ge=0.0, le=3.0, description="Red channel scale")
    green_scale: Optional[float] = Field(None, ge=0.0, le=3.0, description="Green channel scale")
    blue_scale: Optional[float] = Field(None, ge=0.0, le=3.0, description="Blue channel scale")
    tone_mapping: Optional[str] = Field(None, description="Tone mapping method")
    
    @validator('tone_mapping')
    def validate_tone_mapping(cls, v):
        if v is not None and v not in ['reinhard', 'gamma', 'linear']:
            raise ValueError('tone_mapping must be one of: reinhard, gamma, linear')
        return v

class SaveRequest(BaseModel):
    """Model for save request"""
    file_path: str
    save_as_new: bool = False
    new_filename: Optional[str] = None
    
    @validator('file_path')
    def validate_file_path(cls, v):
        if not os.path.exists(v):
            raise ValueError('File path does not exist')
        return v
    
    @validator('new_filename')
    def validate_new_filename(cls, v, values):
        if values.get('save_as_new') and not v:
            raise ValueError('New filename is required when saving as new file')
        return v

class ThumbnailRequest(BaseModel):
    """Model for thumbnail request"""
    file_path: str
    size: int = Field(200, ge=50, le=800, description="Thumbnail size in pixels")
    format: str = Field("PNG", description="Output format")
    
    @validator('format')
    def validate_format(cls, v):
        if v.upper() not in ['PNG', 'JPEG', 'JPEG']:
            raise ValueError('Format must be PNG or JPEG')
        return v.upper()

class PreviewRequest(BaseModel):
    """Model for preview request"""
    file_path: str
    adjustments: Optional[ImageAdjustments] = None
    format: str = Field("PNG", description="Output format")
    quality: Optional[int] = Field(None, ge=1, le=100, description="JPEG quality")

class MetadataResponse(BaseModel):
    """Model for metadata response"""
    file_path: str
    channels: List[str]
    data_window: str
    display_window: str
    channel_info: Dict[str, Any]
    pixel_aspect_ratio: Optional[float] = None
    screen_window_center: Optional[str] = None
    screen_window_width: Optional[float] = None
    line_order: Optional[str] = None
    compression: Optional[str] = None
    chunk_count: Optional[int] = None
    tiles: Optional[str] = None
    envmap: Optional[str] = None
    adopted_neutral: Optional[str] = None
    rendering_transform: Optional[str] = None
    look_mod_transform: Optional[str] = None
    white_luminance: Optional[str] = None
    chromaticities: Optional[str] = None
    white_point: Optional[str] = None
    primaries: Optional[str] = None
    aces_image_container_flag: Optional[str] = None
    multi_view: Optional[str] = None
    world_to_camera: Optional[str] = None
    world_to_ndc: Optional[str] = None
    deep_image_state: Optional[str] = None
    tiledesc: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    version: Optional[str] = None
    max_samples_per_pixel: Optional[str] = None
    dwa_compression_level: Optional[str] = None
    id_manifest: Optional[str] = None
    tile_description: Optional[str] = None
    multi_part: Optional[str] = None
    view: Optional[str] = None
    owner: Optional[str] = None
    comments: Optional[str] = None
    cap_date: Optional[str] = None
    utc_offset: Optional[str] = None
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    altitude: Optional[str] = None
    focus: Optional[str] = None
    exp_time: Optional[str] = None
    aperture: Optional[str] = None
    iso_speed: Optional[str] = None
    key_code: Optional[str] = None
    time_code: Optional[str] = None
    wrapmodes: Optional[str] = None
    frames_per_second: Optional[str] = None

class ImageStats(BaseModel):
    """Model for image statistics"""
    file_path: str
    stats: Dict[str, Any]

class ErrorResponse(BaseModel):
    """Model for error responses"""
    error: str
    detail: Optional[str] = None
    status_code: int = 500

class SuccessResponse(BaseModel):
    """Model for success responses"""
    message: str
    data: Optional[Any] = None

class CacheInfo(BaseModel):
    """Model for cache information"""
    cached_files: int
    cache_keys: List[str]

class SearchRequest(BaseModel):
    """Model for search request"""
    query: str = Field(..., min_length=1, description="Search query")
    directory: Optional[str] = None
    recursive: bool = True

class SearchResponse(BaseModel):
    """Model for search response"""
    query: str
    results: List[FileInfo]
    total_results: int
    search_directory: str

class DriveInfo(BaseModel):
    """Model for drive information"""
    drives: List[str]
    current_drive: str

class NavigationRequest(BaseModel):
    """Model for navigation request"""
    path: str = Field(..., description="Path to navigate to")

class NavigationResponse(BaseModel):
    """Model for navigation response"""
    current_path: str
    parent_path: str
    directory_listing: DirectoryListing
