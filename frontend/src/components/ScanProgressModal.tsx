'use client'

import { useEffect, useState } from 'react';
import api from '@/lib/api';

interface ScanProgressModalProps {
  scanJobId: string;
  onComplete: () => void;
  onClose: () => void;
}

export function ScanProgressModal({ scanJobId, onComplete, onClose }: ScanProgressModalProps) {
  const [job, setJob] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Fetch immediately on mount
    const fetchJob = async () => {
      try {
        console.log('Fetching scan job:', scanJobId);
        console.log('API URL:', `${process.env.NEXT_PUBLIC_API_URL}/api/v1/scan/jobs/${scanJobId}`);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const jobData = await api.scans.get(scanJobId);
        clearTimeout(timeoutId);

        console.log('=== SCAN PROGRESS UPDATE ===');
        console.log('Raw API response:', JSON.stringify(jobData, null, 2));
        console.log('Job status:', jobData?.status);
        console.log('Total emails:', jobData?.total_emails);
        console.log('Processed emails:', jobData?.processed_emails);
        console.log('Invoices found:', jobData?.invoices_found);
        const calcProgress = jobData?.total_emails > 0 ? Math.round((jobData.processed_emails / jobData.total_emails) * 100) : 0;
        console.log('Progress calculation:', jobData?.processed_emails, '/', jobData?.total_emails, '=', calcProgress, '%');
        console.log('===========================');

        setJob(jobData);

        if (jobData.status === 'completed') {
          setTimeout(() => {
            onComplete();
          }, 1500);
        } else if (jobData.status === 'failed') {
          setError(jobData.error_message || 'Scan failed');
        }
      } catch (err: any) {
        console.error('!!! API CALL FAILED !!!');
        console.error('Failed to fetch scan status:', err);
        console.error('Error type:', typeof err);
        console.error('Error keys:', err ? Object.keys(err) : 'null');
        console.error('Error message:', err?.message);
        console.error('Error response:', err?.response);
        console.error('Error stack:', err?.stack);
        setError(err.message || 'Failed to check scan status');
      }
    };

    // Initial fetch
    fetchJob();

    // Poll every 1 second for more responsive updates
    const pollInterval = setInterval(fetchJob, 1000);

    return () => clearInterval(pollInterval);
  }, [scanJobId, onComplete]);

  const progress = job?.total_emails > 0
    ? Math.round(((job.processed_emails || 0) / job.total_emails) * 100)
    : (job?.status === 'processing' ? 5 : 0); // Show 5% if processing but no total yet

  const getStatusMessage = () => {
    if (!job) return 'Starting scan...';
    if (job.status === 'queued') return 'Queued - waiting to start...';
    if (job.status === 'processing') {
      if (job.total_emails === 0) {
        return 'Finding emails to scan...';
      }
      return `Scanning emails (${job.processed_emails || 0} of ${job.total_emails})`;
    }
    if (job.status === 'completed') return 'Scan complete!';
    if (job.status === 'failed') return 'Scan failed';
    return 'Processing...';
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-8 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
          disabled={job?.status === 'processing'}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div className="text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-full mb-6">
            {job?.status === 'completed' ? (
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            ) : error ? (
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-8 h-8 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            )}
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            {error ? 'Scan Failed' : job?.status === 'completed' ? 'Scan Complete!' : 'Scanning Your Gmail'}
          </h2>

          {/* Status */}
          <p className="text-gray-600 mb-6">
            {error || getStatusMessage()}
          </p>

          {/* Progress Bar */}
          {!error && job?.status !== 'completed' && (
            <div className="mb-6">
              <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
                {job?.total_emails === 0 && job?.status === 'processing' ? (
                  // Indeterminate progress bar when finding emails
                  <div className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 animate-pulse w-full opacity-50" />
                ) : (
                  // Normal progress bar
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 transition-all duration-500 rounded-full"
                    style={{ width: `${progress}%` }}
                  />
                )}
              </div>
              <p className="text-sm text-gray-500 mt-2">
                {job?.total_emails === 0 && job?.status === 'processing'
                  ? 'Searching for emails...'
                  : `${progress}% complete`}
              </p>
            </div>
          )}

          {/* Stats */}
          {job && job.status === 'processing' && job.total_emails > 0 && (
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="bg-gray-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-gray-900">{job.processed_emails}</div>
                <div className="text-xs text-gray-600">Emails Scanned</div>
              </div>
              <div className="bg-emerald-50 rounded-lg p-3">
                <div className="text-2xl font-bold text-emerald-600">{job.invoices_found}</div>
                <div className="text-xs text-gray-600">Invoices Found</div>
              </div>
            </div>
          )}

          {/* Debug Info (remove in production) */}
          {job && process.env.NODE_ENV === 'development' && (
            <div className="text-xs text-gray-400 font-mono mb-4 p-2 bg-gray-50 rounded">
              Debug: {job.processed_emails}/{job.total_emails} = {progress}%
            </div>
          )}

          {/* Completion Stats */}
          {job?.status === 'completed' && (
            <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border border-emerald-200 rounded-xl p-4 mb-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-2xl font-bold text-gray-900">{job.total_emails}</div>
                  <div className="text-xs text-gray-600">Emails Scanned</div>
                </div>
                <div>
                  <div className="text-2xl font-bold text-emerald-600">{job.invoices_found}</div>
                  <div className="text-xs text-gray-600">Invoices Found</div>
                </div>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Info */}
          {!error && job?.status !== 'completed' && (
            <p className="text-xs text-gray-500">
              This may take a few minutes. Feel free to close this and check back later.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
