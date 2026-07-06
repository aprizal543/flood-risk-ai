import type { HistoryEntry } from "@/hooks/use-search-history";
import { REALTIME_LABELS, formatCelsius, formatMm, formatPercent, getRealtimeDisplayValues } from "@/lib/realtime-presentation";

const RISK_COLORS: Record<string, string> = {
  "Risiko Rendah": "#22c55e",
  "Risiko Sedang": "#f59e0b",
  "Risiko Tinggi": "#ef4444",
};

export function buildRegionPopupHTML(h: HistoryEntry): string {
  const color = RISK_COLORS[h.tingkatRisiko] ?? "#64748b";
  const displayValues = getRealtimeDisplayValues(h);
  const time = new Date(h.timestamp).toLocaleString("id-ID", {
    day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
  });

  return `<div style="font-family:Inter,system-ui,sans-serif;font-size:11px;line-height:1.6;min-width:200px">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <span style="font-weight:700;font-size:13px">📍 ${h.wilayah}</span>
    <button onclick="window.__regionPopupRemove__('${h.wilayah}')" title="Hapus" style="background:none;border:none;cursor:pointer;font-size:14px;padding:2px 6px;opacity:0.5;border-radius:8px;transition:opacity .15s" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.5'">🗑</button>
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:10px">
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.fri}</td><td style="padding:3px 0;text-align:right;font-weight:700;color:${color}">${h.fri.toFixed(1)}</td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.risk}</td><td style="padding:3px 0;text-align:right"><span style="background:${color}20;color:${color};padding:2px 10px;border-radius:99px;font-size:9px;font-weight:600">${h.tingkatRisiko.replace("Risiko ", "")}</span></td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.rainfall}</td><td style="padding:3px 0;text-align:right">${formatMm(displayValues.rainfall)}</td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.rain7}</td><td style="padding:3px 0;text-align:right">${formatMm(displayValues.rain7)}</td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.humidity}</td><td style="padding:3px 0;text-align:right">${formatPercent(displayValues.humidity)}</td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.tavg}</td><td style="padding:3px 0;text-align:right">${formatCelsius(displayValues.tavg)}</td></tr>
    <tr><td style="padding:3px 0;opacity:0.6">${REALTIME_LABELS.prediction}</td><td style="padding:3px 0;text-align:right">${time}</td></tr>
  </table>
  <button onclick="window.__regionPopupDetail__('${h.wilayah}')" style="display:block;width:100%;margin-top:10px;padding:7px;background:#3b82f6;color:white;border:none;border-radius:12px;font-size:10px;font-weight:600;cursor:pointer;transition:background .15s" onmouseover="this.style.background='#2563eb'" onmouseout="this.style.background='#3b82f6'">Lihat Detail →</button>
</div>`;
}
