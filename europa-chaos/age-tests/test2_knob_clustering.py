"""Test 2: do knobs preserve relict plate-scale organization?

(i)  Ripley's K / Clark-Evans for knob centroids vs CSR within each terrain
(ii) knob -> nearest-plate-edge distance vs CSR null (are knobs plate debris?)
(iii) orientation coherence of neighboring elongated knobs vs permutation null
"""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import transform as shp_transform, unary_union
from shapely.geometry import Point
from shapely import STRtree

sys.path.insert(0, '/agent/repos/ConorNixon/europa-chaos/scripts')
from morpho import local_laea

rng = np.random.default_rng(42)
DATA = '/agent/repos/ConorNixon/europa-chaos/data'
DL = '/tmp/europa/dl'
NSIM = 199

# ---------- load blocks with class ----------
def orientation_deg(g):
    rect = g.minimum_rotated_rectangle
    c = np.asarray(rect.exterior.coords)
    e = c[1:] - c[:-1]
    L = np.hypot(*e.T)
    i = np.argmax(L[:2])
    ang = np.degrees(np.arctan2(e[i][1], e[i][0])) % 180.0
    ar = max(L[:2]) / max(min(L[:2]), 1e-9)
    return ang, ar

terr = gpd.read_file(f'{DATA}/chaos9_final.geojson')
name_map = {'TH_cc': 'Co', 'LH_A': 'A', 'LH_B': 'B', 'LH_C': 'C', 'LH_D': 'D',
            'LH_E': 'E', 'TH_aa': 'aa', 'TH_bb': 'bb', 'TH_dd': 'dd'}
terr['reg'] = terr['name'].map(name_map)

records = {}   # region -> dict(window, knobs(df), plates(list of polys))

leo = gpd.read_file(f'{DL}/leonard/AllBlocks.shp')
jo = gpd.sjoin(leo.set_crs(terr.crs, allow_override=True),
               terr[['reg', 'geometry']], how='left', predicate='intersects')
jo = jo[~jo.index.duplicated(keep='first')]

def ensure(reg):
    if reg not in records:
        records[reg] = dict(window=None, knobs=[], plates=[])
    return records[reg]

for _, r in jo.iterrows():
    if not isinstance(r.get('reg'), str) or r.geometry is None or r.geometry.is_empty:
        continue
    cls = str(r.get('Block_Plat'))
    cls = 'plate' if cls.startswith('Plate') else ('knob' if cls.startswith('Blo') else 'unk')
    ensure(r['reg'])[('plates' if cls == 'plate' else 'knobs')].append((r.geometry, cls))

import collections
files = collections.defaultdict(dict)
for f in glob.glob(f'{DL}/mills/Geojson Files/geojson_Chaos*/Chaos_*.json'):
    m = re.match(r'Chaos_([A-Za-z]+?)(_plates)?\.json$', os.path.basename(f))
    files[m.group(1)]['plates' if m.group(2) else 'all'] = f
for reg, d in files.items():
    allg = [g for g in gpd.read_file(d['all']).geometry
            if g is not None and not g.is_empty and g.geom_type in ('Polygon', 'MultiPolygon')]
    plg = [g for g in gpd.read_file(d['plates']).geometry
           if g is not None and not g.is_empty and g.geom_type in ('Polygon', 'MultiPolygon')] if 'plates' in d else []
    pset = set((round(g.centroid.x, 6), round(g.centroid.y, 6)) for g in plg)
    for geom in allg:
        key = (round(geom.centroid.x, 6), round(geom.centroid.y, 6))
        if key in pset:
            ensure(reg)['plates'].append((geom, 'plate'))
        else:
            ensure(reg)['knobs'].append((geom, 'knob'))

# windows: Leonard true outlines; Mills convex hull of all blocks
for _, r in terr.iterrows():
    if r['reg'] in records:
        records[r['reg']]['window'] = r.geometry
for reg, d in records.items():
    if d['window'] is None:
        allg = [g for g, _ in d['knobs'] + d['plates']]
        d['window'] = unary_union(allg).convex_hull

# ---------- project to per-terrain shared frame & build tables ----------
def project_region(reg, d):
    c = d['window'].representative_point()
    tr = local_laea(c.x, c.y)
    W = shp_transform(tr, d['window']).buffer(0)
    knobs, plates = [], []
    for g, cls in d['knobs']:
        gp = shp_transform(tr, g).buffer(0)
        if gp.is_empty or gp.area <= 0:
            continue
        if gp.geom_type == 'MultiPolygon':
            gp = max(gp.geoms, key=lambda p: p.area)
        L = np.sqrt(gp.area) / 1e3
        if L < 0.05:
            continue                      # degenerate slivers
        ang, ar = orientation_deg(gp)
        knobs.append(dict(x=gp.centroid.x, y=gp.centroid.y, L=L, ang=ang, ar=ar))
    for g, cls in d['plates']:
        gp = shp_transform(tr, g).buffer(0)
        if not gp.is_empty and gp.area > 0:
            plates.append(gp)
    return W, pd.DataFrame(knobs), plates

