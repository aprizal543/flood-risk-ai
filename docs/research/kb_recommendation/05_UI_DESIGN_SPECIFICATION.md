# Frontend UI Specification — Knowledge-Based Recommendation

## 1. Design Principles

1. **Progressive enhancement**: New UI components coexist with existing dashboards. Users see an enriched experience without disruption.
2. **Information layering**: Summary first, detail on demand. Each level reveals more information progressively.
3. **Decision clarity**: Users should immediately understand what to plant, what to avoid, and why.
4. **Scientific transparency**: Every recommendation traces back to a rule and knowledge source.
5. **Mobile-first**: All components responsive down to 360px viewport width.

## 2. UI Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        RECOMMENDATION DASHBOARD                         │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SECTION 1: PREDICTION SUMMARY (UNCHANGED)                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │   │
│  │  │ FRI Gauge│  │ Weather  │  │ Weather  │  │ Risk     │       │   │
│  │  │          │  │ Metrics  │  │ Radar    │  │ Factors  │       │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SECTION 2: KNOWLEDGE-BASED RECOMMENDATION (REDESIGNED)         │   │
│  │                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  2a. DECISION BANNER (NEW)                              │    │   │
│  │  │  ┌──────────────────────────────────────────────────┐   │    │   │
│  │  │  │ 🟢 Keputusan Tanam: Tanam Normal                 │   │    │   │
│  │  │  │ Semua komoditas tersedia.                         │   │    │   │
│  │  │  └──────────────────────────────────────────────────┘   │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  2b. RECOMMENDATION CATEGORY TABS (NEW)                 │    │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                │    │   │
│  │  │  │ ✅ 12    │ │ ⚠️  2   │ │ ❌  3   │                │    │   │
│  │  │  │ Direko-  │ │ Alterna- │ │ Tidak    │                │    │   │
│  │  │  │ mendasi  │ │ tif      │ │ Direko-  │                │    │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘                │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                  │   │
│  │  ┌─────────────────────────────────────────────────────────┐    │   │
│  │  │  2c. COMMODITY CARD LIST (REDESIGNED)                   │    │   │
│  │  │  ┌──────────────────────────────────────────────────┐   │    │   │
│  │  │  │  COMMODITY CARD (see Section 3)                  │   │    │   │
│  │  │  ├──────────────────────────────────────────────────┤   │    │   │
│  │  │  │  COMMODITY CARD                                  │   │    │   │
│  │  │  ├──────────────────────────────────────────────────┤   │    │   │
│  │  │  │  COMMODITY CARD                                  │   │    │   │
│  │  │  └──────────────────────────────────────────────────┘   │    │   │
│  │  └─────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SECTION 3: COMMODITY DETAIL MODAL (NEW)                        │   │
│  │  (Opened on card click)                                         │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SECTION 4: MITIGATION TIMELINE (ENHANCED)                      │   │
│  │  - Per-commodity mitigation actions                             │   │
│  │  - Precondition enforcement                                     │   │
│  │  - Risk-level general actions                                   │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │  SECTION 5: KNOWLEDGE SOURCE FOOTER (NEW)                       │   │
│  │  - Version info                                                 │   │
│  │  - Reference links                                              │   │
│  │  - Assumption status                                            │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 3. Commodity Card Design

### 3.1 Card Layout (Wireframe)

