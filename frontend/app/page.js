'use client';

import Link from 'next/link';
import { useAuth } from '@/features/auth/AuthContext';

export default function Home() {
  const { user, loading } = useAuth();

  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-gray-50 to-gray-100">
      <div className="text-center max-w-2xl px-4">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          AI Quiz Platform
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Transform your notes into AI-powered quizzes. Upload your study
          materials and let AI generate personalized quizzes to test your
          knowledge.
        </p>

        {!loading && (
          <div className="flex gap-4 justify-center">
            {user ? (
              <Link
                href="/dashboard"
                className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
              >
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link
                  href="/signup"
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors shadow-sm"
                >
                  Get Started
                </Link>
                <Link
                  href="/login"
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-white transition-colors shadow-sm"
                >
                  Sign in
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
