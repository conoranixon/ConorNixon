"""Test 1: lineament superposition density vs SFD slope.

If knobby chaos is older, more lineaments should cross (postdate) it.
Density is measured inside each terrain and in a local background annulus
(2 equivalent radii), excluding other chaos, to control regional mapping
density. Mills terrains (no published outlines) use convex hulls of blocks.
"""
import sys
import glob
import os
import re

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import transform as shp_transform, unary_union
from shapely.geometry import box

sys.path.insert(0, '/agent/repos/ConorNixon/europa-chaos/scripts')
from morpho import local_laea

DATA = '/agent/repos/ConorNixon/europa-chaos/data'
DL = '/tmp/europa/dl'

# --- terrain footprints ---
terr = gpd.read_file(f'{DATA}/chaos9_final.geojson')
name_map = {'TH_cc': 'Co', 'LH_A': 'A', 'LH_B': 'B', 'LH_C': 'C', 'LH_D': 'D',
            'LH_E': 'E', 'TH_aa': 'aa', 'TH_bb': 'bb', 'TH_dd': 'dd'}
foot = {}
for _, r in terr.iterrows():
    foot[name_map[r['name']]] = r.geometry

for f in glob.glob(f'{DL}/mills/Geojson Files/geojson_Chaos*/Chaos_*.json'):
    m = re.match(r'Chaos_([A-Za-z]+?)(_plates)?\.json$', os.path.basename(f))
    reg = m.group(1)
    g = gpd.read_file(f)
    geoms = [x for x in g.geometry if x is not None and not x.is_empty]
    u = unary_union(geoms).convex_hull
    foot[reg] = u if reg not in foot or reg in list('ABCDE') + ['Co', 'aa', 'bb', 'dd'] \
        and False else (unary_union([foot[reg], u]).convex_hull if reg in foot else u)

print('footprints:', sorted(foot))

# --- lineaments and chaos units (to exclude chaos from background) ---
lf = gpd.read_file(f'{DL}/sim3513/sim3513_Europa_GIS/shapefiles/LinearFeatures_FINAL.shp')
lf = lf[~lf['Type'].isin(['multi-ring'])]          # drop impact structures
units = gpd.read_file(f'{DL}/sim3513/sim3513_Europa_GIS/shapefiles/GeoUnits_FINAL.shp')
chaos_units = units[units['Geounits'].isin(['chh', 'chl', 'chm', 'chM'])]
chaos_union_parts = list(chaos_units.geometry)

reg_meta = pd.read_csv(f'{DATA}/regions20_full.csv').set_index('region')

rows = []
for reg, poly in foot.items():
    c = poly.representative_point()
    tr = local_laea(c.x, c.y)
    P = shp_transform(tr, poly).buffer(0)
    A_in = P.area / 1e6                                   # km^2
    R_eq = np.sqrt(P.area / np.pi)                        # m
    ann = P.buffer(2 * R_eq).difference(P)
    # pre-filter lineaments by lon/lat bbox (buffer ~ annulus extent in deg)
    deg = 3 * R_eq / 27265000 * 57.3 + 4
    cand = lf.cx[c.x - deg:c.x + deg, c.y - deg:c.y + deg]
    Lin = Lbg = 0.0
    nin = 0
    for geom in cand.geometry:
        gl = shp_transform(tr, geom)
        li = gl.intersection(P).length
        if li > 0:
            Lin += li
            nin += 1
        Lbg += gl.intersection(ann).length
    # remove chaos from the background area (and its lineament length stays:
    # approximation - subtract chaos area from annulus area only)
    ch_cand = chaos_units.cx[c.x - deg:c.x + deg, c.y - deg:c.y + deg]
    ch_area_in_ann = 0.0
    for geom in ch_cand.geometry:
        try:
            ch_area_in_ann += shp_transform(tr, geom).buffer(0).intersection(ann).area
        except Exception:
            pass
    A_bg = max((ann.area - ch_area_in_ann), ann.area * 0.1) / 1e6
    rows.append(dict(region=reg, area_km2=A_in,
                     n_cross=nin,
                     dens_in=Lin / 1e3 / A_in,            # km/km^2
                     dens_bg=Lbg / 1e3 / A_bg,
                     ))

df = pd.DataFrame(rows).set_index('region')
df['ratio'] = df.dens_in / df.dens_bg.replace(0, np.nan)
df['sfd'] = reg_meta['sfd_slope']
df['hemi'] = np.where(df.index.isin(list('ABCDEFGHI')), 'lead', 'trail')
print(df.round(4).to_string())

from scipy import stats
for col in ['dens_in', 'ratio', 'n_cross']:
    s = df.dropna(subset=[col, 'sfd'])
    rho, p = stats.spearmanr(s.sfd, s[col])
    print(f'Spearman {col} vs SFD slope (n={len(s)}): rho={rho:+.3f} p={p:.3f}')
# Leonard terrains only (true outlines, larger areas)
leo = df.loc[[r for r in ['A', 'B', 'C', 'Co', 'D', 'E', 'aa', 'bb', 'dd'] if r in df.index]]
for col in ['dens_in', 'ratio']:
    rho, p = stats.spearmanr(leo.sfd, leo[col])
    print(f'Leonard-9 only {col}: rho={rho:+.3f} p={p:.3f}')
df.to_csv('/tmp/europa/work/test1_superposition.csv')
