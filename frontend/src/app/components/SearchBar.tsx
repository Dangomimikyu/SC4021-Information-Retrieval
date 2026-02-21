import { Search, SlidersHorizontal } from 'lucide-react';

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  showAdvanced: boolean;
  onToggleAdvanced: () => void;
  onSearch: () => void;
}

export function SearchBar({
  searchQuery,
  onSearchChange,
  showAdvanced,
  onToggleAdvanced,
  onSearch,
}: SearchBarProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl mx-auto">
      <div className="flex gap-2 items-center">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Search for teams, players, or sentiment..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black focus:border-transparent"
          />
        </div>
        <button
          type="button"
          onClick={onToggleAdvanced}
          className={`px-4 py-3 border rounded-lg flex items-center gap-2 transition-colors ${
            showAdvanced
              ? 'bg-gray-100 border-gray-400'
              : 'bg-white border-gray-300 hover:bg-gray-50'
          }`}
        >
          <SlidersHorizontal className="w-4 h-4" />
          <span>Advanced</span>
        </button>
        <button
          type="submit"
          className="px-6 py-3 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors"
        >
          Search
        </button>
      </div>
    </form>
  );
}
