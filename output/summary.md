# Earth-crossing NEAs >= 140 m: size-frequency and mass inventory

Data source: NASA/JPL Small-Body Database Query API (snapshot cached in
`data/nea_apollo_aten.csv`).

## Selection

| Step | Count |
|---|---|
| Apollo + Aten asteroids in SBDB | 27,424 |
| ... with no H or measured diameter (dropped) | 0 |
| **Diameter >= 140 m (selected)** | **6,293** |
| ... of which have a *measured* diameter | 784 |

Diameters for the remaining 5,509 objects are estimated
from absolute magnitude H assuming geometric albedo p_V = 0.14.

## Total mass estimate

Assuming spherical bodies:

| Bulk density assumption | Total mass |
|---|---|
| 1300 kg/m^3 (C-type rubble pile) | 4.73e+15 kg |
| **2000 kg/m^3 (nominal)** | **7.28e+15 kg** |
| 2700 kg/m^3 (coherent S-type) | 9.82e+15 kg |

The 10 largest bodies hold 36% of the total mass.

## Ten largest Earth-crossing NEAs

| Object | Class | Diameter (km) | Size source | Mass (kg) |
|---|---|---|---|---|
| 1866 Sisyphus (1972 XA) | APO | 8.48 | measured | 6.39e+14 |
| 53319 (1999 JM8) | APO | 7.00 | measured | 3.59e+14 |
| 52762 (1998 MT24) | APO | 6.74 | measured | 3.21e+14 |
| 7092 Cadmus (1992 LC) | APO | 6.32 | measured | 2.64e+14 |
| 3200 Phaethon (1983 TB) | APO | 6.25 | measured | 2.56e+14 |
| 2212 Hephaistos (1978 SB) | APO | 5.70 | measured | 1.94e+14 |
| 4179 Toutatis (1989 AC) | APO | 5.40 | measured | 1.65e+14 |
| 5731 Zeus (1988 VP4) | APO | 5.23 | measured | 1.50e+14 |
| 16960 (1998 QS52) | APO | 4.86 | from_H | 1.20e+14 |
| 5143 Heracles (1991 VL) | APO | 4.84 | measured | 1.19e+14 |

## Caveats

* **Survey incompleteness:** the catalog is essentially complete above
  ~1 km but only roughly half-complete near 140 m, so the true count and
  the small-body end of the histogram are underestimates. The *mass*
  total is barely affected, since mass is dominated by the largest bodies.
* **Albedo assumption:** a single p_V = 0.14 is used where no
  measurement exists; individual diameters are uncertain by roughly a
  factor of ~1.5 each way (p_V spans ~0.05-0.4).
* **Density/shape:** spherical shapes and a single bulk density are
  assumed; real NEAs are irregular, and density varies by taxonomic type
  (hence the low/high bounds).
* Orbit accessibility (delta-v), spin state, and composition - the factors
  that actually rank mining targets - are not yet considered here.
