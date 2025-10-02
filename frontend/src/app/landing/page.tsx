'use client';

import { Button } from '@/components/ui/Button';
import { useAuth } from '@/contexts/AuthContext';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { DEV_MODE, DEV_USER, DEV_TOKEN } from '@/lib/devMode';

export default function LandingPage() {
  const { login, setUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const router = useRouter();

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await login();
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message || 'Failed to login');
      setIsLoading(false);
    }
  };

  const handleDevLogin = () => {
    if (!DEV_MODE) {
      setError('Dev mode only available in development environment');
      return;
    }

    try {
      api.setAuthToken(DEV_TOKEN);
      setUser(DEV_USER);
      localStorage.setItem('dev_mode', 'true');
      console.log('Dev mode login successful');
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Dev login failed');
    }
  };

  const openLoginModal = () => {
    setShowLoginModal(true);
  };

  const closeLoginModal = () => {
    setShowLoginModal(false);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-gray-200 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-slate-800 to-slate-600 rounded-lg" />
              <span className="text-lg font-bold text-gray-900">Spend Analyzer</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="#how-it-works" className="hidden md:block text-sm font-medium text-gray-600 hover:text-gray-900">
                How it Works
              </a>
              <a href="#pricing" className="hidden md:block text-sm font-medium text-gray-600 hover:text-gray-900">
                Pricing
              </a>
              <a href="#faq" className="hidden md:block text-sm font-medium text-gray-600 hover:text-gray-900">
                FAQ
              </a>
              <Button variant="outline" size="sm" onClick={openLoginModal}>
                Login
              </Button>
              <Button variant="primary" size="sm" onClick={openLoginModal}>
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center max-w-4xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-slate-50 border border-slate-200 rounded-full mb-6">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
              <span className="text-sm font-medium text-slate-700">Automatic invoice analysis for Google Workspace</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Stop wasting money on
              <span className="block text-slate-700">duplicate charges</span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 mb-10 leading-relaxed">
              Automatically scan your Gmail for invoices and receipts. Identify duplicates, unused subscriptions, and price increases in minutes.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Button variant="primary" size="lg" onClick={openLoginModal}>
                Start Free Scan
              </Button>
              <Button variant="outline" size="lg" onClick={() => document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })}>
                See How It Works
              </Button>
            </div>

            <p className="text-sm text-gray-500">
              No credit card required • Scan 90 days of invoices free • 2-minute setup
            </p>
          </div>

          {/* Hero Visual - Dashboard Preview */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-t from-white via-transparent to-transparent h-32 bottom-0 z-10" />
            <div className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-2xl border-2 border-gray-200 shadow-2xl p-6 md:p-8">
              <div className="bg-white rounded-xl border border-gray-200 p-4 md:p-6 mb-4">
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <div className="text-sm text-gray-600 mb-1">Monthly overspend detected</div>
                    <div className="text-4xl md:text-5xl font-bold text-gray-900">$4,850</div>
                  </div>
                  <div className="px-3 py-1.5 bg-red-50 border border-red-200 rounded-full">
                    <span className="text-sm font-semibold text-red-700">12 Issues Found</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-3">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <div className="text-2xl font-bold text-gray-900">$2,499</div>
                    <div className="text-xs text-gray-600 mt-1">Duplicates</div>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                    <div className="text-2xl font-bold text-gray-900">$1,890</div>
                    <div className="text-xs text-gray-600 mt-1">Unused</div>
                  </div>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
                    <div className="text-2xl font-bold text-gray-900">$461</div>
                    <div className="text-xs text-gray-600 mt-1">Increases</div>
                  </div>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-500">
                <div className="bg-white rounded-lg border border-gray-200 p-3">
                  <div className="font-semibold text-gray-900 mb-1">AWS - Duplicate Charge</div>
                  <div>Invoice #12345 charged twice on Jan 15</div>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-3">
                  <div className="font-semibold text-gray-900 mb-1">Zoom - Unused Seats</div>
                  <div>Paying for 50 licenses, only 28 active</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Find savings in 3 simple steps
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              No manual data entry. No spreadsheets. Just connect your Gmail and let us do the work.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-900 text-white rounded-2xl mb-6 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Connect Gmail</h3>
              <p className="text-gray-600 leading-relaxed">
                Sign in with Google Workspace. We only access invoice and receipt emails, never personal messages.
              </p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-900 text-white rounded-2xl mb-6 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Automatic Scan</h3>
              <p className="text-gray-600 leading-relaxed">
                Our AI scans the last 90 days of invoices, extracting vendor names, amounts, and dates automatically.
              </p>
            </div>

            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-900 text-white rounded-2xl mb-6 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Review Savings</h3>
              <p className="text-gray-600 leading-relaxed">
                Get a detailed report of duplicates, unused subscriptions, and price increases. Take action instantly.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Catch every costly mistake
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Advanced detection algorithms identify issues that manual review would miss.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Duplicate Detection</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                Identifies exact and probable duplicate charges, including same vendor billed multiple times within days.
              </p>
              <div className="text-sm text-gray-500 font-medium">
                Average savings: $2,100/month
              </div>
            </div>

            <div className="bg-white border-2 border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-yellow-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Subscription Tracking</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                Finds unused seats, overlapping services, and forgotten subscriptions draining your budget.
              </p>
              <div className="text-sm text-gray-500 font-medium">
                Average savings: $1,800/month
              </div>
            </div>

            <div className="bg-white border-2 border-gray-200 rounded-2xl p-8 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-orange-100 rounded-xl flex items-center justify-center mb-6">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Price Monitoring</h3>
              <p className="text-gray-600 leading-relaxed mb-4">
                Alerts you to vendor price increases over time, so you can negotiate or switch before costs spiral.
              </p>
              <div className="text-sm text-gray-500 font-medium">
                Average savings: $600/month
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Security */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white border-2 border-gray-200 rounded-2xl p-8 md:p-12">
            <div className="flex items-start gap-4 mb-6">
              <div className="w-12 h-12 bg-slate-100 rounded-xl flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-slate-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Your data stays private</h3>
                <p className="text-lg text-gray-600 leading-relaxed mb-6">
                  We only access emails containing invoices and receipts. Your personal emails, contacts, and other data remain completely private and are never accessed or stored.
                </p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">256-bit Encryption</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">GDPR Compliant</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    <span className="text-sm font-medium text-gray-700">No Data Sharing</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Simple, transparent pricing
            </h2>
            <p className="text-xl text-gray-600">
              Start free. Upgrade only if we find significant savings.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border-2 border-gray-200 rounded-2xl p-8">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Free Scan</h3>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold text-gray-900">$0</span>
                </div>
                <p className="text-gray-600 mt-2">Perfect for getting started</p>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">One-time 90-day scan</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">Full analysis report</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">Dashboard access for 7 days</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span className="text-gray-700">Export report (PDF/CSV)</span>
                </li>
              </ul>

              <Button variant="outline" size="lg" className="w-full" onClick={openLoginModal}>
                Start Free Scan
              </Button>
            </div>

            <div className="bg-slate-900 text-white border-2 border-slate-900 rounded-2xl p-8 relative">
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 px-4 py-1 bg-emerald-500 text-white text-sm font-bold rounded-full">
                BEST VALUE
              </div>

              <div className="mb-6">
                <h3 className="text-2xl font-bold mb-2">Pro Plan</h3>
                <div className="flex items-baseline gap-2">
                  <span className="text-5xl font-bold">$49</span>
                  <span className="text-gray-400">/month</span>
                </div>
                <p className="text-gray-400 mt-2">Continuous monitoring and alerts</p>
              </div>

              <ul className="space-y-3 mb-8">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Everything in Free, plus:</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Continuous monitoring</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Weekly email digests</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Real-time alerts for duplicates</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Unlimited historical scans</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  <span>Priority support</span>
                </li>
              </ul>

              <Button variant="primary" size="lg" className="w-full bg-white text-slate-900 hover:bg-gray-100" onClick={openLoginModal}>
                Start Free Trial
              </Button>
            </div>
          </div>

          <p className="text-center text-gray-600 mt-8">
            All plans include a 30-day money-back guarantee. Cancel anytime.
          </p>
        </div>
      </section>

      {/* FAQ */}
      <section id="faq" className="py-24 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-3xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Frequently asked questions
            </h2>
          </div>

          <div className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">What emails do you access?</h3>
              <p className="text-gray-600 leading-relaxed">
                We only access emails that contain invoices, receipts, and billing statements. Your personal emails, contacts, calendar, and other data remain completely private and are never accessed.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">How long does the scan take?</h3>
              <p className="text-gray-600 leading-relaxed">
                Most scans complete within 2-5 minutes, depending on how many invoices you have. You'll receive an email notification when your analysis is ready.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Can I delete my data?</h3>
              <p className="text-gray-600 leading-relaxed">
                Yes, absolutely. You can delete all your data at any time from your account settings. Once deleted, all invoice data and analysis results are permanently removed from our servers.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">What file formats do you support?</h3>
              <p className="text-gray-600 leading-relaxed">
                We support PDF attachments, image files (JPEG, PNG), HTML email receipts, and structured data. Our OCR technology can extract data from scanned documents and screenshots.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">Do you integrate with accounting software?</h3>
              <p className="text-gray-600 leading-relaxed">
                Not yet, but it's on our roadmap. Currently, you can export your findings as PDF or CSV files to use with your existing accounting tools.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h3 className="text-lg font-bold text-gray-900 mb-2">What happens after the free scan?</h3>
              <p className="text-gray-600 leading-relaxed">
                After your free scan, you'll have 7 days to review your results in the dashboard. You can export the report for free. To enable ongoing monitoring and alerts, upgrade to the Pro plan for $49/month.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Ready to stop wasting money?
          </h2>
          <p className="text-xl text-gray-600 mb-10">
            Join businesses who have saved thousands by catching billing mistakes automatically.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button variant="primary" size="lg" onClick={openLoginModal}>
              Start Free Scan
            </Button>
          </div>
          <p className="text-sm text-gray-500 mt-6">
            Takes 2 minutes to set up • No credit card required
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 py-12 px-4 sm:px-6 lg:px-8 bg-slate-50">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            <div>
              <h4 className="font-bold text-gray-900 mb-3">Product</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#how-it-works" className="hover:text-gray-900">How it Works</a></li>
                <li><a href="#pricing" className="hover:text-gray-900">Pricing</a></li>
                <li><a href="#faq" className="hover:text-gray-900">FAQ</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-3">Company</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">About</a></li>
                <li><a href="#" className="hover:text-gray-900">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-3">Legal</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-gray-900">Terms of Service</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-900 mb-3">Connect</h4>
              <ul className="space-y-2 text-sm text-gray-600">
                <li><a href="#" className="hover:text-gray-900">Twitter</a></li>
                <li><a href="#" className="hover:text-gray-900">LinkedIn</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-200 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 bg-gradient-to-br from-slate-800 to-slate-600 rounded-lg" />
              <span className="font-bold text-gray-900">Spend Analyzer</span>
            </div>
            <p className="text-sm text-gray-500">
              © 2025 Spend Analyzer. All rights reserved.
            </p>
          </div>
        </div>
      </footer>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 relative">
            <button
              onClick={closeLoginModal}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="text-center mb-6">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-slate-800 to-slate-600 rounded-2xl mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Get Started</h2>
              <p className="text-gray-600">Connect your Gmail to start finding savings</p>
            </div>

            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            <Button
              variant="primary"
              size="lg"
              className="w-full mb-4"
              onClick={handleGoogleLogin}
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <div className="w-5 h-5 mr-2 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
                    <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                    <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                    <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                    <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                  </svg>
                  Continue with Google Workspace
                </>
              )}
            </Button>

            {DEV_MODE && (
              <>
                <div className="relative my-4">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white text-gray-500">Development Mode</span>
                  </div>
                </div>

                <Button
                  onClick={handleDevLogin}
                  variant="outline"
                  className="w-full mb-4"
                  size="lg"
                >
                  Dev Login (No OAuth)
                </Button>
              </>
            )}

            <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 mt-6">
              <div className="flex items-start gap-2">
                <svg className="w-5 h-5 text-slate-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <p className="text-xs text-slate-600">
                  We only access invoice and receipt emails. Your personal emails remain private and encrypted.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
