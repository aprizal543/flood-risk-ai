"use client";

import { useRef, useCallback } from "react";
import { motion } from "framer-motion";
import { FileText, Printer, Download, Droplets, Wind, Thermometer, MapPin, AlertTriangle, Search } from "lucide-react";
import type { PrediksiRealtimeResponse } from "@/types/api";
import { openPrintWindow } from "@/components/report/ReportPrintWindow";
import { REALTIME_LABELS, formatCelsius, formatMm, formatPercent, getRealtimeDisplayValues } from "@/lib/realtime-presentation";

interface Props {
  data: PrediksiRealtimeResponse | undefined;
}

const RISK_COLORS: Record<string, string> = { "Risiko Rendah": "#22c55e", "Risiko Sedang": "#f59e0b", "Risiko Tinggi": "#ef4444" };
const fadeUp = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 } };

export function ReportsPanel({ data }: Props) {
  const reportRef = useRef<HTMLDivElement>(null);

  const handleExportPDF = useCallback(() => {
    if (!data) return;
    openPrintWindow({ data });
  }, [data]);

  const handlePrint = useCallback(() => {
    if (!data) return;
    openPrintWindow({ data });
  }, [data]);

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center gap-4 px-8">
        <div className="h-14 w-14 rounded-2xl bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center">
          <FileText className="h-6 w-6 text-[var(--text-muted)]" />
        </div>
        <div>
          <p className="text-[12px] font-medium text-[var(--text-primary)]">Belum ada laporan</p>
          <p className="text-[10px] text-[var(--text-muted)] mt-1">Lakukan prediksi terlebih dahulu untuk membuat laporan.</p>
        </div>
        <button className="px-4 py-2 text-[11px] font-medium rounded-[var(--radius-btn)] bg-[var(--brand-primary)] text-white hover:opacity-90 transition-opacity">
          <Search className="h-3.5 w-3.5 inline mr-1.5" />Cari Lokasi
        </button>
      </div>
    );
  }

  const color = RISK_COLORS[data.tingkat_risiko] ?? "#64748b";
  const forecastDate = data.forecast_date ?? data.cuaca.tanggal;
  const now = new Date().toLocaleString("id-ID", { timeZone: "Asia/Jakarta", day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" });
  const displayValues = getRealtimeDisplayValues(data);

  return (
    <div className="h-full flex flex-col">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 pt-3 pb-2 shrink-0">
        <div className="flex items-center gap-2">
          <FileText className="h-4 w-4 text-[var(--brand-primary)]" />
          <h2 className="text-[12px] font-semibold text-[var(--text-primary)]">Laporan Prediksi</h2>
        </div>
        <div className="flex gap-1.5">
          <button onClick={handleExportPDF} className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-medium rounded-[var(--radius-btn)] bg-[var(--brand-primary)] text-white hover:opacity-90 transition-opacity">
            <Download className="h-3 w-3" />Export PDF
          </button>
          <button onClick={handlePrint} className="flex items-center gap-1.5 px-3 py-1.5 text-[10px] font-medium rounded-[var(--radius-btn)] border border-[var(--border)] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
            <Printer className="h-3 w-3" />Print Report
          </button>
        </div>
      </div>

      {/* Report Body */}
      <div className="flex-1 overflow-y-auto px-4 pb-6">
        <div ref={reportRef} className="space-y-6">

          {/* Cover */}
          <motion.div {...fadeUp} className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-6">
            <p className="text-[9px] uppercase tracking-widest text-[var(--text-muted)] font-semibold">FloodRisk AI • Forecast Report</p>
            <h1 className="text-lg font-bold text-[var(--text-primary)] mt-2">{data.wilayah}</h1>
            <p className="text-[10px] text-[var(--text-muted)] mt-1">{forecastDate} • {now} WIB</p>
            <div className="flex items-center gap-3 mt-4">
              <span className="px-3 py-1 rounded-full text-[10px] font-semibold" style={{ backgroundColor: `${color}18`, color }}>{data.tingkat_risiko}</span>
              <span className="text-[10px] text-[var(--text-muted)]">{REALTIME_LABELS.fri} {data.fri.toFixed(1)} • {data.model} v{data.versi_model}</span>
            </div>
          </motion.div>

          {/* Executive Summary */}
          <motion.div {...fadeUp} transition={{ delay: 0.05 }}>
            <RSection title="Ringkasan Eksekutif">
              <p className="text-[11px] text-[var(--text-secondary)] leading-relaxed">
                Pada tanggal <strong>{forecastDate}</strong> wilayah <strong>{data.wilayah}</strong> memiliki {REALTIME_LABELS.fri} sebesar <strong style={{ color }}>{data.fri.toFixed(1)}</strong> ({data.tingkat_risiko}). {REALTIME_LABELS.rainfall} {formatMm(displayValues.rainfall)}, {REALTIME_LABELS.rain7} {formatMm(displayValues.rain7)}, {REALTIME_LABELS.humidity} {formatPercent(displayValues.humidity)}, {REALTIME_LABELS.tavg} {formatCelsius(displayValues.tavg)}. {data.rekomendasi[0] ? `Komoditas paling sesuai: ${data.rekomendasi[0].komoditas} (skor ${data.rekomendasi[0].skor.toFixed(0)}).` : ""}
              </p>
            </RSection>
          </motion.div>

          {/* Weather */}
          <motion.div {...fadeUp} transition={{ delay: 0.1 }}>
            <RSection title="Kondisi Cuaca">
              <div className="grid grid-cols-2 gap-2">
                <WCard icon={Droplets} color="#3b82f6" label={REALTIME_LABELS.rainfall} value={formatMm(displayValues.rainfall)} />
                <WCard icon={Droplets} color="#06b6d4" label={REALTIME_LABELS.rain7} value={formatMm(displayValues.rain7)} />
                <WCard icon={Wind} color="#8b5cf6" label={REALTIME_LABELS.humidity} value={formatPercent(displayValues.humidity)} />
                <WCard icon={Thermometer} color="#f59e0b" label={REALTIME_LABELS.tavg} value={formatCelsius(displayValues.tavg)} />
                <WCard icon={MapPin} color="#64748b" label="Koordinat" value={`${data.cuaca.latitude.toFixed(3)}, ${data.cuaca.longitude.toFixed(3)}`} />
              </div>
            </RSection>
          </motion.div>

          {/* Flood Risk */}
          <motion.div {...fadeUp} transition={{ delay: 0.15 }}>
            <RSection title="Analisis Risiko Banjir">
              <div className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] p-4 text-center">
                <p className="text-4xl font-bold" style={{ color }}>{data.fri.toFixed(1)}</p>
                <span className="inline-block mt-2 px-3 py-1 rounded-full text-[10px] font-semibold" style={{ backgroundColor: `${color}18`, color }}>{data.tingkat_risiko}</span>
                <p className="text-[10px] text-[var(--text-muted)] mt-2 max-w-[250px] mx-auto">
                  {data.fri <= 33 ? "Kondisi aman untuk penanaman normal." : data.fri <= 66 ? "Diperlukan pencegahan dasar." : "Tunda penanaman atau aktifkan perlindungan."}
                </p>
              </div>
            </RSection>
          </motion.div>

          {/* Recommendations */}
          <motion.div {...fadeUp} transition={{ delay: 0.2 }}>
            <RSection title="Rekomendasi Komoditas">
              <div className="space-y-2">
                {data.rekomendasi.slice(0, 5).map((r, i) => (
                  <div key={r.komoditas_id} className="flex items-center gap-3 p-2.5 bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)]">
                    <span className="h-6 w-6 rounded-full bg-green-500/10 text-green-500 text-[10px] font-bold flex items-center justify-center shrink-0">{i + 1}</span>
                    <div className="flex-1 min-w-0">
                      <p className="text-[11px] font-semibold text-[var(--text-primary)]">{r.komoditas}</p>
                      <p className="text-[9px] text-[var(--text-muted)] truncate">{r.ringkasan}</p>
                    </div>
                    <span className="text-[10px] font-bold text-[var(--text-primary)]">{r.skor.toFixed(0)}</span>
                  </div>
                ))}
              </div>
            </RSection>
          </motion.div>

          {/* Mitigation */}
          <motion.div {...fadeUp} transition={{ delay: 0.25 }}>
            <RSection title="Tindakan Mitigasi">
              <div className="relative pl-5 space-y-3">
                <div className="absolute left-[7px] top-2 bottom-2 w-[2px] bg-[var(--border)]" />
                {data.mitigasi.map((m, i) => (
                  <div key={m.prioritas} className="relative flex items-start gap-3">
                    <div className="absolute left-[-13px] h-5 w-5 rounded-full flex items-center justify-center text-[8px] font-bold text-white" style={{ backgroundColor: ["#ef4444", "#f59e0b", "#3b82f6"][i] ?? "#64748b" }}>{m.prioritas}</div>
                    <div className="ml-3">
                      <p className="text-[11px] font-semibold text-[var(--text-primary)]">{m.tindakan}</p>
                      <p className="text-[9px] text-[var(--text-muted)] flex items-center gap-1 mt-0.5"><AlertTriangle className="h-2.5 w-2.5" />{m.kategori}</p>
                    </div>
                  </div>
                ))}
              </div>
            </RSection>
          </motion.div>

          {/* Disclaimer */}
          <motion.div {...fadeUp} transition={{ delay: 0.3 }} className="border-t border-[var(--border)] pt-4 mt-6">
            <p className="text-[9px] text-[var(--text-muted)] leading-relaxed">
              Dokumen ini merupakan hasil analisis otomatis FloodRisk AI berdasarkan data cuaca Open-Meteo dan model Random Forest. Keputusan budidaya tetap berada pada pengguna dengan mempertimbangkan kondisi lapangan dan pengalaman praktis. FloodRisk AI v1.0.0 — UIN Suska Riau.
            </p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function RSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h3 className="text-[10px] uppercase tracking-wider font-semibold text-[var(--text-muted)] mb-3">{title}</h3>
      {children}
    </div>
  );
}

function WCard({ icon: Icon, color, label, value }: { icon: typeof Droplets; color: string; label: string; value: string }) {
  return (
    <div className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] p-3">
      <div className="flex items-center gap-2 mb-1.5">
        <div className="h-6 w-6 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
          <Icon className="h-3 w-3" style={{ color }} />
        </div>
        <span className="text-[9px] text-[var(--text-muted)]">{label}</span>
      </div>
      <p className="text-[13px] font-bold text-[var(--text-primary)]">{value}</p>
    </div>
  );
}
