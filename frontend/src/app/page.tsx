'use client';

import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export default function Home() {
  const router = useRouter();
  const { status } = useAuth();
  const [showDebug, setShowDebug] = useState(false);

  useEffect(() => {
    console.log('Auth status:', status);

    // Immediately redirect to landing for unauthenticated users
    if (status === 'unauthenticated') {
      router.replace('/landing');
      return;
    }

    if (status === 'authenticated') {
      router.replace('/dashboard');
      return;
    }

    // Show debug options after 2 seconds if still loading
    const timer = setTimeout(() => setShowDebug(true), 2000);
    return () => clearTimeout(timer);
  }, [status, router]);

  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-slate-800 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p className="text-gray-600 mb-4">Loading...</p>
        <p className="text-sm text-gray-500">Status: {status}</p>

        {showDebug && (
          <div className="mt-6 space-y-2">
            <p className="text-xs text-gray-400">Taking too long?</p>
            <div className="space-x-2">
              <button
                onClick={() => router.push('/landing')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300"
              >
                Go to Landing
              </button>
              <button
                onClick={() => router.push('/login')}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm hover:bg-gray-300"
              >
                Go to Login
              </button>
              <button
                onClick={() => router.push('/dashboard')}
                className="px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm hover:bg-emerald-700"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
