"use client";

import { motion } from "framer-motion";
import { CloudRain, Droplets, Thermometer } from "lucide-react";
import { StatusBadge } from "@/components/shared";
import { REALTIME_LABELS } from "@/lib/realtime-presentation";

/* ─── HeroFRICard ─── */
interface HeroFRICardProps {
  fri: number;
  tingkatRisiko: string;
}

const riskColor = (fri: number) =>
  fri <= 33 ? "var(--risk-rendah)" : fri <= 66 ? "var(--risk-sedang)" : "var(--risk-tinggi)";

const riskBg = (fri: number) =>
  fri <= 33 ? "var(--risk-rendah-bg)" : fri <= 66 ? "var(--risk-sedang-bg)" : "var(--risk-tinggi-bg)";

export function HeroFRICard({ fri, tingkatRisiko }: HeroFRICardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-lg p-4 border border-[var(--border)]"
      style={{ backgroundColor: riskBg(fri) }}
      aria-label={`${REALTIME_LABELS.fri}: ${fri.toFixed(1)}, ${tingkatRisiko}`}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wide">{REALTIME_LABELS.fri}</p>
          <p className="text-3xl font-bold mt-1" style={{ color: riskColor(fri) }}>
            {fri.toFixed(1)}
          </p>
        </div>
        <StatusBadge level={tingkatRisiko} />
      </div>
      {/* Progress bar */}
      <div className="mt-3 h-2 rounded-full bg-[var(--neutral-200)] overflow-hidden" role="progressbar" aria-valuenow={fri} aria-valuemin={0} aria-valuemax={100}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${fri}%` }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="h-full rounded-full"
          style={{ backgroundColor: riskColor(fri) }}
        />
      </div>
    </motion.div>
  );
}

/* ─── WeatherCard ─── */
interface WeatherCardProps {
  rr: number;
  rh_avg: number;
  tavg: number;
}

export function WeatherCard({ rr, rh_avg, tavg }: WeatherCardProps) {
  const items = [
    { icon: CloudRain, value: `${rr}`, unit: "mm", label: REALTIME_LABELS.rainfall },
    { icon: Droplets, value: `${rh_avg}`, unit: "%", label: REALTIME_LABELS.humidity },
    { icon: Thermometer, value: `${tavg}`, unit: "°C", label: REALTIME_LABELS.tavg },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.05 }}
      className="grid grid-cols-3 gap-2"
    >
      {items.map(({ icon: Icon, value, unit, label }) => (
        <div
          key={label}
          className="flex flex-col items-center p-3 rounded-lg bg-[var(--neutral-100)] border border-[var(--border)]"
        >
          <Icon className="h-4 w-4 text-[var(--text-muted)] mb-1" aria-hidden="true" />
          <span className="text-sm font-bold text-[var(--text-primary)]">
            {value}<span className="text-xs font-normal text-[var(--text-muted)]">{unit}</span>
          </span>
          <span className="text-[10px] text-[var(--text-muted)] mt-0.5">{label}</span>
        </div>
      ))}
    </motion.div>
  );
}
