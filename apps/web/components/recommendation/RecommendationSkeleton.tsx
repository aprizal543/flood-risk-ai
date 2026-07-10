"use client";

import { LoadingSkeleton } from "@/components/shared";

export function RecommendationSkeleton() {
  return (
    <div className="space-y-4">
      <LoadingSkeleton className="h-4 w-48" />
      <LoadingSkeleton className="h-3 w-64" />
      <div className="space-y-2">
        <LoadingSkeleton className="h-12 w-full rounded-[var(--radius-weather)]" />
        <LoadingSkeleton className="h-20 w-full rounded-[var(--radius-weather)]" />
        <LoadingSkeleton className="h-20 w-full rounded-[var(--radius-weather)]" />
      </div>
      <div className="space-y-2">
        <LoadingSkeleton className="h-12 w-full rounded-[var(--radius-weather)]" />
        <LoadingSkeleton className="h-20 w-full rounded-[var(--radius-weather)]" />
      </div>
    </div>
  );
}
