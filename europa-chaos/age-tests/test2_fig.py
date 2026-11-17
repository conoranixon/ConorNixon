"""Figure for the knobby-age hypothesis tests."""
import glob
import os
import re
import sys

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.ops import transform as shp_transform, unary_union
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, '/agent/repos/ConorNixon/europa-chaos/scripts')
from morpho import local_laea

DATA = '/agent/repos/ConorNixon/europa-chaos/data'
DL = '/tmp/europa/dl'
res = pd.read_csv('/tmp/europa/work/test2_clustering.csv').set_index('region')
ori = pd.read_csv('/tmp/europa/work/test2_orientation.csv').set_index('region')
sup = pd.read_csv('/tmp/europa/work/test1_superposition.csv').set_index('region')

fig = plt.figure(figsize=(16, 10))
gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])

# (a) example maps: hh (knobby, clustered+aligned) vs Co (platy, dispersed)
def plot_region(ax, reg, title):
    # knobs / plates
    knobs, plates = [], []
    if reg == 'Co':
        terr = gpd.read_file(f'{DATA}/chaos9_final.geojson')
        w = terr[terr['name'] == 'TH_cc'].geometry.iloc[0]
        leo = gpd.read_file(f'{DL}/leonard/AllBlocks.shp')
        inside = leo[leo.intersects(w)]
        blocks = list(inside.geometry)
        knobs = blocks; plates = []
    else:
        import collections
        d = {}
        for f in glob.glob(f'{DL}/mills/Geojson Files/geojson_Chaos{reg}/Chaos_*.json'):
            d['plates' if '_plates' in f else 'all'] = f
        allg = [g for g in gpd.read_file(d['all']).geometry
                if g is not None and not g.is_empty and g.geom_type in ('Polygon', 'MultiPolygon')]
        plg = [g for g in gpd.read_file(d['plates']).geometry
               if g is not None and not g.is_empty and g.geom_type in ('Polygon', 'MultiPolygon')] if 'plates' in d else []
        pset = set((round(g.centroid.x, 6), round(g.centroid.y, 6)) for g in plg)
        knobs = [g for g in allg if (round(g.centroid.x, 6), round(g.centroid.y, 6)) not in pset]
        plates = plg
        w = unary_union(knobs + plates).convex_hull
    c = w.representative_point()
    tr = local_laea(c.x, c.y)
    W = shp_transform(tr, w)
    xx, yy = W.exterior.xy
    ax.plot(np.array(xx) / 1e3, np.array(yy) / 1e3, color='0.4', lw=1, ls='--')
    for g in plates:
        gp = shp_transform(tr, g)
        if gp.geom_type == 'MultiPolygon':
            gp = max(gp.geoms, key=lambda p: p.area)
        x, y = gp.exterior.xy
        ax.fill(np.array(x) / 1e3, np.array(y) / 1e3, color='#1f6fb2', alpha=0.65, lw=0)
    for g in knobs:
        gp = shp_transform(tr, g)
        if gp.geom_type == 'MultiPolygon':
            gp = max(gp.geoms, key=lambda p: p.area)
        x, y = gp.exterior.xy
        ax.fill(np.array(x) / 1e3, np.array(y) / 1e3, color='crimson', alpha=0.75, lw=0)
    ax.set_aspect('equal')
    ax.set_title(title, fontsize=10)
    ax.set_xlabel('km'); ax.set_ylabel('km')

ax = fig.add_subplot(gs[0, 0])
plot_region(ax, 'hh', '(a) Region hh (knobby): knobs (red) clustered\n(p=0.005), axes aligned (p=0.008); plates blue')
ax = fig.add_subplot(gs[0, 1])
plot_region(ax, 'gg', '(b) Region gg: strongest knob clustering\nat plate scales (p=0.005)')
ax = fig.add_subplot(gs[0, 2])
plot_region(ax, 'Co', '(c) Conamara (platy; all blocks shown):\nblocks DISPERSED vs CSR (p=1.00)')

# (d) clustering excess at 6 km per region
ax = fig.add_subplot(gs[1, 0])
r = res.sort_values('sfd')
exc = r.L6_obs - r.L6_null_med
sig = r.p_cluster6 < 0.05
disp = r.p_cluster6 > 0.95
colors = ['crimson' if s else ('royalblue' if d else '0.7')
          for s, d in zip(sig, disp)]
ax.bar(range(len(r)), exc, color=colors)
ax.set_xticks(range(len(r)))
ax.set_xticklabels(r.index, fontsize=8)
ax.axhline(0, color='k', lw=0.8)
ax.set_ylabel('knob clustering excess at 6 km,\nL(6km) obs - null median [km]')
ax.set_title('(d) Knob clustering: common (red = clustered, p<0.05;\nblue = dispersed) but unrelated to knobbiness ($\\rho$=-0.10, p=0.66)',
             fontsize=10)
ax.text(0.02, 0.95, 'regions ordered knobby $\\rightarrow$ platy $\\rightarrow$',
        transform=ax.transAxes, fontsize=8, va='top')

# (e) knob-to-plate proximity
ax = fig.add_subplot(gs[1, 1])
pr = res.dropna(subset=['p_prox'])
sig = pr.p_prox < 0.05
ax.scatter(pr.dist_null_km[sig], pr.dist_obs_km[sig], c='crimson', s=45,
           label=f'knobs nearer plates than CSR (p<0.05): {sig.sum()}/{len(pr)}')
ax.scatter(pr.dist_null_km[~sig], pr.dist_obs_km[~sig], c='0.6', s=45, label='not significant')
lim = [0, max(pr.dist_null_km.max(), pr.dist_obs_km.max()) * 1.1]
ax.plot(lim, lim, 'k--', lw=0.8)
for reg_, row in pr.iterrows():
    ax.annotate(reg_, (row.dist_null_km, row.dist_obs_km), fontsize=7.5,
                xytext=(3, 3), textcoords='offset points')
ax.set_xlabel('mean knob-plate distance, CSR null [km]')
ax.set_ylabel('observed [km]')
ax.set_title('(e) Knob-plate proximity: significant only in\nE (Murias) and I after bias correction', fontsize=10)
ax.legend(fontsize=8, loc='upper left')

# (f) orientation coherence
ax = fig.add_subplot(gs[1, 2])
sig = ori.p_orient < 0.05
ax.scatter(ori.coh_null[sig], ori.coh_obs[sig], c='crimson', s=45,
           label=f'aligned neighbors (p<0.05): {sig.sum()}/{len(ori)}')
ax.scatter(ori.coh_null[~sig], ori.coh_obs[~sig], c='0.6', s=45, label='not significant')
lim = [0, max(ori.coh_obs.max(), ori.coh_null.max()) * 1.15]
ax.plot(lim, lim, 'k--', lw=0.8)
for reg_, row in ori.iterrows():
    ax.annotate(reg_, (row.coh_null, row.coh_obs), fontsize=7.5,
                xytext=(3, 3), textcoords='offset points')
ax.set_xlabel('orientation coherence, permutation null')
ax.set_ylabel('observed coherence $\\langle\\cos 2\\Delta\\theta\\rangle$')
ax.set_title('(f) Neighboring elongated knobs share\nlong-axis orientations in 3/12 regions', fontsize=10)
ax.legend(fontsize=8, loc='upper left')

plt.tight_layout()
out = '/cursor/stores/bc-0959e656-639f-4f36-9cde-b9d3406f110a/media/europa-chaos/fig7-knob-organization.png'
plt.savefig(out, dpi=165)
print('saved', out)
