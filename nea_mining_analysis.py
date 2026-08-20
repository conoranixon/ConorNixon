#!/usr/bin/env python3
"""
Near-Earth Asteroid (NEA) space-mining candidate survey
=======================================================

Selects Earth-crossing asteroids (Apollo + Aten orbit classes) with
diameter >= 140 m from the NASA/JPL Small-Body Database, builds a
size-frequency histogram, and estimates the total available mass.

Methodology
-----------
* Earth-crossing = JPL orbit classes APO (Apollo: a > 1 au, q < 1.017 au)
  and ATE (Aten: a < 1 au, Q > 0.983 au). Amors and Atiras approach but do
  not cross Earth's orbit, so they are excluded.
* Diameter: measured values (radar/occultation/thermal IR) are used where
  available (~4% of objects). Otherwise the diameter is estimated from the
  absolute magnitude H:  D(km) = (1329 / sqrt(p_V)) * 10^(-H/5)
  with an assumed geometric albedo p_V = 0.14 (the observed NEA average).
* Mass: each body is treated as a sphere with a bulk density of
  2000 kg/m^3 (between rubble-pile C-types ~1300 and coherent S-types
  ~2700). A per-object density is not knowable without spectral data, so
  low/high sensitivity bounds are also reported.

Outputs
-------
* data/nea_apollo_aten.csv        - raw catalog snapshot (cached)
* output/size_frequency_histogram.png
* output/summary.md               - headline numbers and caveats
"""

from __future__ import annotations

import json
import math
import os
import urllib.parse
import urllib.request

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
API_URL = "https://ssd-api.jpl.nasa.gov/sbdb_query.api"
FIELDS = ["spkid", "full_name", "H", "diameter", "albedo", "class", "a", "q", "e", "pha"]
ORBIT_CLASSES = "APO,ATE"          # Apollo + Aten = Earth-crossing
MIN_DIAMETER_KM = 0.140            # 140 m cutoff
ASSUMED_ALBEDO = 0.14              # mean NEA geometric albedo (Mainzer+ 2011)
DENSITY_KG_M3 = 2000.0             # nominal bulk density
DENSITY_LOW = 1300.0               # C-type rubble pile
DENSITY_HIGH = 2700.0              # coherent S-type

DATA_CSV = "data/nea_apollo_aten.csv"
HIST_PNG = "output/size_frequency_histogram.png"
SUMMARY_MD = "output/summary.md"


