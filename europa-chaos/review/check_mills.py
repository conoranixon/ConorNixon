"""Replicate and check the metrics in the Mills et al. draft
(roundness, angularity, jaggedness) on the Leonard22 + Mills23 block data."""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import transform as shp_transform, polylabel
from pyproj import Transformer

sys.path.insert(0, '/agent/repos/ConorNixon/europa-chaos/scripts')
from morpho import local_laea, R_EUROPA

OUT = '/tmp/europa/work/blocks_mills_metrics.csv'


def block_metrics(geom):
    c = geom.representative_point()
    g = shp_transform(local_laea(c.x, c.y), geom).buffer(0)
    if g.geom_type == 'MultiPolygon':
        g = max(g.geoms, key=lambda p: p.area)
    A = g.area          # m^2
    P = g.length        # m
    # max inscribed circle via pole of inaccessibility
    tol = max(np.sqrt(A) / 500.0, 0.5)
    pc = polylabel(g, tolerance=tol)
    r = g.boundary.distance(pc)                    # inscribed radius, m
    verts = np.concatenate([np.asarray(g.exterior.coords)] +
                           [np.asarray(i.coords) for i in g.interiors])
    d = np.hypot(verts[:, 0] - pc.x, verts[:, 1] - pc.y)
    x = d.max()                                    # farthest vertex, m
    alpha = np.degrees(np.arcsin(min(r / x, 1.0)))
    return dict(
        area_km2=A / 1e6, perim_km=P / 1e3,
        L_km=np.sqrt(A) / 1e3,                     # characteristic length
        roundness=np.pi * r**2 / A,
        angularity=(180.0 - alpha) * (x / r) if r > 0 else np.nan,
        J1=P**2 / (4 * np.pi * A),                 # Eq. 3 as written
    )


def load_blocks():
    rows = []
    # Leonard: assign regions via terrain polygons saved in the repo
    terr = gpd.read_file('/agent/repos/ConorNixon/europa-chaos/data/chaos9_final.geojson')
    blocks = gpd.read_file('/tmp/europa/dl/leonard/AllBlocks.shp')
    blocks = blocks.set_crs(terr.crs, allow_override=True)
    j = gpd.sjoin(blocks, terr[['name', 'geometry']], how='left',
                  predicate='intersects')
    j = j[~j.index.duplicated(keep='first')]
    name_map = {'TH_cc': 'Co', 'LH_A': 'A', 'LH_B': 'B', 'LH_C': 'C',
                'LH_D': 'D', 'LH_E': 'E', 'TH_aa': 'aa', 'TH_bb': 'bb',
                'TH_dd': 'dd'}
    for _, row in j.iterrows():
        if row.geometry is None or row.geometry.is_empty:
            continue
        reg = name_map.get(row.get('name'))
        if reg is None:
            continue
        rows.append((reg, 'Leonard22', row.geometry))
    # Mills: region from filename; X.json = knobs, X_plates.json = plates
    for f in glob.glob('/tmp/europa/dl/mills/Geojson Files/geojson_Chaos*/Chaos_*.json'):
        base = os.path.basename(f)
        m = re.match(r'Chaos_([A-Za-z]+?)(_plates)?\.json$', base)
        reg = m.group(1)
        g = gpd.read_file(f)
        for geom in g.geometry:
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type not in ('Polygon', 'MultiPolygon'):
                continue
            rows.append((reg, 'Mills23', geom))
    return rows


if not os.path.exists(OUT):
    rows = load_blocks()
    print('blocks loaded:', len(rows))
    recs = []
    for reg, src, geom in rows:
        try:
            m = block_metrics(geom)
        except Exception as e:
            print('skip', reg, e)
            continue
        m.update(region=reg, source=src)
        recs.append(m)
    df = pd.DataFrame(recs)
    df.to_csv(OUT, index=False)
else:
    df = pd.read_csv(OUT)

print('blocks measured:', len(df))
print(df.groupby('region').size())
print('\nJ1 (= P^2/4piA, dimensionless) overall:',
      df.J1.describe()[['mean', 'min', 'max']].round(3).to_dict())
print('roundness overall:', df.roundness.describe()[['mean', 'min', 'max']].round(3).to_dict())
print('angularity overall:', df.angularity.describe()[['mean', '50%', 'min', 'max']].round(1).to_dict())
