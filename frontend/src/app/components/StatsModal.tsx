import { 
  BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, 
  Tooltip, XAxis, YAxis, Legend, LineChart, Line 
} from 'recharts';
import { X, Layout, MessageSquare } from 'lucide-react';

interface StatsModalProps {
  isOpen: boolean;
  onClose: () => void;
  sentimentCounts: {
    positive: number;
    negative: number;
    neutral: number;
  };
  totalComments: number; // Sum of all nested comments
  totalResults: number;  // Number of Reddit posts found (matches your request)
}

export function StatsModal({ isOpen, onClose, sentimentCounts, totalComments, totalResults }: StatsModalProps) {
  if (!isOpen) return null;

  // Data for the Pie Chart
  const pieData = [
    { name: 'Positive', value: sentimentCounts.positive, color: '#22c55e' },
    { name: 'Negative', value: sentimentCounts.negative, color: '#ef4444' },
    { name: 'Neutral', value: sentimentCounts.neutral, color: '#6b7280' },
  ];

  // Data for the Bar Chart
  const barData = [
    { name: 'Positive', count: sentimentCounts.positive, color: '#22c55e' },
    { name: 'Negative', count: sentimentCounts.negative, color: '#ef4444' },
    { name: 'Neutral', count: sentimentCounts.neutral, color: '#6b7280' },
  ];

  // Mock data for the timeline (You can replace this with real logic later)
  const timelineData = [
    { time: '09:00', positive: 45, negative: 23, neutral: 32 },
    { time: '12:00', positive: 67, negative: 34, neutral: 28 },
    { time: '15:00', positive: 89, negative: 45, neutral: 41 },
    { time: '18:00', positive: 76, negative: 38, neutral: 35 },
    { time: '21:00', positive: 52, negative: 29, neutral: 26 },
  ];

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-5xl w-full max-h-[90vh] overflow-y-auto border border-gray-200 dark:border-gray-700">
        
        {/* Header */}
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 py-4 flex items-center justify-between z-10">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Global Sentiment Statistics</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-xl transition-colors"
          >
            <X className="w-6 h-6 text-gray-500" />
          </button>
        </div>

        <div className="p-8">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-blue-50 dark:bg-blue-900/20 p-5 rounded-2xl border border-blue-100 dark:border-blue-800">
              <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 mb-1 font-medium">
                <Layout className="w-4 h-4" />
                <span>Total Posts</span>
              </div>
              <div className="text-4xl font-black text-blue-900 dark:text-blue-100">{totalResults}</div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700/50 p-5 rounded-2xl border border-gray-100 dark:border-gray-600">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400 mb-1 font-medium">
                <MessageSquare className="w-4 h-4" />
                <span>Total Comments</span>
              </div>
              <div className="text-4xl font-black text-gray-900 dark:text-white">{totalComments}</div>
            </div>

            <div className="bg-green-50 dark:bg-green-900/20 p-5 rounded-2xl border border-green-100 dark:border-green-800">
              <div className="text-green-600 dark:text-green-400 mb-1 font-medium">Positive</div>
              <div className="text-4xl font-black text-green-900 dark:text-green-100">{sentimentCounts.positive}</div>
            </div>

            <div className="bg-red-50 dark:bg-red-900/20 p-5 rounded-2xl border border-red-100 dark:border-red-800">
              <div className="text-red-600 dark:text-red-400 mb-1 font-medium">Negative</div>
              <div className="text-4xl font-black text-red-900 dark:text-red-100">{sentimentCounts.negative}</div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Bar Chart */}
            <div className="bg-white dark:bg-gray-700/30 p-6 rounded-2xl border border-gray-100 dark:border-gray-700">
              <h3 className="font-bold text-lg mb-6 dark:text-white text-center">Sentiment Distribution (Bar)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={barData}>
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
                  <YAxis stroke="#94a3b8" fontSize={12} />
                  <Tooltip cursor={{fill: 'transparent'}} />
                  <Bar dataKey="count" radius={[10, 10, 0, 0]}>
                    {barData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Pie Chart */}
            <div className="bg-white dark:bg-gray-700/30 p-6 rounded-2xl border border-gray-100 dark:border-gray-700">
              <h3 className="font-bold text-lg mb-6 dark:text-white text-center">Sentiment Distribution (Pie)</h3>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={8}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend verticalAlign="bottom" height={36}/>
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Line Chart */}
            <div className="bg-white dark:bg-gray-700/30 p-6 rounded-2xl border border-gray-100 dark:border-gray-700 md:col-span-2">
              <h3 className="font-bold text-lg mb-6 dark:text-white text-center">Sentiment Timeline</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={timelineData}>
                  <XAxis dataKey="time" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="neutral" stroke="#6b7280" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}