'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from './ui/Button';

interface TrialInfo {
  is_trial: boolean;
  trial_ends_at?: string;
  hours_remaining?: number;
  is_expired: boolean;
}

export function TrialCountdownBanner() {
  const router = useRouter();
  const [trialInfo, setTrialInfo] = useState<TrialInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchTrialStatus();
    const interval = setInterval(fetchTrialStatus, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  const fetchTrialStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscription/trial/status`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        setTrialInfo(data);
      }
    } catch (error) {
      console.error('Failed to fetch trial status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !trialInfo || !trialInfo.is_trial) {
    return null;
  }

  const hours = Math.floor(trialInfo.hours_remaining || 0);
  const minutes = Math.round(((trialInfo.hours_remaining || 0) - hours) * 60);

  const getUrgencyColor = () => {
    if (trialInfo.is_expired) return 'bg-red-600';
    if ((trialInfo.hours_remaining || 0) < 12) return 'bg-orange-600';
    return 'bg-blue-600';
  };

  const getMessage = () => {
    if (trialInfo.is_expired) {
      return 'Your trial has expired';
    }
    if (hours === 0 && minutes < 60) {
      return `Trial expires in ${minutes} minutes`;
    }
    if (hours < 24) {
      return `Trial expires in ${hours}h ${minutes}m`;
    }
    return `Trial expires in ${hours} hours`;
  };

  return (
    <div className={`${getUrgencyColor()} text-white`}>
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
                  d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </span>
            <p className="ml-3 font-medium text-white truncate">
              <span className="md:hidden">{getMessage()}</span>
              <span className="hidden md:inline">
                {getMessage()} - Upgrade now to keep full access to your dashboard
              </span>
            </p>
          </div>
          <div className="order-3 mt-2 flex-shrink-0 w-full sm:order-2 sm:mt-0 sm:w-auto">
            <Button
              onClick={() => router.push('/pricing')}
              variant="outline"
              className="bg-white text-gray-900 hover:bg-gray-50"
            >
              Upgrade Now
            </Button>
          </div>
          <div className="order-2 flex-shrink-0 sm:order-3 sm:ml-3">
            <button
              type="button"
              className="-mr-1 flex p-2 rounded-md hover:bg-white hover:bg-opacity-20 focus:outline-none focus:ring-2 focus:ring-white sm:-mr-2"
              onClick={() => setTrialInfo(null)}
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
      </div>
    </div>
  );
}
