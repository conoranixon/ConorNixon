"""Statistical tests: do chaos features separate into distinct populations?"""
import numpy as np
import pandas as pd
import geopandas as gpd
import warnings, sys
warnings.filterwarnings('ignore')
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import diptest

OUT = open('/tmp/europa/work/stats_results2.txt', 'w')
def log(*a):
    s = " ".join(str(x) for x in a)
    print(s); OUT.write(s + "\n")

rng = np.random.default_rng(42)

sim = pd.read_csv('/tmp/europa/work/sim_morpho.csv')
r20 = pd.read_csv('/tmp/europa/work/regions20.csv')
blk = pd.read_csv('/tmp/europa/work/blocks_all.csv')

# ---------- A. SIM3513 global chaos: unit-type differences ----------
log("=" * 70)
log("A. SIM 3513 global chaos polygons (n=%d)" % len(sim))
sim['log_area'] = np.log10(sim.area_km2)
sim['log_aspect'] = np.log10(sim.aspect)
feats = ['log_area', 'circularity', 'solidity', 'log_aspect']
log("\nmedians by unit:")
log(sim.groupby('Geounits')[['area_km2', 'circularity', 'solidity', 'aspect', 'lat']]
    .median().round(3).to_string())
log("\nKruskal-Wallis across chh/chl/chm:")
for f in feats + ['lat']:
    groups = [g[f].dropna().values for _, g in sim.groupby('Geounits')]
    H, p = stats.kruskal(*groups)
    log(f"  {f:12s} H={H:7.2f}  p={p:.3g}")
log("\npairwise Mann-Whitney log_area:")
for a, b in [('chh', 'chl'), ('chh', 'chm'), ('chl', 'chm')]:
    u, p = stats.mannwhitneyu(sim[sim.Geounits == a].log_area,
                              sim[sim.Geounits == b].log_area)
    log(f"  {a} vs {b}: p={p:.3g}")

# ---------- B. clustering on SIM morphometrics ----------
log("\n" + "=" * 70)
log("B. Unsupervised clustering, SIM 3513 morphometrics", feats)
X = StandardScaler().fit_transform(sim[feats].dropna())
log("\nGMM BIC (lower=better):")
bics, sils = {}, {}
for k in range(1, 7):
    gm = GaussianMixture(k, n_init=10, random_state=0).fit(X)
    bics[k] = gm.bic(X)
    if k > 1:
        lab = gm.predict(X)
        sils[k] = silhouette_score(X, lab) if len(set(lab)) > 1 else np.nan
log("  BIC:", {k: round(v, 1) for k, v in bics.items()})
log("  best k by BIC:", min(bics, key=bics.get))
log("  GMM silhouettes:", {k: round(v, 3) for k, v in sils.items()})
log("\nKMeans silhouettes:")
ks = {}
for k in range(2, 7):
    km = KMeans(k, n_init=10, random_state=0).fit(X)
    ks[k] = silhouette_score(X, km.labels_)
log(" ", {k: round(v, 3) for k, v in ks.items()})

# does 2-cluster GMM align with map units?
gm2 = GaussianMixture(2, n_init=10, random_state=0).fit(X)
lab2 = gm2.predict(X)
sim_c = sim.dropna(subset=feats).copy(); sim_c['gmm2'] = lab2
log("\nGMM k=2 vs geologic unit crosstab:")
log(pd.crosstab(sim_c.Geounits, sim_c.gmm2).to_string())
from scipy.stats import chi2_contingency
chi2, p, _, _ = chi2_contingency(pd.crosstab(sim_c.Geounits, sim_c.gmm2))
log(f"chi2={chi2:.2f} p={p:.3g}")
sim_c.to_csv('/tmp/europa/work/sim_morpho_clustered.csv', index=False)

# dip tests
log("\nHartigan dip tests (SIM):")
for f in ['log_area', 'circularity', 'solidity']:
    d, p = diptest.diptest(sim[f].dropna().values)
    log(f"  {f:12s} dip={d:.4f} p={p:.3g}")

