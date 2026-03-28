import { useMemo, useState } from 'react';
import { 
  ThumbsUp, ThumbsDown, Minus, Calendar, 
  User, MessageSquare, Tag, BarChart2,
  ChevronDown, ChevronUp 
} from 'lucide-react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip 
} from 'recharts';

/**
 * Interface representing a single comment inside a Reddit post
 */
export interface NestedComment {
  text: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

/**
 * Interface representing a full Reddit Post
 */
export interface RedditPost {
  id: string;
  author: string;
  title: string;
  content: string;
  timestamp: string;
  source: string;
  team?: string;
  nestedComments: NestedComment[];
}

interface PostCardProps {
  post: RedditPost;
}

export function CommentCard({ post }: PostCardProps) {
  // State to handle the visibility of the comments section
  const [showComments, setShowComments] = useState(false);

  /**
   * Calculate sentiment distribution specifically for THIS post's comments
   */
  const stats = useMemo(() => {
    const counts = { positive: 0, negative: 0, neutral: 0 };
    post.nestedComments.forEach((c) => {
      if (counts[c.sentiment] !== undefined) counts[c.sentiment]++;
    });

    return [
      { name: 'Positive', value: counts.positive, color: '#22c55e' },
      { name: 'Negative', value: counts.negative, color: '#ef4444' },
      { name: 'Neutral', value: counts.neutral, color: '#6b7280' },
    ].filter(item => item.value > 0);
  }, [post.nestedComments]);

  const sentimentConfig = {
    positive: { icon: ThumbsUp, badgeColor: 'bg-green-100 text-green-800 border-green-200' },
    negative: { icon: ThumbsDown, badgeColor: 'bg-red-100 text-red-800 border-red-200' },
    neutral: { icon: Minus, badgeColor: 'bg-gray-100 text-gray-800 border-gray-200' },
  };

  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 mb-8 shadow-sm hover:shadow-md transition-all">
      {/* 1. Post Header */}
      <div className="flex items-center justify-between mb-4 border-b border-gray-50 dark:border-gray-700 pb-3">
        <div className="flex items-center gap-3 text-sm text-gray-500">
          <div className="flex items-center gap-1">
            <User className="w-4 h-4 text-blue-500" />
            <span className="font-semibold text-gray-700 dark:text-gray-300">{post.author}</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded text-xs">
            <Tag className="w-3 h-3" />
            <span>r/{post.source}</span>
          </div>
          <span>•</span>
          <div className="flex items-center gap-1">
            <Calendar className="w-3 h-3" />
            <span>{post.timestamp}</span>
          </div>
        </div>
      </div>

      {/* 2. Content Section */}
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">{post.title}</h3>
      <p className="text-gray-700 dark:text-gray-400 mb-6 line-clamp-3">{post.content}</p>

      {/* 3. Post Stats (Always Visible if comments exist) */}
      {post.nestedComments.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-xl p-4 mb-4 flex flex-col md:flex-row items-center gap-6 border border-gray-100 dark:border-gray-700">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2 text-gray-600 dark:text-gray-300 text-xs font-bold uppercase tracking-wider">
              <BarChart2 className="w-4 h-4" />
              <span>Post Sentiment Insights</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              {stats.map(s => (
                <div key={s.name} className="text-center p-2 rounded-lg bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700">
                  <div className="text-[10px] text-gray-500 uppercase">{s.name}</div>
                  <div className="text-lg font-bold" style={{ color: s.color }}>{s.value}</div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="w-24 h-24">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={stats}
                  innerRadius={20}
                  outerRadius={35}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {stats.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* 4. Toggle Comments Button */}
      <button 
        onClick={() => setShowComments(!showComments)}
        className="flex items-center gap-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 font-bold text-sm transition-colors mb-4"
      >
        <MessageSquare className="w-4 h-4" />
        <span>
          {showComments ? 'Hide' : 'Show'} Comments ({post.nestedComments.length})
        </span>
        {showComments ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* 5. Nested Comments List (Conditional Rendering) */}
      {showComments && (
        <div className="space-y-3 pt-4 border-t border-gray-100 dark:border-gray-700 animate-in fade-in slide-in-from-top-2 duration-300">
          {post.nestedComments.length > 0 ? (
            post.nestedComments.map((comment, index) => {
              const config = sentimentConfig[comment.sentiment];
              const Icon = config.icon;
              return (
                <div key={index} className="pl-4 border-l-4 border-gray-100 dark:border-gray-700 bg-gray-50/30 dark:bg-gray-800/20 p-3 rounded-r-lg flex justify-between items-start gap-4">
                  <p className="text-sm text-gray-700 dark:text-gray-300 italic">"{comment.text}"</p>
                  <div className={`flex items-center gap-1 px-2 py-0.5 rounded-full border shrink-0 ${config.badgeColor}`}>
                    <Icon className="w-3 h-3" />
                    <span className="text-[10px] font-bold uppercase">{comment.sentiment}</span>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="text-sm text-gray-400 italic">No comments available for this post.</p>
          )}
        </div>
      )}
    </div>
  );
}