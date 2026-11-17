"""Diagnostics: identify what the draft actually computed and test the
statistical logic of its jaggedness and hemisphere results."""
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('/tmp/europa/work/blocks_mills_metrics.csv')
reg = pd.read_csv('/agent/repos/ConorNixon/europa-chaos/data/regions20_full.csv')
reg['region'] = reg['region'].replace({'Co': 'Co'})
slopes = reg.set_index('region')['sfd_slope']
# our regions20 uses 'Co'? check naming
print('region names in slopes:', sorted(slopes.index))

LEAD = list('ABCDEFGHI')
df['hemi'] = np.where(df.region.isin(LEAD), 'leading', 'trailing')

# ---- 1. roundness variants ----
# need r and x back: roundness = pi r^2 / A  ->  r = sqrt(roundness*A/pi)
# angularity = (180-alpha)(x/r), alpha=asin(r/x): solve x/r numerically? store ratio:
# from angularity: let q = x/r;  ang = (180 - degrees(asin(1/q))) * q
from scipy.optimize import brentq
def q_from_ang(a):
    f = lambda q: (180 - np.degrees(np.arcsin(min(1/q, 1)))) * q - a
    try:
        return brentq(f, 1.0001, 3000)
    except Exception:
        return np.nan
df['q'] = df.angularity.map(q_from_ang)          # x/r
df['round_rx2'] = 1.0 / df.q**2                  # (r/x)^2 variant

tm = df.groupby('region').agg(
    n=('J1', 'size'),
    roundness=('roundness', 'mean'),
    round_rx2=('round_rx2', 'mean'),
    angularity=('angularity', 'mean'),
    ang_med=('angularity', 'median'),
    J1=('J1', 'mean'),
    medL=('L_km', 'median'),
    meanL=('L_km', 'mean'))
tm['sfd'] = slopes
print('\nper-terrain means:\n', tm.round(3))

for col in ['roundness', 'round_rx2', 'angularity', 'J1']:
    rho, p = stats.spearmanr(tm['sfd'], tm[col])
    print(f'Spearman {col} vs SFD slope (all 20): rho={rho:.3f} p={p:.3f}')

# ---- 2. identify jaggedness variant from Conamara fit (paper: -0.19x+0.91) ----
co = df[df.region == 'Co'].copy()
print('\nConamara blocks:', len(co), 'L range', co.L_km.min().round(2), co.L_km.max().round(2))
variants = {
    'J1 = P^2/4piA (Eq.3, dimensionless)': co.J1,
    'J1/L  [1/km]': co.J1 / co.L_km,
    'J1/A  [1/km^2]': co.J1 / co.area_km2,
    'P/(4piA) [1/km]': co.perim_km / (4 * np.pi * co.area_km2),
    'P/A [1/km]': co.perim_km / co.area_km2,
    '1/A [1/km^2]': 1 / co.area_km2,
}
print('\nConamara: fit log10(J) = m*L + b   (paper: m=-0.19, b=0.91)')
for name, J in variants.items():
    ok = J > 0
    m, b = np.polyfit(co.L_km[ok], np.log10(J[ok]), 1)
    print(f'  {name:42s} m={m:+.3f} b={b:+.3f}')

# ---- 3. per-terrain jaggedness slope (their pipeline) for best variant,
#         real shapes vs null model (every block replaced by a CIRCLE) ----
def jagg_slope(sub, J):
    ok = J > 0
    if ok.sum() < 5:
        return np.nan
    m, b = np.polyfit(sub.L_km[ok], np.log10(J[ok]), 1)
    return m

