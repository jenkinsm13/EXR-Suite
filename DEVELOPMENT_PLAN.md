# EXR Editing Suite - Development Plan

## Project Overview
A high-performance, real-time EXR Editing Suite with Lightroom-esque functionality, built using React frontend, Python backend with OpenEXR, and pywebview for seamless desktop integration.

## Core Features
- **Directory Navigation**: Browse and select EXR files from filesystem
- **Image Library**: Display EXR images with thumbnails and grid view
- **Editing Interface**: Real-time mathematical adjustments (exposure, contrast, color balance, etc.)
- **Metadata Panel**: Display all EXR metadata (header data, chromaticities, color space, etc.)
- **Save Functionality**: 
  - Single click: Save to existing EXR file
  - Shift+click: Save as new EXR file

## Technology Stack (2025 Best Practices)

### Frontend
- **React 18+** with TypeScript
- **Vite** for fast development and optimized builds
- **Tailwind CSS** for modern, responsive UI
- **React Router** for navigation between library and editing views
- **Zustand** for lightweight state management
- **React Query** for efficient data fetching and caching

### Backend
- **Python 3.12+** with type hints
- **FastAPI** for high-performance async API
- **OpenEXR** for EXR file operations
- **NumPy** for efficient image data manipulation
- **Pillow** for image format conversion (EXR ↔ PNG/JPEG for display)
- **Pydantic** for data validation

### Desktop Integration
- **pywebview** for native desktop window
- **PyInstaller** for cross-platform distribution

## Architecture

### High-Level Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React UI      │◄──►│   FastAPI       │◄──►│   OpenEXR       │
│   (pywebview)   │    │   Backend       │    │   Processing    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow
1. **File Operations**: Frontend requests directory listing and file operations
2. **Image Processing**: Backend reads EXR files, processes edits, saves changes
3. **Real-time Updates**: WebSocket/SSE for live preview updates
4. **Metadata Display**: Backend extracts and serves EXR metadata

## Stepwise Implementation

### Phase 1: Project Setup & Foundation
1. **Initialize Project Structure**
   ```bash
   mkdir exr-suite
   cd exr-suite
   mkdir frontend backend
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   # Activate venv
   pip install fastapi uvicorn openexr numpy pillow pydantic python-multipart
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm create vite@latest . -- --template react-ts
   npm install
   npm install tailwindcss @tailwindcss/forms @headlessui/react
   npm install react-router-dom zustand @tanstack/react-query
   ```

4. **pywebview Integration**
   ```bash
   cd backend
   pip install pywebview
   ```

### Phase 2: Core Backend Development
1. **EXR File Operations Module**
   - File reading/writing with OpenEXR
   - Metadata extraction
   - Image data conversion for display

2. **FastAPI Endpoints**
   - Directory listing
   - EXR file operations
   - Image processing operations
   - Metadata retrieval

3. **Image Processing Engine**
   - Mathematical operations (exposure, contrast, etc.)
   - Real-time preview generation
   - Efficient memory management

### Phase 3: Frontend Development
1. **Core Components**
   - File browser/explorer
   - Image library grid
   - Editing interface
   - Metadata panel

2. **State Management**
   - File selection state
   - Editing parameters
   - Real-time preview updates

3. **UI/UX Implementation**
   - Responsive design
   - Keyboard shortcuts
   - Drag & drop support

### Phase 4: Integration & Testing
1. **pywebview Integration**
   - Native window creation
   - Frontend-backend communication
   - Error handling

2. **Performance Optimization**
   - Image caching
   - Lazy loading
   - Memory management

3. **Testing & Debugging**
   - Unit tests
   - Integration tests
   - Performance profiling

### Phase 5: Distribution
1. **PyInstaller Configuration**
   - Cross-platform builds
   - Dependency bundling
   - Icon and metadata

## OpenEXR Implementation Details

