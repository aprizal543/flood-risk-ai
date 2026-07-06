"use client";

import { useLocalStorage } from "@/hooks/use-local-storage";

export interface RiskFilter {
  rendah: boolean;
  sedang: boolean;
  tinggi: boolean;
}

const STORAGE_KEY = "floodrisk_polygon_filter";
const DEFAULT: RiskFilter = { rendah: true, sedang: true, tinggi: true };

const OPTIONS: { key: keyof RiskFilter; label: string; color: string }[] = [
  { key: "rendah", label: "Rendah", color: "#22c55e" },
  { key: "sedang", label: "Sedang", color: "#f59e0b" },
  { key: "tinggi", label: "Tinggi", color: "#ef4444" },
];

export function usePolygonFilter() {
  return useLocalStorage<RiskFilter>(STORAGE_KEY, DEFAULT);
}

interface Props {
  value: RiskFilter;
  onChange: (v: RiskFilter) => void;
}

export function PolygonFilter({ value, onChange }: Props) {
  const allActive = value.rendah && value.sedang && value.tinggi;

  return (
    <div className="absolute top-3 left-[310px] z-10 flex items-center gap-1 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-[var(--radius-btn)] shadow-[var(--shadow-card)] border border-[var(--border)] px-2 py-1.5">
      <button
        onClick={() => onChange({ rendah: true, sedang: true, tinggi: true })}
        className={`px-1.5 py-0.5 text-[9px] rounded font-medium transition-colors ${allActive ? "bg-[var(--brand-primary)] text-white" : "text-[var(--text-muted)] hover:bg-[var(--neutral-100)]"}`}
      >
        Semua
      </button>
      {OPTIONS.map(({ key, label, color }) => (
        <button
          key={key}
          onClick={() => onChange({ ...value, [key]: !value[key] })}
          className={`flex items-center gap-1 px-1.5 py-0.5 text-[9px] rounded font-medium transition-colors ${value[key] ? "bg-[var(--neutral-50)]" : "opacity-40"}`}
        >
          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: color }} />
          {label}
        </button>
      ))}
    </div>
  );
}
