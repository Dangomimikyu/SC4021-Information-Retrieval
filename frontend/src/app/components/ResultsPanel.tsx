import { BarChart3 } from 'lucide-react';
import { CommentCard, Comment } from './CommentCard';

interface ResultsPanelProps {
  comments: Comment[];
  searchQuery: string;
  showStats: boolean;
  onToggleStats: () => void;
}

export function ResultsPanel({ comments, searchQuery, showStats, onToggleStats }: ResultsPanelProps) {
  return (
    <div className="w-full max-w-6xl mx-auto mt-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">
            Search Results for: <span className="text-blue-600">{searchQuery || '*:*'}</span>
          </h2>
          {comments.length === 0 ? (
            <div className="mt-2">
              <p className="text-red-600">Error: Failed to fetch data.</p>
              <p className="text-gray-500">No results found</p>
            </div>
          ) : (
            <p className="text-gray-600 mt-1">{comments.length} comments found</p>
          )}
        </div>
        <button
          onClick={onToggleStats}
          className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <BarChart3 className="w-4 h-4" />
          <span>{showStats ? 'Hide' : 'Show'} Plots</span>
        </button>
      </div>

      {comments.length > 0 && (
        <div className="space-y-4">
          {comments.map((comment) => (
            <CommentCard key={comment.id} comment={comment} />
          ))}
        </div>
      )}
    </div>
  );
}
