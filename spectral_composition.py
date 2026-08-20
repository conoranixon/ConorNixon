#!/usr/bin/env python3
"""
Elemental mass fractions of economically important commodities by
asteroid spectral type.
=====================================================================

Asteroid bulk compositions cannot be measured remotely, so each spectral
type is assigned its accepted meteorite analog and the element abundances
are taken from laboratory analyses of those meteorites:

  spectral type -> meteorite analog
  ------------------------------------------------------------------
  C (B, Ch, Cg..) -> CI / CM carbonaceous chondrites
  S (+ Q)         -> H / L / LL ordinary chondrites (Q = fresh OC)
  M (metallic X)  -> iron meteorites (Fe-Ni metal +- troilite)
  V               -> HED basaltic achondrites (Vesta family)
  D / P           -> Tagish Lake-like ungrouped C2 (analog uncertain)

Primary abundance sources:
  * Lodders (2003), ApJ 591, 1220        - CI chondrite composition
  * Wasson & Kallemeyn (1988)            - H/L/LL chondrite group means
  * Kargel (1994), JGR 99, E10           - metals in iron meteorites
  * Mittlefehldt et al. (1998)           - HED achondrites
  * Zolensky et al. (2002)               - Tagish Lake (D-type analog)

Ranges span the analog group (e.g. CI-CM for C-types, LL-H for S-types,
common iron-meteorite chemical groups for M-types).

Outputs:
  * data/spectral_type_composition.csv  - machine-readable (fractions)
  * output/element_mass_fractions.md    - report table + implied inventory
"""

from __future__ import annotations

import os

import pandas as pd

from nea_mining_analysis import (
    DENSITY_KG_M3,
    MIN_DIAMETER_KM,
    fetch_catalog,
    h_to_diameter_km,
    sphere_mass_kg,
)

CSV_OUT = "data/spectral_type_composition.csv"
CSV_KG_OUT = "data/commodity_mass_by_type_kg.csv"
MD_OUT = "output/element_mass_fractions.md"

TYPES = ["C", "S", "M", "V", "D/P"]

ANALOGS = {
    "C": "CI/CM carbonaceous chondrite",
    "S": "H/L/LL ordinary chondrite",
    "M": "Iron meteorite (Fe-Ni metal)",
    "V": "HED basaltic achondrite",
    "D/P": "Tagish Lake-like C2 (uncertain)",
}

# Approximate debiased share of the NEA population (DeMeo & Carry 2014;
# Binzel et al. 2019). Only a minority of X-complex NEAs are truly
# metallic, hence the small M share.
NEA_SHARE = {"C": 0.15, "S": 0.55, "M": 0.04, "V": 0.04, "D/P": 0.06}

