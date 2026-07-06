"use client";

import { motion } from "framer-motion";
import { REALTIME_LABELS } from "@/lib/realtime-presentation";

interface TrendPoint {
  tanggal: string;
  fri: number;
}

const pointColor = (fri: number) =>
  fri <= 33 ? "var(--risk-rendah)" : fri <= 66 ? "var(--risk-sedang)" : "var(--risk-tinggi)";

export function TrendChart({ data }: { data: TrendPoint[] }) {
  const max = 100;
  const h = 80;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.2 }}
      className="space-y-2"
    >
      <h3 className="text-xs font-semibold uppercase tracking-wide text-[var(--text-muted)]">
        Tren {REALTIME_LABELS.fri} (7 Hari)
      </h3>
      <div className="relative bg-[var(--neutral-100)] rounded-lg p-3 border border-[var(--border)]">
        {/* Simple bar chart */}
        <div className="flex items-end gap-1 justify-between" style={{ height: h }} role="img" aria-label={`Grafik tren ${REALTIME_LABELS.fri} 7 hari terakhir`}>
          {data.map((d, i) => {
            const barH = (d.fri / max) * h;
            return (
              <div key={i} className="flex flex-col items-center flex-1 gap-1">
                <motion.div
                  initial={{ height: 0 }}
                  animate={{ height: barH }}
                  transition={{ duration: 0.4, delay: i * 0.05 }}
                  className="w-full max-w-[24px] rounded-t"
                  style={{ backgroundColor: pointColor(d.fri) }}
                  title={`${d.tanggal}: ${REALTIME_LABELS.fri} ${d.fri}`}
                />
              </div>
            );
          })}
        </div>
        {/* X labels */}
        <div className="flex justify-between mt-1.5">
          {data.map((d, i) => (
            <span key={i} className="text-[9px] text-[var(--text-muted)] flex-1 text-center">
              {d.tanggal.split(" ")[0]}
            </span>
          ))}
        </div>
      </div>
    </motion.div>
  );
}
