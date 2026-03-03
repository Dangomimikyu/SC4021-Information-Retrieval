interface SuggestionPillsProps {
  suggestions: string[];
  onSuggestionClick: (suggestion: string) => void;
}

export function SuggestionPills({ suggestions, onSuggestionClick }: SuggestionPillsProps) {
  return (
    <div className="w-full max-w-3xl mx-auto mt-4">
      <div className="text-sm text-gray-600 mb-2">Try:</div>
      <div className="flex flex-wrap gap-2">
        {suggestions.map((suggestion, index) => (
          <button
            key={index}
            onClick={() => onSuggestionClick(suggestion)}
            className="px-4 py-2 bg-black text-white text-sm rounded-full hover:bg-gray-800 transition-colors"
          >
            {suggestion}
          </button>
        ))}
      </div>
    </div>
  );
}
