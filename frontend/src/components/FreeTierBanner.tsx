import { Button } from './ui/Button';

interface FreeTierBannerProps {
  scansUsed: number;
  scansLimit: number;
}

export function FreeTierBanner({ scansUsed, scansLimit }: FreeTierBannerProps) {
  const remaining = scansLimit - scansUsed;
  const percentage = (scansUsed / scansLimit) * 100;

  return (
    <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl shadow-sm p-6 text-white">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-4">
            <div className="px-3 py-1 rounded-full bg-white/20 backdrop-blur-sm text-xs font-bold">
              FREE PLAN
            </div>
            <span className="text-sm font-medium">{scansUsed} of {scansLimit} scans used</span>
          </div>

          <div className="mb-4">
            <div className="h-2 bg-white/20 rounded-full overflow-hidden mb-2">
              <div
                className="h-full bg-white transition-all duration-500 rounded-full"
                style={{ width: `${percentage}%` }}
              />
            </div>
          </div>

          {remaining <= 3 && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
              <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
              <p className="text-sm">
                <span className="font-bold">8 more issues</span> worth <span className="font-bold">$2,100</span> detected. Upgrade to unlock.
              </p>
            </div>
          )}
        </div>

        <Button variant="outline" size="lg" className="whitespace-nowrap bg-white text-purple-600 border-white hover:bg-gray-50">
          Upgrade Now
        </Button>
      </div>
    </div>
  );
}
