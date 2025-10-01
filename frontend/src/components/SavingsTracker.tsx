import { Card, CardBody, CardHeader } from './ui/Card';
import { Button } from './ui/Button';
import { SavingsMetrics } from '@/types';

interface SavingsTrackerProps {
  savings: SavingsMetrics;
}

export function SavingsTracker({ savings }: SavingsTrackerProps) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900">Savings Tracker</h3>
      </CardHeader>
      <CardBody>
        <div className="space-y-4">
          <div>
            <p className="text-sm text-gray-600">This Month</p>
            <p className="text-2xl font-bold text-green-600">
              ${savings.thisMonth.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">This Year</p>
            <p className="text-2xl font-bold text-green-600">
              ${savings.thisYear.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Total Saved</p>
            <p className="text-2xl font-bold text-green-600">
              ${savings.total.toLocaleString()}
            </p>
          </div>
          <div className="pt-4 space-y-2">
            <Button variant="outline" size="sm" className="w-full">
              Share Results
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              Download Report
            </Button>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
