# EXR Suite Frontend

This is the React frontend for the EXR Editing Suite, a professional-grade application for editing EXR image files.

## Features

- **Directory Navigation**: Browse and select EXR files from the filesystem
- **Image Library**: Display images in a library view with thumbnails
- **Editing Interface**: Real-time mathematical adjustments (exposure, contrast, color balance, etc.)
- **Metadata Panel**: Display comprehensive EXR metadata
- **Save Functionality**: Save directly to existing files or create new ones
- **Performance**: Fast, responsive, and real-time editing

## Technology Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **Tailwind CSS** for styling
- **Zustand** for state management
- **React Query** for data fetching
- **React Router** for navigation
- **Heroicons** for icons

## Development

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

### Project Structure

```
src/
├── components/     # Reusable UI components
├── views/         # Page-level components
├── stores/        # State management
├── types/         # TypeScript type definitions
├── utils/         # Utility functions
└── hooks/         # Custom React hooks
```

## API Integration

The frontend communicates with the Python FastAPI backend through REST endpoints for:
- File system operations
- Image processing and adjustments
- Metadata extraction
- Image saving

## Styling

Uses Tailwind CSS with custom color scheme optimized for image editing workflows.
