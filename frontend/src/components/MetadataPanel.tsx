import React, { useState } from 'react';
import { 
  ChevronDownIcon, 
  ChevronRightIcon,
  InformationCircleIcon,
  PhotoIcon,
  CogIcon,
  CameraIcon
} from '@heroicons/react/24/outline';
import { MetadataResponse } from '../types';

interface MetadataPanelProps {
  metadata: MetadataResponse | null;
  isLoading: boolean;
}

interface MetadataSectionProps {
  title: string;
  icon: React.ComponentType<{ className?: string }>;
  children: React.ReactNode;
  defaultExpanded?: boolean;
}

const MetadataSection: React.FC<MetadataSectionProps> = ({ 
  title, 
  icon: Icon, 
  children, 
  defaultExpanded = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className="border-b border-gray-700 last:border-b-0">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-3 hover:bg-gray-700 transition-colors"
      >
        <div className="flex items-center space-x-2">
          <Icon className="w-5 h-5 text-gray-400" />
          <span className="font-medium text-gray-300">{title}</span>
        </div>
        {isExpanded ? (
          <ChevronDownIcon className="w-4 h-4 text-gray-400" />
        ) : (
          <ChevronRightIcon className="w-4 h-4 text-gray-400" />
        )}
      </button>
      
      {isExpanded && (
        <div className="px-3 pb-3">
          {children}
        </div>
      )}
    </div>
  );
};

const MetadataField: React.FC<{ label: string; value: any }> = ({ label, value }) => {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  return (
    <div className="mb-2">
      <div className="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">
        {label}
      </div>
      <div className="text-sm text-gray-300 font-mono break-all">
        {typeof value === 'string' && value.length > 50 
          ? `${value.substring(0, 50)}...` 
          : String(value)
        }
      </div>
    </div>
  );
};

export const MetadataPanel: React.FC<MetadataPanelProps> = ({ metadata, isLoading }) => {
  if (isLoading) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-exr-accent mx-auto mb-2"></div>
          <div className="text-sm text-gray-400">Loading metadata...</div>
        </div>
      </div>
    );
  }

  if (!metadata) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <InformationCircleIcon className="w-12 h-12 mx-auto mb-2 opacity-50" />
          <div>No metadata available</div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white mb-2">Image Metadata</h2>
        <p className="text-sm text-gray-400">
          EXR file information and properties
        </p>
      </div>

      {/* Metadata Content */}
      <div className="flex-1 overflow-y-auto">
        {/* Basic Information */}
        <MetadataSection title="Basic Information" icon={InformationCircleIcon} defaultExpanded={true}>
          <MetadataField label="Channels" value={metadata.channels.join(', ')} />
          <MetadataField label="Data Window" value={metadata.data_window} />
          <MetadataField label="Display Window" value={metadata.display_window} />
          <MetadataField label="Pixel Aspect Ratio" value={metadata.pixel_aspect_ratio} />
          <MetadataField label="Line Order" value={metadata.line_order} />
          <MetadataField label="Compression" value={metadata.compression} />
        </MetadataSection>

        {/* Channel Information */}
        <MetadataSection title="Channel Details" icon={PhotoIcon}>
          {Object.entries(metadata.channel_info).map(([channelName, info]) => (
            <div key={channelName} className="mb-3 p-2 bg-gray-700 rounded">
              <div className="text-sm font-medium text-gray-300 mb-1">
                {channelName}
              </div>
              <div className="text-xs text-gray-400 space-y-1">
                <div>Type: {info.type}</div>
                <div>X Sampling: {info.xSampling}</div>
                <div>Y Sampling: {info.ySampling}</div>
              </div>
            </div>
          ))}
        </MetadataSection>

        {/* Color Information */}
        <MetadataSection title="Color Information" icon={PhotoIcon}>
          <MetadataField label="Screen Window Center" value={metadata.screen_window_center} />
          <MetadataField label="Screen Window Width" value={metadata.screen_window_width} />
          <MetadataField label="Chromaticities" value={metadata.chromaticities} />
          <MetadataField label="White Point" value={metadata.white_point} />
          <MetadataField label="Primaries" value={metadata.primaries} />
          <MetadataField label="White Luminance" value={metadata.white_luminance} />
          <MetadataField label="ACES Container Flag" value={metadata.aces_image_container_flag} />
        </MetadataSection>

        {/* Technical Information */}
        <MetadataSection title="Technical Details" icon={CogIcon}>
          <MetadataField label="Chunk Count" value={metadata.chunk_count} />
          <MetadataField label="Tiles" value={metadata.tiles} />
          <MetadataField label="Environment Map" value={metadata.envmap} />
          <MetadataField label="Deep Image State" value={metadata.deep_image_state} />
          <MetadataField label="Multi Part" value={metadata.multi_part} />
          <MetadataField label="Version" value={metadata.version} />
          <MetadataField label="Type" value={metadata.type} />
        </MetadataSection>

        {/* Camera Information */}
        <MetadataSection title="Camera Data" icon={CameraIcon}>
          <MetadataField label="World to Camera" value={metadata.world_to_camera} />
          <MetadataField label="World to NDC" value={metadata.world_to_ndc} />
          <MetadataField label="Focus" value={metadata.focus} />
          <MetadataField label="Exposure Time" value={metadata.exp_time} />
          <MetadataField label="Aperture" value={metadata.aperture} />
          <MetadataField label="ISO Speed" value={metadata.iso_speed} />
          <MetadataField label="Key Code" value={metadata.key_code} />
          <MetadataField label="Time Code" value={metadata.time_code} />
        </MetadataSection>

        {/* Location Information */}
        <MetadataSection title="Location Data" icon={CameraIcon}>
          <MetadataField label="Longitude" value={metadata.longitude} />
          <MetadataField label="Latitude" value={metadata.latitude} />
          <MetadataField label="Altitude" value={metadata.altitude} />
          <MetadataField label="Capture Date" value={metadata.cap_date} />
          <MetadataField label="UTC Offset" value={metadata.utc_offset} />
        </MetadataSection>

        {/* Rendering Information */}
        <MetadataSection title="Rendering" icon={CogIcon}>
          <MetadataField label="Rendering Transform" value={metadata.rendering_transform} />
          <MetadataField label="Look Modification Transform" value={metadata.look_mod_transform} />
          <MetadataField label="Adopted Neutral" value={metadata.adopted_neutral} />
          <MetadataField label="Multi View" value={metadata.multi_view} />
          <MetadataField label="View" value={metadata.view} />
        </MetadataSection>

        {/* File Information */}
        <MetadataSection title="File Details" icon={InformationCircleIcon}>
          <MetadataField label="Name" value={metadata.name} />
          <MetadataField label="Owner" value={metadata.owner} />
          <MetadataField label="Comments" value={metadata.comments} />
          <MetadataField label="Frames Per Second" value={metadata.frames_per_second} />
          <MetadataField label="Wrap Modes" value={metadata.wrapmodes} />
        </MetadataSection>
      </div>

      {/* Footer */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <div className="text-xs text-gray-500 text-center">
          {metadata.channels.length} channels • {Object.keys(metadata.channel_info).length} active
        </div>
      </div>
    </div>
  );
};
