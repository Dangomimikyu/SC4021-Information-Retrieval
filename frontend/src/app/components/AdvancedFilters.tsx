import { Calendar } from 'lucide-react';

interface AdvancedFiltersProps {
  sentiment: string;
  onSentimentChange: (value: string) => void;
  source: string;
  onSourceChange: (value: string) => void;
  startDate: string;
  onStartDateChange: (value: string) => void;
  endDate: string;
  onEndDateChange: (value: string) => void;
  commentType: string;
  onCommentTypeChange: (value: string) => void;
  subreddits: string[]; 
  aspect: string;
  onAspectChange: (value: string) => void;
  aspectSentiment: string;
  onAspectSentimentChange: (value: string) => void;
}

export function AdvancedFilters({
  sentiment,
  onSentimentChange,
  source,
  onSourceChange,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
  commentType,
  onCommentTypeChange,
  subreddits,
  aspect,
  onAspectChange,
  aspectSentiment,
  onAspectSentimentChange,
}: AdvancedFiltersProps) {
  return (
    <div className="w-full max-w-3xl mx-auto mt-4 bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Overall Sentiment
            </label>
            <select
              value={sentiment}
              onChange={(e) => onSentimentChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose sentiment</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Subject / Aspect
            </label>
            <input
              type="text"
              placeholder="e.g., Haaland, Referee, VAR"
              value={aspect}
              onChange={(e) => onAspectChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subject Sentiment
            </label>
            <select
              value={aspectSentiment}
              onChange={(e) => onAspectSentimentChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose subject sentiment</option>
              <option value="positive">Positive</option>
              <option value="neutral">Neutral</option>
              <option value="negative">Negative</option>
            </select>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source (Subreddit)
            </label>
            <select
              value={source}
              onChange={(e) => onSourceChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose subreddit</option>
              {subreddits.map((sub) => (
                <option key={sub} value={sub}>
                  {sub}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Comment Type
            </label>
            <select
              value={commentType}
              onChange={(e) => onCommentTypeChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose type</option>
              <option value="match">Match Comment</option>
              <option value="player">Player Discussion</option>
              <option value="transfer">Transfer News</option>
              <option value="general">General Discussion</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Date Range
            </label>
            <div className="space-y-2">
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => onStartDateChange(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
                />
              </div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => onEndDateChange(e.target.value)}
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}