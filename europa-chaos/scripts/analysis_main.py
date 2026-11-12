"""Main quantitative analysis for the Europa chaos sub-types question.

Outputs (to /tmp/europa/work):
  sim_morpho.csv      - morphometrics for 114 SIM 3513 chaos polygons (chh/chl/chm)
  chaos9_morpho.csv   - morphometrics for the 9 Leonard terrains
  regions20.csv       - per-region block stats for all 20 labeled regions
  blocks_all.csv      - combined block table (Leonard 9 + Mills 11)
  stats_results.txt   - clustering / bimodality / group-test results
"""
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings, json, sys
warnings.filterwarnings('ignore')
sys.path.insert(0, '/tmp/europa/work')
from morpho import morphometrics, run

OUT = open('/tmp/europa/work/stats_results.txt', 'w')
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); OUT.write(s + "\n")

# ---------------- 1. SIM 3513 chaos morphometrics ----------------
sim = gpd.read_file('/tmp/europa/usgs/sim3513/sim3513_Europa_GIS/shapefiles/GeoUnits_FINAL.shp')
sim['Geounits'] = sim['Geounits'].replace({'chM': 'chm'})
chaos = sim[sim['Geounits'].isin(['chh', 'chl', 'chm'])].reset_index(drop=True)
dfs = run(chaos, 'SIM3513')
dfs = dfs.merge(chaos[['Geounits']].reset_index().rename(columns={'index': 'src_index'}),
                on='src_index')
dfs.to_csv('/tmp/europa/work/sim_morpho.csv', index=False)
log("SIM3513 chaos morphometrics:", len(dfs), "features",
    dfs.Geounits.value_counts().to_dict())

# ---------------- 2. Nine Leonard terrains ----------------
g9 = gpd.read_file('/tmp/europa/work/chaos9_final.geojson')
d9 = run(g9, 'Leonard9')
d9 = d9.merge(g9.drop(columns='geometry').reset_index().rename(
    columns={'index': 'src_index'}), on='src_index')
d9.to_csv('/tmp/europa/work/chaos9_morpho.csv', index=False)

# ---------------- 3. Blocks: Leonard (9 regions) + Mills (11 regions) ----------------
alb = gpd.read_file('/tmp/europa/zenodo/allblocks/AllBlocks.shp')
alb['Block_Plat'] = alb['Block_Plat'].fillna('').str.strip().replace(
    {'Bloc': 'Block', 'Block\r\nBlock': 'Block', '': None})
# region via spatial join with the 9 terrain polygons (many rows lack Chaos_Lett)
name2code = {'TH_aa': 'aa', 'TH_bb': 'bb', 'TH_cc': 'Co', 'TH_dd': 'dd',
             'LH_A': 'A', 'LH_B': 'B', 'LH_C': 'C', 'LH_D': 'D', 'LH_E': 'E'}
g9j = gpd.read_file('/tmp/europa/work/chaos9_final.geojson')[['name', 'geometry']]
g9j['geometry'] = g9j.geometry.buffer(0.1)
alb['rep'] = alb.geometry.representative_point()
joined = gpd.sjoin(gpd.GeoDataFrame(alb[['rep']], geometry='rep', crs=alb.crs),
                   g9j, how='left', predicate='within')
alb['region'] = joined['name'].map(name2code).values
log("AllBlocks region assignment:", alb['region'].value_counts(dropna=False).to_dict())
alb = alb.rename(columns={'Area__km_': 'area_km2'})
alb['source'] = 'Leonard22'
mills = gpd.read_file('/tmp/europa/zenodo/arcmap/ArcMap Files/LowerRegMapBlocks_raw.shp')
mills['region'] = mills['Chaos_Lett'].str.strip()
mills = mills.rename(columns={'Area': 'area_km2'})
mills['source'] = 'Mills23'
blocks = pd.concat([
    alb[['region', 'area_km2', 'Block_Plat', 'source', 'geometry']],
    mills[['region', 'area_km2', 'Block_Plat', 'source', 'geometry']]
], ignore_index=True)
blocks = blocks.dropna(subset=['region'])
log("\nblocks total:", len(blocks), "by source:", blocks.source.value_counts().to_dict())
log("regions:", sorted(blocks.region.dropna().unique()))

