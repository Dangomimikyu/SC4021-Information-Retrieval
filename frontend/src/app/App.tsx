import { useState, useMemo, useEffect } from 'react';
import { SearchBar } from './components/SearchBar';
import { SuggestionPills } from './components/SuggestionPills';
import { AdvancedFilters } from './components/AdvancedFilters';
import { ResultsPanel } from './components/ResultsPanel';
import { StatsModal } from './components/StatsModal';
import { TopBar } from './components/TopBar';
import { PreferencesMenu } from './components/PreferencesMenu';
import { Comment } from './components/CommentCard';

const mockComments: Comment[] = [
  {
    id: '1',
    author: 'John Smith',
    content: 'Amazing match today! Ronaldo played brilliantly and scored a stunning hat-trick. The team showed incredible fighting spirit throughout the game.',
    sentiment: 'positive',
    confidence: 0.95,
    timestamp: '2026-02-18 14:30',
    team: 'Manchester United',
    keywords: ['Ronaldo', 'hat-trick', 'brilliant'],
    source: 'Twitter',
  },
  {
    id: '2',
    author: 'Sarah Johnson',
    content: 'Disappointed with the team performance. Defense was too weak and kept making mistakes. The coach needs to make changes to the lineup.',
    sentiment: 'negative',
    confidence: 0.89,
    timestamp: '2026-02-18 14:25',
    team: 'Liverpool',
    keywords: ['disappointed', 'defense', 'mistakes'],
    source: 'Reddit',
  },
  {
    id: '3',
    author: 'Mike Williams',
    content: 'The 1-1 draw was fairly balanced. Both teams had chances but failed to capitalize. Need to improve finishing ability.',
    sentiment: 'neutral',
    confidence: 0.78,
    timestamp: '2026-02-18 14:20',
    team: 'Chelsea',
    keywords: ['draw', 'balanced', 'finishing'],
    source: 'Facebook',
  },
  {
    id: '4',
    author: 'Emily Davis',
    content: 'Messi is truly a genius! That assist in the final minutes was world class. Deserves to be called the best player in the world.',
    sentiment: 'positive',
    confidence: 0.97,
    timestamp: '2026-02-18 14:15',
    team: 'Barcelona',
    keywords: ['Messi', 'genius', 'assist'],
    source: 'Twitter',
  },
  {
    id: '5',
    author: 'Robert Brown',
    content: 'The referee made a completely wrong penalty call! This is a terrible decision that affected the match result.',
    sentiment: 'negative',
    confidence: 0.92,
    timestamp: '2026-02-18 14:10',
    team: 'Real Madrid',
    keywords: ['referee', 'penalty', 'wrong'],
    source: 'Twitter',
  },
  {
    id: '6',
    author: 'Lisa Anderson',
    content: 'The match was played at a high pace. Both teams took turns attacking but no goals were scored.',
    sentiment: 'neutral',
    confidence: 0.72,
    timestamp: '2026-02-18 14:05',
    team: 'Arsenal',
    keywords: ['pace', 'attacking'],
    source: 'Reddit',
  },
  {
    id: '7',
    author: 'David Martinez',
    content: 'Well-deserved victory for the home team! Excellent team spirit, all players gave their best for the club jersey.',
    sentiment: 'positive',
    confidence: 0.94,
    timestamp: '2026-02-18 14:00',
    team: 'Manchester City',
    keywords: ['victory', 'team spirit', 'excellent'],
    source: 'Facebook',
  },
  {
    id: '8',
    author: 'Jennifer Wilson',
    content: 'Losing 0-3 at home is shameful. Fire the coach immediately, this is unacceptable.',
    sentiment: 'negative',
    confidence: 0.96,
    timestamp: '2026-02-18 13:55',
    team: 'Tottenham',
    keywords: ['losing', 'shameful', 'fire coach'],
    source: 'Twitter',
  },
  {
    id: '9',
    author: 'Chris Taylor',
    content: 'Young player got to play today and had some decent touches. Still has a lot to learn though.',
    sentiment: 'neutral',
    confidence: 0.68,
    timestamp: '2026-02-18 13:50',
    team: 'Bayern Munich',
    keywords: ['young player', 'learn'],
    source: 'Reddit',
  },
  {
    id: '10',
    author: 'Amanda White',
    content: 'Goal in the 90+3 minute was so dramatic! The team never gave up, this is the true spirit of champions.',
    sentiment: 'positive',
    confidence: 0.98,
    timestamp: '2026-02-18 13:45',
    team: 'Juventus',
    keywords: ['goal', 'dramatic', 'champions'],
    source: 'Twitter',
  },
  {
    id: '11',
    author: 'Kevin Moore',
    content: 'The attack was really poor, couldn\'t create any dangerous chances. Most disappointing is the main striker.',
    sentiment: 'negative',
    confidence: 0.87,
    timestamp: '2026-02-18 13:40',
    team: 'AC Milan',
    keywords: ['attack', 'poor', 'striker'],
    source: 'Facebook',
  },
  {
    id: '12',
    author: 'Rachel Garcia',
    content: 'The match had many controversial situations. Both teams have reasons to complain about the referee.',
    sentiment: 'neutral',
    confidence: 0.75,
    timestamp: '2026-02-18 13:35',
    team: 'PSG',
    keywords: ['controversial', 'referee'],
    source: 'Reddit',
  },
];

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

  // Advanced filter states
  const [sentiment, setSentiment] = useState('');
  const [source, setSource] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [team, setTeam] = useState('');
  const [commentType, setCommentType] = useState('');

  // Apply theme
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
    } else {
      // System preference
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (isDark) {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  }, [theme]);

  const teams = useMemo(() => {
    const teamSet = new Set(mockComments.map(c => c.team).filter(Boolean) as string[]);
    return Array.from(teamSet).sort();
  }, []);

  const filteredComments = useMemo(() => {
    if (!hasSearched) return [];

    return mockComments.filter((comment) => {
      if (sentiment && comment.sentiment !== sentiment) {
        return false;
      }
      if (source && comment.source?.toLowerCase() !== source.toLowerCase()) {
        return false;
      }
      if (team && comment.team !== team) {
        return false;
      }
      if (searchQuery && 
          !comment.content.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !comment.author.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !comment.keywords.some(k => k.toLowerCase().includes(searchQuery.toLowerCase()))) {
        return false;
      }
      if (startDate && comment.timestamp < startDate) {
        return false;
      }
      if (endDate && comment.timestamp > endDate) {
        return false;
      }
      return true;
    });
  }, [sentiment, source, team, searchQuery, startDate, endDate, hasSearched]);

  const sentimentCounts = useMemo(() => {
    return filteredComments.reduce(
      (acc, comment) => {
        acc[comment.sentiment]++;
        return acc;
      },
      { positive: 0, negative: 0, neutral: 0 }
    );
  }, [filteredComments]);

  const handleSearch = () => {
    setHasSearched(true);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setSearchQuery(suggestion);
    setHasSearched(true);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      {/* Top Bar with Preferences */}
      <TopBar onPreferencesClick={() => setShowPreferences(!showPreferences)} theme={theme} />
      
      {/* Preferences Menu */}
      <PreferencesMenu
        isOpen={showPreferences}
        onClose={() => setShowPreferences(false)}
        theme={theme}
        onThemeChange={setTheme}
      />

      {/* Search Section */}
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

          {!hasSearched && (
            <SuggestionPills
              suggestions={suggestions}
              onSuggestionClick={handleSuggestionClick}
            />
          )}

          {showAdvanced && (
            <AdvancedFilters
              sentiment={sentiment}
              onSentimentChange={setSentiment}
              source={source}
              onSourceChange={setSource}
              startDate={startDate}
              onStartDateChange={setStartDate}
              endDate={endDate}
              onEndDateChange={setEndDate}
              team={team}
              onTeamChange={setTeam}
              commentType={commentType}
              onCommentTypeChange={setCommentType}
              teams={teams}
            />
          )}
        </div>
      </div>

      {/* Results Section */}
      {hasSearched && (
        <div className="max-w-7xl mx-auto px-4 py-8 dark:text-white">
          <ResultsPanel
            comments={filteredComments}
            searchQuery={searchQuery}
            showStats={showStats}
            onToggleStats={() => setShowStats(!showStats)}
          />
        </div>
      )}

      {/* Stats Modal */}
      <StatsModal
        isOpen={showStats}
        onClose={() => setShowStats(false)}
        sentimentCounts={sentimentCounts}
        totalComments={filteredComments.length}
      />
    </div>
  );
}
