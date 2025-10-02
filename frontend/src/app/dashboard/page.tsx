'use client'

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { HeroMetric } from '@/components/HeroMetric';
import { IssueCard } from '@/components/IssueCard';
import { FindingsTable } from '@/components/FindingsTable';
import { SavingsTracker } from '@/components/SavingsTracker';
import { ActivityLog } from '@/components/ActivityLog';
import { NotificationsPanel } from '@/components/NotificationsPanel';
import { QuickActionsBar } from '@/components/QuickActionsBar';
import { SecurityBadge } from '@/components/SecurityBadge';
import { FreeTierBanner } from '@/components/FreeTierBanner';
import { MobileActionBar } from '@/components/MobileActionBar';
import { Button } from '@/components/ui/Button';
import api, { FindingResponse } from '@/lib/api';
import { Finding, IssueSummary, DashboardStats } from '@/types';
import { ActivityLogItem, Notification, SavingsMetrics } from '@/types';

export default function DashboardPage() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [findings, setFindings] = useState<Finding[]>([]);
  const [issueSummaries, setIssueSummaries] = useState<IssueSummary[]>([]);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats | null>(null);
  const [savings, setSavings] = useState<SavingsMetrics>({ thisMonth: 0, thisYear: 0, total: 0 });
  const [activityLog, setActivityLog] = useState<ActivityLogItem[]>([]);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

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

      const summaries = mapSummariesToFrontend(findingsSummary);
      setIssueSummaries(summaries);

      const stats: DashboardStats = {
        totalWaste: Math.round((findingsSummary.total_guaranteed_waste + findingsSummary.total_potential_waste) * 100) / 100,
        lastScanned: scanJobs[0]?.completed_at ? new Date(scanJobs[0].completed_at) : new Date(),
        invoicesAnalyzed: invoiceStats.total_invoices || 0,
        issuesFound: findingsSummary.pending_count || 0,
        scansUsed: scanJobs.filter(j => j.status === 'completed').length || 0,
        scansLimit: 10,
      };
      setDashboardStats(stats);

      const totalResolvedSavings = findingsSummary.resolved_count > 0
        ? findingsSummary.total_guaranteed_waste * 0.5
        : 0;

      const calculatedSavings: SavingsMetrics = {
        thisMonth: Math.round(totalResolvedSavings * 0.4),
        thisYear: Math.round(totalResolvedSavings),
        total: Math.round(totalResolvedSavings * 1.2),
      };
      setSavings(calculatedSavings);

      const generatedActivity: ActivityLogItem[] = [
        scanJobs[0] && {
          id: '1',
          timestamp: new Date(scanJobs[0].completed_at || scanJobs[0].created_at),
          message: `Scanned ${scanJobs[0].total_emails.toLocaleString()} emails and found ${scanJobs[0].invoices_found} ${scanJobs[0].invoices_found === 1 ? 'invoice' : 'invoices'}`,
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

      const generatedNotifications: Notification[] = [
        findingsSummary.pending_count > 0 && {
          id: '1',
          type: 'new' as const,
          icon: 'NEW',
          message: `New: ${findingsSummary.pending_count} issues detected`,
          timestamp: new Date(),
        },
      ].filter(Boolean) as Notification[];
      setNotifications(generatedNotifications);

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

    return apiFindings.map(f => ({
      id: f.id,
      status: f.status === 'pending' ? 'new' : f.status === 'resolved' ? 'resolved' : 'in_progress',
      vendor: f.details?.vendor || 'Unknown',
      issue: f.description || f.title,
      amount: f.amount || 0,
      confidence: Math.round((f.confidence_score || 0) * 100),
      confidenceLevel: (f.confidence_score || 0) >= 0.95 ? 'certain' : 'likely',
      type: f.type === 'duplicate' ? 'duplicate' :
            f.type === 'unused_subscription' ? 'subscription' :
            f.type === 'price_increase' ? 'price_increase' : 'duplicate',
      dateFound: new Date(f.created_at),
    }));
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
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
              {user && (
                <div className="hidden md:flex items-center gap-3">
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">{user.name}</div>
                    <div className="text-xs text-gray-500">{user.email}</div>
                  </div>
                  {user.picture && (
                    <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                  )}
                </div>
              )}
              <Button variant="primary" size="sm">
                Upgrade
              </Button>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
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
          />

          {/* Issue Cards Grid - The Hook Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Issues Detected</h2>
                <p className="text-sm text-gray-600 mt-1">Potential savings opportunities across your subscriptions</p>
              </div>
              {dashboardStats.issuesFound > 0 && (
                <Button variant="outline" size="sm">
                  View All
                </Button>
              )}
            </div>

            {dashboardStats.issuesFound > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {issueSummaries.map((summary, idx) => (
                  <div key={summary.type} className={`delay-${(idx + 1) * 100}`}>
                    <IssueCard summary={summary} />
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

          {/* Quick Actions Bar - Desktop Only */}
          <div className="hidden md:block">
            <QuickActionsBar />
          </div>

          {/* Savings Tracker - Mobile */}
          <div className="md:hidden">
            <SavingsTracker savings={savings} />
          </div>

          {/* Smart Notifications */}
          {notifications.length > 0 && <NotificationsPanel notifications={notifications} />}

          {/* Findings Table - The Proof Section */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Detailed Findings</h2>
              <p className="text-sm text-gray-600 mt-1">Review and take action on identified issues</p>
            </div>
            <FindingsTable findings={findings} />
          </div>

          {/* Bottom Section - Engagement & Trust */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {activityLog.length > 0 && (
              <div className="animate-slide-in delay-100">
                <ActivityLog activities={activityLog} />
              </div>
            )}
            {notifications.length > 0 && (
              <div className="space-y-6 animate-slide-in delay-200">
                <NotificationsPanel notifications={notifications} />
              </div>
            )}
          </div>

          {/* Security Badge */}
          <SecurityBadge />
        </div>
      </main>

      {/* Mobile Action Bar */}
      <MobileActionBar />
    </div>
  );
}
