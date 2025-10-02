'use client';

import { useState, useEffect } from 'react';
import { Finding } from '@/types';
import { Button } from './ui/Button';
import api from '@/lib/api';

interface Invoice {
  id: string;
  vendor_name: string;
  invoice_number: string;
  amount: number;
  invoice_date: string;
  due_date?: string;
  extraction_method: string;
  confidence_score: number;
}

interface FindingDetailModalProps {
  finding: Finding;
  onClose: () => void;
}

export function FindingDetailModal({ finding, onClose }: FindingDetailModalProps) {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInvoices();
  }, [finding.id]);

  async function loadInvoices() {
    try {
      setLoading(true);
      const data = await api.findings.getInvoices(finding.id);
      setInvoices(data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setLoading(false);
    }
  }

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'duplicate':
        return 'Duplicate Charge';
      case 'subscription':
        return 'Zombie Subscription';
      case 'price_increase':
        return 'Price Increase';
      default:
        return type;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'duplicate':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'subscription':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'price_increase':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-5 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1 rounded-lg text-sm font-semibold border ${getTypeColor(finding.type)}`}>
              {getTypeLabel(finding.type)}
            </div>
            <h2 className="text-xl font-bold text-gray-900">{finding.vendor}</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {/* Summary */}
          <div className="mb-6">
            <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <div className="text-sm text-gray-600 mb-1">Total Amount</div>
                  <div className="text-2xl font-black text-gray-900">${finding.amount.toLocaleString()}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Issue</div>
                  <div className="text-sm font-medium text-gray-900">{finding.issue}</div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-1">Date Found</div>
                  <div className="text-sm font-medium text-gray-900">
                    {finding.dateFound.toLocaleDateString()}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Related Invoices */}
          <div>
            <h3 className="text-lg font-bold text-gray-900 mb-4">
              Related Invoices ({invoices.length})
            </h3>

            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"></div>
                <p className="mt-2 text-sm text-gray-600">Loading invoices...</p>
              </div>
            ) : invoices.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
                <p className="text-gray-600">No invoices found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {invoices.map((invoice) => (
                  <div
                    key={invoice.id}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:border-emerald-300 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div>
                          <div className="text-xs text-gray-500 mb-0.5">Date</div>
                          <div className="text-sm font-medium text-gray-900">
                            {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'No date'}
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs text-gray-500 mb-0.5">Amount</div>
                        <div className="text-lg font-bold text-gray-900">${invoice.amount.toLocaleString()}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            Status: <span className="font-semibold text-gray-900 capitalize">{finding.status}</span>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" size="sm" onClick={onClose}>
              Close
            </Button>
            <Button variant="primary" size="sm">
              Mark as Resolved
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
