"use client";

import type { HistoryEntry } from "@/hooks/use-search-history";

interface Props {
  wilayah: string | null;
  entry?: HistoryEntry;
}

export function MapStatusBar({ wilayah, entry }: Props) {
  const time = entry
    ? new Date(entry.timestamp).toLocaleString("id-ID", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" }) + " WIB"
    : "—";

  return (
    <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-10 flex items-center gap-3 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-[var(--radius-status)] shadow-[var(--shadow-card)] border border-[var(--border)] px-4 py-2 text-[10px] text-[var(--text-muted)] max-w-[90%] overflow-x-auto">
      <span>📍 <strong className="text-[var(--text-primary)]">{wilayah ?? "Belum dipilih"}</strong></span>
      <span className="text-[var(--border)]">|</span>
      <span>🌦 Open-Meteo</span>
      {entry && (
        <>
          <span className="text-[var(--border)]">|</span>
          <span>📊 <strong>{entry.fri.toFixed(1)}</strong></span>
          <span className="text-[var(--border)]">|</span>
          <span>⚠ {entry.tingkatRisiko}</span>
          <span className="text-[var(--border)]">|</span>
          <span>🕒 {time}</span>
        </>
      )}
    </div>
  );
}
