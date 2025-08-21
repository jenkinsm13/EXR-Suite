// API Response Types
export interface DirectoryItem {
  name: string;
  path: string;
  is_dir: boolean;
  is_file: boolean;
  is_exr: boolean;
  size: number;
  size_human: string;
  modified: string | null;
  extension: string;
}

export interface DirectoryListing {
  current_path: string;
  parent_path: string;
  items: DirectoryItem[];
  directory_count: number;
  file_count: number;
  exr_count: number;
  total_size: number;
}

export interface FileInfo {
  name: string;
  path: string;
  size: number;
  size_human: string;
  modified: string;
  created: string;
  is_exr: boolean;
  extension: string;
  directory: string;
}

export interface ImageAdjustments {
  exposure?: number;
  contrast?: number;
  brightness?: number;
  saturation?: number;
  red_scale?: number;
  green_scale?: number;
  blue_scale?: number;
  tone_mapping?: 'reinhard' | 'gamma' | 'linear';
}

export interface SaveRequest {
  file_path: string;
  save_as_new: boolean;
  new_filename?: string;
}

export interface SuccessResponse {
  message: string;
  data?: any;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  status_code: number;
}

export interface ImageStats {
  file_path: string;
  stats: Record<string, any>;
}

export interface MetadataResponse {
  file_path: string;
  channels: string[];
  data_window: string;
  display_window: string;
  channel_info: Record<string, any>;
  pixel_aspect_ratio?: number;
  screen_window_center?: string;
  screen_window_width?: number;
  line_order?: string;
  compression?: string;
  chunk_count?: number;
  tiles?: string;
  envmap?: string;
  adopted_neutral?: string;
  rendering_transform?: string;
  look_mod_transform?: string;
  white_luminance?: string;
  chromaticities?: string;
  white_point?: string;
  primaries?: string;
  aces_image_container_flag?: string;
  multi_view?: string;
  world_to_camera?: string;
  world_to_ndc?: string;
  deep_image_state?: string;
  tiledesc?: string;
  name?: string;
  type?: string;
  version?: string;
  max_samples_per_pixel?: string;
  dwa_compression_level?: string;
  id_manifest?: string;
  tile_description?: string;
  multi_part?: string;
  view?: string;
  owner?: string;
  comments?: string;
  cap_date?: string;
  utc_offset?: string;
  longitude?: string;
  latitude?: string;
  altitude?: string;
  focus?: string;
  exp_time?: string;
  aperture?: string;
  iso_speed?: string;
  key_code?: string;
  time_code?: string;
  wrapmodes?: string;
  frames_per_second?: string;
}

export interface SearchRequest {
  query: string;
  directory?: string;
  recursive: boolean;
}

export interface SearchResponse {
  query: string;
  results: FileInfo[];
  total_results: number;
  search_directory: string;
}

export interface DriveInfo {
  drives: string[];
  current_drive: string;
}

export interface NavigationRequest {
  path: string;
}

export interface NavigationResponse {
  current_path: string;
  parent_path: string;
  directory_listing: DirectoryListing;
}

// UI State Types
export interface AppState {
  currentDirectory: string;
  selectedFiles: string[];
  editingFile: string | null;
  adjustments: ImageAdjustments;
  metadata: MetadataResponse | null;
  isLoading: boolean;
  error: string | null;
}

export interface SidebarState {
  isCollapsed: boolean;
  activeSection: 'library' | 'editing' | 'metadata';
}

// Component Props Types
export interface FileBrowserProps {
  currentPath: string;
  onPathChange: (path: string) => void;
  onFileSelect: (file: string) => void;
}

export interface ImageLibraryProps {
  files: DirectoryItem[];
  onFileSelect: (file: string) => void;
  onFileDoubleClick: (file: string) => void;
}

export interface EditingInterfaceProps {
  filePath: string;
  adjustments: ImageAdjustments;
  onAdjustmentChange: (adjustments: ImageAdjustments) => void;
  onSave: (saveAsNew: boolean) => void;
}

export interface MetadataPanelProps {
  metadata: MetadataResponse | null;
  isLoading: boolean;
}

export interface ImagePreviewProps {
  filePath: string;
  adjustments: ImageAdjustments;
  onImageLoad?: () => void;
}

// API Client Types
export interface ApiClient {
  listDirectory(path?: string): Promise<DirectoryListing>;
  getFileInfo(filePath: string): Promise<FileInfo>;
  navigateToDirectory(path: string): Promise<NavigationResponse>;
  getParentDirectory(): Promise<NavigationResponse>;
  searchFiles(query: string, directory?: string): Promise<SearchResponse>;
  getDriveLetters(): Promise<DriveInfo>;
  selectDirectory(): Promise<NavigationResponse>;
  getThumbnail: (filePath: string, size?: number) => Promise<string>;
  getPreview: (filePath: string, format?: string) => Promise<string>;
  getPreviewWithAdjustments: (filePath: string, adjustments: ImageAdjustments) => Promise<string>;
  getImageStats: (filePath: string) => Promise<ImageStats>;
  getMetadata: (filePath: string) => Promise<MetadataResponse>;
  getMetadataSummary: (filePath: string) => Promise<any>;
  getChannelMetadata: (filePath: string) => Promise<any>;
  getTechnicalMetadata: (filePath: string) => Promise<any>;
  getColorMetadata: (filePath: string) => Promise<any>;
  getCameraMetadata: (filePath: string) => Promise<any>;
  getRawMetadata: (filePath: string) => Promise<any>;
  applyAdjustments: (filePath: string, adjustments: ImageAdjustments) => Promise<ImageStats>;
  saveImage: (request: SaveRequest) => Promise<SuccessResponse>;
  saveWithAdjustments: (filePath: string, adjustments: ImageAdjustments, saveAsNew: boolean, newFilename?: string) => Promise<SuccessResponse>;
  getAdjustmentPresets: () => Promise<Array<{id: string; name: string; description: string; adjustments: ImageAdjustments}>>;
}
