import { Notification } from '@/types';

interface NotificationsPanelProps {
  notifications: Notification[];
}

export function NotificationsPanel({ notifications }: NotificationsPanelProps) {
  const getNotificationStyle = (type: string) => {
    switch (type) {
      case 'new':
        return 'bg-gradient-to-r from-blue-500/10 to-blue-600/10 border-l-4 border-blue-500';
      case 'trend':
        return 'bg-gradient-to-r from-slate-500/10 to-slate-600/10 border-l-4 border-slate-500';
      case 'reminder':
        return 'bg-gradient-to-r from-amber-500/10 to-orange-500/10 border-l-4 border-orange-500';
      case 'tip':
        return 'bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-l-4 border-green-500';
      default:
        return 'bg-gradient-to-r from-gray-500/10 to-gray-600/10 border-l-4 border-gray-500';
    }
  };

  const getIconBg = (type: string) => {
    switch (type) {
      case 'new':
        return 'bg-gradient-to-br from-blue-500 to-blue-600';
      case 'trend':
        return 'bg-gradient-to-br from-slate-500 to-slate-600';
      case 'reminder':
        return 'bg-gradient-to-br from-amber-500 to-orange-500';
      case 'tip':
        return 'bg-gradient-to-br from-green-500 to-emerald-500';
      default:
        return 'bg-gradient-to-br from-gray-500 to-gray-600';
    }
  };

  const formatTimeSince = (date: Date) => {
    const now = Date.now();
    const diff = now - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (hours < 1) return 'just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    if (days === 1) return 'yesterday';
    return `${days} days ago`;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <h3 className="text-lg font-bold text-gray-900">Smart Notifications</h3>
        <p className="text-sm text-gray-600 mt-1">Important alerts and insights</p>
      </div>
      <div className="p-6 space-y-3">
        {notifications.map((notification, idx) => (
          <div
            key={notification.id}
            className={`p-4 rounded-lg ${getNotificationStyle(notification.type)} hover:shadow-sm transition-shadow group`}
          >
            <div className="flex items-start gap-4">
              <div className={`flex-shrink-0 w-12 h-12 rounded-xl ${getIconBg(notification.type)} flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                <span className="text-xs font-black text-white">{notification.icon}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-gray-900 leading-relaxed">{notification.message}</p>
                <p className="text-xs font-medium text-gray-600 mt-2">{formatTimeSince(notification.timestamp)}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
