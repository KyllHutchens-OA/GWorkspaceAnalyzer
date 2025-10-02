/**
 * API Client for GWorkspace Analyzer
 * Handles all backend communication with type safety
 */

import { Finding, IssueSummary, DashboardStats } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiError {
  message: string;
  status: number;
  detail?: string;
}

export interface ScanJob {
  id: string;
  user_id: string;
  org_id: string | null;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  start_date: string;
  end_date: string;
  total_emails: number;
  processed_emails: number;
  invoices_found: number;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Invoice {
  id: string;
  user_id: string;
  org_id: string | null;
  scan_job_id: string;
  email_id: string;
  vendor_name: string | null;
  amount: number | null;
  currency: string | null;
  invoice_number: string | null;
  invoice_date: string | null;
  due_date: string | null;
  raw_text: string | null;
  extraction_method: string | null;
  confidence_score: number | null;
  created_at: string;
}

export interface FindingResponse {
  id: string;
  org_id: string | null;
  type: 'duplicate' | 'unused_subscription' | 'price_increase' | 'anomaly';
  status: 'pending' | 'resolved' | 'ignored';
  title: string;
  description: string | null;
  amount: number;
  currency: string;
  confidence_score: number | null;
  details: Record<string, any> | null;
  created_at: string;
  resolved_by: string | null;
  resolved_at: string | null;
  user_notes: string | null;
}

class ApiClient {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    if (typeof window !== 'undefined') {
      this.authToken = localStorage.getItem('auth_token');
    }
  }

  setAuthToken(token: string | null) {
    this.authToken = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('auth_token', token);
      } else {
        localStorage.removeItem('auth_token');
      }
    }
  }

  getAuthToken(): string | null {
    return this.authToken;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    if (options.headers) {
      Object.assign(headers, options.headers);
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const error: ApiError = {
          message: errorData.detail || response.statusText,
          status: response.status,
          detail: errorData.detail,
        };
        throw error;
      }

      const data = await response.json();
      return data as T;
    } catch (error) {
      if ((error as ApiError).status) {
        throw error;
      }
      throw {
        message: 'Network error. Please check your connection.',
        status: 0,
      } as ApiError;
    }
  }

  // Auth endpoints
  auth = {
    getLoginUrl: async (): Promise<{ authorization_url: string }> => {
      return this.request('/api/v1/auth/google/login');
    },

    handleCallback: async (code: string, redirect_uri?: string): Promise<{ access_token: string; token_type: string; expires_in: number }> => {
      return this.request('/api/v1/auth/google/callback', {
        method: 'POST',
        body: JSON.stringify({ code, redirect_uri }),
      });
    },

    refreshToken: async (): Promise<{ access_token: string; token_type: string; expires_in: number }> => {
      return this.request('/api/v1/auth/refresh', {
        method: 'POST',
      });
    },

    getCurrentUser: async (): Promise<{
      id: string;
      email: string;
      org_id: string | null;
      preferences: Record<string, any>;
      last_scan_at: string | null;
      scan_count: number;
    }> => {
      return this.request('/api/v1/auth/me');
    },

    logout: () => {
      this.setAuthToken(null);
    },
  };

  // Scan job endpoints
  scans = {
    start: async (startDate?: string, endDate?: string): Promise<ScanJob> => {
      return this.request('/api/v1/scan/start', {
        method: 'POST',
        body: JSON.stringify({
          start_date: startDate,
          end_date: endDate,
        }),
      });
    },

    list: async (limit: number = 10): Promise<ScanJob[]> => {
      return this.request(`/api/v1/scan/jobs?limit=${limit}`);
    },

    get: async (jobId: string): Promise<ScanJob> => {
      return this.request(`/api/v1/scan/jobs/${jobId}`);
    },

    cancel: async (jobId: string): Promise<void> => {
      return this.request(`/api/v1/scan/jobs/${jobId}`, {
        method: 'DELETE',
      });
    },
  };

  // Invoice endpoints
  invoices = {
    list: async (params?: {
      page?: number;
      page_size?: number;
      vendor?: string;
      start_date?: string;
      end_date?: string;
      min_amount?: number;
      max_amount?: number;
    }): Promise<{
      invoices: Invoice[];
      total: number;
      page: number;
      page_size: number;
    }> => {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.page_size) queryParams.set('page_size', params.page_size.toString());
      if (params?.vendor) queryParams.set('vendor', params.vendor);
      if (params?.start_date) queryParams.set('start_date', params.start_date);
      if (params?.end_date) queryParams.set('end_date', params.end_date);
      if (params?.min_amount) queryParams.set('min_amount', params.min_amount.toString());
      if (params?.max_amount) queryParams.set('max_amount', params.max_amount.toString());

      const query = queryParams.toString();
      return this.request(`/api/v1/invoices${query ? '?' + query : ''}`);
    },

    get: async (invoiceId: string): Promise<Invoice> => {
      return this.request(`/api/v1/invoices/${invoiceId}`);
    },

    getStats: async (): Promise<{
      total_invoices: number;
      total_amount: number;
      currency: string;
      monthly_totals: Record<string, number>;
    }> => {
      return this.request('/api/v1/invoices/stats/summary');
    },

    listVendors: async (): Promise<Array<{
      vendor_name_normalized: string;
      invoice_count: number;
      total_spent: number;
      first_invoice_date: string;
      last_invoice_date: string;
    }>> => {
      return this.request('/api/v1/invoices/vendors/list');
    },
  };

  // Findings endpoints
  findings = {
    list: async (params?: {
      page?: number;
      page_size?: number;
      type?: string;
      status?: string;
    }): Promise<{
      findings: FindingResponse[];
      total: number;
      page: number;
      page_size: number;
    }> => {
      const queryParams = new URLSearchParams();
      if (params?.page) queryParams.set('page', params.page.toString());
      if (params?.page_size) queryParams.set('page_size', params.page_size.toString());
      if (params?.type) queryParams.set('type', params.type);
      if (params?.status) queryParams.set('status', params.status);

      const query = queryParams.toString();
      return this.request(`/api/v1/findings${query ? '?' + query : ''}`);
    },

    get: async (findingId: string): Promise<FindingResponse> => {
      return this.request(`/api/v1/findings/${findingId}`);
    },

    getInvoices: async (findingId: string): Promise<Invoice[]> => {
      return this.request(`/api/v1/findings/${findingId}/invoices`);
    },

    update: async (
      findingId: string,
      status: 'pending' | 'resolved' | 'ignored',
      user_notes?: string
    ): Promise<FindingResponse> => {
      return this.request(`/api/v1/findings/${findingId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status, user_notes }),
      });
    },

    getSummary: async (): Promise<{
      pending_count: number;
      resolved_count: number;
      ignored_count: number;
      total_guaranteed_waste: number;
      total_potential_waste: number;
      by_type: Record<string, { count: number; pending: number; total_amount: number }>;
    }> => {
      return this.request('/api/v1/findings/summary');
    },
  };

  // Development/testing endpoints
  dev = {
    seedData: async (): Promise<{ message: string; data: any }> => {
      return this.request('/api/v1/dev/seed', {
        method: 'POST',
      });
    },

    clearData: async (): Promise<{ message: string }> => {
      return this.request('/api/v1/dev/clear', {
        method: 'POST',
      });
    },
  };

  // Health check
  health = async (): Promise<{ status: string; version: string }> => {
    return this.request('/health');
  };
}

export const api = new ApiClient();
export default api;
