"use client";

import { useState, useRef, useCallback } from "react";
import { Search, Loader2, MapPin } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { searchLocations, type GeoResult } from "@/services/geocoding";
import { useDebounce } from "@/hooks/use-debounce";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  value: string;
  onSelect: (name: string, lat: number, lng: number) => void;
}

export function SearchBar({ value, onSelect }: SearchBarProps) {
  const [input, setInput] = useState(value);
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const debouncedInput = useDebounce(input, 300);
  const ref = useRef<HTMLDivElement | null>(null);

  const { data: results = [], isLoading } = useQuery({
    queryKey: ["geocoding", debouncedInput],
    queryFn: () => searchLocations(debouncedInput),
    enabled: debouncedInput.length >= 2 && debouncedInput !== value,
    staleTime: 60_000,
  });

  const hasResults = results.length > 0 && debouncedInput !== value;

  const select = useCallback((r: GeoResult) => {
    setInput(r.name);
    setOpen(false);
    onSelect(r.name, r.latitude, r.longitude);
  }, [onSelect]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!open || !hasResults) return;
    if (e.key === "ArrowDown") { e.preventDefault(); setActive((a) => Math.min(a + 1, results.length - 1)); }
    else if (e.key === "ArrowUp") { e.preventDefault(); setActive((a) => Math.max(a - 1, 0)); }
    else if (e.key === "Enter" && active >= 0) { e.preventDefault(); select(results[active]); }
    else if (e.key === "Escape") { setOpen(false); }
  };

  const handleClickOutside = useCallback((e: MouseEvent) => {
    if (!ref.current?.contains(e.target as Node)) setOpen(false);
  }, []);

  const attachRef = useCallback((node: HTMLDivElement | null) => {
    if (ref.current) document.removeEventListener("mousedown", handleClickOutside);
    ref.current = node;
    if (node) document.addEventListener("mousedown", handleClickOutside);
  }, [handleClickOutside]);

  return (
    <div ref={attachRef} className="absolute top-3 left-3 z-10 w-72">
      <div className="flex items-center gap-2 bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-[var(--radius-search)] shadow-[var(--shadow-card)] border border-[var(--border)] px-4 py-2.5">
        {isLoading ? <Loader2 className="h-4 w-4 text-[var(--text-muted)] animate-spin" /> : <Search className="h-4 w-4 text-[var(--text-muted)]" />}
        <input
          type="text"
          value={input}
          onChange={(e) => { setInput(e.target.value); setOpen(true); setActive(-1); }}
          onFocus={() => hasResults && setOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Cari lokasi..."
          aria-label="Cari lokasi"
          aria-autocomplete="list"
          className="flex-1 text-xs bg-transparent outline-none text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
        />
      </div>

      {open && hasResults && (
        <ul role="listbox" className="mt-1 bg-[var(--bg-card)] rounded-[var(--radius-popup)] shadow-[var(--shadow-popup)] border border-[var(--border)] overflow-hidden">
          {results.map((r, i) => (
            <li
              key={`${r.name}-${r.latitude}-${r.longitude}`}
              role="option"
              aria-selected={i === active}
              className={cn(
                "px-3 py-2.5 cursor-pointer transition-colors",
                i === active ? "bg-[var(--brand-primary)]/10" : "hover:bg-[var(--neutral-50)]"
              )}
              onMouseEnter={() => setActive(i)}
              onClick={() => select(r)}
            >
              <div className="flex items-start gap-2">
                <MapPin className="h-3.5 w-3.5 text-[var(--brand-primary)] mt-0.5 shrink-0" />
                <div>
                  <span className="text-xs font-semibold text-[var(--text-primary)]">{r.name}</span>
                  <div className="text-[10px] text-[var(--text-muted)]">
                    {r.admin1 && <span>{r.admin1} • </span>}{r.country}
                  </div>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
