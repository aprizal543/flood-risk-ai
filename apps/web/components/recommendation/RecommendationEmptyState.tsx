"use client";

import { type LucideIcon, Info, RefreshCw } from "lucide-react";

interface RecommendationEmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  onRetry?: () => void;
}

export function RecommendationEmptyState({
  icon: Icon = Info,
  title,
  description,
  onRetry,
}: RecommendationEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-3 text-[var(--text-muted)]">
      <Icon className="h-8 w-8" aria-hidden="true" />
      <div className="text-center">
        <p className="text-sm font-medium text-[var(--text-primary)]">{title}</p>
        <p className="text-[11px] text-[var(--text-muted)] mt-1 max-w-[280px]">{description}</p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-md bg-[var(--brand-primary)] text-white hover:bg-[var(--brand-primary-dark)] transition-colors"
        >
          <RefreshCw className="h-3 w-3" /> Coba Lagi
        </button>
      )}
    </div>
  );
}