# block shape morphometrics (circularity, aspect) for Knob vs Plate comparison
bm = []
for i, row in blocks.iterrows():
    try:
        m = morphometrics(row.geometry)
    except Exception:
        continue
    m['region'] = row.region; m['Block_Plat'] = row.Block_Plat
    m['source'] = row.source
    # use geodesic geometry area; fall back to attribute
    m['area_attr'] = m['area_km2'] if m['area_km2'] > 0 else row.area_km2
    bm.append(m)
bm = [m for m in bm if m['area_attr'] and m['area_attr'] > 0]
bdf = pd.DataFrame(bm)
bdf.to_csv('/tmp/europa/work/blocks_all.csv', index=False)

# ---------------- 4. Per-region SFD slopes (Leonard method) ----------------
def sfd_slope(areas, total_area=None):
    """ln(cumulative fractional area > x) = m x + b with x = sqrt(block area)."""
    a = np.sort(np.asarray(areas))[::-1]
    x = np.sqrt(a)
    cum = np.cumsum(a)
    A_C = total_area if total_area else a.sum()
    y = np.log(cum / A_C)
    # order by ascending x for the fit (same pairs)
    m, b = np.polyfit(x, y, 1)
    r = np.corrcoef(x, y)[0, 1]
    return m, b, r ** 2

# region metadata from Dunn et al. (2023) Table 3
DUNN = {  # region: (plates, knobs, area_km2, lon, lat)
 'aa': (31, 176, 13151.6, 129.63, 9.42), 'bb': (91, 221, 22553, 128.42, 1.32),
 'Co': (149, 6, 9020.9, 86.65, 9.66), 'dd': (23, 31, 7965.5, 125.38, 3.64),
 'ee': (9, 34, 3127, 131.26, -17.33), 'ff': (23, 24, 2299.1, 143.5, -23.41),
 'gg': (62, 49, 7750.2, 141.83, -26.28), 'hh': (38, 70, 6036.5, 139.78, -36.17),
 'ii': (44, 108, 11718.4, 137.01, -39.41), 'jj': (31, 48, 6921.4, 140.1, -41.28),
 'kk': (8, 23, 1787.6, 137.12, -42.59), 'A': (59, 184, 12255.3, -84.62, 34.41),
 'B': (18, 72, 2761.3, -78.82, 30.68), 'C': (45, 42, 2936.8, -79.36, 25.65),
 'D': (2, 70, 1953.7, -73.95, 25.66), 'E': (3, 84, 7665.5, -82.59, 22.41),
 'F': (14, 27, 2912.9, -75.28, -19.88), 'G': (19, 19, 4286.6, -73.16, -21.25),
 'H': (5, 15, 2237.4, -70.99, -21.26), 'I': (38, 29, 5923.9, -81.44, -30.66)}

# map Leonard letters to Dunn region codes (AllBlocks uses A..E, aa..dd? inspect)
rows = []
for reg, grp in bdf.groupby('region'):
    code = reg
    if code not in DUNN:  # e.g. 'Conamara' naming variants
        code = {'cc': 'Co', 'CC': 'Co', 'Con': 'Co'}.get(reg, reg)
    meta = DUNN.get(code)
    areas = grp.area_attr.values
    m, b, r2 = sfd_slope(areas, meta[2] if meta else None)
    knob_frac = np.nan
    bp = grp.Block_Plat.dropna()
    if len(bp):
        knobs = (bp != 'Plate').sum()   # 'Block'/'Knob' both = non-plate
        knob_frac = knobs / len(bp)
    rows.append(dict(region=code, n_blocks=len(grp), sfd_slope=m, sfd_intercept=b,
                     r2=r2, knob_frac_blocks=knob_frac,
                     med_block_km2=np.median(areas), max_block_km2=areas.max(),
                     source=grp.source.iloc[0],
                     lon=meta[3] if meta else np.nan,
                     lat=meta[4] if meta else np.nan,
                     area_region=meta[2] if meta else np.nan,
                     knob_frac_dunn=meta[1] / (meta[0] + meta[1]) if meta else np.nan,
                     block_area_frac=areas.sum() / meta[2] if meta else np.nan))
r20 = pd.DataFrame(rows)
r20.to_csv('/tmp/europa/work/regions20.csv', index=False)
log("\nPer-region table (20 regions):")
log(r20.round(3).to_string())
OUT.close()
