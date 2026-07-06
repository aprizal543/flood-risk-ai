"use client";

import type { HistoryEntry } from "@/hooks/use-search-history";

interface Props {
  history: HistoryEntry[];
}

const LEVELS = [
  { label: "Rendah", range: "0–33", color: "#22c55e", match: "Risiko Rendah" },
  { label: "Sedang", range: "34–66", color: "#f59e0b", match: "Risiko Sedang" },
  { label: "Tinggi", range: "67–100", color: "#ef4444", match: "Risiko Tinggi" },
] as const;

export function FloodRiskLegend({ history }: Props) {
  return (
    <div className="absolute bottom-14 left-3 z-10 rounded-[var(--radius-legend)] bg-[var(--bg-card)]/90 backdrop-blur-sm shadow-[var(--shadow-card)] border border-[var(--border)] p-3 min-w-[140px]">
      <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-1.5">Legenda Risiko</p>
      {LEVELS.map(({ label, range, color, match }) => {
        const count = history.filter((h) => h.tingkatRisiko === match).length;
        return (
          <div key={label} className="flex items-center gap-2 mb-0.5">
            <div className="h-2.5 w-2.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-[var(--text-primary)] flex-1">{label} <span className="text-[var(--text-muted)]">({range})</span></span>
            {count > 0 && <span className="text-[9px] font-bold" style={{ color }}>{count}</span>}
          </div>
        );
      })}
    </div>
  );
}
