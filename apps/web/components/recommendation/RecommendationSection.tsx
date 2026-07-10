"use client";

import { motion } from "framer-motion";
import { Lightbulb, Info } from "lucide-react";
import type { KnowledgeRecommendation } from "@/types/api";
import { RecommendationGroup } from "./RecommendationGroup";
import { RecommendationSkeleton } from "./RecommendationSkeleton";
import { RecommendationEmptyState } from "./RecommendationEmptyState";

interface RecommendationSectionProps {
  knowledgeRecommendation: KnowledgeRecommendation | null | undefined;
  isLoading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
}

export function RecommendationSection({
  knowledgeRecommendation,
  isLoading,
  error,
  onRetry,
}: RecommendationSectionProps) {
  if (isLoading) {
    return <RecommendationSkeleton />;
  }

  if (error) {
    return (
      <RecommendationEmptyState
        icon={Info}
        title="Gagal Memuat Rekomendasi"
        description={error.message ?? "Terjadi kesalahan saat memuat rekomendasi berbasis knowledge."}
        onRetry={onRetry}
      />
    );
  }

  if (!knowledgeRecommendation) {
    return null;
  }

  const hasItems =
    knowledgeRecommendation.recommended.length > 0 ||
    knowledgeRecommendation.alternative.length > 0 ||
    knowledgeRecommendation.not_recommended.length > 0;

  if (!hasItems) {
    return (
      <RecommendationEmptyState
        icon={Info}
        title="Tidak Ada Rekomendasi"
        description="Belum tersedia rekomendasi komoditas berbasis basis pengetahuan untuk kondisi saat ini."
      />
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-4"
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-1">
        <div className="h-6 w-6 rounded-lg bg-[var(--brand-primary)]/10 flex items-center justify-center">
          <Lightbulb className="h-3.5 w-3.5 text-[var(--brand-primary)]" />
        </div>
        <span className="text-[11px] font-semibold text-[var(--text-primary)]">
          Rekomendasi Berbasis Pengetahuan
        </span>
      </div>
      <p className="text-[11px] text-[var(--text-muted)] leading-relaxed -mt-1">
        Direkomendasikan berdasarkan kondisi risiko banjir saat ini.
      </p>

      {/* Recommended Group */}
      {knowledgeRecommendation.recommended.length > 0 && (
        <RecommendationGroup
          title="Direkomendasikan"
          description="Komoditas yang sangat sesuai dengan kondisi saat ini."
          items={knowledgeRecommendation.recommended}
          status="recommended"
          accentColor="#22c55e"
        />
      )}

      {/* Alternative Group */}
      {knowledgeRecommendation.alternative.length > 0 && (
        <RecommendationGroup
          title="Alternatif"
          description="Komoditas yang dapat dipertimbangkan dengan penyesuaian."
          items={knowledgeRecommendation.alternative}
          status="alternative"
          accentColor="#f59e0b"
        />
      )}

      {/* Not Recommended Group */}
      {knowledgeRecommendation.not_recommended.length > 0 && (
        <RecommendationGroup
          title="Tidak Direkomendasikan"
          description="Komoditas yang berisiko tinggi pada kondisi saat ini."
          items={knowledgeRecommendation.not_recommended}
          status="not_recommended"
          accentColor="#ef4444"
        />
      )}
    </motion.div>
  );
}
