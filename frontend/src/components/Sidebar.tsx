import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  FolderIcon, 
  PhotoIcon, 
  InformationCircleIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { useAppStore } from '../stores/appStore';

export const Sidebar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isCollapsed, activeSection, toggleCollapsed, setActiveSection } = useAppStore();

  const menuItems = [
    {
      id: 'library',
      label: 'Library',
      icon: FolderIcon,
      path: '/',
    },
    {
      id: 'editing',
      label: 'Editing',
      icon: PhotoIcon,
      path: '/edit',
    },
    {
      id: 'metadata',
      label: 'Metadata',
      icon: InformationCircleIcon,
      path: '/metadata',
    },
  ];

  const handleItemClick = (item: typeof menuItems[0]) => {
    setActiveSection(item.id as any);
    if (item.path !== location.pathname) {
      navigate(item.path);
    }
  };

  return (
    <div className={`bg-gray-900 border-r border-gray-700 transition-all duration-300 ${
      isCollapsed ? 'w-16' : 'w-64'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-700">
        {!isCollapsed && (
          <h1 className="text-lg font-semibold text-white">EXR Suite</h1>
        )}
        <button
          onClick={toggleCollapsed}
          className="p-2 rounded-lg hover:bg-gray-700 transition-colors"
        >
          {isCollapsed ? (
            <ChevronRightIcon className="w-5 h-5 text-gray-400" />
          ) : (
            <ChevronLeftIcon className="w-5 h-5 text-gray-400" />
          )}
        </button>
      </div>

      {/* Navigation Menu */}
      <nav className="mt-6">
        <ul className="space-y-2 px-3">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeSection === item.id || 
              (item.id === 'library' && location.pathname === '/') ||
              (item.id === 'editing' && location.pathname.startsWith('/edit')) ||
              (item.id === 'metadata' && location.pathname.startsWith('/metadata'));

            return (
              <li key={item.id}>
                <button
                  onClick={() => handleItemClick(item)}
                  className={`w-full flex items-center px-3 py-2 rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-exr-accent text-white'
                      : 'text-gray-300 hover:text-white hover:bg-gray-700'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  {!isCollapsed && (
                    <span className="ml-3 font-medium">{item.label}</span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* Footer */}
      {!isCollapsed && (
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-700">
          <div className="text-xs text-gray-500 text-center">
            EXR Editing Suite v1.0.0
          </div>
        </div>
      )}
    </div>
  );
};
