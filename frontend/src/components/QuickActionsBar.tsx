import { Button } from './ui/Button';

export function QuickActionsBar() {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">Quick Actions</h3>
        <span className="text-xs text-gray-500">Frequently used</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <Button variant="primary" size="md" className="w-full">
          Scan Emails
        </Button>
        <Button variant="outline" size="md" className="w-full">
          Export CSV
        </Button>
        <Button variant="outline" size="md" className="w-full">
          Connect QB
        </Button>
        <Button variant="outline" size="md" className="w-full">
          Invite Team
        </Button>
      </div>
    </div>
  );
}
