// frontend/src/components/ResultsPanel.tsx
import { BarChart3 } from 'lucide-react';
import { CommentCard, RedditPost } from './CommentCard';

interface ResultsPanelProps {
  posts: RedditPost[]; 
  searchQuery: string;
  showStats: boolean;
  onToggleStats: () => void;
}

export function ResultsPanel({ posts, searchQuery, showStats, onToggleStats }: ResultsPanelProps) {
  return (
    <div className="w-full max-w-6xl mx-auto mt-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold">
            Search Results for: <span className="text-blue-600">{searchQuery || '*:*'}</span>
          </h2>
          {posts.length === 0 ? (
            <p className="text-gray-500 mt-2">No posts found</p>
          ) : (
            <p className="text-gray-600 mt-1">{posts.length} posts analyzed</p>
          )}
        </div>
        <button
          onClick={onToggleStats}
          className="px-4 py-2 bg-black text-white rounded-lg hover:bg-gray-800 transition-colors flex items-center gap-2"
        >
          <BarChart3 className="w-4 h-4" />
          <span>{showStats ? 'Hide' : 'Show'} Statistics</span>
        </button>
      </div>

      <div className="space-y-2">
        {posts.map((post) => (
          <CommentCard key={post.id} post={post} />
        ))}
      </div>
    </div>
  );
}