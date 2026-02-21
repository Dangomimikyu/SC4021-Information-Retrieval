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
  team: string;
  onTeamChange: (value: string) => void;
  commentType: string;
  onCommentTypeChange: (value: string) => void;
  teams: string[];
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
  team,
  onTeamChange,
  commentType,
  onCommentTypeChange,
  teams,
}: AdvancedFiltersProps) {
  return (
    <div className="w-full max-w-3xl mx-auto mt-4 bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left Column */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Sentiment
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
              Date Range
            </label>
            <div className="space-y-2">
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="date"
                  value={startDate}
                  onChange={(e) => onStartDateChange(e.target.value)}
                  placeholder="Select start date"
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
                />
              </div>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="date"
                  value={endDate}
                  onChange={(e) => onEndDateChange(e.target.value)}
                  placeholder="Select end date"
                  className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
                />
              </div>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Teams
            </label>
            <select
              value={team}
              onChange={(e) => onTeamChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Select team</option>
              {teams.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source
            </label>
            <select
              value={source}
              onChange={(e) => onSourceChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose source</option>
              <option value="twitter">Twitter</option>
              <option value="reddit">Reddit</option>
              <option value="facebook">Facebook</option>
              <option value="instagram">Instagram</option>
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
              Features
            </label>
            <select
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-black text-gray-600"
            >
              <option value="">Choose feature</option>
              <option value="hashtags">Contains Hashtags</option>
              <option value="mentions">Contains Mentions</option>
              <option value="links">Contains Links</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );
}
