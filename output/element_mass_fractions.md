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

Each cell gives the mean of the grade range above converted into
kilograms contained in that spectral type's share of the population
(grade x population share x total mass, using the 7.28e+15 kg
inventory from `nea_mining_analysis.py` at 2000 kg/m^3), followed in
parentheses by its notional value at spot prices retrieved 2026-08-20
(k/M/B/T/Q = thousand/million/billion/trillion/quadrillion USD).
The final column sums all types.

| Commodity: mean kg (value at spot) | C-type | S-type | M-type | V-type | D/P-type | All types |
|---|---|---|---|---|---|---|
| *Type mass (share x total)* | *1.1e+15* | *4.0e+15* | *2.9e+14* | *2.9e+14* | *4.4e+14* | *6.1e+15* |
| Water (bound H2O) | 1.6e+14 (n/a) | 2.0e+12 (n/a) | ~0 | ~0 | 4.4e+13 (n/a) | 2.1e+14 (n/a) |
| Carbon (organics) | 3.1e+13 (n/a) | 4.0e+12 (n/a) | ~0 | ~0 | 1.9e+13 (n/a) | 5.4e+13 (n/a) |
| Sulfur | 4.4e+13 ($38T) | 8.8e+13 ($75.7T) | 3.1e+12 ($2.63T) | 2.9e+11 ($250B) | 1.5e+13 ($13.1T) | 1.5e+14 ($130T) |
| Iron (total) | 2.1e+14 ($32.8T) | 9.2e+14 ($142T) | 2.6e+14 ($39.9T) | 4.1e+13 ($6.28T) | 8.3e+13 ($12.8T) | 1.5e+15 ($234T) |
| Nickel | 1.2e+13 ($204T) | 5.5e+13 ($920T) | 2.6e+13 ($441T) | 1.5e+10 ($248B) | 4.8e+12 ($80.9T) | 9.8e+13 ($1.65Q) |
| Cobalt | 5.9e+11 ($33.2T) | 2.6e+12 ($146T) | 1.5e+12 ($81.9T) | 4.7e+09 ($262B) | 2.2e+11 ($12.3T) | 4.9e+12 ($274T) |
| Free Fe-Ni metal | 2.7e+12 (n/a) | 4.0e+14 (n/a) | 2.8e+14 (n/a) | 7.3e+11 (n/a) | 2.2e+12 (n/a) | 6.8e+14 (n/a) |
| Pt-group metals (6 PGM) | 4.1e+09 ($282T) | 1.7e+10 ($1.16Q) | 6.5e+09 ($445T) | 1.5e+06 ($99B) | 1.3e+09 ($89.1T) | 2.9e+10 ($1.97Q) |
| Gold | 1.7e+08 ($24.6T) | 7.2e+08 ($105T) | 2.9e+08 ($42.3T) | 1.5e+06 ($212B) | 5.5e+07 ($7.93T) | 1.2e+09 ($180T) |
| Phosphorus | 1.1e+12 ($1.32T) | 4.1e+12 ($4.96T) | 5.8e+11 ($704B) | 1.2e+11 ($141B) | 4.4e+11 ($528B) | 6.3e+12 ($7.66T) |

### Spot prices used (2026-08-20)

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
  sum to ~84%, so columns do not add to the full 7.28e+15 kg.
