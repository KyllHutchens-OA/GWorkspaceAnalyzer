import { Card, CardBody, CardHeader } from './ui/Card';
import { ActivityLogItem } from '@/types';

interface ActivityLogProps {
  activities: ActivityLogItem[];
}

export function ActivityLog({ activities }: ActivityLogProps) {
  const formatTimeSince = (date: Date) => {
    const now = Date.now();
    const diff = now - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return 'Less than an hour ago';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  const getActivityIcon = (type: string) => {
    const baseClasses = 'w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold';
    switch (type) {
      case 'scan':
        return <div className={`${baseClasses} bg-blue-100 text-blue-700`}>SC</div>;
      case 'finding':
        return <div className={`${baseClasses} bg-green-100 text-green-700`}>FD</div>;
      case 'action':
        return <div className={`${baseClasses} bg-slate-100 text-slate-700`}>AC</div>;
      case 'alert':
        return <div className={`${baseClasses} bg-orange-100 text-orange-700`}>AL</div>;
      default:
        return <div className={`${baseClasses} bg-gray-100 text-gray-700`}>--</div>;
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-bold text-gray-900">Activity Log</h3>
        <p className="text-sm text-gray-600 mt-1">Recent system activity</p>
      </div>
      <div className="divide-y divide-gray-200">
        {activities.map((activity, idx) => (
          <div key={activity.id} className="px-6 py-4 hover:bg-gray-50 transition-colors group">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0 group-hover:scale-110 transition-transform">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 leading-relaxed">{activity.message}</p>
                <p className="text-xs font-medium text-gray-500 mt-1.5">{formatTimeSince(activity.timestamp)}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
