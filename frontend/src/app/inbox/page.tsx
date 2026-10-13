'use client';

/**
 * Inbox page — Asynchronous Clinical Trial Inbox (REQ-07, REQ-10).
 * Polls for new items every 30 seconds.
 */

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { InboxDashboard } from "@/components/InboxDashboard/InboxDashboard";
import { getInbox, markReviewed, ApiError } from "@/lib/apiClient";
import { getCurrentUser } from "@/lib/auth";
import type { InboxItem } from "@/types";

const POLL_INTERVAL_MS = 30_000; // 30 seconds

export default function InboxPage() {
  const router = useRouter();
  const [items, setItems] = useState<InboxItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [authError, setAuthError] = useState<string | null>(null);

  const fetchInbox = useCallback(async () => {
    const user = getCurrentUser();
    if (!user) {
      router.push("/login");
      return;
    }

    try {
      const resp = await getInbox();
      setItems(resp.items);
      setUnreadCount(resp.unread_count);
      setAuthError(null);
    } catch (err) {
      if (err instanceof ApiError && (err.status === 401 || err.status === 403)) {
        setAuthError(
          err.status === 401
            ? "You must be signed in to view the inbox."
            : "You do not have permission to view the inbox."
        );
      }
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  // Initial load + polling
  useEffect(() => {
    fetchInbox();
    const interval = setInterval(fetchInbox, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchInbox]);

  const handleMarkReviewed = useCallback(
    async (id: string) => {
      await markReviewed(id);
      setItems((prev) =>
        prev.map((item) =>
          item.id === id ? { ...item, status: "reviewed" } : item
        )
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    },
    []
  );

  if (authError) {
    return (
      <div
        role="alert"
        className="mx-auto max-w-lg rounded-xl border border-red-200 bg-red-50 p-8 text-center"
      >
        <p className="text-base font-semibold text-red-700">{authError}</p>
        <a
          href="/login"
          className="mt-4 inline-block text-sm text-blue-600 hover:underline"
        >
          Sign in
        </a>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl">
      <InboxDashboard
        items={items}
        unreadCount={unreadCount}
        onMarkReviewed={handleMarkReviewed}
        isLoading={isLoading}
      />
    </div>
  );
}
