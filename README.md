# EXR Editing Suite

A professional-grade desktop application for editing EXR (OpenEXR) image files with real-time adjustments, comprehensive metadata viewing, and mathematical accuracy.

## Features

- **Directory Navigation**: Browse and select EXR files from the filesystem
- **Image Library**: Display images in a library view with thumbnails
- **Real-time Editing**: Make precise mathematical adjustments (exposure, contrast, color balance, etc.)
- **Metadata Panel**: Display comprehensive EXR metadata (header data, chromaticities, color space, etc.)
- **Save Functionality**: 
  - Single click: Save directly to existing EXR file
  - Shift+click: Save as new EXR file
- **Performance**: Fast, responsive, and real-time editing
- **Cross-platform**: Works on Windows, macOS, and Linux

## Technology Stack

### Backend
- **Python 3.8+** with FastAPI
- **OpenEXR** for EXR file handling
- **NumPy** for numerical operations
- **Pillow (PIL)** for image conversion
- **Pydantic** for data validation

### Frontend
- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Query** for data fetching
- **React Router** for navigation

### Desktop Integration
- **pywebview** for seamless desktop integration

## Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- Git

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd EXR-Suite
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Build the frontend**:
   ```bash
   cd frontend
   npm run build
   cd ..
   ```

## Usage

### Development Mode

1. **Start the backend server**:
   ```bash
   cd backend
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8001
   ```

2. **Start the frontend development server**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open your browser** and navigate to `http://localhost:3000`

### Desktop Application

Run the desktop application:
```bash
python main.py
```

## Project Structure

```
EXR-Suite/
├── backend/                 # Python FastAPI backend
│   ├── api/                # API routers
│   ├── core/               # Core business logic
│   ├── utils/              # Utility functions
│   ├── main.py             # FastAPI application
│   └── app.py              # Desktop app integration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── views/          # Page-level components
│   │   ├── stores/         # State management
│   │   ├── types/          # TypeScript definitions
│   │   └── utils/          # Utility functions
│   ├── dist/               # Built frontend (generated)
│   └── package.json        # Frontend dependencies
├── main.py                 # Desktop app entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## API Endpoints

### Files
- `GET /api/files/directory` - List directory contents
- `GET /api/files/file-info` - Get file information
- `POST /api/files/navigate` - Navigate to directory
- `GET /api/files/parent` - Get parent directory
- `POST /api/files/search` - Search for files

### Images
- `GET /api/images/thumbnail/{file_path}` - Get image thumbnail
- `GET /api/images/preview/{file_path}` - Get image preview
- `POST /api/images/preview-with-adjustments` - Get preview with adjustments
- `GET /api/images/stats/{file_path}` - Get image statistics

### Metadata
- `GET /api/metadata/{file_path}` - Get full metadata
- `GET /api/metadata/summary/{file_path}` - Get metadata summary
- `GET /api/metadata/channels/{file_path}` - Get channel information

### Editing
- `POST /api/editing/adjust` - Apply adjustments
- `POST /api/editing/save` - Save image
- `POST /api/editing/save-with-adjustments` - Save with adjustments
- `GET /api/editing/adjustment-presets` - Get adjustment presets

## Development

### Backend Development

The backend uses FastAPI with automatic API documentation. After starting the backend server, visit:
- API documentation: `http://127.0.0.1:8001/docs`
- Alternative docs: `http://127.0.0.1:8001/redoc`

### Frontend Development

The frontend uses Vite for fast development with hot module replacement. Key commands:
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint

### Adding New Features

1. **Backend**: Add new endpoints in `backend/api/` routers
2. **Frontend**: Add new components in `frontend/src/components/`
3. **Types**: Update TypeScript definitions in `frontend/src/types/`
4. **State**: Update Zustand store in `frontend/src/stores/`

## Building for Distribution

### Using PyInstaller

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

### Using cx_Freeze

```bash
pip install cx_Freeze
python setup.py build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenEXR for the excellent EXR file format support
- FastAPI for the modern Python web framework
- React and the ecosystem for the frontend framework
- pywebview for seamless desktop integration
