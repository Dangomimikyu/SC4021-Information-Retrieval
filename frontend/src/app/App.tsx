import { useState, useMemo, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { SpellCheck } from './components/SpellCheck';
import { SuggestionPills } from './components/SuggestionPills';
import { AdvancedFilters } from './components/AdvancedFilters';
import { ResultsPanel } from './components/ResultsPanel';
import { StatsModal } from './components/StatsModal';
import { TopBar } from './components/TopBar';
import { PreferencesMenu } from './components/PreferencesMenu';
import { RedditPost } from './components/CommentCard';

import filterData from '../dataset/filter_options.json';

const suggestions = [
  'Ronaldo performance',
  'Liverpool defense',
  'Champions League',
  'transfer news',
  'Premier League',
];

export default function App() {
  const [searchQuery, setSearchQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  const [suggestion, setSuggestion] = useState('');

  const [sentiment, setSentiment] = useState('');
  const [source, setSource] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [commentType, setCommentType] = useState('');
  
  // NEW: ABSA Filter States
  const [aspect, setAspect] = useState('');
  const [aspectSentiment, setAspectSentiment] = useState('');
  const [timeRange, setTimeRange] = useState('all');

  const [posts, setPosts] = useState<RedditPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPostsFromBackend = async (queryOverride?: string) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    let finalStartDate = startDate; 
    
    if (!finalStartDate && timeRange !== 'all') {
      const d = new Date();
      if (timeRange === '3months') d.setMonth(d.getMonth() - 3);
      else if (timeRange === '9months') d.setMonth(d.getMonth() - 9);
      else if (timeRange === '12months') d.setFullYear(d.getFullYear() - 1);
      finalStartDate = d.toISOString().split('T')[0];
    }

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryOverride || searchQuery,
          sentiment: sentiment || null,
          source: source || null,
          start_date: finalStartDate || null,
          end_date: endDate || null,
          comment_type: commentType || null,
          aspect: aspect || null,
          aspect_sentiment: aspectSentiment || null,
        }),
      });

      if (!response.ok) throw new Error('Failed to connect to backend server');
      
      const data = await response.json();
      setPosts(data.posts || []);
      
      let suggestionText = '';
      const collations = data.spellcheck?.collations;

      if (Array.isArray(collations)) {
        for (let i = 0; i < collations.length; i++) {
          if (typeof collations[i] === 'string' && collations[i] !== 'collation') {
            suggestionText = collations[i];
            break;
          }
        }
      }
      setSuggestion(suggestionText);
    } catch (err: any) {
      setError(err.message);
      setPosts([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) root.classList.add('dark');
      else root.classList.remove('dark');
    }
  }, [theme]);

  const sentimentCounts = useMemo(() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    posts.forEach(post => {
      post.nestedComments.forEach(comment => {
        if (counts[comment.sentiment] !== undefined) {
          counts[comment.sentiment]++;
        }
      });
    });
    return counts;
  }, [posts]);

  const handleSearch = () => fetchPostsFromBackend();

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    fetchPostsFromBackend(suggestion);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <TopBar onPreferencesClick={() => setShowPreferences(!showPreferences)} theme={theme} />
      
      <PreferencesMenu
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        theme={theme}
        onThemeChange={setTheme}
      />

      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 transition-colors">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <h1 className="text-4xl font-bold text-center mb-8 text-gray-900 dark:text-white">
            Football Sentiment Analysis
          </h1>
          
          <SearchBar
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            showAdvanced={showAdvanced}
            onToggleAdvanced={() => setShowAdvanced(!showAdvanced)}
            onSearch={handleSearch}
          />

          <div className="flex justify-center mt-4 mb-6">
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="border border-gray-300 dark:border-gray-600 px-4 py-2 rounded-full bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer text-sm font-medium transition-colors hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <option value="all">All Time</option>
              <option value="3months">Past 3 Months</option>
              <option value="9months">Past 9 Months</option>
              <option value="12months">Past 12 Months</option>
            </select>
          </div>

          {!hasSearched && (
            <SuggestionPills
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
            />
          )}

          {showAdvanced && (
            <AdvancedFilters
              subreddits={filterData.subreddits}
              sentiment={sentiment}
              onSentimentChange={setSentiment}
              source={source}
              onSourceChange={setSource}
              startDate={startDate}
              onStartDateChange={setStartDate}
              endDate={endDate}
              onEndDateChange={setEndDate}
              commentType={commentType}
              onCommentTypeChange={setCommentType}
              aspect={aspect}
              onAspectChange={setAspect}
              aspectSentiment={aspectSentiment}
              onAspectSentimentChange={setAspectSentiment}
            />
          )}
        </div>
      </div>

      {hasSearched && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          {isLoading ? (
            <div className="flex justify-center items-center py-20">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
            </div>
          ) : error ? (
            <div className="text-center py-10 text-red-500 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-100 dark:border-red-900">
              Error: {error}
            </div>
          ) : (
            <>
              {suggestion && (
                <SpellCheck
                  suggestion={suggestion}
                  onClickSuggestion={(s) => {
                    setSearchQuery(s);
                    fetchPostsFromBackend(s);
                  }}
                />
              )}

              <ResultsPanel
                posts={posts}
                searchQuery={searchQuery}
                showStats={showStats}
                onToggleStats={() => setShowStats(!showStats)}
              />
            </>
          )}
        </div>
      )}

      <StatsModal
        isOpen={showStats}
        onClose={() => setShowStats(false)}
        sentimentCounts={sentimentCounts}
        totalComments={posts.reduce((sum, p) => sum + p.nestedComments.length, 0)}
        totalResults={posts.length} 
      />
    </div>
  );
}