### File Reading
```python
import OpenEXR
import numpy as np

def read_exr_file(file_path: str):
    """Read EXR file and return image data and metadata"""
    exr_file = OpenEXR.InputFile(file_path)
    header = exr_file.header()
    
    # Extract metadata
    metadata = {
        'channels': list(header['channels'].keys()),
        'dataWindow': header['dataWindow'],
        'displayWindow': header['displayWindow'],
        'pixelAspectRatio': header.get('pixelAspectRatio', 1.0),
        'screenWindowCenter': header.get('screenWindowCenter', (0.0, 0.0)),
        'screenWindowWidth': header.get('screenWindowWidth', 1.0),
        'lineOrder': header.get('lineOrder', 'INCREASING_Y'),
        'compression': header.get('compression', 'NO_COMPRESSION'),
        'chunkCount': header.get('chunkCount', 1),
        'tiles': header.get('tiles', None),
        'envmap': header.get('envmap', None),
        'adoptedNeutral': header.get('adoptedNeutral', None),
        'renderingTransform': header.get('renderingTransform', None),
        'lookModTransform': header.get('lookModTransform', None),
        'whiteLuminance': header.get('whiteLuminance', None),
        'chromaticities': header.get('chromaticities', None),
        'whitePoint': header.get('whitePoint', None),
        'primaries': header.get('primaries', None),
        'acesImageContainerFlag': header.get('acesImageContainerFlag', None),
        'multiView': header.get('multiView', None),
        'worldToCamera': header.get('worldToCamera', None),
        'worldToNDC': header.get('worldToNDC', None),
        'deepImageState': header.get('deepImageState', None),
        'tiledesc': header.get('tiledesc', None),
        'name': header.get('name', None),
        'type': header.get('type', None),
        'version': header.get('version', None),
        'chunkCount': header.get('chunkCount', None),
        'maxSamplesPerPixel': header.get('maxSamplesPerPixel', None),
        'dwaCompressionLevel': header.get('dwaCompressionLevel', None),
        'idManifest': header.get('idManifest', None),
        'tileDescription': header.get('tileDescription', None),
        'multiPart': header.get('multiPart', None),
        'view': header.get('view', None),
        'owner': header.get('owner', None),
        'comments': header.get('comments', None),
        'capDate': header.get('capDate', None),
        'utcOffset': header.get('utcOffset', None),
        'longitude': header.get('longitude', None),
        'latitude': header.get('latitude', None),
        'altitude': header.get('altitude', None),
        'focus': header.get('focus', None),
        'expTime': header.get('expTime', None),
        'aperture': header.get('aperture', None),
        'isoSpeed': header.get('isoSpeed', None),
        'keyCode': header.get('keyCode', None),
        'timeCode': header.get('timeCode', None),
        'wrapmodes': header.get('wrapmodes', None),
        'framesPerSecond': header.get('framesPerSecond', None),
        'multiView': header.get('multiView', None),
        'worldToCamera': header.get('worldToCamera', None),
        'worldToNDC': header.get('worldToNDC', None),
        'deepImageState': header.get('deepImageState', None),
        'tiledesc': header.get('tiledesc', None),
        'name': header.get('name', None),
        'type': header.get('type', None),
        'version': header.get('version', None),
        'chunkCount': header.get('chunkCount', None),
        'maxSamplesPerPixel': header.get('maxSamplesPerPixel', None),
        'dwaCompressionLevel': header.get('dwaCompressionLevel', None),
        'idManifest': header.get('idManifest', None),
        'tileDescription': header.get('tileDescription', None),
        'multiPart': header.get('multiPart', None),
        'view': header.get('view', None),
        'owner': header.get('owner', None),
        'comments': header.get('comments', None),
        'capDate': header.get('capDate', None),
        'utcOffset': header.get('utcOffset', None),
        'longitude': header.get('longitude', None),
        'latitude': header.get('latitude', None),
        'altitude': header.get('altitude', None),
        'focus': header.get('focus', None),
        'expTime': header.get('expTime', None),
        'aperture': header.get('aperture', None),
        'isoSpeed': header.get('isoSpeed', None),
        'keyCode': header.get('keyCode', None),
        'timeCode': header.get('timeCode', None),
        'wrapmodes': header.get('wrapmodes', None),
        'framesPerSecond': header.get('framesPerSecond', None)
    }
    
    # Read image data
    channels = list(header['channels'].keys())
    data_window = header['dataWindow']
    width = data_window.max.x - data_window.min.x + 1
    height = data_window.max.y - data_window.min.y + 1
    
    # Read all channels
    image_data = {}
    for channel in channels:
        channel_data = exr_file.channel(channel)
        image_data[channel] = np.frombuffer(channel_data, dtype=np.float32).reshape(height, width)
    
    exr_file.close()
    return image_data, metadata
```

