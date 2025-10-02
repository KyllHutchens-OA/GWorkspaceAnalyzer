'use client'

import { useState } from 'react';
import { Button } from './ui/Button';
import { ScanProgressModal } from './ScanProgressModal';
import api from '@/lib/api';

export function QuickActionsBar() {
  const [scanning, setScanning] = useState(false);
  const [showProgress, setShowProgress] = useState(false);
  const [scanJobId, setScanJobId] = useState<string | null>(null);

  async function handleStartScan() {
    try {
      setScanning(true);

      // Only use dev mode if explicitly enabled
      const isDevMode = localStorage.getItem('dev_mode') === 'true';

      if (isDevMode) {
        // Dev mode: Use seed endpoint for testing
        console.log('Dev mode active - using seed endpoint');
        const result = await api.dev.seedData();
        console.log('Seed data result:', result);
        alert(`✅ Scan complete!\n\nFound:\n• ${result.invoices_created} invoices\n• ${result.findings_created} issues\n\nRefreshing dashboard...`);
        setTimeout(() => window.location.reload(), 1500);
      } else {
        // Production: Real Gmail scan
        console.log('Starting real Gmail scan...');
        const scanJob = await api.scans.start();
        console.log('Scan job created:', scanJob);

        // Show progress modal instead of alert
        setScanJobId(scanJob.id);
        setShowProgress(true);
        setScanning(false);
      }
    } catch (error: any) {
      console.error('Failed to start scan:', error);
      const errorMsg = error.detail || error.message || 'Failed to start scan';

      if (error.status === 401) {
        alert(`❌ Authentication required\n\nPlease log in with your Google account to scan Gmail.`);
      } else if (error.status === 403) {
        alert(`❌ Permission denied\n\nMake sure you've granted Gmail access permissions.`);
      } else {
        alert(`❌ Scan failed:\n${errorMsg}`);
      }
    } finally {
      setScanning(false);
    }
  }

  return (
    <>
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-bold text-gray-900">Quick Actions</h3>
          <span className="text-xs text-gray-500">Frequently used</span>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <Button
            variant="primary"
            size="md"
            className="w-full"
            onClick={handleStartScan}
            disabled={scanning}
          >
            {scanning ? 'Starting...' : 'Scan Emails'}
          </Button>
          <Button variant="outline" size="md" className="w-full">
            Export CSV
          </Button>
          <Button variant="outline" size="md" className="w-full">
            Connect QB
          </Button>
          <Button variant="outline" size="md" className="w-full">
            Invite Team
          </Button>
        </div>
      </div>

      {showProgress && scanJobId && (
        <ScanProgressModal
          scanJobId={scanJobId}
          onComplete={() => {
            setShowProgress(false);
            setScanJobId(null);
            window.location.reload();
          }}
          onClose={() => {
            setShowProgress(false);
            setScanJobId(null);
          }}
        />
      )}
    </>
  );
}