def fetch_catalog() -> pd.DataFrame:
    """Download the Apollo+Aten catalog from JPL SBDB (or load the cache)."""
    if os.path.exists(DATA_CSV):
        print(f"Using cached catalog {DATA_CSV}")
        return pd.read_csv(DATA_CSV)

    params = urllib.parse.urlencode(
        {"fields": ",".join(FIELDS), "sb-class": ORBIT_CLASSES, "sb-kind": "a"}
    )
    print("Querying JPL SBDB ...")
    with urllib.request.urlopen(f"{API_URL}?{params}", timeout=300) as resp:
        payload = json.load(resp)

    df = pd.DataFrame(payload["data"], columns=payload["fields"])
    for col in ("H", "diameter", "albedo", "a", "q", "e"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["full_name"] = df["full_name"].str.strip()

    os.makedirs(os.path.dirname(DATA_CSV), exist_ok=True)
    df.to_csv(DATA_CSV, index=False)
    print(f"Fetched {len(df):,} Apollo/Aten asteroids -> {DATA_CSV}")
    return df


def h_to_diameter_km(h: pd.Series, albedo: float = ASSUMED_ALBEDO) -> pd.Series:
    return (1329.0 / math.sqrt(albedo)) * 10.0 ** (-h / 5.0)


def sphere_mass_kg(diameter_km: pd.Series, density: float) -> pd.Series:
    radius_m = diameter_km * 500.0  # km -> m, then /2
    return density * (4.0 / 3.0) * np.pi * radius_m**3


def main() -> None:
    df = fetch_catalog()

    # Best-estimate diameter: measured where available, else from H.
    df["diameter_est_km"] = df["diameter"]
    from_h = df["diameter"].isna() & df["H"].notna()
    df.loc[from_h, "diameter_est_km"] = h_to_diameter_km(df.loc[from_h, "H"])
    df["diameter_source"] = np.where(df["diameter"].notna(), "measured", "from_H")
    df.loc[df["diameter_est_km"].isna(), "diameter_source"] = "unknown"

    no_size = int(df["diameter_est_km"].isna().sum())
    sel = df[df["diameter_est_km"] >= MIN_DIAMETER_KM].copy()

    sel["mass_kg"] = sphere_mass_kg(sel["diameter_est_km"], DENSITY_KG_M3)
    sel["mass_kg_low"] = sphere_mass_kg(sel["diameter_est_km"], DENSITY_LOW)
    sel["mass_kg_high"] = sphere_mass_kg(sel["diameter_est_km"], DENSITY_HIGH)
    sel = sel.sort_values("diameter_est_km", ascending=False)

    total = sel["mass_kg"].sum()
    total_low = sel["mass_kg_low"].sum()
    total_high = sel["mass_kg_high"].sum()
    top10_share = sel["mass_kg"].head(10).sum() / total

    # ------------------------------------------------------------------
    # Size-frequency histogram (log-spaced bins)
    # ------------------------------------------------------------------
    d_m = sel["diameter_est_km"].to_numpy() * 1000.0
    bins = np.logspace(np.log10(140.0), np.log10(d_m.max() * 1.05), 25)

    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(13, 5.5), constrained_layout=True
    )

    measured = sel["diameter_source"] == "measured"
    ax1.hist(
        [d_m[~measured.to_numpy()], d_m[measured.to_numpy()]],
        bins=bins,
        stacked=True,
        color=["#4878cf", "#e8a13c"],
        label=[
            f"Estimated from H (p$_V$={ASSUMED_ALBEDO})",
            "Measured diameter",
        ],
        edgecolor="white",
        linewidth=0.4,
    )
    ax1.set_xscale("log")
    ax1.set_yscale("log")
    ax1.set_xlabel("Diameter (m)")
    ax1.set_ylabel("Number of asteroids per bin")
    ax1.set_title(
        f"Size-frequency distribution: Earth-crossing NEAs $\\geq$ 140 m\n"
        f"(Apollo + Aten, n = {len(sel):,})"
    )
    ax1.legend()
    ax1.grid(True, which="both", alpha=0.25)

    # Cumulative mass vs diameter threshold
    order = np.argsort(d_m)[::-1]
    cum_mass = np.cumsum(sel["mass_kg"].to_numpy()[order])
    ax2.plot(d_m[order], cum_mass / 1e15, color="#c0392b", lw=2)
    ax2.set_xscale("log")
    ax2.set_xlabel("Diameter threshold D (m)")
    ax2.set_ylabel("Cumulative mass in bodies $\\geq$ D  (10$^{15}$ kg)")
    ax2.set_title(
        f"Cumulative mass ($\\rho$ = {DENSITY_KG_M3:.0f} kg/m$^3$)\n"
        f"Total $\\geq$ 140 m: {total:.2e} kg"
    )
    ax2.invert_xaxis()
    ax2.grid(True, which="both", alpha=0.25)

    os.makedirs(os.path.dirname(HIST_PNG), exist_ok=True)
    fig.savefig(HIST_PNG, dpi=160)
    print(f"Histogram -> {HIST_PNG}")

    # ------------------------------------------------------------------
    # Summary report
    # ------------------------------------------------------------------
    n_measured = int(measured.sum())
    top = sel.head(10)[["full_name", "class", "diameter_est_km", "diameter_source", "mass_kg"]]
    top_rows = "\n".join(
        f"| {r.full_name} | {r['class']} | {r.diameter_est_km:,.2f} | "
        f"{r.diameter_source} | {r.mass_kg:.2e} |"
        for _, r in top.iterrows()
    )

    summary = f"""# Earth-crossing NEAs >= 140 m: size-frequency and mass inventory

Data source: NASA/JPL Small-Body Database Query API (snapshot cached in
`data/nea_apollo_aten.csv`).

## Selection

| Step | Count |
|---|---|
| Apollo + Aten asteroids in SBDB | {len(df):,} |
| ... with no H or measured diameter (dropped) | {no_size:,} |
| **Diameter >= 140 m (selected)** | **{len(sel):,}** |
| ... of which have a *measured* diameter | {n_measured:,} |

Diameters for the remaining {len(sel) - n_measured:,} objects are estimated
from absolute magnitude H assuming geometric albedo p_V = {ASSUMED_ALBEDO}.

## Total mass estimate

Assuming spherical bodies:

| Bulk density assumption | Total mass |
|---|---|
| {DENSITY_LOW:.0f} kg/m^3 (C-type rubble pile) | {total_low:.2e} kg |
| **{DENSITY_KG_M3:.0f} kg/m^3 (nominal)** | **{total:.2e} kg** |
| {DENSITY_HIGH:.0f} kg/m^3 (coherent S-type) | {total_high:.2e} kg |

The 10 largest bodies hold {top10_share:.0%} of the total mass.

## Ten largest Earth-crossing NEAs

| Object | Class | Diameter (km) | Size source | Mass (kg) |
|---|---|---|---|---|
{top_rows}

## Caveats

* **Survey incompleteness:** the catalog is essentially complete above
  ~1 km but only roughly half-complete near 140 m, so the true count and
  the small-body end of the histogram are underestimates. The *mass*
  total is barely affected, since mass is dominated by the largest bodies.
* **Albedo assumption:** a single p_V = {ASSUMED_ALBEDO} is used where no
  measurement exists; individual diameters are uncertain by roughly a
  factor of ~1.5 each way (p_V spans ~0.05-0.4).
* **Density/shape:** spherical shapes and a single bulk density are
  assumed; real NEAs are irregular, and density varies by taxonomic type
  (hence the low/high bounds).
* Orbit accessibility (delta-v), spin state, and composition - the factors
  that actually rank mining targets - are not yet considered here.
"""
    with open(SUMMARY_MD, "w") as f:
        f.write(summary)
    print(f"Summary -> {SUMMARY_MD}")

    print(f"\nSelected {len(sel):,} Earth-crossing NEAs >= 140 m")
    print(f"Total mass (rho={DENSITY_KG_M3:.0f}): {total:.3e} kg "
          f"(range {total_low:.2e} - {total_high:.2e})")


if __name__ == "__main__":
    main()
