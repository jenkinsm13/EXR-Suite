import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { 
  AppState, 
  ImageAdjustments, 
  MetadataResponse,
  DirectoryListing
} from '../types';

interface AppStore extends AppState {
  // Sidebar state
  isCollapsed: boolean;
  activeSection: 'library' | 'editing' | 'metadata';
  
  // Actions
  setCurrentDirectory: (path: string) => void;
  setSelectedFiles: (files: string[]) => void;
  setEditingFile: (file: string | null) => void;
  setAdjustments: (adjustments: ImageAdjustments) => void;
  updateAdjustment: (key: keyof ImageAdjustments, value: number | string) => void;
  setMetadata: (metadata: MetadataResponse | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  resetAdjustments: () => void;
  
  // Sidebar actions
  toggleCollapsed: () => void;
  setActiveSection: (section: 'library' | 'editing' | 'metadata') => void;
  
  // Directory management
  setDirectoryListing: (listing: DirectoryListing) => void;
  navigateToDirectory: (path: string) => void;
  goToParentDirectory: () => void;
  
  // File selection
  selectFile: (filePath: string) => void;
  deselectFile: (filePath: string) => void;
  clearSelection: () => void;
  
  // Utility
  reset: () => void;
}

const initialAdjustments: ImageAdjustments = {
  exposure: 0,
  contrast: 1,
  brightness: 0,
  saturation: 1,
  red_scale: 1,
  green_scale: 1,
  blue_scale: 1,
  tone_mapping: undefined,
};

const initialState: AppState & { isCollapsed: boolean; activeSection: 'library' | 'editing' | 'metadata' } = {
  currentDirectory: '',
  selectedFiles: [],
  editingFile: null,
  adjustments: initialAdjustments,
  metadata: null,
  isLoading: false,
  error: null,
  isCollapsed: false,
  activeSection: 'library',
};

export const useAppStore = create<AppStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Sidebar actions
      toggleCollapsed: () => {
        set((state) => ({ isCollapsed: !state.isCollapsed }));
      },

      setActiveSection: (section: 'library' | 'editing' | 'metadata') => {
        set({ activeSection: section });
      },

      // Actions
      setCurrentDirectory: (path: string) => {
        set({ currentDirectory: path });
      },

      setSelectedFiles: (files: string[]) => {
        set({ selectedFiles: files });
      },

      setEditingFile: (file: string | null) => {
        set({ editingFile: file });
        if (!file) {
          set({ adjustments: initialAdjustments });
        }
      },

      setAdjustments: (adjustments: ImageAdjustments) => {
        set({ adjustments });
      },

      updateAdjustment: (key: keyof ImageAdjustments, value: number | string) => {
        set((state) => ({
          adjustments: {
            ...state.adjustments,
            [key]: value,
          },
        }));
      },

      setMetadata: (metadata: MetadataResponse | null) => {
        set({ metadata });
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },

      setError: (error: string | null) => {
        set({ error });
      },

      resetAdjustments: () => {
        set({ adjustments: initialAdjustments });
      },

      // Directory management
      setDirectoryListing: (listing: DirectoryListing) => {
        set({ currentDirectory: listing.current_path });
      },

      navigateToDirectory: (path: string) => {
        set({ currentDirectory: path });
      },

      goToParentDirectory: () => {
        const current = get().currentDirectory;
        const parent = current.split('\\').slice(0, -1).join('\\');
        if (parent) {
          set({ currentDirectory: parent });
        }
      },

      // File selection
      selectFile: (filePath: string) => {
        set((state) => ({
          selectedFiles: [...state.selectedFiles, filePath],
        }));
      },

      deselectFile: (filePath: string) => {
        set((state) => ({
          selectedFiles: state.selectedFiles.filter((f) => f !== filePath),
        }));
      },

      clearSelection: () => {
        set({ selectedFiles: [] });
      },

      // Utility
      reset: () => {
        set(initialState);
      },
    }),
    {
      name: 'exr-editing-suite-store',
    }
  )
);

// Selectors for better performance
export const useCurrentDirectory = () => useAppStore((state) => state.currentDirectory);
export const useSelectedFiles = () => useAppStore((state) => state.selectedFiles);
export const useEditingFile = () => useAppStore((state) => state.editingFile);
export const useAdjustments = () => useAppStore((state) => state.adjustments);
export const useMetadata = () => useAppStore((state) => state.metadata);
export const useIsLoading = () => useAppStore((state) => state.isLoading);
export const useError = () => useAppStore((state) => state.error);
export const useIsCollapsed = () => useAppStore((state) => state.isCollapsed);
export const useActiveSection = () => useAppStore((state) => state.activeSection);

// Action selectors
export const useAppActions = () => useAppStore((state) => ({
  setCurrentDirectory: state.setCurrentDirectory,
  setSelectedFiles: state.setSelectedFiles,
  setEditingFile: state.setEditingFile,
  setAdjustments: state.setAdjustments,
  updateAdjustment: state.updateAdjustment,
  setMetadata: state.setMetadata,
  setLoading: state.setLoading,
  setError: state.setError,
  resetAdjustments: state.resetAdjustments,
  toggleCollapsed: state.toggleCollapsed,
  setActiveSection: state.setActiveSection,
  navigateToDirectory: state.navigateToDirectory,
  goToParentDirectory: state.goToParentDirectory,
  selectFile: state.selectFile,
  deselectFile: state.deselectFile,
  clearSelection: state.clearSelection,
  reset: state.reset,
}));
