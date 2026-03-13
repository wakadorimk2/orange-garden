# Heatmap Metric Derivation Spec

> Scope: Issue #407 - source normalization and shipped density derivation
> Status: draft
> Role: source of truth for the metric-side pipeline that sits before bucket mapping, palette, and UI rendering

---

## 1. Purpose

This document defines the metric-side baseline and future derivation seam for the shipped heatmap.

Step 1 of Issue #407 fixes the current shipped semantics first, before comparing normalization or introducing a future derived metric.

This step does not change `/api/heatmap`.

---

## 2. Current Shipped Baseline

The current shipped heatmap metric is `shipped_density`.

Per local date, the shipped count is:

```text
shipped_density[date] = count(events WHERE
    local_date(ts) == date
    AND domain != "summary"
    AND source != "web-form-ui"
)
```

This is the current `display_population`.

Operationally, `/api/heatmap` returns the last local 28 days, including zero-value days, as:

```json
[{ "date": "YYYY-MM-DD", "count": N }]
```

Current implementation reference:

- `src/personal_mcp/tools/daily_summary.py::count_events_by_date`
- `docs/heatmap-state-density-spec.md` Section 2 and Section 3

---

## 3. Included And Excluded Populations

### Included in current shipped heatmap

- user-authored non-summary events
- events that belong to the current shipped observation surface

### Excluded from current shipped heatmap

- `domain == "summary"`
  - daily summary artifacts
  - derived data, not primary observation input
- `source == "web-form-ui"`
  - UI telemetry
  - system-generated interaction records

This exclusion fixes the current shipped heatmap as an observation-first surface rather than a raw activity counter.

---

## 4. Debug Boundary

The following fields are debug or verification surfaces and are not the shipped primary metric:

- `raw_count`
- `telemetry_count`
- `life_count`

`/api/heatmap/debug` may expose these values for verification, but Step 1 keeps them outside the shipped baseline contract.

In other words:

- shipped surface: `shipped_density`
- debug surface: raw and comparison-oriented breakdowns

---

## 5. What Step 1 Does Not Decide

Step 1 intentionally does not decide any of the following:

- source-family normalization strategy
- weighting across source families
- compression or cap policy
- future normalized metric naming
- bucket thresholds
- palette behavior
- temporal aggregation policy
- history navigation or summarized rendering semantics

Those belong to later steps in Issue #407 or to downstream issues such as `#355`, `#408`, and UI-track issues.

---

## 6. Why This Baseline Must Be Fixed First

The current dataset already shows a large gap between raw activity volume and shipped observation value.

As of the 2026-03-12 audit snapshot:

- the primary 365-day window contains 360 zero days
- only 5 days are currently non-zero
- non-zero shipped density values range from 7 to 41

This is enough to justify a future normalization discussion, but not enough reason to blur the meaning of the current shipped metric.

Step 1 therefore treats current shipped semantics as a fixed baseline that later design steps can compare against.

---

## 7. Downstream Implications

### For `#355`

`#355` should treat current `shipped_density` semantics as a fixed input meaning until Issue `#407` defines a successor normalized input contract.

### For `#360`

`#360` can compare raw, shipped, and future normalized views, but should not redefine the shipped baseline here.

### For `#408`

`#408` may assume a daily metric input exists, but should not redefine the current shipped observation population.

---

## 8. Decision Summary For Step 1

- keep current `/api/heatmap` semantics fixed as the baseline
- treat current shipped heatmap as `display_population`, not raw activity count
- keep debug metrics outside the shipped baseline contract
- postpone normalization and derivation design to later steps of `#407`

---

## 9. References

- `docs/heatmap-state-density-spec.md`
- `docs/heatmap-density-audit-2026-03-12.md`
- `src/personal_mcp/tools/daily_summary.py`
- Issue `#407`
- Issue `#355`
- Issue `#360`
- Issue `#408`
