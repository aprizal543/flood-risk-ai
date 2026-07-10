"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, Droplets, Leaf, AlertTriangle, FileText, Database } from "lucide-react";
import type { KnowledgeCommodityItem } from "@/types/api";
import { RecommendationBadge, type RecommendationStatus } from "./RecommendationBadge";

interface CommodityCardProps {
  item: KnowledgeCommodityItem;
  status: RecommendationStatus;
  index: number;
}

const VULNERABILITY_COLORS: Record<string, string> = {
  "Sangat Rendah": "#22c55e",
  "Rendah": "#3b82f6",
  "Sedang": "#f59e0b",
  "Tinggi": "#ef4444",
  "Sangat Tinggi": "#dc2626",
};

export function CommodityCard({ item, status, index }: CommodityCardProps) {
  const [expanded, setExpanded] = useState(false);
  const vulnColor = VULNERABILITY_COLORS[item.vulnerability] ?? "#64748b";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.2 }}
      className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] overflow-hidden hover:border-[var(--border-hover)] transition-all"
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-3 p-3 text-left hover:bg-[var(--bg-card-hover)] transition-colors"
        aria-expanded={expanded}
      >
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="text-[13px] font-semibold text-[var(--text-primary)] truncate">
              {item.komoditas}
            </h4>
            <RecommendationBadge status={status} />
          </div>
          <div className="flex items-center gap-3 text-[10px] text-[var(--text-muted)]">
            <span className="flex items-center gap-1">
              <Droplets className="h-3 w-3" />
              Genangan {item.maximum_inundation_duration}
            </span>
            <span className="flex items-center gap-1">
              <Leaf className="h-3 w-3" style={{ color: vulnColor }} />
              Kerentanan {item.vulnerability}
            </span>
          </div>
        </div>
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
          className="shrink-0"
        >
          <ChevronDown className="h-4 w-4 text-[var(--text-muted)]" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25, ease: "easeInOut" }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 pt-0 space-y-3 border-t border-[var(--border)]">
              {/* Reason */}
              <div className="pt-3">
                <p className="text-[9px] uppercase tracking-wide font-semibold text-[var(--text-muted)] mb-1.5 flex items-center gap-1">
                  <FileText className="h-3 w-3" /> Alasan
                </p>
                <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed bg-[var(--bg-input)] rounded-lg p-2.5 border border-[var(--border)]">
                  {item.reason}
                </p>
              </div>

              {/* Impacts */}
              <div>
                <p className="text-[9px] uppercase tracking-wide font-semibold text-[var(--text-muted)] mb-1.5 flex items-center gap-1">
                  <AlertTriangle className="h-3 w-3" /> Dampak
                </p>
                <ul className="space-y-1">
                  {item.main_impacts.map((impact, i) => (
                    <li key={i} className="flex items-start gap-2 text-[10px] text-[var(--text-secondary)]">
                      <span className="h-1.5 w-1.5 rounded-full bg-[var(--risk-tinggi)] shrink-0 mt-1" />
                      {impact}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Symptoms */}
              <div>
                <p className="text-[9px] uppercase tracking-wide font-semibold text-[var(--text-muted)] mb-1.5 flex items-center gap-1">
                  <Leaf className="h-3 w-3" /> Gejala
                </p>
                <ul className="space-y-1">
                  {item.damage_symptoms.map((symptom, i) => (
                    <li key={i} className="flex items-start gap-2 text-[10px] text-[var(--text-secondary)]">
                      <span className="h-1.5 w-1.5 rounded-full bg-[var(--risk-sedang)] shrink-0 mt-1" />
                      {symptom}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Source */}
              {item.source && (
                <div className="flex items-center gap-1.5">
                  <Database className="h-3 w-3 text-[var(--text-muted)]" />
                  <span className="text-[8px] text-[var(--text-muted)]">Sumber: {item.source}</span>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
