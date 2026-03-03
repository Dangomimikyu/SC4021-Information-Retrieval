import { ThumbsUp, ThumbsDown, Minus, Calendar, User, MessageSquare } from 'lucide-react';

export interface Comment {
  id: string;
  author: string;
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  confidence: number;
  timestamp: string;
  team?: string;
  keywords: string[];
  source?: string;
}

interface CommentCardProps {
  comment: Comment;
}

export function CommentCard({ comment }: CommentCardProps) {
  const sentimentConfig = {
    positive: {
      icon: ThumbsUp,
      bgColor: 'bg-green-50',
      borderColor: 'border-l-green-500',
      textColor: 'text-green-700',
      badgeColor: 'bg-green-100 text-green-800',
    },
    negative: {
      icon: ThumbsDown,
      bgColor: 'bg-red-50',
      borderColor: 'border-l-red-500',
      textColor: 'text-red-700',
      badgeColor: 'bg-red-100 text-red-800',
    },
    neutral: {
      icon: Minus,
      bgColor: 'bg-gray-50',
      borderColor: 'border-l-gray-500',
      textColor: 'text-gray-700',
      badgeColor: 'bg-gray-100 text-gray-800',
    },
  };

  const config = sentimentConfig[comment.sentiment];
  const SentimentIcon = config.icon;

  return (
    <div className={`bg-white border-l-4 ${config.borderColor} rounded-lg shadow-sm hover:shadow-md transition-shadow p-5`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
            <User className="w-5 h-5 text-gray-600" />
          </div>
          <div>
            <div className="font-semibold text-gray-900">{comment.author}</div>
            <div className="flex items-center gap-2 text-sm text-gray-500">
              <Calendar className="w-3 h-3" />
              <span>{comment.timestamp}</span>
              {comment.source && (
                <>
                  <span>•</span>
                  <MessageSquare className="w-3 h-3" />
                  <span>{comment.source}</span>
                </>
              )}
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {comment.team && (
            <span className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">
              {comment.team}
            </span>
          )}
          <div className={`${config.badgeColor} px-3 py-1.5 rounded-full flex items-center gap-1.5`}>
            <SentimentIcon className="w-4 h-4" />
            <span className="text-sm font-medium capitalize">{comment.sentiment}</span>
          </div>
          <div className="text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1.5 rounded-full">
            {Math.round(comment.confidence * 100)}%
          </div>
        </div>
      </div>
      
      <p className="text-gray-800 leading-relaxed mb-3 ml-13">{comment.content}</p>
      
      {comment.keywords.length > 0 && (
        <div className="flex gap-2 flex-wrap ml-13">
          {comment.keywords.map((keyword, index) => (
            <span
              key={index}
              className="text-xs bg-blue-50 text-blue-700 px-2.5 py-1 rounded-full border border-blue-200"
            >
              #{keyword}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
