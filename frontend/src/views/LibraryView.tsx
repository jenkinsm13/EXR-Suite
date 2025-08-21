import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  FolderIcon, 
  PhotoIcon, 
  DocumentIcon,
  ArrowUpIcon,
  MagnifyingGlassIcon,
  FolderOpenIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../utils/api';
import { DirectoryItem } from '../types';
import { useAppStore, useCurrentDirectory, useSelectedFiles } from '../stores/appStore';

// Thumbnail component for EXR files
const Thumbnail: React.FC<{ filePath: string; size?: number }> = ({ filePath, size = 200 }) => {
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  React.useEffect(() => {
    let isMounted = true;
    
    const loadThumbnail = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Use a timeout to prevent blocking the UI
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 5000)
        );
        
        const thumbnailPromise = apiClient.getThumbnail(filePath, size);
        
        const url = await Promise.race([thumbnailPromise, timeoutPromise]) as string;
        
        if (isMounted) {
          setImageUrl(url);
          setIsLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message);
          setIsLoading(false);
        }
      }
    };

    // Load thumbnail in background
    loadThumbnail();

    return () => {
      isMounted = false;
    };
  }, [filePath, size]);

  // Cleanup on unmount
  React.useEffect(() => {
    return () => {
      if (imageUrl && imageUrl.startsWith('blob:')) {
        URL.revokeObjectURL(imageUrl);
      }
    };
  }, [imageUrl]);

  if (isLoading) {
    return (
      <div className="w-16 h-16 bg-gray-700 rounded-lg flex items-center justify-center">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-exr-accent"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="w-16 h-16 bg-gray-700 rounded-lg flex items-center justify-center">
        <PhotoIcon className="w-8 h-8 text-gray-400" />
      </div>
    );
  }

  return (
    <img
      src={imageUrl!}
      alt="Thumbnail"
      className="w-16 h-16 object-cover rounded-lg"
      onError={() => setError('Failed to load thumbnail')}
    />
  );
};

