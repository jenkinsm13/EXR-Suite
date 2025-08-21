import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { 
  SunIcon, 
  AdjustmentsHorizontalIcon, 
  SparklesIcon,
  SwatchIcon,
  EyeIcon
} from '@heroicons/react/24/outline';
import { apiClient } from '../utils/api';
import type { ImageAdjustments } from '../types';

interface EditingInterfaceProps {
  filePath: string;
  adjustments: ImageAdjustments;
  onAdjustmentChange: (adjustments: ImageAdjustments) => void;
  onSave: (saveAsNew: boolean) => void;
}

interface AdjustmentPreset {
  id: string;
  name: string;
  description: string;
  adjustments: ImageAdjustments;
}

export const EditingInterface: React.FC<EditingInterfaceProps> = ({
  adjustments,
  onAdjustmentChange,
  onSave
}) => {
  const [localAdjustments, setLocalAdjustments] = useState<ImageAdjustments>(adjustments);

  // Fetch adjustment presets
  const { data: presets = [] } = useQuery<AdjustmentPreset[]>({
    queryKey: ['adjustment-presets'],
    queryFn: () => apiClient.getAdjustmentPresets(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });

  // Update local adjustments when props change
  useEffect(() => {
    setLocalAdjustments(adjustments);
  }, [adjustments]);

  // Apply adjustments to parent after a short delay
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onAdjustmentChange(localAdjustments);
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [localAdjustments, onAdjustmentChange]);

  const handleAdjustmentChange = (key: keyof ImageAdjustments, value: number | string | undefined) => {
    setLocalAdjustments(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handlePresetApply = (preset: AdjustmentPreset) => {
    setLocalAdjustments(preset.adjustments);
    toast.success(`Applied preset: ${preset.name}`);
  };

  const handleReset = () => {
    const defaultAdjustments: ImageAdjustments = {
      exposure: 0,
      contrast: 1,
      brightness: 0,
      saturation: 1,
      red_scale: 1,
      green_scale: 1,
      blue_scale: 1,
      tone_mapping: undefined,
    };
    setLocalAdjustments(defaultAdjustments);
    toast.success('Adjustments reset to default');
  };

  const createSlider = (
    key: keyof ImageAdjustments,
    label: string,
    min: number,
    max: number,
    step: number,
    icon: React.ComponentType<{ className?: string }>,
    unit?: string
  ) => {
    const Icon = icon;
    const value = localAdjustments[key] as number;
    
    return (
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <Icon className="w-4 h-4 text-gray-400" />
            <span className="text-sm font-medium text-gray-300">{label}</span>
          </div>
          <span className="text-sm text-gray-400 font-mono">
            {value}{unit}
          </span>
        </div>
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => handleAdjustmentChange(key, parseFloat(e.target.value))}
          className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{min}{unit}</span>
          <span>{max}{unit}</span>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-700 pb-4">
        <h2 className="text-lg font-semibold text-white mb-2">Image Adjustments</h2>
        <p className="text-sm text-gray-400">
          Make precise adjustments to your EXR image
        </p>
      </div>

      {/* Adjustment Presets */}
      {presets.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-sm font-medium text-gray-300 flex items-center space-x-2">
            <SparklesIcon className="w-4 h-4" />
            <span>Presets</span>
          </h3>
          <div className="grid grid-cols-2 gap-2">
            {presets.map((preset) => (
              <button
                key={preset.id}
                onClick={() => handlePresetApply(preset)}
                className="p-2 text-xs bg-gray-700 hover:bg-gray-600 rounded text-gray-300 hover:text-white transition-colors"
                title={preset.description}
              >
                {preset.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Basic Adjustments */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-300 flex items-center space-x-2">
          <AdjustmentsHorizontalIcon className="w-4 h-4" />
          <span>Basic Adjustments</span>
        </h3>
        
        {createSlider('exposure', 'Exposure', -5, 5, 0.1, SunIcon, ' EV')}
        {createSlider('contrast', 'Contrast', 0.1, 3, 0.1, AdjustmentsHorizontalIcon)}
        {createSlider('brightness', 'Brightness', -2, 2, 0.1, SunIcon)}
        {createSlider('saturation', 'Saturation', 0, 3, 0.1, SwatchIcon)}
      </div>

      {/* Color Adjustments */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-300 flex items-center space-x-2">
          <SwatchIcon className="w-4 h-4" />
          <span>Color Adjustments</span>
        </h3>
        
        {createSlider('red_scale', 'Red Scale', 0, 3, 0.1, SwatchIcon)}
        {createSlider('green_scale', 'Green Scale', 0, 3, 0.1, SwatchIcon)}
        {createSlider('blue_scale', 'Blue Scale', 0, 3, 0.1, SwatchIcon)}
      </div>

      {/* Tone Mapping */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-300 flex items-center space-x-2">
          <EyeIcon className="w-4 h-4" />
          <span>Tone Mapping</span>
        </h3>
        
        <select
          value={localAdjustments.tone_mapping || ''}
          onChange={(e) => handleAdjustmentChange('tone_mapping', e.target.value || undefined)}
          className="w-full p-2 bg-gray-700 border border-gray-600 rounded text-gray-300 focus:border-exr-accent focus:outline-none"
        >
          <option value="">None (Linear)</option>
          <option value="reinhard">Reinhard</option>
          <option value="gamma">Gamma Correction</option>
          <option value="aces">ACES</option>
        </select>
      </div>

      {/* Actions */}
      <div className="space-y-3 pt-4 border-t border-gray-700">
        <button
          onClick={handleReset}
          className="w-full px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-md transition-colors"
        >
          Reset All
        </button>
        
        <div className="grid grid-cols-2 gap-2">
          <button
            onClick={() => onSave(false)}
            className="px-4 py-2 bg-exr-accent hover:bg-exr-accent-dark text-white rounded-md transition-colors"
          >
            Save
          </button>
          <button
            onClick={() => onSave(true)}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-md transition-colors"
          >
            Save As
          </button>
        </div>
      </div>
    </div>
  );
};
