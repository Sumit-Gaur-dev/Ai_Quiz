'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/features/auth/AuthContext';

export default function DashboardPage() {
  const router = useRouter();
  const { user, session, loading: authLoading, signOut } = useAuth();

  const [profile, setProfile] = useState(null);
  const [profileLoading, setProfileLoading] = useState(false);
  const [editName, setEditName] = useState('');
  const [updating, setUpdating] = useState(false);
  const [feedback, setFeedback] = useState({ type: '', message: '' });

  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/login');
    }
  }, [user, authLoading, router]);

  // Fetch backend profile data using token
  useEffect(() => {
    if (session?.access_token) {
      const fetchProfile = async () => {
        setProfileLoading(true);
        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api/v1';

        try {
          const res = await fetch(`${apiBase}/profiles/me`, {
            headers: {
              Authorization: `Bearer ${session.access_token}`,
            },
          });

          if (res.ok) {
            const data = await res.json();
            setProfile(data.profile);
            setEditName(data.profile.display_name || '');
          }
        } catch (err) {
          console.error('Failed to load profile:', err);
        } finally {
          setProfileLoading(false);
        }
      };

      fetchProfile();
    }
  }, [session]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!editName.trim()) return;

    setUpdating(true);
    setFeedback({ type: '', message: '' });

    const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000/api/v1';

    try {
      const res = await fetch(`${apiBase}/profiles/me`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${session.access_token}`,
        },
        body: JSON.stringify({ display_name: editName.trim() }),
      });

      const data = await res.json();

      if (res.ok) {
        setProfile(data.profile);
        setFeedback({ type: 'success', message: 'Profile updated successfully!' });
      } else {
        setFeedback({
          type: 'error',
          message: data.error?.message || 'Failed to update profile',
        });
      }
    } catch (err) {
      setFeedback({ type: 'error', message: err.message || 'Network error' });
    } finally {
      setUpdating(false);
    }
  };

  const handleSignOut = async () => {
    await signOut();
    router.push('/login');
  };

  if (authLoading || (!user && authLoading)) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-sm text-gray-500">Loading session...</p>
        </div>
      </main>
    );
  }

  if (!user) {
    return null; // router.push handles redirect
  }

  const displayName =
    profile?.display_name ||
    user.user_metadata?.display_name ||
    user.email?.split('@')[0] ||
    'Learner';

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Top Navigation */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link href="/dashboard" className="text-xl font-bold text-blue-600">
            AI Quiz Platform
          </Link>

          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-700 hidden sm:inline">
              Signed in as <strong className="font-medium text-gray-900">{user.email}</strong>
            </span>
            <button
              onClick={handleSignOut}
              className="px-3.5 py-1.5 text-sm font-medium text-gray-700 hover:text-gray-900 border border-gray-300 rounded-lg hover:bg-gray-100 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Welcome, {displayName}!</h1>
          <p className="text-gray-600 text-sm mt-1">
            Your personalized learning dashboard and quiz center.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* User Profile Card */}
          <div className="md:col-span-1 bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <h2 className="text-base font-semibold text-gray-900 mb-4">Account Profile</h2>

            {feedback.message && (
              <div
                className={`mb-4 p-3 rounded-lg text-xs ${
                  feedback.type === 'success'
                    ? 'bg-green-50 text-green-700 border border-green-200'
                    : 'bg-red-50 text-red-700 border border-red-200'
                }`}
              >
                {feedback.message}
              </div>
            )}

            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-gray-500 mb-1">
                  Email
                </label>
                <input
                  type="text"
                  disabled
                  value={user.email || ''}
                  className="w-full px-3 py-2 bg-gray-100 border border-gray-200 rounded-lg text-sm text-gray-500 cursor-not-allowed"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1" htmlFor="displayName">
                  Display name
                </label>
                <input
                  id="displayName"
                  type="text"
                  required
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  placeholder="Your display name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={updating || profileLoading}
                className="w-full py-2 px-3 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded-lg disabled:opacity-50 transition-colors"
              >
                {updating ? 'Saving...' : 'Update display name'}
              </button>
            </form>

            <div className="mt-6 pt-4 border-t border-gray-100 text-xs text-gray-400">
              <p>User ID: {user.id}</p>
              {profile?.created_at && (
                <p className="mt-1">
                  Joined: {new Date(profile.created_at).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>

          {/* Quick Actions / MVP Placeholders */}
          <div className="md:col-span-2 space-y-6">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900 mb-2">My Notes</h2>
              <p className="text-sm text-gray-500 mb-4">
                Upload and manage your study materials. Notes will be ingested and chunked in Phase 2.
              </p>
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center text-sm text-gray-400">
                Notes feature will be enabled in Phase 2
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <h2 className="text-base font-semibold text-gray-900 mb-2">Generated Quizzes</h2>
              <p className="text-sm text-gray-500 mb-4">
                Generate source-grounded quizzes directly from your notes. Quiz generation arrives in Phase 3.
              </p>
              <div className="border-2 border-dashed border-gray-200 rounded-lg p-6 text-center text-sm text-gray-400">
                Quiz generation feature will be enabled in Phase 3
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

