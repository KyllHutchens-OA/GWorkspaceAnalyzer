import { Button } from './ui/Button';
import { IssueSummary } from '@/types';

interface IssueCardProps {
  summary: IssueSummary;
}

export function IssueCard({ summary }: IssueCardProps) {
  const borderColors = {
    red: 'border-red-200',
    yellow: 'border-yellow-200',
    orange: 'border-orange-200',
  };

  const bgColors = {
    red: 'bg-red-50',
    yellow: 'bg-yellow-50',
    orange: 'bg-orange-50',
  };

  const textColors = {
    red: 'text-red-700',
    yellow: 'text-yellow-700',
    orange: 'text-orange-700',
  };

  const iconColors = {
    red: 'bg-red-500',
    yellow: 'bg-yellow-500',
    orange: 'bg-orange-500',
  };

  return (
    <div className="group bg-white border-2 border-gray-200 rounded-xl hover:shadow-lg transition-all duration-200 overflow-hidden">
      {/* Header */}
      <div className={`${bgColors[summary.color]} ${borderColors[summary.color]} border-b-2 px-4 md:px-6 py-3 md:py-4`}>
        <div className="flex items-center gap-2 md:gap-3">
          <div className={`w-8 h-8 md:w-10 md:h-10 ${iconColors[summary.color]} rounded-lg flex items-center justify-center flex-shrink-0`}>
            <div className="w-4 h-4 md:w-5 md:h-5 bg-white rounded"></div>
          </div>
          <div className="flex-1">
            <h3 className="text-xs md:text-sm font-bold text-gray-900">{summary.label}</h3>
            <p className="text-xs text-gray-600 mt-0.5">{summary.count} {summary.count === 1 ? 'issue' : 'issues'} found</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 md:p-6">
        <div className="mb-3 md:mb-4">
          <div className="text-3xl md:text-4xl font-black text-gray-900 tracking-tight mb-1">
            ${summary.totalAmount.toLocaleString()}
          </div>
          <p className="text-xs md:text-sm text-gray-600">potential savings/month</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-3 md:p-4 mb-3 md:mb-4 border border-gray-200">
          <p className="text-xs md:text-sm text-gray-700 leading-relaxed">
            {summary.example}
          </p>
        </div>

        <Button
          variant="outline"
          size="sm"
          className="w-full"
        >
          View Details
        </Button>
      </div>
    </div>
  );
}
