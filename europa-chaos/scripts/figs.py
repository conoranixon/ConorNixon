"""Generate all report figures into the project media directory."""
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import rasterio, warnings
warnings.filterwarnings('ignore')

MEDIA = '/cursor/stores/self/media/europa-chaos'
TIF = ('/tmp/europa/usgs/sim3513/sim3513_Europa_GIS/Rasters/'
       'Europa_Voyager_GalileoSSI_global_mosaic_500m_SpFill.tif')
M_PER_DEG = 1562090.0 * np.pi / 180
UC = {'chh': '#e8b63c', 'chl': '#c0503a', 'chm': '#7a6fb0'}
ULAB = {'chh': 'chh (high-albedo chaos)', 'chl': 'chl (low-albedo chaos)',
        'chm': 'chm (mottled chaos)'}

sim_shp = gpd.read_file('/tmp/europa/usgs/sim3513/sim3513_Europa_GIS/shapefiles/GeoUnits_FINAL.shp')
sim_shp['Geounits'] = sim_shp['Geounits'].replace({'chM': 'chm'})
chaos_shp = sim_shp[sim_shp.Geounits.isin(['chh', 'chl', 'chm'])]
g9 = gpd.read_file('/tmp/europa/work/chaos9_final.geojson')
simm = pd.read_csv('/tmp/europa/work/sim_morpho_clustered.csv')
r20 = pd.read_csv('/tmp/europa/work/regions20_full.csv')
blk = pd.read_csv('/tmp/europa/work/blocks_all.csv')


