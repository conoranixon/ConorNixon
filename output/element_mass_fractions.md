# Expected element mass fractions by asteroid spectral type

Compositions are inferred from each type's meteorite analog (asteroid
interiors cannot be assayed remotely). Ranges span the analog group,
e.g. LL to H chondrites for S-types. Sources: Lodders (2003) for CI;
Wasson & Kallemeyn (1988) for ordinary chondrite group means;
Kargel (1994) for iron-meteorite metals; Mittlefehldt et al. (1998) for
HEDs; Zolensky et al. (2002) for Tagish Lake.

| Commodity | C-type | S-type | M-type | V-type | D/P-type |
|---|---|---|---|---|---|
| *Meteorite analog* | *CI/CM carbonaceous chondrite* | *H/L/LL ordinary chondrite* | *Iron meteorite (Fe-Ni metal)* | *HED basaltic achondrite* | *Tagish Lake-like C2 (uncertain)* |
| *Approx. share of NEAs* | *~15%* | *~55%* | *~4%* | *~4%* | *~6%* |
| Water (bound H2O) | 10-20 wt% | 0-1000 ppm | ~0 | ~0 | 5-15 wt% |
| Carbon (organics) | 2.2-3.5 wt% | 0-2000 ppm | ~0 | ~0 | 3-5.5 wt% |
| Sulfur | 2.7-5.4 wt% | 2-2.4 wt% | 0.1-2 wt% | 0-2000 ppm | 3-4 wt% |
| Iron (total) | 18-21 wt% | 18.5-27.5 wt% | 85-93 wt% | 13-15 wt% | 18-20 wt% |
| Nickel | 1-1.2 wt% | 1-1.7 wt% | 6-12 wt% | 1-100 ppm | 1-1.2 wt% |
| Cobalt | 500-580 ppm | 490-810 ppm | 4000-6000 ppm | 2-30 ppm | 450-550 ppm |
| Free Fe-Ni metal | 0-5000 ppm | 2-18 wt% | 90-100 wt% | 0-5000 ppm | 0-1 wt% |
| Pt-group metals (6 PGM) | 3.3-4.3 ppm | 3-5.5 ppm | 5-40 ppm | 0-0.01 ppm | 2.5-3.5 ppm |
| Gold | 0.14-0.17 ppm | 0.14-0.22 ppm | 0.5-1.5 ppm | 0-0.01 ppm | 0.1-0.15 ppm |
| Phosphorus | 900-1100 ppm | 950-1100 ppm | 1000-3000 ppm | 300-500 ppm | 900-1100 ppm |

Population shares are debiased NEA fractions (DeMeo & Carry 2014); they
do not sum to 100% because X-complex objects of unknown metal content
and rarer classes are omitted.

## Extractability notes

* **C:** Water/organics released by moderate heating (~300-600 C); Fe is oxidized (magnetite, silicates) and hard to reduce; PGMs dispersed.
* **S:** Free Fe-Ni metal grains are magnetically separable and carry most of the Ni, Co, PGM and Au; silicate fraction is slag.
* **M:** Essentially ore-grade Fe-Ni already; PGMs at 10-100x terrestrial crustal grade, recoverable e.g. by Mond (carbonyl) processing.
* **V:** Basaltic rock: usable as bulk shielding/regolith only; metal and volatile poor.
* **D/P:** Likely the most volatile-rich, but no confirmed meteorite analog exists; all values are extrapolations.

## Implied commodity inventory of the >= 140 m Earth-crossing population

Combining these grades with the mass inventory from
`nea_mining_analysis.py` (total 7.28e+15 kg at 2000 kg/m^3) and
weighting by the population shares above:

| Commodity | Mass low (kg) | Mass high (kg) |
|---|---|---|
| Water (bound H2O) | 1.3e+14 | 2.9e+14 |
| Carbon (organics) | 3.7e+13 | 7.0e+13 |
| Sulfur | 1.2e+14 | 1.8e+14 |
| Iron (total) | 1.3e+15 | 1.7e+15 |
| Nickel | 7.4e+13 | 1.2e+14 |
| Cobalt | 3.9e+12 | 5.9e+12 |
| Free Fe-Ni metal | 3.4e+14 | 1.0e+15 |
| Pt-group metals (6 PGM) | 1.8e+10 | 4.0e+10 |
| Gold | 9.0e+08 | 1.6e+09 |
| Phosphorus | 5.6e+12 | 7.1e+12 |

These are order-of-magnitude figures: they assume the population shares
apply uniformly across sizes, whereas the actual types of the largest
(mass-dominating) bodies are individually known and should be used for
any target-specific estimate.
