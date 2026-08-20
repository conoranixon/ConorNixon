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

## Implied commodity masses (kg) in the >= 140 m Earth-crossing population

Each cell converts the grade above into kilograms contained in that
spectral type's share of the population: grade x (population share x
total mass), using the 7.28e+15 kg inventory from
`nea_mining_analysis.py` (2000 kg/m^3). The final column sums all types.

| Commodity (kg) | C-type | S-type | M-type | V-type | D/P-type | All types |
|---|---|---|---|---|---|---|
| *Type mass (share x total)* | *1.1e+15* | *4.0e+15* | *2.9e+14* | *2.9e+14* | *4.4e+14* | *6.1e+15* |
| Water (bound H2O) | 1.1e+14-2.2e+14 | 0-4.0e+12 | ~0 | ~0 | 2.2e+13-6.5e+13 | 1.3e+14-2.9e+14 |
| Carbon (organics) | 2.4e+13-3.8e+13 | 0-8.0e+12 | ~0 | ~0 | 1.3e+13-2.4e+13 | 3.7e+13-7.0e+13 |
| Sulfur | 2.9e+13-5.9e+13 | 8.0e+13-9.6e+13 | 2.9e+11-5.8e+12 | 0-5.8e+11 | 1.3e+13-1.7e+13 | 1.2e+14-1.8e+14 |
| Iron (total) | 2.0e+14-2.3e+14 | 7.4e+14-1.1e+15 | 2.5e+14-2.7e+14 | 3.8e+13-4.4e+13 | 7.9e+13-8.7e+13 | 1.3e+15-1.7e+15 |
| Nickel | 1.1e+13-1.3e+13 | 4.1e+13-6.8e+13 | 1.7e+13-3.5e+13 | 2.9e+08-2.9e+10 | 4.4e+12-5.2e+12 | 7.4e+13-1.2e+14 |
| Cobalt | 5.5e+11-6.3e+11 | 2.0e+12-3.2e+12 | 1.2e+12-1.7e+12 | 5.8e+08-8.7e+09 | 2.0e+11-2.4e+11 | 3.9e+12-5.9e+12 |
| Free Fe-Ni metal | 0-5.5e+12 | 8.0e+13-7.2e+14 | 2.6e+14-2.9e+14 | 0-1.5e+12 | 0-4.4e+12 | 3.4e+14-1.0e+15 |
| Pt-group metals (6 PGM) | 3.6e+09-4.7e+09 | 1.2e+10-2.2e+10 | 1.5e+09-1.2e+10 | 0-2.9e+06 | 1.1e+09-1.5e+09 | 1.8e+10-4.0e+10 |
| Gold | 1.5e+08-1.9e+08 | 5.6e+08-8.8e+08 | 1.5e+08-4.4e+08 | 0-2.9e+06 | 4.4e+07-6.5e+07 | 9.0e+08-1.6e+09 |
| Phosphorus | 9.8e+11-1.2e+12 | 3.8e+12-4.4e+12 | 2.9e+11-8.7e+11 | 8.7e+10-1.5e+11 | 3.9e+11-4.8e+11 | 5.6e+12-7.1e+12 |

These are order-of-magnitude figures: they assume the population shares
apply uniformly across sizes, whereas the actual types of the largest
(mass-dominating) bodies are individually known and should be used for
any target-specific estimate. Shares sum to ~84% of the population, so
columns do not add up to the full 7.28e+15 kg.