def global_mosaic(decim=10):
    with rasterio.open(TIF) as r:
        img = r.read(1, out_shape=(r.height // decim, r.width // decim))
    img = np.roll(img, img.shape[1] // 2, axis=1)  # center lon 0
    return img


# ---------------- fig 1: global map ----------------
img = global_mosaic()
fig, ax = plt.subplots(figsize=(16, 8.6))
ax.imshow(img, cmap='gray', extent=(-180, 180, -90, 90), vmin=0, vmax=255)
for u, c in UC.items():
    chaos_shp[chaos_shp.Geounits == u].plot(ax=ax, facecolor=c, alpha=0.42,
                                            edgecolor=c, lw=0.7)
g9.boundary.plot(ax=ax, color='#19d2ff', lw=1.4)
mills = r20[r20.source == 'Mills23']
ax.scatter(mills.lon, mills.lat, s=90, facecolor='none', edgecolor='#30ff80',
           lw=1.8, zorder=5)
for _, r in r20.iterrows():
    ax.annotate(r.region, (r.lon, r.lat), xytext=(5, 5),
                textcoords='offset points', color='white', fontsize=9,
                fontweight='bold')
handles = [mpatches.Patch(facecolor=c, alpha=0.5, label=ULAB[u]) for u, c in UC.items()]
handles += [plt.Line2D([], [], color='#19d2ff', lw=1.6,
                       label='Leonard et al. (2022) terrain outlines (9)'),
            plt.Line2D([], [], marker='o', mfc='none', mec='#30ff80', ls='',
                       ms=10, label='Mills (2023) block-mapped regions (11)')]
ax.legend(handles=handles, loc='lower left', fontsize=10, framealpha=0.85)
ax.set_xlabel('East longitude (deg)'); ax.set_ylabel('Latitude (deg)')
ax.set_title('Europa chaos terrain: USGS SIM 3513 chaos units over the '
             'Voyager/Galileo 500 m global mosaic')
ax.set_xlim(-180, 180); ax.set_ylim(-90, 90)
plt.savefig(f'{MEDIA}/fig1-global-chaos-map.png', dpi=140, bbox_inches='tight')
plt.close()
print("fig1 done")

# ---------------- fig 2: SIM morphometrics ----------------
fig, axs = plt.subplots(2, 3, figsize=(16, 9))
a = axs[0, 0]
bins = np.linspace(1.5, 5.6, 28)
for u, c in UC.items():
    a.hist(np.log10(simm[simm.Geounits == u].area_km2), bins=bins, alpha=0.55,
           color=c, label=u)
a.set_xlabel('log10 area (km²)'); a.set_ylabel('count')
a.set_title('(a) Size by map unit — KW p=0.068'); a.legend()

a = axs[0, 1]
for u, c in UC.items():
    s = simm[simm.Geounits == u]
    a.scatter(np.log10(s.area_km2), s.circularity, c=c, s=26, alpha=0.8, label=u)
a.set_xlabel('log10 area (km²)'); a.set_ylabel('circularity 4πA/P²')
a.set_title('(b) Shape vs size — no unit separation'); a.legend()

a = axs[0, 2]
data = [simm[simm.Geounits == u].solidity for u in UC]
bp = a.boxplot(data, tick_labels=list(UC), patch_artist=True)
for patch, c in zip(bp['boxes'], UC.values()):
    patch.set_facecolor(c); patch.set_alpha(0.6)
a.set_ylabel('solidity (A / convex hull A)')
a.set_title('(c) Boundary complexity — KW p=0.45')

a = axs[1, 0]
for u, c in UC.items():
    s = simm[simm.Geounits == u]
    a.scatter(s.lon, s.lat, c=c, s=18 + 2.2 * np.sqrt(s.area_km2 / 100), alpha=0.75)
a.axhline(0, color='gray', lw=0.5); a.axvline(0, color='gray', lw=0.5)
a.set_xlabel('East longitude'); a.set_ylabel('Latitude')
a.set_title('(d) Global distribution (marker ∝ √area)')

a = axs[1, 1]
x = np.sort(simm.area_km2.values)
ccdf = 1 - np.arange(len(x)) / len(x)
a.loglog(x, ccdf, 'o', ms=4, color='#444', label='all SIM chaos (n=114)')
from scipy import stats as st
mu, sig = np.mean(np.log(x)), np.std(np.log(x))
xx = np.logspace(np.log10(x.min()), np.log10(x.max()), 100)
a.loglog(xx, 1 - st.norm.cdf(np.log(xx), mu, sig), '-', color='#e8b63c',
         label=f'lognormal fit (μ={mu:.1f}, σ={sig:.1f})')
a.set_xlabel('area (km²)'); a.set_ylabel('CCDF')
a.set_title('(e) Size distribution — unimodal, dip p=0.96'); a.legend()

a = axs[1, 2]
a.hist(np.abs(simm.lat), bins=18, color='#888', alpha=0.8)
a.set_xlabel('|latitude| (deg)'); a.set_ylabel('count')
a.set_title('(f) Latitude distribution of SIM chaos')
plt.suptitle('SIM 3513 global chaos polygons (n=114): morphometrics by map unit',
             fontsize=14, y=1.00)
plt.tight_layout()
plt.savefig(f'{MEDIA}/fig2-sim3513-morphometrics.png', dpi=130, bbox_inches='tight')
plt.close()
print("fig2 done")

# ---------------- fig 3: clustering ----------------
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import linkage, dendrogram

feats = ['log_area', 'circularity', 'solidity', 'log_aspect']
simc = simm.dropna(subset=feats).copy()
X = StandardScaler().fit_transform(simc[feats])
bic, sil = {}, {}
for k in range(1, 7):
    gm = GaussianMixture(k, n_init=10, random_state=0).fit(X)
    bic[k] = gm.bic(X)
for k in range(2, 7):
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    sil[k] = silhouette_score(X, km.labels_)
gm3 = GaussianMixture(3, n_init=10, random_state=0).fit(X)
lab3 = gm3.predict(X)
P = PCA(2).fit(X); XY = P.transform(X)

fig, axs = plt.subplots(2, 2, figsize=(14, 11))
a = axs[0, 0]
a.plot(list(bic), list(bic.values()), 'o-', color='#c0503a', label='GMM BIC')
a.set_xlabel('number of components k'); a.set_ylabel('BIC', color='#c0503a')
a2 = a.twinx()
a2.plot(list(sil), list(sil.values()), 's--', color='#3a7ac0', label='k-means silhouette')
a2.set_ylabel('silhouette', color='#3a7ac0'); a2.axhline(0.5, color='#3a7ac0', lw=0.6, ls=':')
a2.set_ylim(0, 0.8)
a.set_title('(a) Model selection: BIC min at k=3, but silhouettes ≤0.41\n'
            '(weak structure; 0.5+ would indicate well-separated clusters)')

a = axs[0, 1]
mk = {'chh': '^', 'chl': 'o', 'chm': 's'}
cc = ['#1b9e77', '#d95f02', '#7570b3']
for u in UC:
    s = simc.Geounits == u
    a.scatter(XY[s.values, 0], XY[s.values, 1], c=[cc[l] for l in lab3[s.values]],
              marker=mk[u], s=46, edgecolor='k', lw=0.4, alpha=0.85)
a.set_xlabel(f'PC1 ({P.explained_variance_ratio_[0]*100:.0f}%)')
a.set_ylabel(f'PC2 ({P.explained_variance_ratio_[1]*100:.0f}%)')
hs = [plt.Line2D([], [], marker=mk[u], ls='', mec='k', mfc='w', label=u) for u in mk]
hs += [mpatches.Patch(color=cc[i], label=f'GMM cluster {i}') for i in range(3)]
a.legend(handles=hs, fontsize=9)
a.set_title('(b) PCA of morphometrics: GMM clusters (color)\nvs geologic unit (marker) — no correspondence')

a = axs[1, 0]
Z = linkage(X, 'ward')
dendrogram(Z, ax=a, no_labels=True, color_threshold=0.7 * Z[:, 2].max())
a.set_title('(c) Ward hierarchical clustering: no deep gap between merges')
a.set_ylabel('merge distance')

a = axs[1, 1]
ct = pd.crosstab(simc.Geounits, lab3, normalize='index')
im = a.imshow(ct.values, cmap='Blues', vmin=0, vmax=1)
a.set_xticks(range(3), [f'cluster {i}' for i in range(3)])
a.set_yticks(range(3), ct.index)
for i in range(ct.shape[0]):
    for j in range(ct.shape[1]):
        a.text(j, i, f'{ct.values[i, j]:.2f}', ha='center', va='center',
               color='black', fontsize=12)
plt.colorbar(im, ax=a, shrink=0.8)
a.set_title('(d) Fraction of each map unit per GMM cluster\n(χ² vs k=2: p=0.57 — clusters orthogonal to units)')
plt.suptitle('Unsupervised clustering of SIM 3513 chaos morphometrics', fontsize=14)
plt.tight_layout()
plt.savefig(f'{MEDIA}/fig3-clustering.png', dpi=130, bbox_inches='tight')
plt.close()
print("fig3 done")

# ---------------- fig 4: platy-knobby continuum ----------------
fig, axs = plt.subplots(2, 3, figsize=(17, 10))
cmap = plt.cm.viridis
norm = plt.Normalize(r20.sfd_slope.min(), r20.sfd_slope.max())

a = axs[0, 0]
for reg, grp in blk.groupby('region'):
    ar = np.sort(grp.area_attr.values)[::-1]
    x = np.sqrt(ar); cum = np.cumsum(ar)
    meta = r20[r20.region == reg]
    if not len(meta):
        continue
    AC = meta.area_region.iloc[0]
    sl = meta.sfd_slope.iloc[0]
    a.plot(x, np.log(cum / AC), '-', color=cmap(norm(sl)), lw=1.3, alpha=0.9)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm); sm.set_array([])
plt.colorbar(sm, ax=a, label='SFD slope m (km⁻¹)')
a.set_xlabel('block length scale x = √area (km)')
a.set_ylabel('ln cumulative fractional block area')
a.set_title('(a) Cumulative block-area SFDs, 20 regions')

a = axs[0, 1]
a.hist(r20.sfd_slope, bins=12, color='#5a8f5a', alpha=0.85)
a.set_xlabel('SFD slope m (km⁻¹)'); a.set_ylabel('regions')
a.set_title('(b) Slope distribution: unimodal\n(dip p=0.19; GMM BIC prefers k=1)')

a = axs[0, 2]
sc = a.scatter(r20.knob_frac_dunn, r20.sfd_slope, c=r20.sfd_slope, cmap=cmap,
               s=70, edgecolor='k', lw=0.5)
for _, r in r20.iterrows():
    a.annotate(r.region, (r.knob_frac_dunn, r.sfd_slope), xytext=(4, 4),
               textcoords='offset points', fontsize=8)
a.set_xlabel('knob fraction (knobs / all blocks)')
a.set_ylabel('SFD slope m (km⁻¹)')
a.set_title('(c) Knobbiness vs slope (ρ=-0.34, p=0.14)\nCo=Conamara (platy), E=Murias, D (knobby)')

a = axs[1, 0]
a.scatter(r20.area_region, r20.sfd_slope, c=r20.sfd_slope, cmap=cmap, s=70,
          edgecolor='k', lw=0.5)
for _, r in r20.iterrows():
    a.annotate(r.region, (r.area_region, r.sfd_slope), xytext=(4, 4),
               textcoords='offset points', fontsize=8)
a.set_xscale('log')
a.set_xlabel('chaos region area (km²)'); a.set_ylabel('SFD slope m (km⁻¹)')
a.set_title('(d) Larger chaos → platier blocks\n(Spearman ρ=0.59, p=0.006)')

a = axs[1, 1]
a.scatter(r20.lat, r20.sfd_slope, c=r20.sfd_slope, cmap=cmap, s=70,
          edgecolor='k', lw=0.5)
for _, r in r20.iterrows():
    a.annotate(r.region, (r.lat, r.sfd_slope), xytext=(4, 4),
               textcoords='offset points', fontsize=8)
a.set_xlabel('latitude (deg)'); a.set_ylabel('SFD slope m (km⁻¹)')
a.set_title('(e) Slope vs latitude (ρ(|lat|)=0.03, p=0.90)\nno latitudinal control')

a = axs[1, 2]
lb = blk.dropna(subset=['Block_Plat']).copy()
lb['is_plate'] = lb.Block_Plat == 'Plate'
bins = np.linspace(0, 2.6, 30)
a.hist(np.log10(lb[~lb.is_plate].area_attr), bins=bins, alpha=0.6,
       color='#b06030', label=f'knobs (n={len(lb[~lb.is_plate])})', density=True)
a.hist(np.log10(lb[lb.is_plate].area_attr), bins=bins, alpha=0.6,
       color='#3a7ac0', label=f'plates (n={len(lb[lb.is_plate])})', density=True)
a.set_xlabel('log10 block area (km²)'); a.set_ylabel('density')
a.set_title('(f) Knob vs plate sizes: overlapping continuum\n(combined dip p≈1, unimodal)')
a.legend()
plt.suptitle('The platy–knobby spectrum across 20 block-mapped chaos regions '
             '(2,643 blocks)', fontsize=14)
plt.tight_layout()
plt.savefig(f'{MEDIA}/fig4-platy-knobby-continuum.png', dpi=130, bbox_inches='tight')
plt.close()
print("fig4 done")

# ---------------- fig 5: endmember close-ups ----------------
def crop(lon, lat, half_deg):
    """Read a window around (lon,lat in ±180 east) at full res."""
    with rasterio.open(TIF) as r:
        lon360 = lon % 360
        x0 = (lon360 - 180 - half_deg) * M_PER_DEG
        x1 = (lon360 - 180 + half_deg) * M_PER_DEG
        y0 = (lat - half_deg) * M_PER_DEG
        y1 = (lat + half_deg) * M_PER_DEG
        win = rasterio.windows.from_bounds(x0, y0, x1, y1, r.transform)
        img = r.read(1, window=win)
    return img, (lon - half_deg, lon + half_deg, lat - half_deg, lat + half_deg)

alb = gpd.read_file('/tmp/europa/zenodo/allblocks/AllBlocks.shp')
mills_shp = gpd.read_file('/tmp/europa/zenodo/arcmap/ArcMap Files/LowerRegMapBlocks_raw.shp')
cases = [('TH_cc  Conamara Chaos — "platy" endmember (m=-0.27, 96% plates)',
          86.65, 9.66, 2.3, 'Co'),
         ('LH_E  Murias Chaos — "knobby" endmember (m=-0.74, 97% knobs)',
          -82.59, 22.41, 2.0, 'E'),
         ('LH_D — knobbiest SFD (m=-1.11, 97% knobs)', -73.95, 25.66, 1.4, 'D'),
         ('Region I (Mills) — mixed plates+knobs (m=-0.56)', -81.44, -30.66, 1.6, 'I')]
fig, axs = plt.subplots(2, 2, figsize=(15, 14))
for ax, (title, lon, lat, half, reg) in zip(axs.ravel(), cases):
    img, ext = crop(lon, lat, half)
    ax.imshow(img, cmap='gray', extent=ext, vmin=0, vmax=255)
    name = {'Co': 'TH_cc', 'E': 'LH_E', 'D': 'LH_D'}.get(reg)
    if name is not None:
        g9[g9.name == name].boundary.plot(ax=ax, color='#19d2ff', lw=1.6)
    src = alb if reg in ('Co', 'E', 'D') else mills_shp
    sub = src.cx[ext[0]:ext[1], ext[2]:ext[3]]
    if 'Block_Plat' in sub.columns:
        plates = sub[sub.Block_Plat.fillna('').str.strip() == 'Plate']
        other = sub[sub.Block_Plat.fillna('').str.strip() != 'Plate']
        other.boundary.plot(ax=ax, color='#ff9a3c', lw=0.7)
        plates.boundary.plot(ax=ax, color='#30ff80', lw=0.9)
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3])
    ax.set_title(title, fontsize=11)
    ax.set_xlabel('East longitude'); ax.set_ylabel('Latitude')
hs = [plt.Line2D([], [], color='#30ff80', label='plates'),
      plt.Line2D([], [], color='#ff9a3c', label='knobs/blocks'),
      plt.Line2D([], [], color='#19d2ff', label='chaos terrain outline')]
fig.legend(handles=hs, loc='lower center', ncol=3, fontsize=11)
plt.suptitle('Endmember and intermediate chaos morphologies (Galileo 500 m mosaic)',
             fontsize=14, y=0.995)
plt.tight_layout(rect=(0, 0.02, 1, 1))
plt.savefig(f'{MEDIA}/fig5-endmember-closeups.png', dpi=130, bbox_inches='tight')
plt.close()
print("fig5 done")
