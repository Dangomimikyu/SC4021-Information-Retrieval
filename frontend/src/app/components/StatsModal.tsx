import { BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis, Legend, LineChart, Line } from 'recharts';
import { X } from 'lucide-react';

interface StatsModalProps {
  isOpen: boolean;
  onClose: () => void;
  sentimentCounts: {
    positive: number;
    negative: number;
    neutral: number;
  };
  totalComments: number;
}

export function StatsModal({ isOpen, onClose, sentimentCounts, totalComments }: StatsModalProps) {
  if (!isOpen) return null;

  const pieData = [
    { name: 'Positive', value: sentimentCounts.positive, color: '#22c55e' },
    { name: 'Negative', value: sentimentCounts.negative, color: '#ef4444' },
    { name: 'Neutral', value: sentimentCounts.neutral, color: '#6b7280' },
  ];

  const barData = [
    { name: 'Positive', count: sentimentCounts.positive, fill: '#22c55e' },
    { name: 'Negative', count: sentimentCounts.negative, fill: '#ef4444' },
    { name: 'Neutral', count: sentimentCounts.neutral, fill: '#6b7280' },
  ];

  const timelineData = [
    { time: '09:00', positive: 45, negative: 23, neutral: 32 },
    { time: '12:00', positive: 67, negative: 34, neutral: 28 },
    { time: '15:00', positive: 89, negative: 45, neutral: 41 },
    { time: '18:00', positive: 76, negative: 38, neutral: 35 },
    { time: '21:00', positive: 52, negative: 29, neutral: 26 },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <h2 className="text-2xl font-bold">Sentiment Analysis Statistics</h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-6 rounded-lg border border-blue-200">
              <div className="text-sm text-blue-700 mb-1">Total Comments</div>
              <div className="text-4xl font-bold text-blue-900">{totalComments}</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 p-6 rounded-lg border border-green-200">
              <div className="text-sm text-green-700 mb-1">Positive</div>
              <div className="text-4xl font-bold text-green-900">{sentimentCounts.positive}</div>
            </div>
            <div className="bg-gradient-to-br from-red-50 to-red-100 p-6 rounded-lg border border-red-200">
              <div className="text-sm text-red-700 mb-1">Negative</div>
              <div className="text-4xl font-bold text-red-900">{sentimentCounts.negative}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-lg mb-4">Sentiment Distribution (Bar)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={barData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
              <h3 className="font-semibold text-lg mb-4">Sentiment Distribution (Pie)</h3>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 md:col-span-2">
              <h3 className="font-semibold text-lg mb-4">Sentiment Timeline</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={timelineData}>
                  <XAxis dataKey="time" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} />
                  <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} />
                  <Line type="monotone" dataKey="neutral" stroke="#6b7280" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
