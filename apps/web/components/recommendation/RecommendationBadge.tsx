"use client";

import { cn } from "@/lib/utils";
import { CheckCircle2, HelpCircle, ThumbsDown, ThumbsUp } from "lucide-react";

export type RecommendationStatus = "recommended" | "sangat_direkomendasikan" | "alternative" | "not_recommended";

interface RecommendationBadgeProps {
  status: RecommendationStatus;
  className?: string;
}

const BADGE_CONFIG: Record<RecommendationStatus, { label: string; icon: typeof CheckCircle2; color: string; bg: string }> = {
  sangat_direkomendasikan: {
    label: "Sangat Direkomendasikan",
    icon: CheckCircle2,
    color: "#22c55e",
    bg: "#22c55e15",
  },
  recommended: {
    label: "Direkomendasikan",
    icon: ThumbsUp,
    color: "#3b82f6",
    bg: "#3b82f615",
  },
  alternative: {
    label: "Alternatif",
    icon: HelpCircle,
    color: "#f59e0b",
    bg: "#f59e0b15",
  },
  not_recommended: {
    label: "Tidak Direkomendasikan",
    icon: ThumbsDown,
    color: "#ef4444",
    bg: "#ef444415",
  },
};

export function RecommendationBadge({ status, className }: RecommendationBadgeProps) {
  const cfg = BADGE_CONFIG[status];
  const Icon = cfg.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-semibold",
        className
      )}
      style={{ backgroundColor: cfg.bg, color: cfg.color }}
      role="status"
      aria-label={cfg.label}
    >
      <Icon className="h-3 w-3" aria-hidden="true" />
      {cfg.label}
    </span>
  );
}
