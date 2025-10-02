'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { supabase } from '@/lib/supabase';

export default function AuthCallbackPage() {
  const [error, setError] = useState<string | null>(null);
  const [hasRun, setHasRun] = useState(false);
  const router = useRouter();

  useEffect(() => {
    if (!hasRun) {
      setHasRun(true);
      handleCallback();
    }
  }, [hasRun]);

  const handleCallback = async () => {
    try {
      console.log('Processing Supabase auth callback...');

      const { data, error: sessionError } = await supabase.auth.getSession();

      if (sessionError) {
        console.error('Session error:', sessionError);
        throw new Error(sessionError.message);
      }

      if (!data.session) {
        throw new Error('No session found');
      }

      console.log('Session established:', data.session.user.email);

      // Redirect immediately to dashboard
      router.push('/dashboard');

    } catch (err: any) {
      console.error('Callback error:', err);
      setError(err.message || 'Authentication failed');
    }
  };

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-slate-50 flex items-center justify-center px-4">
        <div className="max-w-md w-full">
          <div className="bg-white border border-red-200 rounded-2xl shadow-lg p-8">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Authentication Failed</h2>
              <p className="text-gray-600 mb-4">{error}</p>
              <button
                onClick={() => router.push('/login')}
                className="px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700"
              >
                Back to Login
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }


  // Show simple loading state while redirecting
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-white to-slate-50 flex items-center justify-center px-4">
      <div className="text-center">
        <div className="w-16 h-16 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <h2 className="text-xl font-bold text-gray-900">Redirecting to dashboard...</h2>
      </div>
    </div>
  );
}
