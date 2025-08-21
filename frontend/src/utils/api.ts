import { 
  DirectoryListing, 
  FileInfo, 
  NavigationResponse, 
  SearchResponse, 
  DriveInfo,
  ImageAdjustments,
  ImageStats,
  MetadataResponse,
  SaveRequest,
  SuccessResponse,
  ApiClient
} from '../types';

// Use relative URLs so it works with any port
const API_BASE_URL = '/api';

class ApiClientImpl implements ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Files API
  async listDirectory(path?: string): Promise<DirectoryListing> {
    const params = path ? `?path=${encodeURIComponent(path)}` : '';
    return this.request<DirectoryListing>(`/files/directory${params}`);
  }

  async getFileInfo(filePath: string): Promise<FileInfo> {
    const params = `?file_path=${encodeURIComponent(filePath)}`;
    return this.request<FileInfo>(`/files/file-info${params}`);
  }

  async navigateToDirectory(path: string): Promise<NavigationResponse> {
    return this.request<NavigationResponse>('/files/navigate', {
      method: 'POST',
      body: JSON.stringify({ path }),
    });
  }

  async getParentDirectory(): Promise<NavigationResponse> {
    return this.request<NavigationResponse>('/files/parent');
  }

  async searchFiles(query: string, directory?: string): Promise<SearchResponse> {
    return this.request<SearchResponse>('/files/search', {
      method: 'POST',
      body: JSON.stringify({ query, directory, recursive: true }),
    });
  }

  async getDriveLetters(): Promise<DriveInfo> {
    return this.request<DriveInfo>('/files/drives');
  }

  async selectDirectory(): Promise<NavigationResponse> {
    return this.request<NavigationResponse>('/files/select-directory', {
      method: 'POST',
    });
  }

  // Images API
  async getThumbnail(filePath: string, size: number = 200): Promise<string> {
    const params = `?size=${size}&format=PNG`;
    const response = await fetch(`${API_BASE_URL}/images/thumbnail/${encodeURIComponent(filePath)}${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }

  async getPreview(filePath: string, format: string = 'PNG'): Promise<string> {
    const params = `?format=${format}`;
    const response = await fetch(`${API_BASE_URL}/images/preview/${encodeURIComponent(filePath)}${params}`);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }

  async getPreviewWithAdjustments(filePath: string, adjustments: ImageAdjustments): Promise<string> {
    const response = await fetch(`${API_BASE_URL}/images/preview-with-adjustments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_path: filePath,
        adjustments,
        format: 'PNG',
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const blob = await response.blob();
    return URL.createObjectURL(blob);
  }

  async getImageStats(filePath: string): Promise<ImageStats> {
    return this.request<ImageStats>(`/images/stats/${encodeURIComponent(filePath)}`);
  }

  // Metadata API
  async getMetadata(filePath: string): Promise<MetadataResponse> {
    return this.request<MetadataResponse>(`/metadata/${encodeURIComponent(filePath)}`);
  }

  async getMetadataSummary(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/summary/${encodeURIComponent(filePath)}`);
  }

  async getChannelMetadata(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/channels/${encodeURIComponent(filePath)}`);
  }

  async getTechnicalMetadata(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/technical/${encodeURIComponent(filePath)}`);
  }

  async getColorMetadata(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/color/${encodeURIComponent(filePath)}`);
  }

  async getCameraMetadata(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/camera/${encodeURIComponent(filePath)}`);
  }

  async getRawMetadata(filePath: string): Promise<any> {
    return this.request<any>(`/metadata/raw/${encodeURIComponent(filePath)}`);
  }

  // Editing API
  async applyAdjustments(filePath: string, adjustments: ImageAdjustments): Promise<ImageStats> {
    return this.request<ImageStats>('/editing/adjust', {
      method: 'POST',
      body: JSON.stringify({
        file_path: filePath,
        adjustments,
      }),
    });
  }

  async saveImage(request: SaveRequest): Promise<SuccessResponse> {
    return this.request<SuccessResponse>('/editing/save', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async saveWithAdjustments(
    filePath: string, 
    adjustments: ImageAdjustments, 
    saveAsNew: boolean, 
    newFilename?: string
  ): Promise<SuccessResponse> {
    return this.request<SuccessResponse>('/editing/save-with-adjustments', {
      method: 'POST',
      body: JSON.stringify({
        file_path: filePath,
        adjustments,
        save_as_new: saveAsNew,
        new_filename: newFilename,
      }),
    });
  }

  async getAdjustmentPresets(): Promise<Array<{id: string; name: string; description: string; adjustments: ImageAdjustments}>> {
    return this.request<Array<{id: string; name: string; description: string; adjustments: ImageAdjustments}>>('/editing/adjustment-presets');
  }

  // Utility methods
  async getPreviewUrl(filePath: string, adjustments?: ImageAdjustments): Promise<string> {
    if (adjustments) {
      return this.getPreviewWithAdjustments(filePath, adjustments);
    }
    return this.getPreview(filePath);
  }

  async getThumbnailUrl(filePath: string, size: number = 200): Promise<string> {
    return this.getThumbnail(filePath, size);
  }
}

// Export singleton instance
export const apiClient = new ApiClientImpl();

// Export the class for testing
export { ApiClientImpl };