```
┌──────────────────────────────────────────────────────────────────┐
│  [RECOMMENDATION BADGE]                             [SCORE] 92.5 │
│  🟢 Sangat Direkomendasikan                       ━━━━━━━━━━━━━ │
│                                                                  │
│  Kangkung                                        [▶ Expand]      │
│  Ipomoea aquatica  •  sayuran_daun                               │
│                                                                  │
│  ┌──────┬───────────────────────────────────────────────────┐   │
│  │      │ Vulnerability:  ■■■■■ Sangat Tinggi               │   │
│  │ ICON │ Inundation:     ■■■■■ >7 hari                     │   │
│  │      │ Drainase:       ■□□□□ Minimal                     │   │
│  │      │ Siklus:         25 hari                           │   │
│  └──────┴───────────────────────────────────────────────────┘   │
│                                                                  │
│  Dampak Utama:                                                    │
│  • Pertumbuhan subur di genangan                                 │
│  • Adaptasi semi-aquatic                                         │
│                                                                  │
│  Gejala Kerusakan:                                                │
│  • Tidak ada gejala kerusakan berarti (pada genangan <7 hari)    │
│                                                                  │
│  Aturan yang Diterapkan:                                          │
│   R_M1: Kelompok toleransi A lolos seleksi                     │
│   R_M5: Prioritas toleransi > ekonomi                          │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Card States

| State | Visual | Description |
|-------|--------|-------------|
| **Recommended** | Green left border, green badge | Commodity is safe to plant |
| **Alternative** | Amber left border, amber badge | Conditional recommendation with preconditions |
| **Not Recommended** | Red left border, red badge | Commodity should not be planted |
| **Expanded** | Full card with all details | User tapped "Expand" |
| **Collapsed** | Summary view only | Default state |

### 3.3 Recommendation Badge Specifications

| Category | Label | Color | Icon |
|----------|-------|-------|------|
| `direkomendasikan` (score ≥ 80) | Sangat Direkomendasikan | `#22c55e` | `check_circle` |
| `direkomendasikan` (score 60–79) | Direkomendasikan | `#16a34a` | `check_circle` |
| `alternatif` | Alternatif (Dengan Syarat) | `#f59e0b` | `warning` |
| `tidak_direkomendasikan` | Tidak Direkomendasikan | `#ef4444` | `cancel` |

### 3.4 Vulnerability Indicator (Visual Bar)

Each commodity card includes a horizontal bar visualization for key attributes:

```
Vulnerability:  ■■■■■■■□□□  70%  (Sangat Tinggi)
Inundation:     ■■■■■■■■■■  100% (>7 hari)
Drainase:       ■■□□□□□□□□  20%  (Minimal)
```

The bar is color-coded:
- Green (safe) for favourable attributes
- Red (warning) for unfavourable attributes
- Width proportional to ordinal position (0–100%)

## 4. Decision Banner Design

### 4.1 Wireframe

```
┌──────────────────────────────────────────────────────────────────┐
│  [ICON]  KEPUTUSAN TANAM: TANAM DENGAN PENCEGAHAN               │
│          Risiko meningkat. Pilih komoditas dengan toleransi      │
│          banjir sedang hingga tinggi.                            │
│                                                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐                                     │
│  │ ✅ 7 │ │ ⚠️ 2 │ │ ❌ 6 │                                     │
│  │ Dire-│ │ Alter│ │ Tidak│                                     │
│  │ kom  │ │ natif│ │ Direk│                                     │
│  └──────┘ └──────┘ └──────┘                                     │
└──────────────────────────────────────────────────────────────────┘
```

### 4.2 Decision Banner States

| Risk Level | Keputusan Tanam | Background | Icon |
|------------|-----------------|------------|------|
| Rendah | Tanam Normal | `bg-green-50` / dark: `bg-green-950` | ✅ |
| Sedang | Tanam Dengan Pencegahan | `bg-amber-50` / dark: `bg-amber-950` | ⚠️ |
| Tinggi | Tunda atau Lindungi | `bg-red-50` / dark: `bg-red-950` | 🛑 |

## 5. Category Tabs Design

### 5.1 Wireframe

```
┌──────────────────────────────────────────────────────────────────┐
│  [✅ Recommended (7)]  [⚠️ Alternative (2)]  [❌ Not Rec. (6)]   │
└──────────────────────────────────────────────────────────────────┘
```

- Active tab: underlined, bold text, matching category color
- Inactive tabs: muted text
- Count badge: small pill with count number
- When `not_recommended` tab is active, cards show red styling and `alasan_penolakan`

## 6. Commodity Detail Modal

### 6.1 Wireframe

```
┌──────────────────────────────────────────────────────────────┐
│  ✕                                                Kangkung   │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Nama Ilmiah    │  Ipomoea aquatica                   │  │
│  │  Kategori       │  sayuran_daun                       │  │
│  │  Toleransi      │  Sangat Tinggi                      │  │
│  │  Genangan Maks  │  >7 hari                            │  │
│  │  Drainase       │  Minimal                            │  │
│  │  Siklus Tanam   │  25 hari                            │  │
│  │  Prioritas Eko  │  Sangat Tinggi                      │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  Dampak Utama:                                                 │
│  • Pertumbuhan subur di genangan                              │
│  • Adaptasi semi-aquatic                                      │
│                                                               │
│  Gejala Kerusakan:                                             │
│  • Tidak ada gejala kerusakan berarti                         │
│                                                               │
│  Rekomendasi Penanaman:                                        │
│  Semi-aquatic; tumbuh subur di kondisi tergenang.             │
│  Ideal untuk area rawan banjir.                               │
│                                                               │
│  Sumber Ilmiah:                                                │
│  📖 FAO aquatic vegetable cultivation guides [Asumsi]         │
│                                                               │
│  [  Lihat Detail di Aturan  ]  [  Tutup  ]                    │
└──────────────────────────────────────────────────────────────┘
```

