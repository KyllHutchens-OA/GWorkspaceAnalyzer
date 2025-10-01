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
import {
  mockDashboardStats,
  mockIssueSummaries,
  mockFindings,
  mockSavings,
  mockActivityLog,
  mockNotifications,
} from '@/lib/mockData';

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg" />
              <div>
                <h1 className="text-lg font-bold text-gray-900">GWorkspace Analyzer</h1>
              </div>
            </div>
            <div className="flex items-center gap-6">
              <div className="hidden md:flex items-center gap-2">
                <span className="text-sm text-gray-600">Total Saved</span>
                <span className="text-2xl font-black text-green-600">${mockSavings.total.toLocaleString()}</span>
              </div>
              <Button variant="primary" size="sm">
                Upgrade
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
              scansUsed={mockDashboardStats.scansUsed}
              scansLimit={mockDashboardStats.scansLimit}
            />
          </div>

          {/* Hero Metric - Above the Fold */}
          <HeroMetric
            amount={mockDashboardStats.totalWaste}
            lastScanned={mockDashboardStats.lastScanned}
            invoicesAnalyzed={mockDashboardStats.invoicesAnalyzed}
            issuesFound={mockDashboardStats.issuesFound}
          />

          {/* Issue Cards Grid - The Hook Section */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Issues Detected</h2>
                <p className="text-sm text-gray-600 mt-1">Potential savings opportunities across your subscriptions</p>
              </div>
              <Button variant="outline" size="sm">
                View All
              </Button>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {mockIssueSummaries.map((summary, idx) => (
                <div key={summary.type} className={`delay-${(idx + 1) * 100}`}>
                  <IssueCard summary={summary} />
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions Bar - Desktop Only */}
          <div className="hidden md:block">
            <QuickActionsBar />
          </div>

          {/* Savings Tracker - Mobile */}
          <div className="md:hidden">
            <SavingsTracker savings={mockSavings} />
          </div>

          {/* Smart Notifications */}
          <NotificationsPanel notifications={mockNotifications} />

          {/* Findings Table - The Proof Section */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Detailed Findings</h2>
              <p className="text-sm text-gray-600 mt-1">Review and take action on identified issues</p>
            </div>
            <FindingsTable findings={mockFindings} />
          </div>

          {/* Bottom Section - Engagement & Trust */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="animate-slide-in delay-100">
              <ActivityLog activities={mockActivityLog} />
            </div>
            <div className="space-y-6 animate-slide-in delay-200">
              <NotificationsPanel notifications={mockNotifications} />
            </div>
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