### File Writing
```python
def write_exr_file(file_path: str, image_data: dict, metadata: dict, original_header=None):
    """Write image data to EXR file with metadata preservation"""
    if original_header:
        header = original_header.copy()
    else:
        # Create new header
        height, width = next(iter(image_data.values())).shape
        header = OpenEXR.Header(width, height)
        
        # Set channels
        header['channels'] = {}
        for channel_name in image_data.keys():
            header['channels'][channel_name] = Imath.Channel(Imath.FLOAT)
    
    # Create output file
    exr_file = OpenEXR.OutputFile(file_path, header)
    
    # Prepare data for writing
    data_to_write = {}
    for channel_name, channel_data in image_data.items():
        data_to_write[channel_name] = channel_data.astype(np.float32).tobytes()
    
    # Write pixels
    exr_file.writePixels(data_to_write)
    exr_file.close()
```

### Image Processing Operations
```python
def adjust_exposure(image_data: dict, exposure_value: float) -> dict:
    """Adjust exposure by multiplying pixel values by 2^exposure_value"""
    adjusted_data = {}
    for channel_name, channel_data in image_data.items():
        adjusted_data[channel_name] = np.clip(
            channel_data * (2 ** exposure_value), 
            0.0, 
            np.finfo(np.float32).max
        )
    return adjusted_data

def adjust_contrast(image_data: dict, contrast_value: float) -> dict:
    """Adjust contrast using power function"""
    adjusted_data = {}
    for channel_name, channel_data in image_data.items():
        # Normalize to 0-1 range first
        normalized = (channel_data - channel_data.min()) / (channel_data.max() - channel_data.min())
        # Apply contrast
        adjusted = np.power(normalized, contrast_value)
        # Scale back to original range
        adjusted_data[channel_name] = adjusted * (channel_data.max() - channel_data.min()) + channel_data.min()
    return adjusted_data

def adjust_color_balance(image_data: dict, red_scale: float, green_scale: float, blue_scale: float) -> dict:
    """Adjust color balance by scaling RGB channels"""
    adjusted_data = {}
    scales = {'R': red_scale, 'G': green_scale, 'B': blue_scale}
    
    for channel_name, channel_data in image_data.items():
        if channel_name in scales:
            adjusted_data[channel_name] = np.clip(
                channel_data * scales[channel_name], 
                0.0, 
                np.finfo(np.float32).max
            )
        else:
            adjusted_data[channel_name] = channel_data.copy()
    
    return adjusted_data
```

## FastAPI Backend Structure

### Main Application
```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI(title="EXR Editing Suite API", version="1.0.0")

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(files_router, prefix="/api/files", tags=["files"])
app.include_router(images_router, prefix="/api/images", tags=["images"])
app.include_router(editing_router, prefix="/api/editing", tags=["editing"])
app.include_router(metadata_router, prefix="/api/metadata", tags=["metadata"])

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
```

### API Endpoints
```python
# files_router.py
@router.get("/directory")
async def list_directory(path: str = ""):
    """List contents of directory"""
    pass

@router.get("/file-info")
async def get_file_info(file_path: str):
    """Get EXR file information"""
    pass

# images_router.py
@router.get("/thumbnail/{file_path:path}")
async def get_thumbnail(file_path: str, size: int = 200):
    """Get thumbnail image for display"""
    pass

@router.get("/preview/{file_path:path}")
async def get_preview(file_path: str):
    """Get preview image for editing"""
    pass

# editing_router.py
@router.post("/adjust")
async def adjust_image(file_path: str, adjustments: dict):
    """Apply image adjustments"""
    pass

@router.post("/save")
async def save_image(file_path: str, save_as_new: bool = False):
    """Save edited image"""
    pass

# metadata_router.py
@router.get("/{file_path:path}")
async def get_metadata(file_path: str):
    """Get EXR file metadata"""
    pass
```

## Frontend React Structure

### Main App Component
```typescript
// App.tsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LibraryView } from './views/LibraryView';
import { EditingView } from './views/EditingView';
import { Sidebar } from './components/Sidebar';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen bg-gray-900">
          <Sidebar />
          <main className="flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<LibraryView />} />
              <Route path="/edit/:filePath" element={<EditingView />} />
            </Routes>
          </main>
        </div>
      </Router>
    </QueryClientProvider>
  );
}
```