# ---------- C. 20-region platy-knobby continuum ----------
log("\n" + "=" * 70)
log("C. 20 labeled regions: SFD slope continuum test")
m = r20.sfd_slope.values
d, p = diptest.diptest(m)
log(f"SFD slope: dip={d:.4f} p={p:.3g}  (p>0.05 = no evidence of multimodality)")
d2, p2 = diptest.diptest(r20.knob_frac_dunn.values)
log(f"knob fraction: dip={d2:.4f} p={p2:.3g}")
# 1D GMM BIC on slopes
m1 = m.reshape(-1, 1)
for k in (1, 2, 3):
    g = GaussianMixture(k, n_init=10, random_state=0).fit(m1)
    log(f"  slope GMM k={k}: BIC={g.bic(m1):.1f}")
rho, p = stats.spearmanr(r20.sfd_slope, r20.knob_frac_dunn)
log(f"Spearman slope vs knob_frac: rho={rho:.3f} p={p:.3g}")
rho, p = stats.spearmanr(r20.sfd_slope, np.abs(r20.lat))
log(f"Spearman slope vs |lat|: rho={rho:.3f} p={p:.3g}")
rho, p = stats.spearmanr(r20.sfd_slope, r20.area_region)
log(f"Spearman slope vs region area: rho={rho:.3f} p={p:.3g}")
rho, p = stats.spearmanr(r20.knob_frac_dunn, np.abs(r20.lat))
log(f"Spearman knob_frac vs |lat|: rho={rho:.3f} p={p:.3g}")
lead = r20[r20.lon < 0]; trail = r20[r20.lon > 0]
u, p = stats.mannwhitneyu(lead.sfd_slope, trail.sfd_slope)
log(f"leading (n={len(lead)}) vs trailing (n={len(trail)}) slope MW p={p:.3g}")

# ---------- D. blocks: knobs vs plates ----------
log("\n" + "=" * 70)
log("D. Block level: Knob/Block vs Plate")
lb = blk.dropna(subset=['Block_Plat']).copy()
lb['is_plate'] = lb.Block_Plat == 'Plate'
lb['log_area'] = np.log10(lb.area_attr)
log("counts:", lb.Block_Plat.value_counts().to_dict())
for f in ['log_area', 'circularity', 'solidity', 'aspect']:
    u, p = stats.mannwhitneyu(lb[lb.is_plate][f].dropna(),
                              lb[~lb.is_plate][f].dropna())
    med_p = lb[lb.is_plate][f].median(); med_k = lb[~lb.is_plate][f].median()
    log(f"  {f:12s} plate med={med_p:7.3f} knob med={med_k:7.3f}  MW p={p:.3g}")
d, p = diptest.diptest(lb.log_area.values)
log(f"block log-area dip test: dip={d:.4f} p={p:.3g}")
d, p = diptest.diptest(blk.area_attr.apply(np.log10).dropna().values)
log(f"ALL blocks log-area dip: dip={d:.4f} p={p:.3g}")

# overlap: can a single threshold separate plates from knobs?
from sklearn.linear_model import LogisticRegression
Xb = lb[['log_area', 'circularity', 'solidity']].dropna()
yb = lb.loc[Xb.index, 'is_plate']
lr = LogisticRegression().fit(Xb, yb)
log(f"logistic plate-vs-knob accuracy: {lr.score(Xb, yb):.3f} "
    f"(baseline {max(yb.mean(), 1-yb.mean()):.3f})")

# ---------- E. SIM chaos size distribution + spatial ----------
log("\n" + "=" * 70)
log("E. Spatial statistics, SIM 3513 chaos")
total_chaos = sim.area_km2.sum()
A_europa = 4 * np.pi * 1562.09 ** 2
log(f"total mapped chaos area {total_chaos:.3e} km2 = {100*total_chaos/A_europa:.1f}% of surface")
lead = sim[(sim.lon > -180) & (sim.lon < 0)]
trail = sim[sim.lon > 0]
log(f"leading (lon<0): n={len(lead)} area={lead.area_km2.sum():.2e}; "
    f"trailing: n={len(trail)} area={trail.area_km2.sum():.2e}")
for u in ['chh', 'chl', 'chm']:
    s = sim[sim.Geounits == u]
    log(f"  {u}: n={len(s)}, |lat| median={np.abs(s.lat).median():.1f}, "
        f"area total={s.area_km2.sum():.2e} km2")
u, p = stats.mannwhitneyu(np.abs(sim[sim.Geounits=='chl'].lat), np.abs(sim[sim.Geounits=='chm'].lat))
log(f"chl vs chm |lat| MW p={p:.3g}")
OUT.close()
