"use client";

import { motion } from "framer-motion";
import { Droplets, Thermometer, Wind, ShieldAlert, AlertTriangle, Lightbulb, Search } from "lucide-react";
import { ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, Radar, BarChart, Bar, XAxis, YAxis, Cell, Tooltip } from "recharts";
import type { PrediksiRealtimeResponse } from "@/types/api";
import { REALTIME_LABELS, formatNoDecimal, getRealtimeDisplayValues } from "@/lib/realtime-presentation";

interface Props {
  data: PrediksiRealtimeResponse | undefined;
  onSwitchDashboard: () => void;
}

const RISK_COLORS: Record<string, string> = { "Risiko Rendah": "#22c55e", "Risiko Sedang": "#f59e0b", "Risiko Tinggi": "#ef4444" };
const fadeUp = { initial: { opacity: 0, y: 12 }, animate: { opacity: 1, y: 0 } };
const stagger = { animate: { transition: { staggerChildren: 0.08 } } };

export function AnalyticsPanel({ data, onSwitchDashboard }: Props) {
  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center gap-4 px-8">
        <div className="h-16 w-16 rounded-full bg-[var(--bg-card)] border border-[var(--border)] flex items-center justify-center">
          <Search className="h-7 w-7 text-[var(--text-muted)]" />
        </div>
        <div>
          <p className="text-sm font-medium text-[var(--text-primary)]">Belum ada data</p>
          <p className="text-[11px] text-[var(--text-muted)] mt-1">Lakukan prediksi terlebih dahulu untuk melihat visualisasi.</p>
        </div>
        <button onClick={onSwitchDashboard} className="px-4 py-2 text-[11px] font-medium rounded-[var(--radius-btn)] bg-[var(--brand-primary)] text-white hover:opacity-90 transition-opacity">
          Cari Lokasi
        </button>
      </div>
    );
  }

  const color = RISK_COLORS[data.tingkat_risiko] ?? "#64748b";
  const friPct = Math.min(data.fri / 100, 1);
  const forecastDate = data.forecast_date ?? data.cuaca.tanggal;
  const displayValues = getRealtimeDisplayValues(data);
  const rainfallPct = displayValues.rainfall === null ? 0 : Math.min(displayValues.rainfall / 50, 1);
  const rain7Pct = displayValues.rain7 === null ? 0 : Math.min(displayValues.rain7 / 150, 1);
  const humidityPct = displayValues.humidity === null ? 0 : displayValues.humidity / 100;
  const tavgPct = displayValues.tavg === null ? 0 : Math.min(Math.max((displayValues.tavg - 20) / 15, 0), 1);

  const radarData = [
    { factor: REALTIME_LABELS.rainfall, value: rainfallPct * 100 },
    { factor: REALTIME_LABELS.rain7, value: rain7Pct * 100 },
    { factor: REALTIME_LABELS.humidity, value: displayValues.humidity ?? 0 },
    { factor: REALTIME_LABELS.tavg, value: tavgPct * 100 },
    { factor: REALTIME_LABELS.fri, value: data.fri },
  ];

  const barData = data.rekomendasi.slice(0, 5).map((r, i) => ({
    name: r.komoditas, score: r.skor, rank: i + 1,
  }));

  return (
    <motion.div {...stagger} className="space-y-8 overflow-y-auto h-full pb-6">
      {/* Section 1: Hero Gauge */}
      <motion.div {...fadeUp} className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-5 text-center min-h-[380px] flex flex-col items-center justify-center">
        <p className="text-[10px] uppercase tracking-widest font-semibold text-[var(--text-muted)] mb-3">{REALTIME_LABELS.fri}</p>
        <div className="relative w-64 h-32 mx-auto mb-2">
          <svg viewBox="0 0 120 60" className="w-full h-full">
            <path d="M 10 55 A 50 50 0 0 1 110 55" fill="none" stroke="var(--border)" strokeWidth="10" strokeLinecap="round" />
            <motion.path
              d="M 10 55 A 50 50 0 0 1 110 55"
              fill="none" stroke={color} strokeWidth="10" strokeLinecap="round"
              strokeDasharray="157"
              initial={{ strokeDashoffset: 157 }}
              animate={{ strokeDashoffset: 157 * (1 - friPct) }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex items-end justify-center">
            <motion.span
              className="text-6xl font-bold"
              style={{ color }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              {data.fri.toFixed(1)}
            </motion.span>
          </div>
        </div>
        <span className="inline-block px-4 py-1.5 rounded-full text-[11px] font-semibold" style={{ backgroundColor: `${color}18`, color }}>
          {data.tingkat_risiko}
        </span>
        <p className="text-[11px] text-[var(--text-muted)] mt-3">Prakiraan {forecastDate}</p>
        <p className="text-[10px] text-[var(--text-muted)] mt-0.5">
          {data.updated_at ? new Date(data.updated_at).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" }) + " WIB" : ""}
        </p>
        <p className="text-[10px] text-[var(--text-muted)] mt-2 max-w-[240px] mx-auto leading-relaxed">
          {data.fri <= 33 ? "Kondisi aman untuk penanaman normal tanpa pencegahan khusus." : data.fri <= 66 ? "Perlu tindakan pencegahan dasar untuk melindungi tanaman." : "Tunda penanaman atau aktifkan perlindungan maksimal."}
        </p>
      </motion.div>

      {/* Section 2: Weather Cards */}
      <motion.div {...fadeUp} className="grid grid-cols-2 gap-3">
        <MetricCard icon={Droplets} color="#3b82f6" label={REALTIME_LABELS.rainfall} value={formatNoDecimal(displayValues.rainfall)} unit={displayValues.rainfall === null ? "" : "mm"} pct={rainfallPct} badge={displayValues.rainfall === null ? "—" : displayValues.rainfall > 30 ? "Tinggi" : displayValues.rainfall > 10 ? "Sedang" : "Rendah"} />
        <MetricCard icon={Droplets} color="#06b6d4" label={REALTIME_LABELS.rain7} value={formatNoDecimal(displayValues.rain7)} unit={displayValues.rain7 === null ? "" : "mm"} pct={rain7Pct} badge={displayValues.rain7 === null ? "—" : displayValues.rain7 > 100 ? "Tinggi" : displayValues.rain7 > 50 ? "Sedang" : "Rendah"} />
        <MetricCard icon={Wind} color="#8b5cf6" label={REALTIME_LABELS.humidity} value={formatNoDecimal(displayValues.humidity)} unit={displayValues.humidity === null ? "" : "%"} pct={humidityPct} badge={displayValues.humidity === null ? "—" : displayValues.humidity > 85 ? "Tinggi" : "Normal"} />
        <MetricCard icon={Thermometer} color="#f59e0b" label={REALTIME_LABELS.tavg} value={displayValues.tavg === null ? "—" : displayValues.tavg.toFixed(1)} unit={displayValues.tavg === null ? "" : "°C"} pct={tavgPct} badge={displayValues.tavg === null ? "—" : "Normal"} />
        <MetricCard icon={ShieldAlert} color={color} label={REALTIME_LABELS.fri} value={`${data.fri.toFixed(1)}`} unit="/100" pct={friPct} badge={data.tingkat_risiko.replace("Risiko ", "")} />
      </motion.div>

      {/* Section 3: Radar Chart */}
      <motion.div {...fadeUp}>
        <SectionHeader title="Komposisi Faktor Risiko" subtitle={`Visualisasi faktor cuaca yang memengaruhi ${REALTIME_LABELS.fri}.`} />
        <div className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-2">
          <ResponsiveContainer width="100%" height={320}>
            <RadarChart data={radarData} outerRadius="85%">
              <PolarGrid stroke="var(--border)" />
              <PolarAngleAxis dataKey="factor" tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
              <Radar dataKey="value" stroke={color} fill={color} fillOpacity={0.15} strokeWidth={2} animationDuration={1000} />
              <Tooltip contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 12, fontSize: 10 }} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Section 4: Recommendation Bar */}
      <motion.div {...fadeUp}>
        <SectionHeader title="Rekomendasi Komoditas" subtitle="Top 5 komoditas berdasarkan kesesuaian kondisi saat ini." />
        <div className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-4">
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={barData} layout="vertical" margin={{ left: 4, right: 12, top: 4, bottom: 4 }}>
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 9, fill: "var(--text-muted)" }} axisLine={false} tickLine={false} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 10, fill: "var(--text-primary)" }} width={80} axisLine={false} tickLine={false} />
              <Tooltip contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 12, fontSize: 10 }} />
              <Bar dataKey="score" radius={[0, 8, 8, 0]} animationDuration={800}>
                {barData.map((_, i) => <Cell key={i} fill={`hsl(${145 - i * 10}, 70%, ${50 + i * 5}%)`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* Section 5: Mitigation Timeline */}
      <motion.div {...fadeUp}>
        <SectionHeader title="Tindakan Mitigasi" subtitle="Prioritas tindakan berdasarkan analisis risiko." />
        <div className="space-y-3">
          {data.mitigasi.map((m, i) => (
            <motion.button
              key={m.prioritas}
              onClick={onSwitchDashboard}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="w-full flex items-start gap-3 p-3 bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] text-left hover:border-[var(--border-hover)] hover:translate-y-[-1px] transition-all"
            >
              <div className="h-7 w-7 rounded-full flex items-center justify-center text-[10px] font-bold text-white shrink-0" style={{ backgroundColor: ["#ef4444", "#f59e0b", "#3b82f6"][i] ?? "#64748b" }}>
                {m.prioritas}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[11px] font-semibold text-[var(--text-primary)]">{m.tindakan}</p>
                <div className="flex items-center gap-1.5 mt-1">
                  <AlertTriangle className="h-3 w-3 text-[var(--text-muted)]" />
                  <span className="text-[9px] text-[var(--text-muted)]">{m.kategori}</span>
                </div>
              </div>
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Section 6: Insight Card */}
      <motion.div {...fadeUp}>
        <InsightCard data={data} />
      </motion.div>
    </motion.div>
  );
}

function MetricCard({ icon: Icon, color, label, value, unit, pct, badge }: {
  icon: typeof Droplets; color: string; label: string; value: string; unit: string; pct: number; badge: string;
}) {
  return (
    <motion.div {...fadeUp} className="bg-[var(--bg-card)] rounded-[var(--radius-weather)] border border-[var(--border)] p-3.5 hover:border-[var(--border-hover)] hover:translate-y-[-2px] transition-all cursor-default">
      <div className="flex items-center gap-2 mb-2">
        <div className="h-7 w-7 rounded-xl flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
          <Icon className="h-3.5 w-3.5" style={{ color }} />
        </div>
        <span className="text-[9px] uppercase tracking-wide font-medium text-[var(--text-muted)]">{label}</span>
      </div>
      <p className="text-xl font-bold text-[var(--text-primary)]">{value}<span className="text-[10px] font-normal text-[var(--text-muted)] ml-0.5">{unit}</span></p>
      <div className="flex items-center gap-2 mt-2">
        <div className="flex-1 h-1.5 bg-[var(--border)] rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ backgroundColor: color }}
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(pct, 1) * 100}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          />
        </div>
        <span className="text-[8px] font-semibold" style={{ color }}>{badge}</span>
      </div>
    </motion.div>
  );
}

function SectionHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <div className="mb-3">
      <h3 className="text-[11px] font-semibold text-[var(--text-primary)]">{title}</h3>
      <p className="text-[9px] text-[var(--text-muted)] mt-0.5">{subtitle}</p>
    </div>
  );
}