# Mass fractions as (low, high) tuples; None = effectively absent (<1e-9).
# Values are dimensionless fractions (0.10 = 10 wt%; 1e-6 = 1 ppm).
COMPOSITION = {
    "Water (bound H2O)": {
        "C": (0.10, 0.20),      # CM ~13%, CI ~20% in phyllosilicates
        "S": (0.0, 0.001),
        "M": None,
        "V": None,
        "D/P": (0.05, 0.15),
    },
    "Carbon (organics)": {
        "C": (0.022, 0.035),
        "S": (0.0, 0.002),
        "M": None,
        "V": None,
        "D/P": (0.030, 0.055),
    },
    "Sulfur": {
        "C": (0.027, 0.054),
        "S": (0.020, 0.024),
        "M": (0.001, 0.02),     # troilite (FeS) nodules, group-dependent
        "V": (0.0, 0.002),
        "D/P": (0.030, 0.040),
    },
    "Iron (total)": {
        "C": (0.18, 0.21),      # mostly oxidized: magnetite/silicates
        "S": (0.185, 0.275),    # LL -> H
        "M": (0.85, 0.93),
        "V": (0.13, 0.15),      # in pyroxene/ilmenite, not metal
        "D/P": (0.18, 0.20),
    },
    "Nickel": {
        "C": (0.0102, 0.0120),
        "S": (0.0102, 0.0171),  # LL -> H
        "M": (0.06, 0.12),
        "V": (1e-6, 1e-4),      # strongly siderophile-depleted
        "D/P": (0.010, 0.012),
    },
    "Cobalt": {
        "C": (5.0e-4, 5.8e-4),
        "S": (4.9e-4, 8.1e-4),
        "M": (0.004, 0.006),
        "V": (2e-6, 3e-5),
        "D/P": (4.5e-4, 5.5e-4),
    },
    "Free Fe-Ni metal": {
        "C": (0.0, 0.005),
        "S": (0.02, 0.18),      # LL ~2% -> H ~18%; drives extractability
        "M": (0.90, 1.0),
        "V": (0.0, 0.005),
        "D/P": (0.0, 0.01),
    },
    "Pt-group metals (6 PGM)": {
        "C": (3.3e-6, 4.3e-6),  # sum Ru+Rh+Pd+Os+Ir+Pt
        "S": (3.0e-6, 5.5e-6),  # LL -> H
        "M": (5.0e-6, 4.0e-5),  # group-dependent; some IIAB >1e-4
        "V": (0.0, 1e-8),
        "D/P": (2.5e-6, 3.5e-6),
    },
    "Gold": {
        "C": (1.4e-7, 1.7e-7),
        "S": (1.4e-7, 2.2e-7),
        "M": (5.0e-7, 1.5e-6),
        "V": (0.0, 1e-8),
        "D/P": (1.0e-7, 1.5e-7),
    },
    "Phosphorus": {
        "C": (9e-4, 1.1e-3),
        "S": (9.5e-4, 1.1e-3),
        "M": (0.001, 0.003),    # schreibersite (Fe,Ni)3P
        "V": (3e-4, 5e-4),
        "D/P": (9e-4, 1.1e-3),
    },
}

# ----------------------------------------------------------------------
# Spot prices, USD per kg of contained element (retrieved 2026-08-20).
#   Au $4,520/ozt (Kitco); Pt $1,817, Pd $1,312, Rh $8,800, Ru $1,750,
#   Ir $4,000/ozt (Kitco/Umicore/TradingEconomics); Ni $16,841/t and
#   Co $56,290/t (LME/TradingEconomics); Fe from 62% iron ore at $95.4/t
#   -> $154/t contained Fe; S $860/t (ADNOC FOB, Hormuz-inflated record);
#   P from Morocco phosphate rock $158/t at ~13.1% P -> $1,206/t P.
# The PGM basket is the six-metal price weighted by CI-chondritic
# proportions (Ru 20%, Rh 4%, Pd 17%, Os 15%, Ir 14%, Pt 30%); osmium has
# no liquid market and is carried at a nominal $400/ozt.
# ----------------------------------------------------------------------
PRICE_DATE = "2026-08-20"
OZT = 31.1035e-3  # kg per troy ounce

PRICES_USD_PER_KG = {
    "Water (bound H2O)": None,       # no terrestrial spot market
    "Carbon (organics)": None,       # no spot market for raw organics
    "Sulfur": 0.86,
    "Iron (total)": 0.154,
    "Nickel": 16.84,
    "Cobalt": 56.29,
    "Free Fe-Ni metal": None,        # value already carried by Fe/Ni/Co/PGM rows
    "Pt-group metals (6 PGM)": 68000.0,
    "Gold": 4520.0 / OZT,
    "Phosphorus": 1.21,
}

EXTRACTABILITY_NOTES = {
    "C": "Water/organics released by moderate heating (~300-600 C); Fe is "
         "oxidized (magnetite, silicates) and hard to reduce; PGMs dispersed.",
    "S": "Free Fe-Ni metal grains are magnetically separable and carry most "
         "of the Ni, Co, PGM and Au; silicate fraction is slag.",
    "M": "Essentially ore-grade Fe-Ni already; PGMs at 10-100x terrestrial "
         "crustal grade, recoverable e.g. by Mond (carbonyl) processing.",
    "V": "Basaltic rock: usable as bulk shielding/regolith only; metal and "
         "volatile poor.",
    "D/P": "Likely the most volatile-rich, but no confirmed meteorite "
           "analog exists; all values are extrapolations.",
}


