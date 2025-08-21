import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { ArrowLeftIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { MetadataPanel } from '../components/MetadataPanel';
import { apiClient } from '../utils/api';


export const MetadataView: React.FC = () => {
  const { filePath } = useParams<{ filePath: string }>();
  const navigate = useNavigate();

  
  const [decodedFilePath, setDecodedFilePath] = useState<string>('');

  useEffect(() => {
    if (filePath) {
      setDecodedFilePath(decodeURIComponent(filePath));
    }
  }, [filePath]);

  const { data: metadata, isLoading, error } = useQuery({
    queryKey: ['metadata', decodedFilePath],
    queryFn: () => apiClient.getMetadata(decodedFilePath),
    enabled: !!decodedFilePath,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  useEffect(() => {
    if (error) {
      toast.error('Failed to load metadata');
    }
  }, [error]);

  const handleBackToLibrary = () => {
    navigate('/');
  };

  const handleBackToEditing = () => {
    if (decodedFilePath) {
      navigate(`/editing/${encodeURIComponent(decodedFilePath)}`);
    }
  };

  if (!decodedFilePath) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <DocumentTextIcon className="w-16 h-16 mx-auto mb-4 opacity-50" />
          <div className="text-lg mb-2">No file selected</div>
          <div className="text-sm">Please select an EXR file from the library</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBackToLibrary}
              className="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Library</span>
            </button>
            
            <div className="text-gray-400">/</div>
            
            <button
              onClick={handleBackToEditing}
              className="text-gray-400 hover:text-white transition-colors"
            >
              Editing
            </button>
            
            <div className="text-gray-400">/</div>
            
            <span className="text-white font-medium">Metadata</span>
          </div>
          
          <div className="text-sm text-gray-400">
            {decodedFilePath.split('\\').pop()}
          </div>
        </div>
        
        <div className="mt-2">
          <h1 className="text-xl font-semibold text-white">EXR Metadata</h1>
          <p className="text-sm text-gray-400">
            Complete metadata information for the selected EXR file
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        <div className="h-full p-4">
                     <MetadataPanel 
             metadata={metadata || null} 
             isLoading={isLoading} 
           />
        </div>
      </div>

      {/* Footer Actions */}
      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-400">
            {metadata && (
              <>
                {metadata.channels.length} channels • 
                {Object.keys(metadata.channel_info).length} active channels
              </>
            )}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleBackToEditing}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-md transition-colors"
            >
              Back to Editing
            </button>
            
            <button
              onClick={handleBackToLibrary}
              className="px-4 py-2 bg-exr-accent hover:bg-exr-accent-dark text-white rounded-md transition-colors"
            >
              Back to Library
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
