"use client";

import type { PrediksiRealtimeResponse } from "@/types/api";
import { REALTIME_LABELS, formatCelsius, formatMm, formatPercent, getRealtimeDisplayValues } from "@/lib/realtime-presentation";

interface Props {
  data: PrediksiRealtimeResponse;
}

const RISK_COLORS: Record<string, string> = {
  "Risiko Rendah": "#16a34a",
  "Risiko Sedang": "#d97706",
  "Risiko Tinggi": "#dc2626",
};

const RISK_BG: Record<string, string> = {
  "Risiko Rendah": "#dcfce7",
  "Risiko Sedang": "#fef3c7",
  "Risiko Tinggi": "#fee2e2",
};

function formatDate(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString("id-ID", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return dateStr;
  }
}

function formatDateTime(): string {
  return new Date().toLocaleString("id-ID", {
    timeZone: "Asia/Jakarta",
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }) + " WIB";
}

/**
 * PrintableReport — Professional A4 document for print/PDF export.
 * This is NOT a dashboard view. It renders a static, paginated document
 * suitable for academic submission, government stakeholders, and formal reports.
 */
export function PrintableReport({ data }: Props) {
  const color = RISK_COLORS[data.tingkat_risiko] ?? "#64748b";
  const bgColor = RISK_BG[data.tingkat_risiko] ?? "#f1f5f9";
  const forecastDate = data.forecast_date ?? data.cuaca.tanggal;
  const generatedAt = formatDateTime();
  const displayValues = getRealtimeDisplayValues(data);

  return (
    <div className="print-report">
      {/* ═══════════════════════════════════════════════════════════
          PAGE 1 — COVER + EXECUTIVE SUMMARY + WEATHER + FLOOD RISK
         ═══════════════════════════════════════════════════════════ */}
      <section className="print-page">
        <PageHeader wilayah={data.wilayah} />

        {/* Cover */}
        <div className="report-cover">
          <p className="cover-brand">FloodRisk AI</p>
          <h1 className="cover-title">
            Agricultural Flood Risk<br />Forecast Report
          </h1>
          <div className="cover-meta">
            <MetaRow label="Wilayah" value={data.wilayah} />
            <MetaRow label="Tanggal Prakiraan" value={formatDate(forecastDate)} />
            <MetaRow label="Waktu Generate" value={generatedAt} />
            <MetaRow label="Model" value={`${data.model} v${data.versi_model}`} />
            <MetaRow label="Sumber Cuaca" value={data.sumber_data} />
            <MetaRow label="Versi Aplikasi" value="FloodRisk AI v1.0.0" />
          </div>
          <div
            className="cover-badge"
            style={{ backgroundColor: bgColor, color, borderColor: color }}
          >
            <span className="badge-fri">{data.fri.toFixed(1)}</span>
            <span className="badge-label">{data.tingkat_risiko}</span>
          </div>
        </div>

        {/* Executive Summary */}
        <SectionHeading title="Ringkasan Eksekutif" />
        <p className="report-text">
          Pada tanggal <strong>{formatDate(forecastDate)}</strong>, wilayah{" "}
          <strong>{data.wilayah}</strong> menunjukkan {REALTIME_LABELS.fri} sebesar{" "}
          <strong style={{ color }}>{data.fri.toFixed(1)}</strong> dari skala 0–100,
          dikategorikan sebagai <strong style={{ color }}>{data.tingkat_risiko}</strong>.
          {data.fri <= 33
            ? " Kondisi aman untuk melakukan penanaman normal tanpa perlindungan khusus."
            : data.fri <= 66
              ? " Diperlukan tindakan pencegahan dasar sebelum melakukan budidaya."
              : " Risiko tinggi — disarankan untuk menunda penanaman atau mengaktifkan sistem perlindungan."}
        </p>
        {data.rekomendasi[0] && (
          <p className="report-text">
            Komoditas hortikultura paling sesuai untuk kondisi ini:{" "}
            <strong>{data.rekomendasi[0].komoditas}</strong> dengan skor kesesuaian{" "}
            <strong>{data.rekomendasi[0].skor.toFixed(0)}/100</strong>.
          </p>
        )}

        {/* Weather Summary */}
        <SectionHeading title="Kondisi Cuaca" />
        <table className="report-table">
          <thead>
            <tr>
              <th>Parameter</th>
              <th>Nilai</th>
              <th>Keterangan</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{REALTIME_LABELS.rainfall}</td>
              <td><strong>{formatMm(displayValues.rainfall)}</strong></td>
              <td>{displayValues.rainfall === null ? "Tidak tersedia" : displayValues.rainfall > 50 ? "Hujan lebat" : displayValues.rainfall > 20 ? "Hujan sedang" : displayValues.rainfall > 0 ? "Hujan ringan" : "Tidak hujan"}</td>
            </tr>
            <tr>
              <td>{REALTIME_LABELS.rain7}</td>
              <td><strong>{formatMm(displayValues.rain7)}</strong></td>
              <td>{displayValues.rain7 === null ? "Tidak tersedia" : displayValues.rain7 > 100 ? "Akumulasi tinggi" : displayValues.rain7 > 50 ? "Akumulasi sedang" : "Akumulasi rendah"}</td>
            </tr>
            <tr>
              <td>{REALTIME_LABELS.humidity}</td>
              <td><strong>{formatPercent(displayValues.humidity)}</strong></td>
              <td>{displayValues.humidity === null ? "Tidak tersedia" : displayValues.humidity > 80 ? "Sangat lembap" : displayValues.humidity > 60 ? "Lembap" : "Normal"}</td>
            </tr>
            <tr>
              <td>{REALTIME_LABELS.tavg}</td>
              <td><strong>{formatCelsius(displayValues.tavg)}</strong></td>
              <td>{displayValues.tavg === null ? "Tidak tersedia" : displayValues.tavg > 33 ? "Panas" : displayValues.tavg < 22 ? "Dingin" : "Normal"}</td>
            </tr>
            <tr>
              <td>Koordinat</td>
              <td><strong>{data.cuaca.latitude.toFixed(4)}, {data.cuaca.longitude.toFixed(4)}</strong></td>
              <td>{data.wilayah}</td>
            </tr>
          </tbody>
        </table>

        {/* Flood Risk Gauge */}
        <SectionHeading title="Analisis Risiko Banjir" />
        <div className="risk-gauge">
          <div className="gauge-bar">
            <div className="gauge-fill" style={{ width: `${Math.min(data.fri, 100)}%`, backgroundColor: color }} />
            <div className="gauge-marker" style={{ left: `${Math.min(data.fri, 100)}%` }} />
          </div>
          <div className="gauge-labels">
            <span>0 — Rendah</span>
            <span>33 — Sedang</span>
            <span>67 — Tinggi</span>
            <span>100</span>
          </div>
          <div className="gauge-result" style={{ color }}>
            <span className="gauge-value">{data.fri.toFixed(1)}</span>
            <span className="gauge-level">{data.tingkat_risiko}</span>
          </div>
          <p className="report-text gauge-desc">
            {REALTIME_LABELS.fri} dihitung berdasarkan fitur cuaca FRI v2 menggunakan model {data.model}.
            Skala 0–33 (Rendah), 34–66 (Sedang), 67–100 (Tinggi). Semakin tinggi nilai {REALTIME_LABELS.fri},
            semakin besar risiko banjir yang berpotensi merusak tanaman hortikultura.
          </p>
        </div>

        <PageFooter page={1} totalPages={3} />
      </section>

      {/* ═══════════════════════════════════════════════════════════
          PAGE 2 — COMMODITY RECOMMENDATIONS + MITIGATION
         ═══════════════════════════════════════════════════════════ */}
      <section className="print-page">
        <PageHeader wilayah={data.wilayah} />

        {/* Commodity Recommendation Table */}
        <SectionHeading title="Rekomendasi Komoditas Hortikultura" />
        <p className="report-text">
          Peringkat kesesuaian komoditas berdasarkan analisis multikriteria terhadap
          kondisi cuaca dan tingkat risiko banjir saat ini.
        </p>
        <table className="report-table recommendation-table">
          <thead>
            <tr>
              <th className="col-rank">#</th>
              <th>Komoditas</th>
              <th className="col-score">Skor</th>
              <th className="col-compat">Kesesuaian</th>
              <th>Alasan</th>
            </tr>
          </thead>
          <tbody>
            {data.rekomendasi.map((r, i) => (
              <tr key={r.komoditas_id}>
                <td className="col-rank">{i + 1}</td>
                <td><strong>{r.komoditas}</strong></td>
                <td className="col-score">{r.skor.toFixed(0)}</td>
                <td className="col-compat">
                  <span
                    className="compat-badge"
                    style={{
                      backgroundColor: r.skor >= 70 ? "#dcfce7" : r.skor >= 40 ? "#fef3c7" : "#fee2e2",
                      color: r.skor >= 70 ? "#16a34a" : r.skor >= 40 ? "#d97706" : "#dc2626",
                    }}
                  >
                    {r.skor >= 70 ? "Tinggi" : r.skor >= 40 ? "Sedang" : "Rendah"}
                  </span>
                </td>
                <td className="col-reason">{r.ringkasan}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Mitigation Timeline */}
        <SectionHeading title="Tindakan Mitigasi" />
        <p className="report-text">
          Prioritas tindakan mitigasi berdasarkan tingkat risiko banjir saat ini.
          Urutan menunjukkan prioritas pelaksanaan.
        </p>
        <table className="report-table mitigation-table">
          <thead>
            <tr>
              <th className="col-priority">Prioritas</th>
              <th className="col-category">Kategori</th>
              <th>Tindakan</th>
            </tr>
          </thead>
          <tbody>
            {data.mitigasi.map((m) => (
              <tr key={m.prioritas}>
                <td className="col-priority">
                  <span
                    className="priority-badge"
                    style={{
                      backgroundColor: m.prioritas === 1 ? "#fee2e2" : m.prioritas === 2 ? "#fef3c7" : "#dbeafe",
                      color: m.prioritas === 1 ? "#dc2626" : m.prioritas === 2 ? "#d97706" : "#2563eb",
                    }}
                  >
                    P{m.prioritas}
                  </span>
                </td>
                <td className="col-category">{m.kategori}</td>
                <td>{m.tindakan}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <PageFooter page={2} totalPages={3} />
      </section>

      {/* ═══════════════════════════════════════════════════════════
          PAGE 3 — AI SUMMARY + INSIGHTS + METADATA + DISCLAIMER
         ═══════════════════════════════════════════════════════════ */}
      <section className="print-page">
        <PageHeader wilayah={data.wilayah} />

        {/* Quick Insights */}
        <SectionHeading title="Ringkasan Cepat" />
        <div className="insights-grid">
          <InsightCard
            label="Status Tanam"
            value={
              data.fri <= 33
                ? "Aman — Tanam Normal"
                : data.fri <= 66
                  ? "Waspada — Perlu Pencegahan"
                  : "Bahaya — Tunda Penanaman"
            }
            color={color}
          />
          <InsightCard
            label="Komoditas Terbaik"
            value={data.rekomendasi[0]?.komoditas ?? "—"}
            color="#16a34a"
          />
          <InsightCard
            label="Skor Tertinggi"
            value={data.rekomendasi[0] ? `${data.rekomendasi[0].skor.toFixed(0)}/100` : "—"}
            color="#2563eb"
          />
          <InsightCard
            label="Jumlah Mitigasi"
            value={`${data.mitigasi.length} tindakan`}
            color="#7c3aed"
          />
        </div>

        {/* Metadata */}
        <SectionHeading title="Metadata Teknis" />
        <table className="report-table metadata-table">
          <tbody>
            <tr><td>Sistem</td><td>FloodRisk AI — Sistem Pendukung Keputusan Risiko Banjir</td></tr>
            <tr><td>Model Prediksi</td><td>{data.model} v{data.versi_model}</td></tr>
            <tr><td>Sumber Data Cuaca</td><td>{data.sumber_data}</td></tr>
            <tr><td>Waktu Prediksi</td><td>{data.waktu_prediksi}</td></tr>
            <tr><td>Data Historis</td><td>{data.hari_historis} hari</td></tr>
            <tr><td>Fitur Model</td><td>{REALTIME_LABELS.rainfall}, {REALTIME_LABELS.rain7}, {REALTIME_LABELS.humidity}, {REALTIME_LABELS.tavg}</td></tr>
            <tr><td>Target</td><td>{REALTIME_LABELS.fri} 0–100</td></tr>
            <tr><td>Klasifikasi</td><td>Rendah (0–33) • Sedang (34–66) • Tinggi (67–100)</td></tr>
          </tbody>
        </table>

        {/* Disclaimer */}
        <SectionHeading title="Disclaimer" />
        <div className="disclaimer-box">
          <p>
            Dokumen ini merupakan hasil analisis otomatis oleh sistem FloodRisk AI
            berdasarkan data cuaca dari Open-Meteo dan model prediksi Machine Learning.
            Hasil prediksi bersifat estimasi dan tidak menjamin kondisi aktual di lapangan.
          </p>
          <p>
            Keputusan budidaya tetap berada pada pengguna dengan mempertimbangkan
            kondisi lapangan, pengalaman praktis, dan konsultasi dengan pihak berwenang
            (Dinas Pertanian, BPBD, BMKG).
          </p>
        </div>

        {/* Authors & License */}
        <div className="report-authors">
          <SectionHeading title="Informasi Dokumen" />
          <table className="report-table metadata-table">
            <tbody>
              <tr><td>Institusi</td><td>Universitas Islam Negeri Sultan Syarif Kasim Riau</td></tr>
              <tr><td>Program Studi</td><td>Teknik Informatika</td></tr>
              <tr><td>Peneliti</td><td>Aprizal</td></tr>
              <tr><td>Lisensi</td><td>Research Project — Non-commercial</td></tr>
            </tbody>
          </table>
        </div>

        <PageFooter page={3} totalPages={3} />
      </section>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════
   SUB-COMPONENTS
   ═══════════════════════════════════════════════════════════ */

function PageHeader({ wilayah }: { wilayah: string }) {
  return (
    <header className="page-header">
      <span className="header-title">FloodRisk AI — Forecast Report | {wilayah}</span>
    </header>
  );
}

function PageFooter({ page, totalPages }: { page: number; totalPages: number }) {
  const now = new Date();
  const dateStr = now.toLocaleDateString("id-ID", {
    timeZone: "Asia/Jakarta",
    day: "2-digit",
    month: "long",
    year: "numeric",
  });
  const timeStr = now.toLocaleTimeString("id-ID", {
    timeZone: "Asia/Jakarta",
    hour: "2-digit",
    minute: "2-digit",
  });
  return (
    <footer className="page-footer">
      <span className="footer-date">{dateStr} • {timeStr} WIB</span>
      <span className="footer-page">Halaman {page} / {totalPages}</span>
    </footer>
  );
}

function SectionHeading({ title }: { title: string }) {
  return (
    <div className="section-heading">
      <h2>{title}</h2>
      <div className="section-divider" />
    </div>
  );
}

function MetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="meta-row">
      <span className="meta-label">{label}</span>
      <span className="meta-value">{value}</span>
    </div>
  );
}

function InsightCard({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <div className="insight-card">
      <span className="insight-label">{label}</span>
      <span className="insight-value" style={{ color }}>{value}</span>
    </div>
  );
}
