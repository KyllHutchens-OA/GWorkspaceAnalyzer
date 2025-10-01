'use client';

import { Finding } from '@/types';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

interface FindingCardProps {
  finding: Finding;
}

export function FindingCard({ finding }: FindingCardProps) {
  const getStatusColor = (type: string) => {
    switch (type) {
      case 'duplicate':
        return 'bg-red-500';
      case 'subscription':
        return 'bg-yellow-500';
      case 'price_increase':
        return 'bg-orange-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getActionButton = () => {
    if (finding.type === 'duplicate') {
      return (
        <Button variant="danger" size="md" className="w-full">
          Dispute Charge
        </Button>
      );
    }
    if (finding.type === 'subscription') {
      return (
        <Button variant="primary" size="md" className="w-full">
          {finding.issue.includes('unused') ? 'Downgrade Plan' : 'Consolidate'}
        </Button>
      );
    }
    return (
      <Button variant="outline" size="md" className="w-full">
        Negotiate Price
      </Button>
    );
  };

  const formatDate = (date: Date) => {
    const now = Date.now();
    const diff = now - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (hours < 1) return 'Just now';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    const days = Math.floor(hours / 24);
    if (days === 1) return 'Yesterday';
    return `${days} days ago`;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getStatusColor(finding.type)}`} />
          <span className="text-xs font-semibold text-gray-600 uppercase">
            {finding.type.replace('_', ' ')}
          </span>
        </div>
        <Badge confidence={finding.confidenceLevel}>{finding.confidence}%</Badge>
      </div>

      {/* Vendor */}
      <h3 className="text-lg font-bold text-gray-900 mb-1">{finding.vendor}</h3>

      {/* Issue */}
      <p className="text-sm text-gray-600 mb-3">{finding.issue}</p>

      {/* Amount */}
      <div className="mb-3">
        <div className="text-3xl font-black text-gray-900">
          ${finding.amount.toLocaleString()}
          {finding.type === 'subscription' && (
            <span className="text-base font-medium text-gray-500">/mo</span>
          )}
        </div>
        <p className="text-xs text-gray-500 mt-1">Found {formatDate(finding.dateFound)}</p>
      </div>

      {/* Action */}
      {getActionButton()}
    </div>
  );
}