## 7. Knowledge Source Footer

### 7.1 Wireframe

```
┌──────────────────────────────────────────────────────────────────┐
│  ⓘ  Sumber Pengetahuan                                          │
│  ├─ Pengetahuan v1.0  •  Aturan v1.0  •  17 komoditas          │
│  ├─ Status: Asumsi Penelitian — Referensi menunggu review       │
│  └─ Lihat semua referensi ilmiah → [Link]                       │
└──────────────────────────────────────────────────────────────────┘
```

## 8. Responsive Behaviour

| Breakpoint | Layout Changes |
|------------|----------------|
| ≥ 1024px | 2-column commodity card grid; full detail modal |
| 768–1023px | Single column cards; full detail modal |
| 480–767px | Single column; simplified cards; modal collapses to bottom sheet |
| < 480px | Compact cards; hide scientific names; full-screen bottom sheet modal |

## 9. Component Hierarchy (React)

```
DashboardScreen
├── PredictionSummary (UNCHANGED)
│   ├── FRIHeroGauge
│   ├── WeatherMetricsGrid
│   ├── RiskRadarChart
│   └── QuickInsights
│
├── KBRecommendationSection (NEW — replaces RecommendationAccordion)
│   ├── DecisionBanner (NEW)
│   ├── RecommendationTabs (NEW)
│   │   ├── TabButton("recommended", count)
│   │   ├── TabButton("alternative", count)
│   │   └── TabButton("not_recommended", count)
│   ├── CommodityCardList (REDESIGNED)
│   │   ├── CommodityCard
│   │   │   ├── RecommendationBadge
│   │   │   ├── CommoditySummary
│   │   │   ├── VulnerabilityBars
│   │   │   ├── ImpactsList
│   │   │   └── RulesApplied
│   │   └── CommodityCardSkeleton
│   ├── CommodityDetailModal (NEW)
│   │   ├── CommodityInfoTable
│   │   ├── ImpactsSection
│   │   ├── RecommendationNotes
│   │   └── ScientificReference
│   └── KnowledgeSourceFooter (NEW)
│
├── MitigationTimeline (ENHANCED)
│   ├── GeneralMitigationActions
│   └── PerCommodityMitigation
│
└── AIAssistantPanel (UNCHANGED)
```

## 10. Color Scheme

| Category | Light Mode | Dark Mode | Usage |
|----------|------------|-----------|-------|
| Recommended | `#22c55e` (green-500) | `#4ade80` (green-400) | Badge, borders, icons |
| Alternative | `#f59e0b` (amber-500) | `#fbbf24` (amber-400) | Badge, borders, icons |
| Not Recommended | `#ef4444` (red-500) | `#f87171` (red-400) | Badge, borders, icons |
| Low Risk Banner | `#dcfce7` bg | `#052e16` bg | Decision banner |
| Medium Risk Banner | `#fef3c7` bg | `#451a03` bg | Decision banner |
| High Risk Banner | `#fee2e2` bg | `#450a0a` bg | Decision banner |
| Vulnerability Bar | Green→Red gradient | Green→Red gradient | Attribute indicator |

## 11. Interaction Design

| Interaction | Behaviour |
|-------------|-----------|
| Tap commodity card | Opens CommodityDetailModal |
| Tap badge | Scrolls to rule explanation |
| Swipe card (mobile) | Switches to next/previous commodity |
| Tap tab | Filters card list by category |
| Long-press vulnerability bar | Shows tooltip with ordinal value |
| Pull-to-refresh | Triggers new prediction fetch |

## 12. Accessibility Requirements

- All badges and icons must have `aria-label` descriptions
- Colour is never the sole indicator of recommendation category (text labels always present)
- Tab order: Decision banner → Tabs → Cards → Mitigation → Knowledge source
- Focus indicators on all interactive elements
- Screen reader announcements on tab switch and card expand
- All colour combinations meet WCAG AA contrast ratio (4.5:1 for normal text)
