import { Card, CardBody } from './Card';

interface StatCardProps {
  label: string;
  value: string | number;
  subtext?: string;
  icon?: string;
  trend?: 'up' | 'down';
  className?: string;
}

export function StatCard({ label, value, subtext, icon, trend, className = '' }: StatCardProps) {
  return (
    <Card className={className}>
      <CardBody>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-600">{label}</p>
            <div className="mt-2 flex items-baseline">
              <p className="text-3xl font-bold text-gray-900">{value}</p>
              {trend && (
                <span
                  className={`ml-2 text-sm font-medium ${
                    trend === 'up' ? 'text-red-600' : 'text-green-600'
                  }`}
                >
                  {trend === 'up' ? '↑' : '↓'}
                </span>
              )}
            </div>
            {subtext && <p className="mt-1 text-sm text-gray-500">{subtext}</p>}
          </div>
          {icon && <span className="text-4xl ml-4">{icon}</span>}
        </div>
      </CardBody>
    </Card>
  );
}
