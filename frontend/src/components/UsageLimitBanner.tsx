'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from './ui/Button';

interface UsageInfo {
  invoice_limit: number;
  invoices_used: number;
  invoices_remaining: number;
  usage_percentage: number;
  is_approaching_limit: boolean;
  is_at_limit: boolean;
  tier: string;
}

export function UsageLimitBanner() {
  const router = useRouter();
  const [usage, setUsage] = useState<UsageInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [dismissed, setDismissed] = useState(false);

  useEffect(() => {
    fetchUsage();
  }, []);

  const fetchUsage = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscription/usage`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setUsage(data);
      }
    } catch (error) {
      console.error('Failed to fetch usage:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !usage || dismissed) {
    return null;
  }

  // Only show banner if approaching limit (80%+) or at limit (95%+)
  if (!usage.is_approaching_limit && !usage.is_at_limit) {
    return null;
  }

  // Don't show for unlimited tiers
  if (usage.invoice_limit >= 999999) {
    return null;
  }

  const getBannerColor = () => {
    if (usage.is_at_limit) return 'bg-red-600';
    return 'bg-yellow-600';
  };

  const getMessage = () => {
    if (usage.is_at_limit) {
      return `Invoice limit reached: ${usage.invoices_used}/${usage.invoice_limit}`;
    }
    return `You've used ${usage.invoices_used}/${usage.invoice_limit} invoices this month (${Math.round(usage.usage_percentage)}%)`;
  };

  return (
    <div className={`${getBannerColor()} text-white`}>
      <div className="max-w-7xl mx-auto py-3 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between flex-wrap">
          <div className="w-0 flex-1 flex items-center">
            <span className="flex p-2 rounded-lg bg-white bg-opacity-20">
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </span>
            <div className="ml-3">
              <p className="font-medium text-white">{getMessage()}</p>
              {usage.is_at_limit ? (
                <p className="text-sm text-white opacity-90">
                  Upgrade to Business for unlimited processing
                </p>
              ) : (
                <p className="text-sm text-white opacity-90">
                  {usage.invoices_remaining} invoices remaining this month
                </p>
              )}
            </div>
          </div>
          <div className="order-3 mt-2 flex-shrink-0 w-full sm:order-2 sm:mt-0 sm:w-auto">
            <Button
              onClick={() => router.push('/pricing')}
              variant="outline"
              className="bg-white text-gray-900 hover:bg-gray-50"
            >
              Upgrade Plan
            </Button>
          </div>
          <div className="order-2 flex-shrink-0 sm:order-3 sm:ml-3">
            <button
              type="button"
              className="-mr-1 flex p-2 rounded-md hover:bg-white hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-white sm:-mr-2"
              onClick={() => setDismissed(true)}
            >
              <span className="sr-only">Dismiss</span>
              <svg
                className="h-5 w-5 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Progress bar */}
        <div className="mt-3">
          <div className="bg-white bg-opacity-20 rounded-full h-2 overflow-hidden">
            <div
              className="bg-white h-full transition-all duration-300"
              style={{ width: `${Math.min(100, usage.usage_percentage)}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