def rand_points(n, W, exclude=None):
    minx, miny, maxx, maxy = W.bounds
    pts = []
    while len(pts) < n:
        xs = rng.uniform(minx, maxx, n * 3)
        ys = rng.uniform(miny, maxy, n * 3)
        for x, y in zip(xs, ys):
            p = Point(x, y)
            if W.contains(p) and (exclude is None or not exclude.contains(p)):
                pts.append((x, y))
                if len(pts) == n:
                    break
    return np.array(pts)

def ripley_L(pts, W, rs):
    """L(r)-r with simple border correction via intensity in window."""
    n = len(pts)
    A = W.area
    d = np.sqrt(((pts[:, None, :] - pts[None, :, :])**2).sum(-1))
    iu = np.triu_indices(n, 1)
    dd = d[iu]
    out = []
    lam = n / A
    for r in rs:
        K = 2 * (dd < r).sum() / n / lam
        out.append(np.sqrt(K / np.pi) - r)
    return np.array(out)

rows = []
orient_rows = []
RS = np.array([2e3, 4e3, 6e3, 8e3, 10e3])    # m: plate length scales

for reg in sorted(records):
    W, kn, plates = project_region(reg, records[reg])
    n = len(kn)
    if n < 15:
        continue
    pts = kn[['x', 'y']].values
    Lobs = ripley_L(pts, W, RS)
    sims = np.array([ripley_L(rand_points(n, W), W, RS) for _ in range(NSIM)])
    rank = (sims < Lobs).sum(0)             # how many sims below observed
    pclu = (NSIM + 1 - rank) / (NSIM + 1)   # small => strong clustering
    # summarize at 6 km (typical plate diameter)
    i6 = 2
    rows.append(dict(region=reg, n_knobs=n, n_plates=len(plates),
                     L6_obs=Lobs[i6] / 1e3,
                     L6_null_med=np.median(sims[:, i6]) / 1e3,
                     L6_null_hi=np.percentile(sims[:, i6], 97.5) / 1e3,
                     p_cluster6=pclu[i6]))
    # (ii) knob->plate proximity
    if len(plates) >= 3 and n >= 10:
        tree = STRtree(plates)
        pl_union = unary_union(plates)
        def mean_dist(ps):
            ds = []
            for x, y in ps:
                p = Point(x, y)
                ds.append(pl_union.distance(p))
            return np.mean(ds)
        dobs = mean_dist(pts)
        dnull = np.array([mean_dist(rand_points(n, W, exclude=pl_union))
                          for _ in range(100)])
        pprox = ((dnull <= dobs).sum() + 1) / 101      # small => knobs nearer plates
        rows[-1].update(dist_obs_km=dobs / 1e3,
                        dist_null_km=np.median(dnull) / 1e3, p_prox=pprox)
    # (iii) orientation coherence among elongated knobs
    el = kn[kn.ar >= 1.3].reset_index(drop=True)
    if len(el) >= 15:
        p2 = el[['x', 'y']].values
        dmat = np.sqrt(((p2[:, None, :] - p2[None, :, :])**2).sum(-1))
        iu = np.triu_indices(len(el), 1)
        near = dmat[iu] < 6e3
        if near.sum() >= 20:
            th = np.radians(el.ang.values * 2)
            def coh(theta):
                dth = (theta[:, None] - theta[None, :])[iu][near]
                return np.cos(dth).mean()
            cobs = coh(th)
            cnull = np.array([coh(rng.permutation(th)) for _ in range(499)])
            pori = ((cnull >= cobs).sum() + 1) / 500
            orient_rows.append(dict(region=reg, n_elong=len(el),
                                    n_pairs=int(near.sum()),
                                    coh_obs=cobs, coh_null=cnull.mean(),
                                    p_orient=pori))

res = pd.DataFrame(rows).set_index('region')
meta = pd.read_csv(f'{DATA}/regions20_full.csv').set_index('region')
res['sfd'] = meta['sfd_slope']
print(res.round(3).to_string())
ori = pd.DataFrame(orient_rows).set_index('region') if orient_rows else None
if ori is not None:
    ori['sfd'] = meta['sfd_slope']
    print('\norientation coherence:\n', ori.round(3).to_string())

res.to_csv('/tmp/europa/work/test2_clustering.csv')
if ori is not None:
    ori.to_csv('/tmp/europa/work/test2_orientation.csv')

from scipy import stats
ok = res.dropna(subset=['sfd'])
rho, p = stats.spearmanr(ok.sfd, ok.L6_obs - ok.L6_null_med)
print(f'\nclustering excess at 6 km vs SFD slope: rho={rho:+.3f} p={p:.3f}')
print('regions with significant knob clustering at 6 km (p<0.05):',
      list(res[res.p_cluster6 < 0.05].index))
if 'p_prox' in res:
    print('knob-near-plate significant (p<0.05):',
          list(res[res.p_prox.notna() & (res.p_prox < 0.05)].index),
          'of', list(res[res.p_prox.notna()].index))
