"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

/* ─── RecommendationCard ─── */
interface Recommendation {
  komoditas: string;
  skor: number;
  tingkat_keyakinan: number;
  alasan: string[];
  ringkasan: string;
}

export function RecommendationCard({ items }: { items: Recommendation[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.1 }}
      className="space-y-2"
    >
      <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
        Rekomendasi Komoditas
      </h3>
      <div className="space-y-1.5">
        {items.map((item, i) => (
          <CommodityItem key={item.komoditas} item={item} rank={i + 1} />
        ))}
      </div>
    </motion.div>
  );
}

function CommodityItem({ item, rank }: { item: Recommendation; rank: number }) {
  const [expanded, setExpanded] = useState(false);
  const barColor = item.skor >= 80 ? "var(--risk-rendah)" : item.skor >= 60 ? "var(--risk-sedang)" : "var(--risk-tinggi)";

  return (
    <div
      className="rounded-md border border-[var(--border)] bg-white dark:bg-[var(--neutral-100)] overflow-hidden"
      style={{ borderLeftWidth: 3, borderLeftColor: barColor }}
    >
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 p-2.5 text-left hover:bg-[var(--neutral-50)] transition-colors"
        aria-expanded={expanded}
        aria-label={`${item.komoditas}, skor ${item.skor}`}
      >
        <span className="flex items-center justify-center h-5 w-5 rounded-full bg-[var(--neutral-200)] text-[10px] font-bold text-[var(--text-muted)]">
          {rank}
        </span>
        <span className="flex-1 text-sm font-medium text-[var(--text-primary)]">{item.komoditas}</span>
        <span className="text-xs font-bold text-[var(--text-muted)]">{item.skor.toFixed(1)}</span>
        <ChevronDown className={cn("h-3.5 w-3.5 text-[var(--text-muted)] transition-transform duration-200", expanded && "rotate-180")} />
      </button>

      {/* Score bar */}
      <div className="px-2.5 pb-2">
        <div className="h-1 rounded-full bg-[var(--neutral-200)] overflow-hidden">
          <div className="h-full rounded-full" style={{ width: `${item.skor}%`, backgroundColor: barColor }} />
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-1.5">
              <ul className="space-y-0.5">
                {item.alasan.map((a) => (
                  <li key={a} className="text-xs text-[var(--text-muted)] flex gap-1.5">
                    <span className="text-[var(--brand-primary)]">•</span>{a}
                  </li>
                ))}
              </ul>
              <p className="text-xs italic text-[var(--text-muted)]">{item.ringkasan}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

/* ─── MitigationTimeline ─── */
interface Mitigation {
  prioritas: number;
  kategori: string;
  tindakan: string;
}

const KATEGORI_COLORS: Record<string, string> = {
  Drainase: "#3b82f6",
  Monitoring: "#8b5cf6",
  "Persiapan Lahan": "#10b981",
  Panen: "#f59e0b",
  Perlindungan: "#ef4444",
  Penanaman: "#6366f1",
  Pemulihan: "#14b8a6",
  Dokumentasi: "#6b7280",
};

export function MitigationTimeline({ items }: { items: Mitigation[] }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.15 }}
      className="space-y-2"
    >
      <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
        Tindakan Mitigasi
      </h3>
      <div className="space-y-2 relative pl-4">
        {/* Timeline line */}
        <div className="absolute left-[7px] top-1 bottom-1 w-0.5 bg-[var(--neutral-200)]" />
        {items.map((m) => (
          <div key={m.prioritas} className="relative flex gap-2.5">
            <div
              className="absolute left-[-13px] top-1.5 h-2.5 w-2.5 rounded-full border-2 border-white"
              style={{ backgroundColor: KATEGORI_COLORS[m.kategori] ?? "#6b7280" }}
            />
            <div className="flex-1">
              <span
                className="inline-block text-[10px] font-medium px-1.5 py-0.5 rounded"
                style={{ backgroundColor: (KATEGORI_COLORS[m.kategori] ?? "#6b7280") + "20", color: KATEGORI_COLORS[m.kategori] ?? "#6b7280" }}
              >
                {m.kategori}
              </span>
              <p className="text-xs text-[var(--text-primary)] mt-0.5">{m.tindakan}</p>
            </div>
          </div>
        ))}
      </div>
    </motion.div>
  );
}