export const LibraryView: React.FC = () => {
  const navigate = useNavigate();
  const currentDirectory = useCurrentDirectory();
  const selectedFiles = useSelectedFiles();
  const { setCurrentDirectory, setSelectedFiles, selectFile, deselectFile, clearSelection } = useAppStore();
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch directory listing
  const { data: directoryListing, isLoading, error, refetch } = useQuery({
    queryKey: ['directory', currentDirectory],
    queryFn: () => apiClient.listDirectory(currentDirectory),
    enabled: !!currentDirectory,
  });

  const handleSelectDirectory = async () => {
    try {
      const response = await apiClient.selectDirectory();
      setCurrentDirectory(response.current_path);
      clearSelection();
      toast.success(`Selected directory: ${response.current_path}`);
    } catch (error: any) {
      if (error.message.includes('No directory selected')) {
        // User cancelled the dialog, don't show error
        return;
      }
      toast.error(`Failed to select directory: ${error.message}`);
    }
  };

  const handleFileDoubleClick = (item: DirectoryItem) => {
    if (item.is_dir) {
      // Navigate to directory
      apiClient.navigateToDirectory(item.path).then((response) => {
        setCurrentDirectory(response.current_path);
        clearSelection();
      }).catch((error) => {
        toast.error(`Failed to navigate to directory: ${error.message}`);
      });
    } else if (item.is_exr) {
      // Open EXR file for editing
      navigate(`/edit/${encodeURIComponent(item.path)}`);
    } else {
      toast.error('Only EXR files can be opened for editing');
    }
  };

  const handleFileClick = (item: DirectoryItem, event: React.MouseEvent) => {
    if (event.ctrlKey || event.metaKey) {
      // Multi-select
      if (selectedFiles.includes(item.path)) {
        deselectFile(item.path);
      } else {
        selectFile(item.path);
      }
    } else {
      // Single select
      setSelectedFiles([item.path]);
    }
  };

  const handleParentDirectory = () => {
    apiClient.getParentDirectory().then((response) => {
      setCurrentDirectory(response.current_path);
      clearSelection();
    }).catch((error) => {
      toast.error(`Failed to navigate to parent directory: ${error.message}`);
    });
  };

  const handleSearch = () => {
    if (searchQuery.trim()) {
      apiClient.searchFiles(searchQuery, currentDirectory).then((results) => {
        // For now, just show results in a toast
        toast.success(`Found ${results.total_results} files matching "${searchQuery}"`);
      }).catch((error) => {
        toast.error(`Search failed: ${error.message}`);
      });
    }
  };

  const getFileIcon = (item: DirectoryItem) => {
    if (item.is_dir) {
      return <FolderIcon className="w-8 h-8 text-blue-400" />;
    } else if (item.is_exr) {
      return <PhotoIcon className="w-8 h-8 text-green-400" />;
    } else {
      return <DocumentIcon className="w-8 h-8 text-gray-400" />;
    }
  };

  const formatFileSize = (size: number) => {
    if (size === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(size) / Math.log(k));
    return parseFloat((size / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  // Show directory selection prompt if no directory is selected
  if (!currentDirectory) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-900">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="mb-8">
            <FolderOpenIcon className="w-24 h-24 text-gray-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-white mb-2">Welcome to EXR Editing Suite</h1>
            <p className="text-gray-400 mb-8">
              Select a directory to browse and edit your EXR files
            </p>
          </div>
          
          <button
            onClick={handleSelectDirectory}
            className="btn-primary text-lg px-8 py-4 flex items-center justify-center mx-auto space-x-2"
          >
            <FolderOpenIcon className="w-6 h-6" />
            <span>Select Directory</span>
          </button>
          
          <p className="text-sm text-gray-500 mt-4">
            You can also use the "Select Directory" button in the toolbar once a directory is open
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">Error loading directory</div>
          <div className="text-gray-400 mb-4">{error.message}</div>
          <div className="space-x-4">
            <button
              onClick={() => refetch()}
              className="btn-primary"
            >
              Retry
            </button>
            <button
              onClick={handleSelectDirectory}
              className="btn-secondary"
            >
              Select Different Directory
            </button>
          </div>
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
              onClick={handleParentDirectory}
              className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
              title="Go to parent directory"
            >
              <ArrowUpIcon className="w-5 h-5 text-gray-400" />
            </button>
            <button
              onClick={handleSelectDirectory}
              className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
              title="Select directory"
            >
              <FolderOpenIcon className="w-5 h-5 text-gray-400" />
            </button>
            <div className="text-sm text-gray-400">
              Current: <span className="text-white font-mono">{currentDirectory}</span>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <div className="relative">
              <input
                type="text"
                placeholder="Search files..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                className="input-field pl-10 pr-4 py-2 w-64"
              />
              <MagnifyingGlassIcon className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
            </div>
            <button
              onClick={handleSearch}
              className="btn-primary"
            >
              Search
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-exr-accent mx-auto mb-4"></div>
              <div className="text-gray-400">Loading directory...</div>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 2xl:grid-cols-6 gap-4">
            {directoryListing?.items.map((item) => (
              <div
                key={item.path}
                onClick={(e) => handleFileClick(item, e)}
                onDoubleClick={() => handleFileDoubleClick(item)}
                className={`card cursor-pointer transition-all duration-200 hover:scale-105 ${
                  selectedFiles.includes(item.path)
                    ? 'ring-2 ring-exr-accent bg-gray-700'
                    : 'hover:bg-gray-700'
                }`}
              >
                <div className="flex flex-col items-center text-center">
                  {item.is_exr ? (
                    <Thumbnail filePath={item.path} />
                  ) : (
                    getFileIcon(item)
                  )}
                  <div className="mt-3 text-sm font-medium text-white truncate w-full">
                    {item.name}
                  </div>
                  <div className="mt-1 text-xs text-gray-400">
                    {item.is_file ? formatFileSize(item.size) : 'Directory'}
                  </div>
                  {item.modified && (
                    <div className="mt-1 text-xs text-gray-500">
                      {new Date(item.modified).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="bg-gray-800 border-t border-gray-700 p-4">
        <div className="flex items-center justify-between text-sm text-gray-400">
          <div>
            {directoryListing && (
              <>
                {directoryListing.directory_count} directories, {directoryListing.file_count} files
                {directoryListing.exr_count > 0 && ` (${directoryListing.exr_count} EXR files)`}
              </>
            )}
          </div>
          <div>
            {directoryListing && `Total size: ${formatFileSize(directoryListing.total_size)}`}
          </div>
        </div>
      </div>
    </div>
  );
};
