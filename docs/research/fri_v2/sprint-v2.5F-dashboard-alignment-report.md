# Sprint v2.5F Dashboard Alignment Report

## Scope

Dashboard presentation only. No backend, model, feature engineering, prediction logic, API routing, authentication, database, or deployment code was changed.

## Changes

- Added frontend display mapping for realtime FRI v2 values in `apps/web/lib/realtime-presentation.ts`.
- Updated realtime dashboard cards and radar labels to use public labels only:
  - Curah Hujan
  - Akumulasi Hujan 7 Hari
  - Kelembapan
  - Suhu Rata-rata
  - Flood Risk Index
  - Risiko
  - Prediksi
- Updated map popup history rendering to remove temperature range and display FRI v2-aligned labels.
- Updated AI evidence panel to remove Tmax/Tmin temperature range and display FRI v2-aligned values.
- Updated report panel and printable report weather summary to remove internal feature names and legacy Tmax/Tmin/range display.
- Extended frontend TypeScript response types with optional runtime fields for already-returned feature values only.

## Data Handling

- The frontend does not calculate `Rain7`, `Tavg`, FRI, or risk class.
- Values are read only from the realtime response or saved history entry.
- If `Akumulasi Hujan 7 Hari` or `Suhu Rata-rata` are not present in the realtime response, the UI displays `—`.
- Optional internal response keys are mapped to public labels and are not displayed directly.

## Files Changed

- `apps/web/lib/realtime-presentation.ts`
- `apps/web/types/api.ts`
- `apps/web/hooks/use-search-history.ts`
- `apps/web/components/dashboard/dashboard-screen.tsx`
- `apps/web/components/dashboard/dashboard-panel.tsx`
- `apps/web/components/dashboard/analytics-panel.tsx`
- `apps/web/components/dashboard/ai-support-panel.tsx`
- `apps/web/components/dashboard/reports-panel.tsx`
- `apps/web/components/map/RegionPopup.ts`
- `apps/web/components/report/PrintableReport.tsx`

## Guardrails

- Backend: unchanged
- Random Forest artifacts: unchanged
- Feature engineering: unchanged
- Prediction logic: unchanged
- API route contract: unchanged
- Authentication/session flow: unchanged

## Validation

Local frontend validation passed from `apps/web`:

- `npm run lint`
- `npx tsc --noEmit`
- `npm run build`

Build warnings observed and unchanged from prior frontend validation:

- Next.js inferred the workspace root because multiple lockfiles exist.
- Next.js reports the `middleware` file convention is deprecated in favor of `proxy`.