rows = []
for r_, sub in df.groupby('region'):
    J_real = sub.perim_km / (4 * np.pi * sub.area_km2)      # P/(4piA) variant
    J_real2 = sub.J1 / sub.area_km2                          # J1/A variant
    # null: circle of identical area -> P = 2*sqrt(pi*A), shape info erased
    P_circ = 2 * np.sqrt(np.pi * sub.area_km2)
    J_null = P_circ / (4 * np.pi * sub.area_km2)
    J_null2 = 1 / sub.area_km2
    rows.append(dict(region=r_,
                     js_real=jagg_slope(sub, J_real),
                     js_real2=jagg_slope(sub, J_real2),
                     js_null=jagg_slope(sub, J_null),
                     js_null2=jagg_slope(sub, J_null2),
                     mean_J_real=J_real.mean(),
                     mean_J_null=J_null.mean()))
js = pd.DataFrame(rows).set_index('region')
js['sfd'] = slopes
print('\nper-terrain jaggedness slopes (real vs circle-null):\n', js.round(3))
for col in ['js_real', 'js_real2', 'js_null', 'js_null2', 'mean_J_real', 'mean_J_null']:
    sub = js.dropna(subset=[col, 'sfd'])
    rho, p = stats.spearmanr(sub['sfd'], sub[col])
    print(f'Spearman {col} vs SFD slope: rho={rho:+.3f} p={p:.3f}')

# ---- 4. roundness vs block size (resolution confound) ----
rho, p = stats.spearmanr(df.L_km, df.roundness)
print(f'\nroundness vs L (all blocks): rho={rho:+.3f} p={p:.2g}')
rho, p = stats.spearmanr(df.L_km, df.round_rx2)
print(f'round_rx2 vs L (all blocks): rho={rho:+.3f} p={p:.2g}')

# ---- 5. hemisphere tests ----
print('\nhemisphere block counts:', df.hemi.value_counts().to_dict())
print('mean roundness lead/trail:',
      df.groupby('hemi').roundness.mean().round(3).to_dict(),
      ' median:', df.groupby('hemi').roundness.median().round(3).to_dict())
print('mean (r/x)^2 lead/trail:', df.groupby('hemi').round_rx2.mean().round(3).to_dict())
print('mean angularity lead/trail:', df.groupby('hemi').angularity.mean().round(1).to_dict(),
      ' median:', df.groupby('hemi').angularity.median().round(1).to_dict())

# Hotelling T2, block level (as in the paper)
X = df[['area_km2', 'perim_km', 'roundness', 'angularity']].copy()
X['logA'] = np.log10(X.pop('area_km2'))
X['logP'] = np.log10(X.pop('perim_km'))
X['logJrel'] = np.log10(df.perim_km / (4 * np.pi * df.area_km2))
X = X[['logA', 'logP', 'roundness', 'angularity', 'logJrel']].replace(
    [np.inf, -np.inf], np.nan)
ok = X.notna().all(axis=1) & (df.angularity < 5000)
X, h = X[ok].values, df.hemi[ok].values
x1, x2 = X[h == 'leading'], X[h == 'trailing']
n1, n2, p_ = len(x1), len(x2), X.shape[1]
d = x1.mean(0) - x2.mean(0)
S = ((n1 - 1) * np.cov(x1.T) + (n2 - 1) * np.cov(x2.T)) / (n1 + n2 - 2)
T2 = n1 * n2 / (n1 + n2) * d @ np.linalg.solve(S, d)
F = T2 * (n1 + n2 - p_ - 1) / ((n1 + n2 - 2) * p_)
pval = 1 - stats.f.cdf(F, p_, n1 + n2 - p_ - 1)
print(f'\nHotelling T2 block-level: T2={T2:.1f} F={F:.1f} p={pval:.2g} (n={n1},{n2})')

# terrain-level comparison (the statistically honest unit)
tm['hemi'] = np.where(tm.index.isin(LEAD), 'leading', 'trailing')
for col in ['roundness', 'angularity', 'J1']:
    l = tm[tm.hemi == 'leading'][col]
    t = tm[tm.hemi == 'trailing'][col]
    u, p2 = stats.mannwhitneyu(l, t)
    print(f'terrain-level Mann-Whitney {col}: lead_mean={l.mean():.3f} '
          f'trail_mean={t.mean():.3f} p={p2:.3f} (n=9 vs 11)')