### Key Components
1. **FileBrowser**: Directory navigation and file selection
2. **ImageLibrary**: Grid view of EXR files with thumbnails
3. **EditingInterface**: Sliders and controls for image adjustments
4. **MetadataPanel**: Display of all EXR metadata
5. **ImagePreview**: Real-time preview of edited image
6. **Toolbar**: Save buttons and editing tools

## pywebview Integration

### Main Entry Point
```python
# main.py
import webview
import threading
from backend.main import app
import uvicorn

def start_backend():
    """Start FastAPI backend in separate thread"""
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")

if __name__ == "__main__":
    # Start backend
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Create pywebview window
    webview.create_window(
        'EXR Editing Suite',
        'http://127.0.0.1:8001',
        width=1400,
        height=900,
        resizable=True,
        text_select=True
    )
    webview.start()
```

## Performance Considerations

### Real-time Responsiveness
1. **Image Caching**: Cache processed images and thumbnails
2. **Lazy Loading**: Load images only when needed
3. **Background Processing**: Process edits in background threads
4. **Memory Management**: Efficient handling of large EXR files
5. **WebSocket Updates**: Real-time preview updates

### Optimization Strategies
1. **NumPy Vectorization**: Use vectorized operations for image processing
2. **Memory Mapping**: Memory-map large files when possible
3. **Chunked Processing**: Process large images in chunks
4. **GPU Acceleration**: Consider CUDA/OpenCL for heavy operations

## Gotchas & Challenges

### OpenEXR Specific
1. **Memory Usage**: EXR files can be very large, monitor memory usage
2. **Channel Types**: Handle different data types (FLOAT, HALF, UINT) properly
3. **Metadata Preservation**: Ensure all metadata is preserved during save operations
4. **Error Handling**: Robust error handling for corrupted or unsupported files

### Performance Issues
1. **Large File Loading**: Implement progress indicators for large files
2. **Real-time Updates**: Balance quality vs. performance for live preview
3. **Memory Leaks**: Careful management of OpenEXR file handles

### Cross-platform Compatibility
1. **File Paths**: Handle different path separators and encodings
2. **Dependencies**: Ensure OpenEXR works on all target platforms
3. **pywebview Issues**: Test thoroughly on each platform

### Development Challenges
1. **Hot Reloading**: pywebview doesn't support hot reloading during development
2. **Debugging**: Separate debugging for frontend and backend
3. **Build Process**: Complex build process with multiple technologies

## Testing Strategy

### Backend Testing
1. **Unit Tests**: Test individual image processing functions
2. **Integration Tests**: Test API endpoints with real EXR files
3. **Performance Tests**: Test with large files and measure memory usage

### Frontend Testing
1. **Component Tests**: Test individual React components
2. **Integration Tests**: Test user workflows
3. **Performance Tests**: Test with large image libraries

### End-to-End Testing
1. **User Workflows**: Test complete editing workflows
2. **File Operations**: Test file loading, editing, and saving
3. **Error Handling**: Test error conditions and edge cases

## Deployment & Distribution

### Development
1. **Local Development**: Separate frontend and backend servers
2. **Hot Reloading**: Frontend development with Vite
3. **Debugging**: Integrated debugging for both frontend and backend

### Production Build
1. **Frontend Build**: Optimized React build with Vite
2. **Backend Packaging**: Python executable with PyInstaller
3. **Asset Bundling**: Include all necessary assets and dependencies

### Distribution
1. **Windows**: .exe installer with PyInstaller
2. **macOS**: .app bundle with py2app
3. **Linux**: AppImage or package manager distribution

## Timeline Estimate

- **Phase 1**: 1-2 weeks (Project setup and foundation)
- **Phase 2**: 2-3 weeks (Core backend development)
- **Phase 3**: 3-4 weeks (Frontend development)
- **Phase 4**: 2-3 weeks (Integration and testing)
- **Phase 5**: 1-2 weeks (Distribution and final testing)

**Total Estimated Time**: 9-14 weeks

## Success Metrics

1. **Performance**: Real-time editing with files up to 4K resolution
2. **Usability**: Intuitive interface similar to Lightroom
3. **Reliability**: Stable operation with various EXR file types
4. **Compatibility**: Cross-platform support
5. **User Experience**: Smooth workflow from file selection to saving
