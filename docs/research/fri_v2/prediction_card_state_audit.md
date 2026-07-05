# Prediction Card State Audit - FRI v2

## Status

Strict read-only audit completed. No source code was modified. This document is the only intended output.

## Final Verdict

⚠ Multiple state synchronization issues

The dismissal path does not clear the authoritative selected-region state. The popup close control only hides the visual popup, while the explicit remove path in `dashboard-screen.tsx` reassigns `wilayah` to another region instead of clearing selection. As a result, the card/selection remains active after the first click and only disappears after a subsequent dismissal against the newly selected region.

## 1. State Flow Diagram

```text
Map marker / search result / detail button
  -> setWilayah(w)
  -> useWilayahSync updates URL + localStorage
  -> DashboardScreen rerenders with wilayah
  -> useRealtimePrediction(wilayah)
  -> realtime API response
  -> useEffect upsert(history entry)
  -> useSearchHistory history array updates
  -> MapContainer derives activeEntry = history.find(h.wilayah === wilayah)
  -> MapContainer opens popup for wilayah
  -> RegionPopup renders
  -> close/remove action
     -> popup.close() only, or
     -> onRemoveCity(w) -> remove(w) -> setWilayah(remaining[0] || "Pekanbaru")
  -> new wilayah remains selected instead of being cleared
```

## 2. Component Interaction Diagram

```text
DashboardScreen
  |-- useWilayahSync() -> wilayah, setWilayah
  |-- useSearchHistory() -> history, upsert, remove, clear
  |-- useRealtimePrediction(wilayah)
  |-- MapContainer
        |-- activeEntry = history.find(h.wilayah === wilayah)
        |-- window.__regionPopupDetail__ -> onMarkerClick -> setWilayah
        |-- window.__regionPopupRemove__ -> onRemoveCity
        |-- popup refs / marker refs
        |-- openPopup(wilayah)
        |-- openAllPopups()
  |-- DashboardPanel / AISupportPanel / ReportsPanel
        |-- consume same `data`
```

## 3. State Ownership Table

| State | Owner | Initial Value | Update Path | Clear Path | Notes |
|---|---|---|---|---|---|
| `wilayah` | `useWilayahSync` in `DashboardScreen` | URL param, localStorage, or `Pekanbaru` | `setWilayah(w)` from search, marker click, detail button, or fallback removal | No true clear path; `handleRemoveCity` falls back to another wilayah or `Pekanbaru` | This is the authoritative selected-region state. |
| `history` | `useSearchHistory` | `[]` | `upsert(entry)` after realtime response | `remove(w)`, `clear()`, `clear(wilayah)` | Stores last prediction snapshot per wilayah. |
| `activeMenu` | `useWorkspaceStore` | `dashboard` | `switchTo(menu)` | N/A | Unrelated to the bug. |
| `activeEntry` | Derived in `MapContainer` | `undefined` if no match | `history.find(h => h.wilayah === wilayah)` | Clears only when `wilayah` or matching history entry disappears | Derived state, not independently owned. |
| Popup visibility | MapLibre popup refs in `MapContainer` | Closed until opened | `popup.addTo(map)` / `popup.remove()` | `popup.remove()` | Visual popup state is separate from selection state. |

## 4. Close Button Execution Flow

### Visual popup close button

`MapContainer` creates popups with `closeButton: true` and `closeOnClick: false`.

```ts
const popup = new maplibregl.Popup({
  offset: 20,
  maxWidth: "260px",
  closeButton: true,
  closeOnClick: false,
  className: "region-popup",
})
```

There is no application-level `onClose` callback wired to the maplibre close button. So the X only closes the popup UI layer.

### Custom remove action in popup content

`RegionPopup.ts` also injects a custom remove button:

```html
onclick="window.__regionPopupRemove__('${h.wilayah}')"
```

That delegates to:

```ts
window.__regionPopupRemove__ = (w: string) => onRemoveCity(w);
```

Then `DashboardScreen.handleRemoveCity()` executes:

```ts
remove(w);
if (w === wilayah) {
  const remaining = history.filter((h) => h.wilayah !== w);
  setWilayah(remaining.length > 0 ? remaining[0].wilayah : "Pekanbaru");
}
```

