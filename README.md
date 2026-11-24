# Energy-Poverty Trajectory Clustering for Indonesian Provinces (2025 → 2050)

> **Status:** work-in-progress, partial publication.
> This repository publishes a small, fully reproducible slice of my ongoing
> undergraduate thesis on residential cooling energy poverty in Indonesia.
> It is **not peer-reviewed**.
## What is this?

For each of Indonesia's 34 provinces we compare a **simulated residential
cooling demand** (EnergyPlus archetype, hourly weather) with the **normalised
per-customer consumption planned in the national electricity plan (RUPTL)**:

    EP = Simulated − RUPTL   [kWh/customer/year]

`EP > 0` means cooling need that the grid does not yet serve (*suppressed
demand*). Combining EP with the urbanisation ratio (UR) and hourly Cooling
Degree Days (CDD, base 25 °C; 2050 = morphed SSP2-4.5), we cluster provinces
**(a)** per year ("static" layers) and **(b)** on their 2025→2050 *trajectory*
(ΔEP, ΔUR, ΔCDD), to obtain groups that can be mapped to differentiated
energy-policy interventions.

## Documentation & Mathematical Formulation

For a rigorous mathematical explanation of the methods used in this repository, please refer to the technical note provided in the `docs/` folder:

📄 **`docs/projection_cluster_notes.tex`** (PDF also available on the same directory).

This document details:
1. **Data Projections to 2050:**
   - **Compound Annual Growth Rate (CAGR)** formulation for RUPTL electricity consumption projections.
   - **Logistic Growth Model (LGM)** formulation for Urbanization Ratio (UR) projections.
2. **Silhouette Cluster Analysis:**
   - Z-score standardization and Euclidean distance metrics.
   - K-Means algorithm formulation (WCSS minimization).
   - Silhouette coefficient equations ($a(i)$, $b(i)$, $s(i)$) and the statistical screening rules (C1-C4) used to select the optimal $k$.

## Data

`data/province_panel.csv` (34 rows) — see `data/DATA_NOTE.md` for provenance,
conventions, and the columns deliberately **not** redistributed (raw RUPTL
tables and per-province EnergyPlus outputs remain in the thesis dataset until
validation is complete). All clustering results in this repo reproduce fully
from the published file.

Known data artifacts, treated as *anomaly clusters*, not population regimes:
- Bali, Sumatera Selatan, DIY → explosive RUPTL CAGR projections;
- Jawa Barat, DIY → highland EPW stations understating baseline CDD.

## Methods (short version)

1. z-score standardisation per layer (incommensurable units);
2. K-Means (k-means++ seeding, 100 restarts, seed 42);
3. silhouette sweep S(k), k = 2…6, with Kaufman–Rousseeuw bands;
4. screening: C1 no singletons, C2 min cluster silhouette ≥ 0.25;
   C4 (theoretical admissibility) applied manually and documented;
5. k\* = argmax S(k) over admissible k, overridable by an explicit,
   documented policy decision.

**Adopted solutions.** Static 2025: k = 2 (S ≈ 0.61, "reasonable" band).
Trajectory: the unconstrained silhouette optimum is k = 4 (S ≈ 0.465); the
published policy-level analysis uses **k = 2** (mainstream n = 30 vs anomaly
n = 4), a decision taken with the thesis supervisor for matrix simplicity.
Both are reproducible from the CLI (`--force-k`).

## Repository layout

```
data/            province panel + provenance note
src/epcluster/   config, data, clustering, plotting, mapping
scripts/         run_clustering.py, make_figures.py
outputs/         generated CSV/JSON/PNG 
```

## Quick start

```bash
pip install -r requirements.txt
python scripts/run_clustering.py --layer trajectory --force-k 2
python scripts/make_figures.py --layer trajectory --k 2        # add --map for choropleth
```

Outputs: `outputs/membership_*.csv`, `outputs/centroids_*.csv`,
`outputs/summary_*.json`, `outputs/figures/*.png`.

## Reproducibility & honesty notes

- Seed 42 and 100 restarts are locked in `src/epcluster/config.py`.
- Silhouette values for these continuous geographical data fall in the
  "weak but real" band; this is expected and reported.
- Static layers are standardised per year, so cluster membership expresses
  *relative* position; absolute change is read from the trajectory layer.
- EP 2050 inherits RUPTL projection assumptions; 2050 clusters are therefore
  scenario-driven regimes, and alternative projections are sensitivity checks
  in the thesis (not yet published here).


