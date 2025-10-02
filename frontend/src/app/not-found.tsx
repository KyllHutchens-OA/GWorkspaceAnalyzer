import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-sm border border-gray-200 p-8 text-center">
        <div className="text-6xl font-black text-slate-700 mb-4">404</div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Page not found</h2>
        <p className="text-gray-600 mb-6">
          The page you&rsquo;re looking for doesn&rsquo;t exist or has been moved.
        </p>
        <Link
          href="/dashboard"
          className="inline-block bg-emerald-600 text-white px-6 py-2.5 rounded-lg font-semibold hover:bg-emerald-700 transition-colors"
        >
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
}
