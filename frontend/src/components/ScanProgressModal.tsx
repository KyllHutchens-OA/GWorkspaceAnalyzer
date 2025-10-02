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
    const pollInterval = setInterval(async () => {
      try {
        const jobData = await api.scans.get(scanJobId);
        setJob(jobData);

        if (jobData.status === 'completed') {
          clearInterval(pollInterval);
          setTimeout(() => {
            onComplete();
          }, 1500);
        } else if (jobData.status === 'failed') {
          clearInterval(pollInterval);
          setError(jobData.error_message || 'Scan failed');
        }
      } catch (err: any) {
        console.error('Failed to poll scan status:', err);
        setError(err.message || 'Failed to check scan status');
        clearInterval(pollInterval);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [scanJobId, onComplete]);

  const progress = job?.total_emails > 0
    ? Math.round((job.processed_emails / job.total_emails) * 100)
    : 0;

  const getStatusMessage = () => {
    if (!job) return 'Starting scan...';
    if (job.status === 'queued') return 'Queued - waiting to start...';
    if (job.status === 'processing') {
      return `Scanning emails (${job.processed_emails} of ${job.total_emails})`;
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
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 to-teal-600 transition-all duration-500 rounded-full"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-sm text-gray-500 mt-2">{progress}% complete</p>
            </div>
          )}

          {/* Stats */}
          {job && job.status === 'processing' && (
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
