import React from 'react';

interface SpellCheckProps {
  suggestion: string;
  onClickSuggestion: (suggestion: string) => void;
}

export function SpellCheck({ suggestion, onClickSuggestion }: SpellCheckProps) {
  if (!suggestion) return null;
  return (
    <div className="mb-4 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-900 text-center">
      <p className="text-blue-800 dark:text-blue-200">
        Did you mean:{" "}
        <button 
          onClick={() => onClickSuggestion(suggestion)}
          className="font-bold hover:underline cursor-pointer ml-1"
        >
          {suggestion}
        </button>
      </p>
    </div>
  );
}