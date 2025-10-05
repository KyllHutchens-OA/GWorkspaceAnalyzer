'use client'

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { HeroMetric } from '@/components/HeroMetric';
import { IssueCard } from '@/components/IssueCard';
import { FindingsTable } from '@/components/FindingsTable';
import { SavingsTracker } from '@/components/SavingsTracker';
import { ActivityLog } from '@/components/ActivityLog';
import { FreeTierBanner } from '@/components/FreeTierBanner';
import { MobileActionBar } from '@/components/MobileActionBar';
import { ScanProgressModal } from '@/components/ScanProgressModal';
import { TrialCountdownBanner } from '@/components/TrialCountdownBanner';
import { UsageLimitBanner } from '@/components/UsageLimitBanner';
import { Button } from '@/components/ui/Button';
import api, { FindingResponse } from '@/lib/api';
import { Finding, IssueSummary, DashboardStats } from '@/types';
import { ActivityLogItem, Notification, SavingsMetrics } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isLoading: authLoading, logout } = useAuth();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [filteredFindings, setFilteredFindings] = useState<Finding[]>([]);
  const [activeFilter, setActiveFilter] = useState<string | null>(null);
  const [issueSummaries, setIssueSummaries] = useState<IssueSummary[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [savings, setSavings] = useState<SavingsMetrics>({ thisMonth: 0, thisYear: 0, total: 0 });
  const [activityLog, setActivityLog] = useState<ActivityLogItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showScanProgress, setShowScanProgress] = useState(false);
  const [scanJobId, setScanJobId] = useState<string | null>(null);
  const findingsTableRef = useRef<HTMLDivElement>(null);

  const handleLogout = async () => {
    try {
      await logout();
      // Navigation handled by AuthContext logout
    } catch (error) {
      console.error('Logout error:', error);
      // Force navigation even if logout fails
      router.push('/login');
    }
  };

  const scrollToFindings = () => {
    findingsTableRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const handleFilterByType = (type: string) => {
    setActiveFilter(type);
    const filtered = findings.filter(f => f.type === type);
    setFilteredFindings(filtered);
    scrollToFindings();
  };

  const handleViewAllIssues = () => {
    setActiveFilter(null);
    setFilteredFindings(findings);
    scrollToFindings();
  };

  const handleExportCSV = () => {
    const dataToExport = activeFilter ? filteredFindings : findings;

    const headers = ['Vendor', 'Issue', 'Type', 'Amount', 'Status', 'Date Found'];
    const rows = dataToExport.map(f => [
      f.vendor,
      f.issue,
      f.type,
      f.amount.toString(),
      f.status,
      f.dateFound.toISOString()
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `findings-export-${new Date().toISOString().split('T')[0]}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleStartScan = async () => {
    try {
      const scanJob = await api.scans.start();
      setScanJobId(scanJob.id);
      setShowScanProgress(true);
    } catch (error: any) {
      console.error('Failed to start scan:', error);
      alert(`Failed to start scan: ${error.message || 'Unknown error'}`);
    }
  };

  useEffect(() => {
    // Wait for auth to finish loading
    if (authLoading) return;

    // Redirect to login if not authenticated
    if (!user) {
      router.push('/login');
      return;
    }

    // Load dashboard data only when authenticated
    loadDashboardData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user, authLoading]);

  async function loadDashboardData() {
    try {
      setLoading(true);
      setError(null);

      console.log('Loading dashboard data...');

      // Load data with individual error handling
      let findingsData: FindingResponse[] = [];
      let findingsSummary: any = { pending_count: 0, total_potential_waste: 0, by_type: {} };
      let invoiceStats: any = { total_invoices: 0 };
      let scanJobs: any[] = [];

      try {
        const response: any = await api.findings.list({ status: 'pending', page_size: 50 });
        console.log('Findings loaded:', response);
        // Handle paginated response
        findingsData = response.findings || response;
      } catch (e: any) {
        console.error('Failed to load findings:', e);
      }

      try {
        findingsSummary = await api.findings.getSummary();
        console.log('Summary loaded:', findingsSummary);
      } catch (e: any) {
        console.error('Failed to load summary:', e);
      }

      try {
        invoiceStats = await api.invoices.getStats();
        console.log('Invoice stats loaded:', invoiceStats);
      } catch (e: any) {
        console.error('Failed to load invoice stats:', e);
      }

      try {
        scanJobs = await api.scans.list(1);
        console.log('Scan jobs loaded:', scanJobs);
      } catch (e: any) {
        console.error('Failed to load scan jobs:', e);
      }

      const mappedFindings = mapFindingsToFrontend(findingsData);
      setFindings(mappedFindings);
      setFilteredFindings(mappedFindings);

      const summaries = mapSummariesToFrontend(findingsSummary);
      setIssueSummaries(summaries);

      const totalWaste = (findingsSummary.total_guaranteed_waste || 0) + (findingsSummary.total_potential_waste || 0);
      const stats: DashboardStats = {
        totalWaste: Math.round(totalWaste * 100) / 100 || 0,
        lastScanned: scanJobs[0]?.completed_at ? new Date(scanJobs[0].completed_at) : new Date(),
        invoicesAnalyzed: invoiceStats.total_invoices || 0,
        issuesFound: findingsSummary.pending_count || 0,
        scansUsed: scanJobs.filter(j => j.status === 'completed').length || 0,
        scansLimit: 10,
      };
      setDashboardStats(stats);

      const totalResolvedSavings = findingsSummary.resolved_count > 0
        ? (findingsSummary.total_guaranteed_waste || 0) * 0.5
        : 0;

      const totalPendingAmount = findingsSummary.total_potential_waste || 0;

      const calculatedSavings: SavingsMetrics = {
        thisMonth: Math.round(totalResolvedSavings * 0.4) || 0,
        thisYear: Math.round(totalResolvedSavings) || 0,
        total: Math.round(totalResolvedSavings * 1.2) || totalResolvedSavings || totalPendingAmount || 0,
      };
      setSavings(calculatedSavings);

      // Only show completed scans in activity log
      const completedScans = scanJobs.filter(j => j.status === 'completed');
      const latestCompletedScan = completedScans[0];

      const generatedActivity: ActivityLogItem[] = [
        latestCompletedScan && {
          id: '1',
          timestamp: new Date(latestCompletedScan.completed_at || latestCompletedScan.created_at),
          message: `Scanned ${latestCompletedScan.total_emails.toLocaleString()} emails and found ${latestCompletedScan.invoices_found} ${latestCompletedScan.invoices_found === 1 ? 'invoice' : 'invoices'}`,
          type: 'scan' as const,
        },
        invoiceStats.total_invoices > 0 && {
          id: '2',
          timestamp: new Date(),
          message: `Analyzed ${invoiceStats.total_invoices.toLocaleString()} ${invoiceStats.total_invoices === 1 ? 'invoice' : 'invoices'} totaling $${Math.round(invoiceStats.total_amount).toLocaleString()}`,
          type: 'action' as const,
        },
        findingsSummary.pending_count > 0 && {
          id: '3',
          timestamp: new Date(),
          message: `Detected ${findingsSummary.pending_count} ${findingsSummary.pending_count === 1 ? 'issue' : 'issues'} requiring attention worth $${stats.totalWaste.toLocaleString()}`,
          type: 'finding' as const,
        },
      ].filter(Boolean) as ActivityLogItem[];
      setActivityLog(generatedActivity);

    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(typeof err === 'string' ? err : err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }

  function mapFindingsToFrontend(apiFindings: FindingResponse[]): Finding[] {
    if (!Array.isArray(apiFindings)) {
      console.error('Expected array of findings, got:', apiFindings);
      return [];
    }

    return apiFindings.map(f => {
      // Extract vendor name from title (e.g., "Duplicate charge: AWS" -> "AWS")
      let vendor = 'Unknown';
      if (f.title) {
        const match = f.title.match(/:\s*(.+)$/);
        if (match) {
          vendor = match[1];
        }
      }

      return {
        id: f.id,
        status: f.status === 'pending' ? 'new' : f.status === 'resolved' ? 'resolved' : 'in_progress',
        vendor: vendor,
        issue: f.description || f.title,
        amount: f.amount || 0,
        confidence: Math.round((f.confidence_score || 0) * 100),
        confidenceLevel: (f.confidence_score || 0) >= 0.95 ? 'certain' : 'likely',
        type: f.type === 'duplicate' ? 'duplicate' :
              f.type === 'unused_subscription' ? 'subscription' :
              f.type === 'price_increase' ? 'price_increase' : 'duplicate',
        dateFound: new Date(f.created_at),
      };
    });
  }

  function mapSummariesToFrontend(summary: any): IssueSummary[] {
    const byType = summary.by_type || {};

    const duplicateData = byType.duplicate || { count: 0, total_amount: 0 };
    const subscriptionData = byType.unused_subscription || { count: 0, total_amount: 0 };
    const priceIncreaseData = byType.price_increase || { count: 0, total_amount: 0 };

    return [
      {
        type: 'duplicate',
        totalAmount: Math.round(duplicateData.total_amount * 100) / 100,
        count: duplicateData.count,
        example: 'Duplicate charges detected',
        color: 'red',
        icon: '',
        label: 'Duplicate Charges',
      },
      {
        type: 'subscription',
        totalAmount: Math.round(subscriptionData.total_amount * 100) / 100,
        count: subscriptionData.count,
        example: 'Unused subscriptions found',
        color: 'yellow',
        icon: '',
        label: 'Zombie Subscriptions',
      },
      {
        type: 'price_increase',
        totalAmount: Math.round(priceIncreaseData.total_amount * 100) / 100,
        count: priceIncreaseData.count,
        example: 'Price increases detected',
        color: 'orange',
        icon: '',
        label: 'Price Increases',
      },
    ];
  }

  // Show loading while auth is checking or data is loading
  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Redirect will happen in useEffect if not authenticated
  if (!user) {
    return null;
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-4xl mb-4">⚠️</div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">Failed to Load Dashboard</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <Button onClick={() => loadDashboardData()}>Retry</Button>
        </div>
      </div>
    );
  }

  if (!dashboardStats) {
    return null;
  }
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Subscription Banners */}
      <TrialCountdownBanner />
      <UsageLimitBanner />

      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-emerald-500 rounded-lg shadow-sm" />
              <div>
                <h1 className="text-lg font-bold text-gray-900">GWorkspace Analyzer</h1>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="hidden md:flex items-center gap-2">
                <span className="text-sm text-gray-600">Total Saved</span>
                <span className="text-2xl font-black text-green-600">${savings.total.toLocaleString()}</span>
              </div>
              <Button variant="primary" size="sm">
                Upgrade
              </Button>
              {user && (
                <div className="relative">
                  <button
                    onClick={() => setShowUserMenu(!showUserMenu)}
                    className="hidden md:flex items-center gap-3 hover:bg-gray-50 rounded-lg p-2 transition-colors"
                  >
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-xs text-gray-500">{user.email}</div>
                    </div>
                    {user.picture && (
                      <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                    )}
                    <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  {showUserMenu && (
                    <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                      <button
                        onClick={() => {
                          setShowUserMenu(false);
                          handleLogout();
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Logout
                      </button>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-12 pb-24 md:pb-12">
        <div className="space-y-8 md:space-y-12">
          {/* Free Tier Banner */}
          <div className="animate-slide-in">
            <FreeTierBanner
              scansUsed={dashboardStats.scansUsed}
              scansLimit={dashboardStats.scansLimit}
              lockedIssuesCount={0}
              lockedIssuesValue={0}
            />
          </div>

          {/* Hero Metric - Above the Fold */}
          <HeroMetric
            amount={dashboardStats.totalWaste}
            lastScanned={dashboardStats.lastScanned}
            invoicesAnalyzed={dashboardStats.invoicesAnalyzed}
            issuesFound={dashboardStats.issuesFound}
            onReviewAllIssues={handleViewAllIssues}
            onExportReport={handleExportCSV}
            onStartScan={handleStartScan}
          />

          {/* Issue Cards Grid - The Hook Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Issues Detected</h2>
                <p className="text-sm text-gray-600 mt-1">Potential savings opportunities across your subscriptions</p>
              </div>
              {dashboardStats.issuesFound > 0 && (
                <Button variant="outline" size="sm" onClick={handleViewAllIssues}>
                  View All
                </Button>
              )}
            </div>

            {dashboardStats.issuesFound > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {issueSummaries.map((summary, idx) => (
                  <div key={summary.type} className={`delay-${(idx + 1) * 100}`}>
                    <IssueCard
                      summary={summary}
                      onViewDetails={() => handleFilterByType(summary.type)}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-gradient-to-br from-emerald-50 to-teal-50 border-2 border-emerald-200 rounded-xl p-12 text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-emerald-600 rounded-full mb-4">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">All Clear!</h3>
                <p className="text-gray-600 max-w-md mx-auto">
                  {dashboardStats.invoicesAnalyzed > 0
                    ? `We analyzed ${dashboardStats.invoicesAnalyzed} invoices and found no duplicate charges, unused subscriptions, or unexpected price increases.`
                    : 'Run a scan to analyze your Gmail for invoices and find potential savings.'}
                </p>
                {dashboardStats.invoicesAnalyzed === 0 && (
                  <div className="mt-6">
                    <Button variant="primary" size="lg">
                      Start Your First Scan
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Savings Tracker - Mobile */}
          <div className="md:hidden">
            <SavingsTracker savings={savings} />
          </div>

          {/* Findings Table - The Proof Section */}
          <div ref={findingsTableRef}>
            <div className="mb-6 flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">
                  {activeFilter ? `${activeFilter === 'duplicate' ? 'Duplicate Charges' : activeFilter === 'subscription' ? 'Zombie Subscriptions' : 'Price Increases'}` : 'Detailed Findings'}
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  {activeFilter
                    ? `Showing ${filteredFindings.length} ${activeFilter} ${filteredFindings.length === 1 ? 'finding' : 'findings'}`
                    : 'Review and take action on identified issues'
                  }
                </p>
              </div>
              <div className="flex items-center gap-2">
                {activeFilter && (
                  <Button variant="outline" size="sm" onClick={handleViewAllIssues}>
                    Show All
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={handleExportCSV}>
                  Export CSV
                </Button>
              </div>
            </div>
            <FindingsTable findings={filteredFindings} />
          </div>

          {/* Bottom Section - Activity Log */}
          {activityLog.length > 0 && (
            <div className="animate-slide-in delay-100">
              <ActivityLog activities={activityLog} />
            </div>
          )}
        </div>
      </main>

      {/* Mobile Action Bar */}
      <MobileActionBar />

      {/* Scan Progress Modal */}
      {showScanProgress && scanJobId && (
        <ScanProgressModal
          scanJobId={scanJobId}
          onComplete={() => {
            // Reload page to show fresh data
            window.location.reload();
          }}
          onClose={() => {
            setShowScanProgress(false);
            setScanJobId(null);
          }}
        />
      )}
    </div>
  );
}