function InsightCard({ data }: { data: PrediksiRealtimeResponse }) {
  const insights = generateInsights(data);
  return (
    <div className="bg-[var(--bg-card)] rounded-[var(--radius-card)] border border-[var(--border)] p-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="h-6 w-6 rounded-lg bg-amber-500/10 flex items-center justify-center">
          <Lightbulb className="h-3.5 w-3.5 text-amber-400" />
        </div>
        <span className="text-[11px] font-semibold text-[var(--text-primary)]">Insight Hari Ini</span>
      </div>
      <div className="space-y-2">
        {insights.map((text, i) => (
          <p key={i} className="text-[10px] text-[var(--text-secondary)] leading-relaxed pl-3 border-l-2 border-[var(--border)]">{text}</p>
        ))}
      </div>
    </div>
  );
}

function generateInsights(data: PrediksiRealtimeResponse): string[] {
  const { fri } = data;
  const displayValues = getRealtimeDisplayValues(data);
  const insights: string[] = [];
  if (displayValues.rainfall === null) insights.push(`${REALTIME_LABELS.rainfall} belum tersedia pada respons prediksi.`);
  else if (displayValues.rainfall > 30) insights.push(`${REALTIME_LABELS.rainfall} merupakan faktor dominan yang memengaruhi ${REALTIME_LABELS.fri} hari ini.`);
  else if (displayValues.rainfall < 5) insights.push(`${REALTIME_LABELS.rainfall} sangat rendah — risiko genangan minimal untuk lahan pertanian.`);
  else insights.push(`${REALTIME_LABELS.rainfall} dalam kategori moderat — monitoring drainase disarankan.`);

  if (displayValues.rain7 === null) insights.push(`${REALTIME_LABELS.rain7} belum tersedia pada respons realtime.`);
  else if (displayValues.rain7 > 100) insights.push(`${REALTIME_LABELS.rain7} tinggi, sehingga pemantauan drainase dan genangan perlu diprioritaskan.`);
  else insights.push(`${REALTIME_LABELS.rain7} berada pada tingkat yang masih perlu dipantau bersama kondisi lahan.`);

  if (displayValues.humidity === null) insights.push(`${REALTIME_LABELS.humidity} belum tersedia pada respons prediksi.`);
  else if (displayValues.humidity > 85) insights.push(`${REALTIME_LABELS.humidity} relatif tinggi berpotensi meningkatkan kerentanan tanaman terhadap penyakit.`);
  else insights.push(`${REALTIME_LABELS.humidity} dalam batas optimal untuk pertumbuhan tanaman.`);

  if (fri < 33) insights.push("Kondisi saat ini mendukung penanaman normal tanpa pencegahan khusus.");
  else if (fri > 66) insights.push("Disarankan menunda penanaman atau menerapkan perlindungan tanaman secara intensif.");
  else insights.push("Diperlukan tindakan pencegahan dasar seperti penguatan drainase dan mulsa.");
  return insights;
}
