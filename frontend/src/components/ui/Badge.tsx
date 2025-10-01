import { ConfidenceLevel } from '@/types';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'success' | 'warning' | 'danger' | 'info';
  confidence?: ConfidenceLevel;
}

export function Badge({ children, variant = 'default', confidence }: BadgeProps) {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  };

  const confidenceVariants = {
    certain: 'bg-green-100 text-green-800',
    likely: 'bg-yellow-100 text-yellow-800',
    possible: 'bg-orange-100 text-orange-800',
  };

  const className = confidence
    ? confidenceVariants[confidence]
    : variants[variant];

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${className}`}>
      {children}
    </span>
  );
}
