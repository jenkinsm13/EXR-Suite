import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  ArrowLeftIcon,
  InformationCircleIcon,
  DocumentArrowDownIcon,
  DocumentArrowUpIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../utils/api';
import type { ImageAdjustments } from '../types';
import { useAppStore } from '../stores/appStore';
import { EditingInterface } from '../components/EditingInterface';
import { ImagePreview } from '../components/ImagePreview';
import { MetadataPanel } from '../components/MetadataPanel';

export const EditingView: React.FC = () => {
  const { filePath } = useParams<{ filePath: string }>();
  const navigate = useNavigate();
  const { 
    adjustments,
    metadata,
    setEditingFile, 
    setAdjustments, 
    setMetadata, 
    setError 
  } = useAppStore();

  const [isSaving, setIsSaving] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);

  // Decode the file path from URL
  const decodedFilePath = filePath ? decodeURIComponent(filePath) : '';

  // Set editing file when component mounts
  useEffect(() => {
    if (decodedFilePath) {
      setEditingFile(decodedFilePath);
    }
    return () => {
      setEditingFile(null);
    };
  }, [decodedFilePath, setEditingFile]);

  // Fetch metadata
  const { data: metadataData, isLoading: metadataLoading, error: metadataError } = useQuery({
    queryKey: ['metadata', decodedFilePath],
    queryFn: () => apiClient.getMetadata(decodedFilePath),
    enabled: !!decodedFilePath,
  });

  // Update metadata in store when data changes
  useEffect(() => {
    if (metadataData) {
      setMetadata(metadataData);
    }
  }, [metadataData, setMetadata]);

  // Handle metadata errors
  useEffect(() => {
    if (metadataError) {
      toast.error(`Failed to load metadata: ${metadataError.message}`);
      setError(metadataError.message);
    }
  }, [metadataError, setError]);

  const handleAdjustmentChange = (newAdjustments: ImageAdjustments) => {
    setAdjustments(newAdjustments);
  };

  const handleSave = async (saveAsNew: boolean) => {
    if (!decodedFilePath) return;

    setIsSaving(true);
    try {
      let newFilename: string | undefined;
      
      if (saveAsNew) {
        const originalName = decodedFilePath.split('\\').pop()?.split('.')[0] || 'edited';
        newFilename = `${originalName}_edited`;
      }

      const response = await apiClient.saveWithAdjustments(
        decodedFilePath,
        adjustments,
        saveAsNew,
        newFilename
      );

      toast.success(response.message);
      
      if (saveAsNew) {
        // Navigate to the new file's directory
        const newFilePath = response.data?.output_path;
        if (newFilePath) {
          const newDir = newFilePath.split('\\').slice(0, -1).join('\\');
          navigate('/', { state: { navigateTo: newDir } });
        }
      }
    } catch (error: any) {
      toast.error(`Failed to save: ${error.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const handleBackToLibrary = () => {
    navigate('/');
  };

  const handleResetAdjustments = () => {
    setAdjustments({
      exposure: 0,
      contrast: 1,
      brightness: 0,
      saturation: 1,
      red_scale: 1,
      green_scale: 1,
      blue_scale: 1,
      tone_mapping: undefined,
    });
    toast.success('Adjustments reset to default');
  };

  if (!decodedFilePath) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">No file selected</div>
          <button onClick={handleBackToLibrary} className="btn-primary">
            Back to Library
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-gray-900">
      {/* Header */}
      <div className="bg-gray-800 border-b border-gray-700 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={handleBackToLibrary}
              className="flex items-center space-x-2 btn-secondary"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              <span>Back to Library</span>
            </button>
            <div className="text-sm text-gray-400">
              Editing: <span className="text-white font-mono">{decodedFilePath.split('\\').pop()}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => navigate(`/metadata/${encodeURIComponent(decodedFilePath)}`)}
              className="p-2 rounded-lg text-gray-400 hover:bg-gray-700 transition-colors"
              title="View full metadata"
            >
              <InformationCircleIcon className="w-5 h-5" />
            </button>
            <button
              onClick={() => setShowMetadata(!showMetadata)}
              className={`p-2 rounded-lg transition-colors ${
                showMetadata ? 'bg-exr-accent text-white' : 'text-gray-400 hover:bg-gray-700'
              }`}
              title="Toggle metadata panel"
            >
              <InformationCircleIcon className="w-5 h-5" />
            </button>
            <button
              onClick={handleResetAdjustments}
              className="btn-secondary"
              disabled={isSaving}
            >
              Reset
            </button>
            <button
              onClick={() => handleSave(false)}
              disabled={isSaving}
              className="btn-primary"
            >
              <DocumentArrowDownIcon className="w-5 h-5 mr-2" />
              {isSaving ? 'Saving...' : 'Save'}
            </button>
            <button
              onClick={() => handleSave(true)}
              disabled={isSaving}
              className="btn-secondary"
            >
              <DocumentArrowUpIcon className="w-5 h-5 mr-2" />
              Save As
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editing Interface */}
        <div className="w-80 bg-gray-800 border-r border-gray-700 p-4 overflow-y-auto">
          <EditingInterface
            filePath={decodedFilePath}
            adjustments={adjustments}
            onAdjustmentChange={handleAdjustmentChange}
            onSave={handleSave}
          />
        </div>

        {/* Image Preview */}
        <div className="flex-1 flex flex-col">
          <ImagePreview
            filePath={decodedFilePath}
            adjustments={adjustments}
          />
        </div>

        {/* Metadata Panel */}
        {showMetadata && (
          <div className="w-80 bg-gray-800 border-l border-gray-700 p-4 overflow-y-auto">
            <MetadataPanel
              metadata={metadata}
              isLoading={metadataLoading}
            />
          </div>
        )}
      </div>
    </div>
  );
};