def fmt(pair) -> str:
    """Format a (low, high) fraction pair with sensible units."""
    if pair is None:
        return "~0"
    lo, hi = pair
    if hi >= 0.01:  # display as wt%
        lo_s = f"{lo * 100:.1f}".rstrip("0").rstrip(".")
        hi_s = f"{hi * 100:.1f}".rstrip("0").rstrip(".")
        return f"{hi_s} wt%" if lo_s == hi_s else f"{lo_s}-{hi_s} wt%"
    # display as ppm
    def p(x):
        s = f"{x * 1e6:.2f}".rstrip("0").rstrip(".")
        return s
    return f"{p(hi)} ppm" if p(lo) == p(hi) else f"{p(lo)}-{p(hi)} ppm"


def implied_inventory() -> tuple[float, pd.DataFrame]:
    """Combine composition with the >=140 m Earth-crossing mass inventory."""
    df = fetch_catalog()
    d = df["diameter"].fillna(h_to_diameter_km(df["H"]))
    total_mass = sphere_mass_kg(d[d >= MIN_DIAMETER_KM], DENSITY_KG_M3).sum()

    rows = []
    for commodity, per_type in COMPOSITION.items():
        lo = hi = 0.0
        for t, pair in per_type.items():
            if pair is None:
                continue
            lo += NEA_SHARE[t] * pair[0] * total_mass
            hi += NEA_SHARE[t] * pair[1] * total_mass
        rows.append({"commodity": commodity, "mass_low_kg": lo, "mass_high_kg": hi})
    return total_mass, pd.DataFrame(rows)


