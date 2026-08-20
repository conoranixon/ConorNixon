# ConorNixon
Conor Nixon home page

## NEA space-mining survey

`nea_mining_analysis.py` surveys Earth-crossing Near-Earth Asteroids
(Apollo + Aten orbit classes) with diameter >= 140 m as candidate
space-mining targets, using live data from the NASA/JPL Small-Body
Database Query API.

Run it with:

```bash
pip install -r requirements.txt
python3 nea_mining_analysis.py
```

Outputs:

* `data/nea_apollo_aten.csv` — cached catalog snapshot (delete to re-fetch)
* `output/size_frequency_histogram.png` — size-frequency distribution and
  cumulative mass vs. diameter threshold
* `output/summary.md` — selection counts, total mass estimate with density
  sensitivity bounds, ten largest bodies, and caveats
