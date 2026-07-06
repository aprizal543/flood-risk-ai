"use client";

import { BarChart3 } from "lucide-react";
import { useState } from "react";
import type { HistoryEntry } from "@/hooks/use-search-history";
import { REALTIME_LABELS } from "@/lib/realtime-presentation";

interface Props {
  history: HistoryEntry[];
}

export function SpatialStatistics({ history }: Props) {
  const [open, setOpen] = useState(false);

  if (history.length === 0) return null;

  const tinggi = history.filter((h) => h.tingkatRisiko === "Risiko Tinggi").length;
  const sedang = history.filter((h) => h.tingkatRisiko === "Risiko Sedang").length;
  const rendah = history.filter((h) => h.tingkatRisiko === "Risiko Rendah").length;
  const friValues = history.map((h) => h.fri);
  const avgFri = friValues.reduce((a, b) => a + b, 0) / friValues.length;
  const maxFri = Math.max(...friValues);
  const minFri = Math.min(...friValues);

  return (
    <div className="absolute top-[80px] left-3 z-[5]">
      <button
        onClick={() => setOpen((o) => !o)}
        title="Statistik Spasial"
        className="flex items-center gap-1.5 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-[var(--radius-btn)] shadow-[var(--shadow-card)] border border-[var(--border)] px-3 py-2 text-[10px] font-medium text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
      >
        <BarChart3 className="h-3.5 w-3.5" />
        <span>Statistik</span>
      </button>
      {open && (
        <div className="mt-1 bg-[var(--bg-card)] rounded-[var(--radius-popup)] shadow-[var(--shadow-popup)] border border-[var(--border)] p-3 w-48">
          <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-2">Statistik Spasial</p>
          <div className="space-y-1 text-[10px]">
            <Row label="Wilayah Dianalisis" value={String(history.length)} />
            <Row label="Risiko Tinggi" value={String(tinggi)} color="#ef4444" />
            <Row label="Risiko Sedang" value={String(sedang)} color="#f59e0b" />
            <Row label="Risiko Rendah" value={String(rendah)} color="#22c55e" />
            <div className="border-t border-[var(--border)] my-1" />
            <Row label={`Rata-rata ${REALTIME_LABELS.fri}`} value={avgFri.toFixed(1)} />
            <Row label={`${REALTIME_LABELS.fri} Tertinggi`} value={maxFri.toFixed(1)} />
            <Row label={`${REALTIME_LABELS.fri} Terendah`} value={minFri.toFixed(1)} />
          </div>
        </div>
      )}
    </div>
  );
}

function Row({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="flex justify-between">
      <span className="text-[var(--text-muted)]">{label}</span>
      <span className="font-semibold" style={color ? { color } : undefined}>{value}</span>
    </div>
  );
}
