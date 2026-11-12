# Europa Chaos Terrain Sub-Type Analysis

Research project investigating whether all areas on Europa labeled "chaos"
(chaotic terrain) are the same type of geologic feature, or whether multiple
sub-types with different formation mechanisms have been lumped into a single
category.

**Headline finding:** canonical chaos features form a single continuous
platy-to-knobby spectrum (no statistical evidence for discrete sub-types),
with a small number of true outliers (e.g. Murias Chaos as an extrusive
cryovolcanic dome, Moytura Chaos, candidate impact-breach sites) that likely
represent distinct mechanisms grouped under the chaos label.

## Contents

- `report/` — the full report as Markdown (figures render on GitHub) and PDF,
  plus a 14-slide deck version (`europa-chaos-subtypes-slides.pptx` / `.pdf`).
- `figures/` — the six report figures (global map, morphometrics, clustering,
  platy–knobby continuum, endmember close-ups, microchaos).
- `scripts/` — Python analysis pipeline:
  - `morpho.py` — local equal-area projection morphometrics (area, perimeter,
    circularity, solidity on the Europa 2000 sphere).
  - `chain_borders.py`, `assemble9.py` — reconstruction of closed terrain
    polygons from the Leonard et al. (2022) arc-segment shapefiles.
  - `analysis_main.py`, `analysis_stats.py` — morphometric computation,
    dip tests, GMM/BIC, clustering, and non-parametric statistics.
  - `figs.py` — figure generation.
  - `md2pdf.py`, `make_deck.py` — Markdown-to-PDF rendering of the report and
    slide deck generation.
- `data/` — derived datasets (reconstructed terrain GeoJSONs, per-feature
  morphometric CSVs, block catalogs, statistics output).

## Source data (not included; large external downloads)

- Leonard et al. (2022) chaos outlines and block catalog — Zenodo 12775125
- Mills (2023) microchaos catalog — Zenodo 10162452
- USGS Europa 500 m global mosaic and SIM 3513 geologic map GIS data
