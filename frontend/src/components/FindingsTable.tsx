'use client';

import { useState } from 'react';
import { Finding, IssueType, ConfidenceLevel } from '@/types';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import { FindingCard } from './FindingCard';

interface FindingsTableProps {
  findings: Finding[];
}

type FilterType = 'all' | IssueType;
type FilterAmount = 'all' | '100' | '500' | '1000';
type FilterConfidence = 'all' | ConfidenceLevel;
type FilterStatus = 'all' | 'new' | 'in_progress' | 'resolved' | 'ignored';

export function FindingsTable({ findings }: FindingsTableProps) {
  const [filterType, setFilterType] = useState<FilterType>('all');
  const [filterAmount, setFilterAmount] = useState<FilterAmount>('all');
  const [filterConfidence, setFilterConfidence] = useState<FilterConfidence>('all');
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all');

  const filteredFindings = findings.filter((finding) => {
    if (filterType !== 'all' && finding.type !== filterType) return false;
    if (filterAmount !== 'all' && finding.amount < parseInt(filterAmount)) return false;
    if (filterConfidence !== 'all' && finding.confidenceLevel !== filterConfidence) return false;
    if (filterStatus !== 'all' && finding.status !== filterStatus) return false;
    return true;
  });

  const getStatusColor = (type: IssueType) => {
    switch (type) {
      case 'duplicate':
        return 'bg-red-500';
      case 'subscription':
        return 'bg-yellow-500';
      case 'price_increase':
        return 'bg-orange-500';
    }
  };

  // Sort by date for mobile (newest first)
  const sortedFindings = [...filteredFindings].sort((a, b) =>
    b.dateFound.getTime() - a.dateFound.getTime()
  );

  return (
    <div className="space-y-4">
      {/* Mobile Cards (Horizontal Scroll) */}
      <div className="md:hidden">
        <div className="flex gap-4 overflow-x-auto pb-4 snap-x snap-mandatory scrollbar-hide -mx-4 px-4">
          {sortedFindings.map((finding) => (
            <div key={finding.id} className="min-w-[85vw] snap-start">
              <FindingCard finding={finding} />
            </div>
          ))}
        </div>
        {sortedFindings.length === 0 && (
          <div className="text-center py-12 bg-white border border-gray-200 rounded-xl">
            <p className="text-gray-500">No findings match your filters</p>
          </div>
        )}
      </div>

      {/* Desktop Filters & Table */}
      <div className="hidden md:block space-y-4">
      {/* Filters */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-semibold text-gray-700 uppercase tracking-wide">Filters</h3>
          <button className="text-sm text-purple-600 hover:text-purple-700 font-medium">Reset</button>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Issue Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value as FilterType)}
              className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
            >
              <option value="all">All Issues</option>
              <option value="duplicate">Duplicates</option>
              <option value="subscription">Subscriptions</option>
              <option value="price_increase">Price Increases</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
            <select
              value={filterAmount}
              onChange={(e) => setFilterAmount(e.target.value as FilterAmount)}
              className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
            >
              <option value="all">All Amounts</option>
              <option value="100">Over $100</option>
              <option value="500">Over $500</option>
              <option value="1000">Over $1,000</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Confidence</label>
            <select
              value={filterConfidence}
              onChange={(e) => setFilterConfidence(e.target.value as FilterConfidence)}
              className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
            >
              <option value="all">All Levels</option>
              <option value="certain">Certain (100%)</option>
              <option value="likely">Likely (80%+)</option>
              <option value="possible">Possible (60%+)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value as FilterStatus)}
              className="w-full bg-white border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500 transition-colors"
            >
              <option value="all">All Statuses</option>
              <option value="new">New</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="ignored">Ignored</option>
            </select>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Vendor
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Issue
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
                  Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredFindings.map((finding, idx) => (
                <tr key={finding.id} className="hover:bg-gray-50 transition-colors group">
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(finding.type)} shadow-lg group-hover:scale-125 transition-transform`} />
                  </td>
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className="text-sm font-bold text-gray-900">{finding.vendor}</div>
                  </td>
                  <td className="px-6 py-5">
                    <div className="text-sm text-gray-700">{finding.issue}</div>
                  </td>
                  <td className="px-6 py-5 whitespace-nowrap">
                    <div className="text-base font-black text-gray-900">
                      ${finding.amount.toLocaleString()}
                      {finding.type === 'subscription' && (
                        <span className="text-xs font-medium text-gray-500">/mo</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge confidence={finding.confidenceLevel}>{finding.confidence}%</Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    {finding.type === 'duplicate' && (
                      <Button variant="danger" size="sm">
                        Dispute
                      </Button>
                    )}
                    {finding.type === 'subscription' && (
                      <Button variant="primary" size="sm">
                        {finding.issue.includes('unused') ? 'Downgrade' : 'Consolidate'}
                      </Button>
                    )}
                    {finding.type === 'price_increase' && (
                      <Button variant="outline" size="sm">
                        Negotiate
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {filteredFindings.length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500">No findings match your filters</p>
          </div>
        )}
      </div>
      </div>
    </div>
  );
}
