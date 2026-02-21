import { Settings, Sun, Moon, Monitor, X } from 'lucide-react';

interface PreferencesMenuProps {
  isOpen: boolean;
  onClose: () => void;
  theme: 'light' | 'dark' | 'system';
  onThemeChange: (theme: 'light' | 'dark' | 'system') => void;
}

export function PreferencesMenu({ isOpen, onClose, theme, onThemeChange }: PreferencesMenuProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 z-40"
        onClick={onClose}
      />
      
      {/* Preferences Panel */}
      <div className="fixed top-16 right-4 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-2xl border border-gray-200 dark:border-gray-700 z-50">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
          <h3 className="font-semibold text-lg text-gray-900 dark:text-white">Preferences</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          </button>
        </div>

        <div className="p-4 space-y-6">
          {/* Theme Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Theme
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              Select your theme preference.
            </p>
            
            <div className="space-y-2">
              <button
                onClick={() => onThemeChange('light')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg border transition-all ${
                  theme === 'light'
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 text-blue-900 dark:text-blue-100'
                    : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                <Sun className="w-5 h-5" />
                <span className="font-medium">Light</span>
              </button>

              <button
                onClick={() => onThemeChange('dark')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg border transition-all ${
                  theme === 'dark'
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 text-blue-900 dark:text-blue-100'
                    : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                <Moon className="w-5 h-5" />
                <span className="font-medium">Dark</span>
              </button>

              <button
                onClick={() => onThemeChange('system')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg border transition-all ${
                  theme === 'system'
                    ? 'bg-blue-50 dark:bg-blue-900/30 border-blue-500 text-blue-900 dark:text-blue-100'
                    : 'bg-white dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600'
                }`}
              >
                <Monitor className="w-5 h-5" />
                <span className="font-medium">System</span>
              </button>
            </div>
          </div>

          {/* Position Section */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Position
            </label>
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
              Adjust the placement of your dev tools.
            </p>
            <select
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
              defaultValue="top-right"
            >
              <option value="top-right">Top Right</option>
              <option value="top-left">Top Left</option>
              <option value="bottom-right">Bottom Right</option>
              <option value="bottom-left">Bottom Left</option>
            </select>
          </div>

          {/* Dev Tools Options */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
              Developer Tools
            </label>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">Hide Dev Tools for this session</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    Hide Dev Tools until you restart your dev server, or 1 day.
                  </div>
                </div>
                <button className="px-3 py-1.5 text-sm bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded hover:bg-gray-50 dark:hover:bg-gray-500 transition-colors text-gray-700 dark:text-gray-200">
                  Hide
                </button>
              </div>

              <div className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="text-sm font-medium text-gray-900 dark:text-white mb-1">
                  Disable Dev Tools for this project
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  To disable this UI completely, set <code className="px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-gray-800 dark:text-gray-200">devIndicators: false</code> in your <code className="px-1 py-0.5 bg-gray-200 dark:bg-gray-600 rounded text-gray-800 dark:text-gray-200">next.config</code> file.
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="w-full px-4 py-2 bg-gray-900 dark:bg-gray-700 text-white rounded-lg hover:bg-gray-800 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </>
  );
}
