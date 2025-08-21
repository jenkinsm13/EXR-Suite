import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  MagnifyingGlassIcon, 
  MagnifyingGlassMinusIcon,
  MagnifyingGlassPlusIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../utils/api';
import type { ImageAdjustments } from '../types';

interface ImagePreviewProps {
  filePath: string;
  adjustments: ImageAdjustments;
  onImageLoad?: () => void;
}

interface ViewportState {
  scale: number;
  translateX: number;
  translateY: number;
  isDragging: boolean;
  lastMousePos: { x: number; y: number };
}

export const ImagePreview: React.FC<ImagePreviewProps> = ({
  filePath,
  adjustments,
  onImageLoad
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  
  const [viewport, setViewport] = useState<ViewportState>({
    scale: 1,
    translateX: 0,
    translateY: 0,
    isDragging: false,
    lastMousePos: { x: 0, y: 0 }
  });

  const [isLoading, setIsLoading] = useState(false);

  // Fetch image with adjustments
  const { data: imageUrl, error, refetch } = useQuery({
    queryKey: ['preview-with-adjustments', filePath, adjustments],
    queryFn: () => apiClient.getPreviewWithAdjustments(filePath, adjustments),
    enabled: !!filePath,
    staleTime: 30 * 1000, // 30 seconds
  });

  // Handle image load
  const handleImageLoad = useCallback(() => {
    setIsLoading(false);
    onImageLoad?.();
  }, [onImageLoad]);

  // Handle image error
  const handleImageError = useCallback(() => {
    setIsLoading(false);
    toast.error('Failed to load image preview');
  }, []);

  // Reset viewport to fit image
  const resetViewport = useCallback(() => {
    setViewport(prev => ({
      ...prev,
      scale: 1,
      translateX: 0,
      translateY: 0
    }));
  }, []);

  // Zoom in/out
  const handleZoom = useCallback((delta: number) => {
    setViewport(prev => {
      const newScale = Math.max(0.1, Math.min(10, prev.scale + delta));
      return { ...prev, scale: newScale };
    });
  }, []);

  // Handle mouse wheel for zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.2 : 0.2;
    handleZoom(delta);
  }, [handleZoom]);

  // Handle mouse down for panning
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 0) { // Left mouse button
      setViewport(prev => ({
        ...prev,
        isDragging: true,
        lastMousePos: { x: e.clientX, y: e.clientY }
      }));
    }
  }, []);

  // Handle mouse move for panning
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (viewport.isDragging) {
      const deltaX = e.clientX - viewport.lastMousePos.x;
      const deltaY = e.clientY - viewport.lastMousePos.y;
      
      setViewport(prev => ({
        ...prev,
        translateX: prev.translateX + deltaX,
        translateY: prev.translateY + deltaY,
        lastMousePos: { x: e.clientX, y: e.clientY }
      }));
    }
  }, [viewport.isDragging, viewport.lastMousePos]);

  // Handle mouse up to stop panning
  const handleMouseUp = useCallback(() => {
    setViewport(prev => ({ ...prev, isDragging: false }));
  }, []);

  // Handle double click to reset viewport
  const handleDoubleClick = useCallback(() => {
    resetViewport();
  }, [resetViewport]);

  // Update loading state when query changes
  useEffect(() => {
    if (imageUrl) {
      setIsLoading(true);
    }
  }, [imageUrl]);

  // Add global mouse event listeners for panning
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      setViewport(prev => ({ ...prev, isDragging: false }));
    };

    const handleGlobalMouseMove = (e: MouseEvent) => {
      if (viewport.isDragging) {
        const deltaX = e.clientX - viewport.lastMousePos.x;
        const deltaY = e.clientY - viewport.lastMousePos.y;
        
        setViewport(prev => ({
          ...prev,
          translateX: prev.translateX + deltaX,
          translateY: prev.translateY + deltaY,
          lastMousePos: { x: e.clientX, y: e.clientY }
        }));
      }
    };

    if (viewport.isDragging) {
      document.addEventListener('mousemove', handleGlobalMouseMove);
      document.addEventListener('mouseup', handleGlobalMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleGlobalMouseMove);
      document.removeEventListener('mouseup', handleGlobalMouseUp);
    };
  }, [viewport.isDragging, viewport.lastMousePos]);

  // Cleanup image URL when component unmounts
  useEffect(() => {
    return () => {
      if (imageUrl && imageUrl.startsWith('blob:')) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  if (error) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">Failed to load image</div>
          <button 
            onClick={() => refetch()}
            className="px-4 py-2 bg-exr-accent hover:bg-exr-accent-dark text-white rounded-md transition-colors flex items-center space-x-2 mx-auto"
          >
            <ArrowPathIcon className="w-4 h-4" />
            <span>Retry</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between p-3 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => handleZoom(-0.5)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom Out"
          >
            <MagnifyingGlassMinusIcon className="w-4 h-4" />
          </button>
          
          <span className="text-sm text-gray-300 font-mono">
            {Math.round(viewport.scale * 100)}%
          </span>
          
          <button
            onClick={() => handleZoom(0.5)}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
            title="Zoom In"
          >
            <MagnifyingGlassPlusIcon className="w-4 h-4" />
          </button>
        </div>
        
        <button
          onClick={resetViewport}
          className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
          title="Reset View"
        >
          <MagnifyingGlassIcon className="w-4 h-4" />
        </button>
      </div>

      {/* Image Container */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-hidden bg-gray-900 relative"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onDoubleClick={handleDoubleClick}
        style={{ cursor: viewport.isDragging ? 'grabbing' : 'grab' }}
      >
        {imageUrl && (
          <div
            className="absolute inset-0 flex items-center justify-center"
            style={{
              transform: `translate(${viewport.translateX}px, ${viewport.translateY}px) scale(${viewport.scale})`,
              transformOrigin: 'center center',
              transition: viewport.isDragging ? 'none' : 'transform 0.1s ease-out'
            }}
          >
            <img
              ref={imageRef}
              src={imageUrl}
              alt="EXR Preview"
              className="max-w-none select-none"
              onLoad={handleImageLoad}
              onError={handleImageError}
              draggable={false}
            />
          </div>
        )}
        
        {/* Loading Overlay */}
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-75">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-exr-accent mx-auto mb-2"></div>
              <div className="text-sm text-gray-400">Loading preview...</div>
            </div>
          </div>
        )}
        
        {/* No Image State */}
        {!imageUrl && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <div className="text-lg mb-2">No image loaded</div>
              <div className="text-sm">Select an EXR file to preview</div>
            </div>
          </div>
        )}
      </div>

      {/* Status Bar */}
      <div className="p-2 bg-gray-800 border-t border-gray-700 text-xs text-gray-400">
        <div className="flex items-center justify-between">
          <span>
            {filePath ? filePath.split('\\').pop() : 'No file selected'}
          </span>
          <span>
            {viewport.scale !== 1 && (
              <>
                Zoom: {Math.round(viewport.scale * 100)}% • 
                Pan: ({Math.round(viewport.translateX)}, {Math.round(viewport.translateY)})
              </>
            )}
          </span>
        </div>
      </div>
    </div>
  );
};
