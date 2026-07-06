"use client";

import { Info, Droplets, RotateCcw, Trash2 } from "lucide-react";
import { useLocalStorage } from "@/hooks/use-local-storage";
import { STORAGE_KEYS } from "@/lib/constants";

interface SettingsProps {
  onClearHistory: () => void;
  onClearAI: () => void;
}

export function SettingsPanel({ onClearHistory, onClearAI }: SettingsProps) {
  const [, setTheme] = useLocalStorage(STORAGE_KEYS.theme, "light");

  return (
    <div className="p-4 space-y-5 overflow-y-auto h-full">
      <h2 className="text-sm font-bold text-[var(--text-primary)]">Settings</h2>

      {/* General */}
      <SettingsSection title="General">
        <SettingsRow label="Tema" description="Pilih tema tampilan">
          <select onChange={(e) => setTheme(e.target.value)} defaultValue="light" className="text-[10px] px-2 py-1 rounded border border-[var(--border)] bg-transparent text-[var(--text-primary)]">
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </SettingsRow>
      </SettingsSection>

      {/* Prediction */}
      <SettingsSection title="Prediction">
        <SettingsRow label="Model Default" description="Model prediksi yang digunakan">
          <span className="text-[10px] text-[var(--text-primary)] font-medium">Random Forest</span>
        </SettingsRow>
        <SettingsRow label="Sumber Data" description="Provider cuaca">
          <span className="text-[10px] text-[var(--text-primary)] font-medium">Open-Meteo</span>
        </SettingsRow>
      </SettingsSection>

      {/* LLM */}
      <SettingsSection title="AI Provider">
        <SettingsRow label="LLM Provider" description="Konfigurasi via environment variable">
          <span className="text-[10px] text-[var(--text-primary)] font-medium">{process.env.NEXT_PUBLIC_LLM_PROVIDER ?? "gemini"}</span>
        </SettingsRow>
      </SettingsSection>

      {/* Map */}
      <SettingsSection title="Map">
        <SettingsRow label="Timezone" description="Zona waktu prakiraan">
          <span className="text-[10px] text-[var(--text-primary)] font-medium">Asia/Jakarta (WIB)</span>
        </SettingsRow>
      </SettingsSection>

      {/* Actions */}
      <SettingsSection title="Workspace">
        <div className="space-y-2">
          <ActionButton icon={Trash2} label="Hapus Riwayat Prediksi" onClick={onClearHistory} variant="warning" />
          <ActionButton icon={Trash2} label="Hapus Percakapan AI" onClick={onClearAI} variant="warning" />
          <ActionButton icon={RotateCcw} label="Reset Workspace" onClick={() => { onClearHistory(); onClearAI(); }} variant="danger" />
        </div>
      </SettingsSection>
    </div>
  );
}

export function AboutPanel() {
  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full">
      <div className="flex items-center gap-2">
        <Droplets className="h-5 w-5 text-blue-500" />
        <h2 className="text-sm font-bold text-[var(--text-primary)]">FloodRisk AI</h2>
      </div>
      <p className="text-[10px] text-[var(--text-muted)]">Sistem Pendukung Keputusan Risiko Banjir untuk Hortikultura</p>

      <div className="space-y-3 text-xs">
        <AboutSection title="Application" value="Flood Risk Decision Support System" />
        <AboutSection title="Version" value="1.0.0" />
        <AboutSection title="Release Date" value="5 juli  2026" />
        <AboutSection title="University" value="Universitas Hang Tuah Pekanbaru" />
        <AboutSection title="Research" value="Prediksi Risiko Banjir menggunakan Machine Learning untuk Lahan Hortikultura" />
        <AboutSection title="Prediction Data Collection" value="Stamet SSK II Pekanbaru" />
        <AboutSection title="Model Prediction" value="Random Forest" />
        <AboutSection title="Weather Provider" value="Open-Meteo" />
        <AboutSection title="License" value="Research Project — Non-commercial" />
      </div>

      <div className="pt-3 border-t border-[var(--border)]">
        <p className="text-[10px] text-[var(--text-muted)]">
          <Info className="h-3 w-3 inline mr-1" />
          Data cuaca dari Open-Meteo. Batas wilayah dari geoBoundaries. Model dilatih dari data historis BMKG Pekanbaru.
        </p>
      </div>
    </div>
  );
}

function SettingsSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-[10px] font-semibold uppercase text-[var(--text-muted)] mb-2">{title}</h3>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function SettingsRow({ label, description, children }: { label: string; description: string; children: React.ReactNode }) {
  return (
    <div className="flex items-center justify-between py-1.5">
      <div>
        <p className="text-[11px] font-medium text-[var(--text-primary)]">{label}</p>
        <p className="text-[9px] text-[var(--text-muted)]">{description}</p>
      </div>
      {children}
    </div>
  );
}

function ActionButton({ icon: Icon, label, onClick, variant }: { icon: typeof Trash2; label: string; onClick: () => void; variant: "warning" | "danger" }) {
  const cls = variant === "danger"
    ? "border-red-200 text-red-600 hover:bg-red-50"
    : "border-amber-200 text-amber-600 hover:bg-amber-50";
  return (
    <button onClick={onClick} className={`w-full flex items-center gap-2 px-3 py-2 text-[10px] font-medium rounded-lg border transition-colors ${cls}`}>
      <Icon className="h-3.5 w-3.5" /> {label}
    </button>
  );
}

function AboutSection({ title, value }: { title: string; value: string }) {
  return (
    <div>
      <p className="text-[10px] font-semibold uppercase text-[var(--text-muted)]">{title}</p>
      <p className="text-xs text-[var(--text-primary)]">{value}</p>
    </div>
  );
}