def fmt_usd(value: float) -> str:
    """Human-readable dollars: $3.4M, $120B, $45T ..."""
    for cut, suffix in ((1e15, "Q"), (1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if value >= cut:
            return f"${value / cut:.3g}{suffix}"
    return f"${value:.0f}"


def fmt_kg_cell(mean_kg: float, price) -> str:
    """Format one cell: mean mass in kg plus spot value in parentheses."""
    if mean_kg <= 0:
        return "~0"
    mass = f"{mean_kg:.1e}"
    if price is None:
        return f"{mass} (n/a)"
    return f"{mass} ({fmt_usd(mean_kg * price)})"


def build_kg_table(total_mass: float) -> tuple[str, pd.DataFrame]:
    """Mean commodity mass per type (kg) with value at spot prices."""
    type_mass = {t: NEA_SHARE[t] * total_mass for t in TYPES}

    header = (
        "| Commodity: mean kg (value at spot) | "
        + " | ".join(f"{t}-type" for t in TYPES)
        + " | All types |"
    )
    sep = "|---" * (len(TYPES) + 2) + "|"
    mass_row = (
        "| *Type mass (share x total)* | "
        + " | ".join(f"*{type_mass[t]:.1e}*" for t in TYPES)
        + f" | *{sum(type_mass.values()):.1e}* |"
    )

    body_rows, records = [], []
    for commodity, per_type in COMPOSITION.items():
        price = PRICES_USD_PER_KG[commodity]
        cells, total = [], 0.0
        for t in TYPES:
            pair = per_type[t]
            mean = 0.0 if pair is None else 0.5 * (pair[0] + pair[1]) * type_mass[t]
            total += mean
            cells.append(fmt_kg_cell(mean, price))
            records.append(
                {
                    "spectral_type": t,
                    "commodity": commodity,
                    "mass_mean_kg": mean,
                    "spot_price_usd_per_kg": price,
                    "value_usd": None if price is None else mean * price,
                }
            )
        body_rows.append(
            f"| {commodity} | " + " | ".join(cells)
            + f" | {fmt_kg_cell(total, price)} |"
        )

    md = "\n".join([header, sep, mass_row] + body_rows)
    return md, pd.DataFrame(records)


def main() -> None:
    # ---------------- machine-readable CSV ----------------
    records = []
    for commodity, per_type in COMPOSITION.items():
        for t in TYPES:
            pair = per_type[t]
            records.append(
                {
                    "spectral_type": t,
                    "meteorite_analog": ANALOGS[t],
                    "commodity": commodity,
                    "mass_fraction_low": 0.0 if pair is None else pair[0],
                    "mass_fraction_high": 0.0 if pair is None else pair[1],
                }
            )
    os.makedirs(os.path.dirname(CSV_OUT), exist_ok=True)
    pd.DataFrame(records).to_csv(CSV_OUT, index=False)
    print(f"CSV -> {CSV_OUT}")

    # ---------------- report table ----------------
    header = "| Commodity | " + " | ".join(f"{t}-type" for t in TYPES) + " |"
    sep = "|---" * (len(TYPES) + 1) + "|"
    analog_row = (
        "| *Meteorite analog* | "
        + " | ".join(f"*{ANALOGS[t]}*" for t in TYPES)
        + " |"
    )
    share_row = (
        "| *Approx. share of NEAs* | "
        + " | ".join(f"*~{NEA_SHARE[t] * 100:.0f}%*" for t in TYPES)
        + " |"
    )
    body = "\n".join(
        f"| {commodity} | "
        + " | ".join(fmt(per_type[t]) for t in TYPES)
        + " |"
        for commodity, per_type in COMPOSITION.items()
    )

    total_mass, _ = implied_inventory()
    kg_table_md, kg_df = build_kg_table(total_mass)
    kg_df.to_csv(CSV_KG_OUT, index=False)
    print(f"CSV -> {CSV_KG_OUT}")
    notes = "\n".join(f"* **{t}:** {n}" for t, n in EXTRACTABILITY_NOTES.items())

    md = f"""# Expected element mass fractions by asteroid spectral type

Compositions are inferred from each type's meteorite analog (asteroid
interiors cannot be assayed remotely). Ranges span the analog group,
e.g. LL to H chondrites for S-types. Sources: Lodders (2003) for CI;
Wasson & Kallemeyn (1988) for ordinary chondrite group means;
Kargel (1994) for iron-meteorite metals; Mittlefehldt et al. (1998) for
HEDs; Zolensky et al. (2002) for Tagish Lake.

{header}
{sep}
{analog_row}
{share_row}
{body}

Population shares are debiased NEA fractions (DeMeo & Carry 2014); they
do not sum to 100% because X-complex objects of unknown metal content
and rarer classes are omitted.

## Extractability notes

{notes}

## Implied commodity masses (kg) in the >= 140 m Earth-crossing population

Each cell gives the mean of the grade range above converted into
kilograms contained in that spectral type's share of the population
(grade x population share x total mass, using the {total_mass:.2e} kg
inventory from `nea_mining_analysis.py` at 2000 kg/m^3), followed in
parentheses by its notional value at spot prices retrieved {PRICE_DATE}
(k/M/B/T/Q = thousand/million/billion/trillion/quadrillion USD).
The final column sums all types.

{kg_table_md}

### Spot prices used ({PRICE_DATE})

| Commodity | Price (USD/kg contained element) | Basis |
|---|---|---|
| Sulfur | $0.86 | ADNOC FOB $860/t (Hormuz-disruption record high) |
| Iron | $0.15 | 62% Fe iron ore at $95.4/t, contained-Fe basis |
| Nickel | $16.84 | LME $16,841/t |
| Cobalt | $56.29 | benchmark $56,290/t |
| PGM basket | $68,000 | Pt/Pd/Rh/Ru/Ir/Os spot weighted by chondritic proportions |
| Gold | $145,320 | $4,520/ozt |
| Phosphorus | $1.21 | Morocco phosphate rock $158/t at ~13.1% P |
| Water, organics | n/a | no terrestrial spot market (in-space value is delivery-cost driven) |
| Free Fe-Ni metal | n/a | value already carried by the Fe/Ni/Co/PGM/Au rows |

### Caveats on the valuations

* These are *notional* figures at today's spot prices. Annual world mine
  production is ~9 kt Au, ~0.4 kt PGM, ~3.5 Mt Ni: selling even a tiny
  fraction of the asteroidal inventory would collapse the price. Treat
  the numbers as resource scale, not revenue.
* Sulfur is quoted at an all-time-high, geopolitically inflated price
  (~6x its 2020-2024 norm).
* Population shares apply uniformly across sizes here, whereas the types
  of the largest (mass-dominating) bodies are individually known; shares
  sum to ~84%, so columns do not add to the full {total_mass:.2e} kg.
"""
    os.makedirs(os.path.dirname(MD_OUT), exist_ok=True)
    with open(MD_OUT, "w") as f:
        f.write(md)
    print(f"Report -> {MD_OUT}")


if __name__ == "__main__":
    main()