## 5. First Click vs Second Click

### After the first click

State changes that happen:

- The popup may close visually (`popup.remove()` from the maplibre X, or `remove(w)` from the custom button).
- If the custom remove path is used, the clicked wilayah is removed from `history`.
- If the removed wilayah was the current selection, `setWilayah(...)` immediately selects another region or `Pekanbaru`.

State that remains unchanged:

- There is no state representing “no selected region”.
- `wilayah` is never cleared to empty/null.
- `MapContainer` still has an active selection derived from `wilayah`.

Why the card can still stay visible:

- `activeEntry` is derived from `history.find(h => h.wilayah === wilayah)`.
- `MapStatusBar` and polygon highlighting also key off `wilayah`.
- The UI therefore keeps showing a selected region even after one dismissal.

### After the second click

- The user is now dismissing the fallback-selected region.
- That second dismissal finally removes the currently selected snapshot, so the card disappears.

## 6. Duplicate State Check

### Single source of truth?

No.

### Actual ownership

- `wilayah` is the authoritative selected-region state.
- `history` stores rendered prediction snapshots.
- Popup visibility is an independent MapLibre UI state.
- `activeEntry` is derived from both `history` and `wilayah`.

### Why this matters

The close action is expected to clear selection, but the code only manipulates popup visibility or history membership. It never transitions selection into a cleared state.

## 7. Race / Effect / Propagation Check

No strong evidence of a race condition is required to explain the bug.

Observed behavior is consistent with deterministic synchronization:

- `handleRemoveCity()` reassigns `wilayah`.
- `MapContainer` derives `activeEntry` from that reassigned `wilayah`.
- `openPopup(wilayah)` is also tied to `wilayah` and can reopen the same selected context.
- No async API response is needed to overwrite the dismissal action.

## 8. Selection Sync Check

| Area | Synchronizes Correctly? | Evidence |
|---|---|---|
| `selectedRegion` / `wilayah` | No | Removal path reassigns to another wilayah instead of clearing. |
| Prediction card / popup | Partially | Popup can close visually, but selection remains active. |
| Map marker / polygon | Partially | Highlighting follows `wilayah`, so selection persists. |
| Analytics | Yes | Reads the current realtime `data`, not dismissal state. |
| Reports | Yes | Reads the current realtime `data`, not dismissal state. |
| AI evidence | Yes | Reads the current realtime `data`, not dismissal state. |

## 9. Root Cause

**One root cause:** the dismissal flow does not clear the authoritative `wilayah` selection; instead, `handleRemoveCity()` preserves selection by switching to another region (or `Pekanbaru`) after removing the current one, while the popup close button itself only closes the visual popup with no app-state callback.

Evidence:

- `MapContainer` wires popup actions through globals and has no close callback for the popup X.
- `DashboardScreen.handleRemoveCity()` reassigns `wilayah` instead of clearing it.
- `MapContainer` derives `activeEntry` from `history.find(h => h.wilayah === wilayah)`, so any non-cleared `wilayah` keeps the selection active.

## 10. Minimal Implementation Plan

Documentation-only recommendation for a future fix:

1. Change the dismissal handler to clear selection instead of selecting another region when the user closes the prediction card.
2. Make the popup close callback and the custom remove action share one selection-clearing path.
3. Keep `history` removal separate from selection clearing so the card can close immediately even when history remains.
4. Update `MapContainer`/`DashboardScreen` only, because those are the components that own selection and history coordination.

## 11. Regression Risk

If fixed correctly, these areas could be affected:

| Area | Risk |
|---|---|
| Dashboard | Selected-region context may no longer auto-fallback to the next history item. |
| Popup | Popup close behavior changes from visual-only to state-clearing. |
| Realtime | No model impact; only selection state is affected. |
| Analytics | Minimal; should continue to follow the current `data` prop. |
| Reports | Minimal; should continue to follow the current `data` prop. |
| AI | Minimal; should continue to follow the current `data` prop. |
| Map interaction | Highest risk; marker/polygon selection and popup open/close flow are coupled here. |
