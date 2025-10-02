'use client';

export function MobileActionBar() {
  return (
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50 safe-area-inset-bottom">
      <div className="grid grid-cols-3 gap-2 p-3">
        <button className="flex flex-col items-center gap-1 py-2 px-3 rounded-lg hover:bg-gray-50 active:bg-gray-100 transition-colors">
          <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <span className="text-xs font-semibold text-gray-700">Scan</span>
        </button>

        <button className="flex flex-col items-center gap-1 py-2 px-3 rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 active:bg-emerald-800 transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          <span className="text-xs font-semibold">Review</span>
        </button>

        <button className="flex flex-col items-center gap-1 py-2 px-3 rounded-lg hover:bg-gray-50 active:bg-gray-100 transition-colors">
          <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          <span className="text-xs font-semibold text-gray-700">Export</span>
        </button>
      </div>
    </div>
  );
}
