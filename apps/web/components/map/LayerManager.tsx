"use client";

import { Layers } from "lucide-react";
import { useState } from "react";
import { useLocalStorage } from "@/hooks/use-local-storage";

export interface LayerVisibility {
  markers: boolean;
  polygons: boolean;
  borders: boolean;
  labels: boolean;
}

const STORAGE_KEY = "floodrisk_layer_visibility";
const DEFAULT: LayerVisibility = { markers: true, polygons: true, borders: true, labels: true };

const LAYER_OPTIONS: { key: keyof LayerVisibility; label: string }[] = [
  { key: "markers", label: "Marker" },
  { key: "polygons", label: "Flood Risk Polygon" },
  { key: "borders", label: "Administrative Boundary" },
  { key: "labels", label: "Region Labels" },
];

interface Props {
  value: LayerVisibility;
  onChange: (v: LayerVisibility) => void;
}

export function useLayerVisibility() {
  return useLocalStorage<LayerVisibility>(STORAGE_KEY, DEFAULT);
}

export function LayerManager({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="relative">
      <button
        title="Layers"
        aria-label="Layers"
        onClick={() => setOpen((o) => !o)}
        className="flex items-center justify-center h-8 w-8 rounded-md text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--neutral-100)] transition-colors"
      >
        <Layers className="h-4 w-4" />
      </button>
      {open && (
        <div className="absolute right-0 top-10 w-52 bg-[var(--bg-card)] rounded-[var(--radius-popup)] shadow-[var(--shadow-popup)] border border-[var(--border)] p-2.5 z-20">
          <p className="text-[10px] font-semibold text-[var(--text-muted)] uppercase mb-1.5">Layers</p>
          {LAYER_OPTIONS.map(({ key, label }) => (
            <label key={key} className="flex items-center gap-2 py-1 cursor-pointer">
              <input
                type="checkbox"
                checked={value[key]}
                onChange={() => onChange({ ...value, [key]: !value[key] })}
                className="h-3 w-3 rounded accent-[var(--brand-primary)]"
              />
              <span className="text-[11px] text-[var(--text-primary)]">{label}</span>
            </label>
          ))}
        </div>
      )}
    </div>
  );
}
