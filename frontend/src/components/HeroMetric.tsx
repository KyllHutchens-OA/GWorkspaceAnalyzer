import { Button } from './ui/Button';

interface HeroMetricProps {
  amount: number;
  lastScanned: Date;
  invoicesAnalyzed: number;
  issuesFound: number;
}

export function HeroMetric({ amount, lastScanned, invoicesAnalyzed, issuesFound }: HeroMetricProps) {
  const formatTimeSince = (date: Date) => {
    const hours = Math.floor((Date.now() - date.getTime()) / (1000 * 60 * 60));
    if (hours < 1) return 'less than an hour ago';
    if (hours === 1) return '1 hour ago';
    if (hours < 24) return `${hours} hours ago`;
    const days = Math.floor(hours / 24);
    return days === 1 ? '1 day ago' : `${days} days ago`;
  };

  return (
    <div className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6 md:p-12 overflow-hidden">
      <div className="max-w-4xl mx-auto">
        {/* Alert Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 md:px-4 md:py-2 bg-red-50 border border-red-200 rounded-full mb-4 md:mb-6">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          <span className="text-xs md:text-sm font-semibold text-red-700">{issuesFound} Issues Found</span>
        </div>

        {/* Main Metric */}
        <div className="mb-6 md:mb-8">
          <h1 className="text-base md:text-2xl text-gray-600 mb-2 md:mb-3">
            Monthly overspend detected
          </h1>
          <div className="text-5xl md:text-8xl font-black text-gray-900 mb-1 md:mb-2 tracking-tight">
            ${amount.toLocaleString()}
          </div>
          <p className="text-sm md:text-lg text-gray-500">Based on {invoicesAnalyzed.toLocaleString()} invoices analyzed</p>
        </div>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <Button variant="primary" size="lg">
            Review All Issues
          </Button>
          <Button variant="outline" size="lg">
            Export Report
          </Button>
        </div>

        {/* Status Bar */}
        <div className="flex items-center gap-6 pt-6 border-t border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-500" />
            <span className="text-sm text-gray-600">
              Scanned <span className="font-semibold text-gray-900">{formatTimeSince(lastScanned)}</span>
            </span>
          </div>
          <div className="hidden sm:block w-px h-4 bg-gray-300" />
          <span className="text-sm text-gray-600">
            Next scan in <span className="font-semibold text-gray-900">6 hours</span>
          </span>
        </div>
      </div>
    </div>
  );
}
