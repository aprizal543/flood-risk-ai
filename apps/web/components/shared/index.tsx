"use client";

import { cn } from "@/lib/utils";
import { AlertTriangle, RefreshCw, Inbox } from "lucide-react";

/* ─── StatusBadge ─── */
interface StatusBadgeProps {
  level: string;
  className?: string;
}

const BADGE_COLORS: Record<string, string> = {
  "Risiko Rendah": "bg-[var(--risk-rendah)]/15 text-[var(--risk-rendah)]",
  "Risiko Sedang": "bg-[var(--risk-sedang)]/15 text-[var(--risk-sedang)]",
  "Risiko Tinggi": "bg-[var(--risk-tinggi)]/15 text-[var(--risk-tinggi)]",
};

export function StatusBadge({ level, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold",
        BADGE_COLORS[level] ?? "bg-neutral-100 text-neutral-600",
        className
      )}
      role="status"
      aria-label={level}
    >
      {level}
    </span>
  );
}

/* ─── LoadingSkeleton ─── */
export function LoadingSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-[var(--neutral-200)]", className)}
      aria-hidden="true"
    />
  );
}

/* ─── EmptyState ─── */
export function EmptyState({ pesan = "Tidak ada data tersedia" }: { pesan?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-2 text-[var(--text-muted)]">
      <Inbox className="h-8 w-8" aria-hidden="true" />
      <p className="text-sm">{pesan}</p>
    </div>
  );
}

/* ─── ErrorState ─── */
interface ErrorStateProps {
  pesan: string;
  onRetry?: () => void;
}

export function ErrorState({ pesan, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-8 gap-3 text-[var(--text-muted)]" role="alert">
      <AlertTriangle className="h-8 w-8 text-[var(--risk-sedang)]" aria-hidden="true" />
      <p className="text-sm text-center">{pesan}</p>
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
