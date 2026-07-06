"use client";

import { Plus, Minus, Crosshair, Layers, Maximize2, Search } from "lucide-react";

/* ─── MapToolbar ─── */
export function MapToolbar() {
  const buttons = [
    { icon: Plus, label: "Perbesar" },
    { icon: Minus, label: "Perkecil" },
    { icon: Crosshair, label: "Lokasi saya" },
    { icon: Layers, label: "Layer peta" },
    { icon: Maximize2, label: "Layar penuh" },
  ];

  return (
    <div
      className="absolute top-3 right-3 z-10 flex flex-col gap-1 rounded-lg bg-white/95 dark:bg-[var(--neutral-100)]/95 shadow-md border border-[var(--border)] p-1"
      role="toolbar"
      aria-label="Kontrol peta"
    >
      {buttons.map(({ icon: Icon, label }) => (
        <button
          key={label}
          title={label}
          aria-label={label}
          className="flex items-center justify-center h-8 w-8 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--neutral-100)] transition-colors"
        >
          <Icon className="h-4 w-4" />
        </button>
      ))}
    </div>
  );
}

/* ─── FloatingLegend ─── */
export function FloatingLegend() {
  const levels = [
    { label: "Rendah (0–33)", color: "var(--risk-rendah)" },
    { label: "Sedang (34–66)", color: "var(--risk-sedang)" },
    { label: "Tinggi (67–100)", color: "var(--risk-tinggi)" },
  ];

  return (
    <div
      className="absolute bottom-6 left-3 z-10 rounded-lg bg-white/95 dark:bg-[var(--neutral-100)]/95 shadow-md border border-[var(--border)] p-2.5"
      aria-label="Legenda risiko"
    >
      <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-1.5">Legenda</p>
      <div className="space-y-1">
        {levels.map(({ label, color }) => (
          <div key={label} className="flex items-center gap-2">
            <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-[10px] text-[var(--text-primary)]">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ─── SearchBar ─── */
interface SearchBarProps {
  value: string;
  onSearch: (wilayah: string) => void;
}

export function SearchBar({ value, onSearch }: SearchBarProps) {
  return (
    <div className="absolute top-3 left-3 z-10">
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const input = (e.currentTarget.elements.namedItem("wilayah") as HTMLInputElement).value.trim();
          if (input) onSearch(input);
        }}
        className="flex items-center gap-2 bg-white/95 dark:bg-[var(--neutral-100)]/95 rounded-lg shadow-md border border-[var(--border)] px-3 py-2 w-56"
      >
        <Search className="h-4 w-4 text-[var(--text-muted)]" aria-hidden="true" />
        <input
          name="wilayah"
          type="text"
          defaultValue={value}
          placeholder="Cari wilayah..."
          aria-label="Cari wilayah"
          className="flex-1 text-xs bg-transparent outline-none text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
        />
      </form>
    </div>
  );
}
