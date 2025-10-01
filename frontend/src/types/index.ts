export type IssueType = 'duplicate' | 'subscription' | 'price_increase';
export type IssueStatus = 'new' | 'in_progress' | 'resolved' | 'ignored';
export type ConfidenceLevel = 'certain' | 'likely' | 'possible';

export interface Finding {
  id: string;
  status: IssueStatus;
  vendor: string;
  issue: string;
  amount: number;
  confidence: number;
  confidenceLevel: ConfidenceLevel;
  type: IssueType;
  dateFound: Date;
}

export interface IssueSummary {
  type: IssueType;
  totalAmount: number;
  count: number;
  example: string;
  color: 'red' | 'yellow' | 'orange';
  icon: string;
  label: string;
}

export interface SavingsMetrics {
  thisMonth: number;
  thisYear: number;
  total: number;
}

export interface DashboardStats {
  totalWaste: number;
  lastScanned: Date;
  invoicesAnalyzed: number;
  issuesFound: number;
  scansUsed: number;
  scansLimit: number;
}

export interface ActivityLogItem {
  id: string;
  timestamp: Date;
  message: string;
  type: 'scan' | 'finding' | 'action' | 'alert';
}

export interface Notification {
  id: string;
  type: 'new' | 'trend' | 'reminder' | 'tip';
  icon: string;
  message: string;
  timestamp: Date;
}

export type AuthStatus = 'authenticated' | 'unauthenticated' | 'loading';
export type AuthError = 'access_denied' | 'invalid_scope' | 'server_error' | 'temporarily_unavailable' | 'unknown';

export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  emailVerified: boolean;
  createdAt: Date;
  lastLoginAt: Date;
}

export interface AuthSession {
  user: User;
  accessToken: string;
  refreshToken?: string;
  expiresAt: Date;
}
