'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/hooks/useUser';

// Dynamically import AIAssistantUI with no SSR to avoid hydration issues
const AIAssistantUI = dynamic(() => import('../components/AIAssistantUI'), {
  ssr: false,
  loading: () => (
    <div className="h-screen w-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-600 dark:border-zinc-600 dark:border-t-zinc-300"></div>
          <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">Loading MITRA...</p>
        </div>
      </div>
    </div>
  )
});

export default function Page() {
  const [mounted, setMounted] = useState(false);
  const { user, loading } = useUser();
  const router = useRouter();
  
  useEffect(() => {
    setMounted(true);
  }, []);

  // Handle onboarding redirect
  useEffect(() => {
    if (!loading && user && !user.onboarding_completed) {
      router.push('/onboarding');
    }
  }, [user, loading, router]);

  if (!mounted) {
    return (
      <div className="h-screen w-full bg-zinc-50 text-zinc-900">
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-600"></div>
            <p className="mt-2 text-sm text-zinc-600">Initializing...</p>
          </div>
        </div>
      </div>
    );
  }

  // Show loading while checking authentication and onboarding status
  if (loading) {
    return (
      <div className="h-screen w-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-600 dark:border-zinc-600 dark:border-t-zinc-300"></div>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">Checking authentication...</p>
          </div>
        </div>
      </div>
    );
  }

  // Don't render main app if user needs onboarding (redirect will handle this)
  if (user && !user.onboarding_completed) {
    return (
      <div className="h-screen w-full bg-zinc-50 text-zinc-900 dark:bg-zinc-950 dark:text-zinc-100">
        <div className="flex h-full items-center justify-center">
          <div className="text-center">
            <div className="h-8 w-8 animate-spin rounded-full border-4 border-zinc-300 border-t-zinc-600 dark:border-zinc-600 dark:border-t-zinc-300"></div>
            <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">Redirecting to onboarding...</p>
          </div>
        </div>
      </div>
    );
  }

  return <AIAssistantUI />;
}
