import { useState, useMemo, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { SuggestionPills } from './components/SuggestionPills';
import { AdvancedFilters } from './components/AdvancedFilters';
import { ResultsPanel } from './components/ResultsPanel';
import { StatsModal } from './components/StatsModal';
import { TopBar } from './components/TopBar';
import { PreferencesMenu } from './components/PreferencesMenu';
// Import the RedditPost interface defined in your CommentCard
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
  // --- UI & Navigation State ---
  const [searchQuery, setSearchQuery] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');

  // --- Advanced Filter States ---
  const [sentiment, setSentiment] = useState('');
  const [source, setSource] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [commentType, setCommentType] = useState('');

  // --- Data & API State ---
  // We now store an array of "RedditPost" objects instead of flat comments
  const [posts, setPosts] = useState<RedditPost[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  /**
   * Fetches search results from the Node.js backend.
   * Sends user query and all active filters in a POST request.
   */
  const fetchPostsFromBackend = async (queryOverride?: string) => {
    setIsLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryOverride || searchQuery,
          sentiment: sentiment || null,
          source: source || null,
          start_date: startDate || null,
          end_date: endDate || null,
          comment_type: commentType || null,
        }),
      });

      if (!response.ok) throw new Error('Failed to connect to backend server');
      
      const data = await response.json();
      
      // Update state with the posts returned from Solr/Backend
      setPosts(data.posts || []); 
    } catch (err: any) {
      setError(err.message);
      setPosts([]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Effect to handle Theme Switching (Dark/Light Mode).
   * Modifies the document root class for Tailwind CSS support.
   */
  useEffect(() => {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      // System default theme logic
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) root.classList.add('dark');
      else root.classList.remove('dark');
    }
  }, [theme]);

  /**
   * Memoized calculation of total sentiment distribution.
   * This iterates through every post and sums up the sentiment of all nested comments.
   */
  const sentimentCounts = useMemo(() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    
    posts.forEach(post => {
      // Check each comment inside the post to update global stats
      post.nestedComments.forEach(comment => {
        if (counts[comment.sentiment] !== undefined) {
          counts[comment.sentiment]++;
        }
      });
    });
    
    return counts;
  }, [posts]);

  // --- Event Handlers ---
  const handleSearch = () => fetchPostsFromBackend();

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    fetchPostsFromBackend(suggestion); // Execute search immediately on click
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Top Navigation Bar */}
      <TopBar onPreferencesClick={() => setShowPreferences(!showPreferences)} theme={theme} />
      
      {/* User Preferences Popup */}
      <PreferencesMenu
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        theme={theme}
        onThemeChange={setTheme}
      />

      {/* Main Search Section */}
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

          {/* Quick Suggestions (Hidden after first search) */}
          {!hasSearched && (
            <SuggestionPills
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
            />
          )}

          {/* Advanced Filter Dropdowns */}
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
            />
          )}
        </div>
      </div>

      {/* Results Display Area */}
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
            <ResultsPanel
              posts={posts} // Pass the list of Reddit posts
              searchQuery={searchQuery}
              showStats={showStats}
              onToggleStats={() => setShowStats(!showStats)}
            />
          )}
        </div>
      )}

      {/* Global Statistics Charts Modal */}
      <StatsModal
        isOpen={showStats}
        onClose={() => setShowStats(false)}
        sentimentCounts={sentimentCounts}
        // totalComments is still needed for the UI summary boxes
        totalComments={posts.reduce((sum, p) => sum + p.nestedComments.length, 0)}
        totalResults={posts.length} // Number of unique Reddit posts found
      />
    </div>
  );
}