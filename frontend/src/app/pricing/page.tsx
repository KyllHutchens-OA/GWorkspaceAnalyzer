'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';

interface PricingTier {
  id: string;
  name: string;
  price: number;
  billing_period: string;
  description: string;
  features: string[];
  limits?: {
    invoice_limit: number;
    gmail_accounts: number;
  };
  roi?: string;
  guarantee?: string;
  contact_sales?: boolean;
}

export default function PricingPage() {
  const router = useRouter();
  const [tiers, setTiers] = useState<PricingTier[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTier, setCurrentTier] = useState<string>('free');

  useEffect(() => {
    fetchPricing();
    fetchCurrentSubscription();
  }, []);

  const fetchPricing = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscription/pricing`);
      const data = await response.json();
      setTiers(data.tiers || []);
    } catch (error) {
      console.error('Failed to fetch pricing:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentSubscription = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscription/status`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setCurrentTier(data.subscription.tier);
      }
    } catch (error) {
      console.error('Failed to fetch subscription:', error);
    }
  };

  const handleUpgrade = async (tierId: string) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/login');
      return;
    }

    if (tierId === 'free') {
      router.push('/login');
      return;
    }

    router.push(`/upgrade?tier=${tierId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading pricing...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Stop Wasting Money on Duplicate Charges
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Automatically scan your Gmail for invoices and catch duplicate charges, zombie subscriptions, and price increases.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {tiers.map((tier) => (
            <PricingCard
              key={tier.id}
              tier={tier}
              currentTier={currentTier}
              onSelect={() => handleUpgrade(tier.id)}
            />
          ))}
        </div>

        <div className="mt-16 bg-white rounded-lg shadow-sm p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Money-Back Guarantee</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            If we don't save you at least $500 in the first 30 days on the Saver plan,
            we'll refund your money and give you an extra $100 for wasting your time.
          </p>
        </div>

        <div className="mt-8 text-center">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

function PricingCard({
  tier,
  currentTier,
  onSelect,
}: {
  tier: PricingTier;
  currentTier: string;
  onSelect: () => void;
}) {
  const isCurrentTier = currentTier === tier.id;
  const isPopular = tier.id === 'saver';
  const isFree = tier.id === 'free';

  return (
    <Card className={`relative flex flex-col ${isPopular ? 'ring-2 ring-blue-600' : ''}`}>
      {isPopular && (
        <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
          <span className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium">
            Most Popular
          </span>
        </div>
      )}

      <div className="p-6 flex-1">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">{tier.name}</h3>
        <p className="text-gray-600 text-sm mb-4">{tier.description}</p>

        <div className="mb-6">
          <span className="text-4xl font-bold text-gray-900">${tier.price}</span>
          {tier.price > 0 && (
            <span className="text-gray-600 ml-2">/{tier.billing_period}</span>
          )}
        </div>

        {tier.roi && (
          <div className="mb-4 p-3 bg-green-50 rounded-lg">
            <p className="text-sm font-medium text-green-800">
              {tier.roi} ROI
            </p>
          </div>
        )}

        <div className="space-y-3 mb-6">
          {tier.features.map((feature, index) => (
            <div key={index} className="flex items-start">
              <svg
                className="h-5 w-5 text-green-500 mr-2 flex-shrink-0 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <span className="text-sm text-gray-700">{feature}</span>
            </div>
          ))}
        </div>

        {tier.guarantee && (
          <p className="text-xs text-gray-500 mb-4 italic">{tier.guarantee}</p>
        )}
      </div>

      <div className="p-6 pt-0">
        <Button
          onClick={onSelect}
          variant={isPopular ? 'primary' : 'outline'}
          fullWidth
          disabled={isCurrentTier}
        >
          {isCurrentTier
            ? 'Current Plan'
            : tier.contact_sales
            ? 'Contact Sales'
            : isFree
            ? 'Start Free Audit'
            : `Upgrade to ${tier.name}`}
        </Button>
      </div>
    </Card>
  );
}
