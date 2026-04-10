import { Settings, ChevronDown } from 'lucide-react';
import { useState } from 'react';

interface TopBarProps {
  onPreferencesClick: () => void;
  theme: 'light' | 'dark' | 'system';
}

export function TopBar({ onPreferencesClick, theme }: TopBarProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="fixed top-4 right-4 z-30">
      {/* Toggle Button */}
      <button
        onClick={() => setIsMenuOpen(!isMenuOpen)}
        className="w-10 h-10 rounded-full bg-gray-900 dark:bg-gray-700 text-white flex items-center justify-center hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors shadow-lg"
      >
        <span className="text-sm font-bold">N</span>
      </button>

      {/* Dropdown Menu */}
      {isMenuOpen && (
        <>
          <div 
            className="fixed inset-0 z-30"
            onClick={() => setIsMenuOpen(false)}
          />
          <div className="absolute top-12 right-0 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 min-w-[200px] z-40 overflow-hidden">
            <div className="p-2">
              <div className="flex items-center justify-between px-3 py-2 text-sm text-gray-600 dark:text-gray-300">
                <span>Route</span>
                <span className="text-gray-900 dark:text-white font-medium">Static</span>
              </div>
              
              <div className="flex items-center justify-between px-3 py-2 text-sm text-gray-600 dark:text-gray-300">
                <span>Turbopack</span>
                <span className="text-gray-900 dark:text-white font-medium">Enabled</span>
              </div>
              
              <button
                onClick={() => {
                  setIsMenuOpen(false);
                  onPreferencesClick();
                }}
                className="w-full flex items-center justify-between px-3 py-2 text-sm text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
              >
                <span>Preferences</span>
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
