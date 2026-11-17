"""Follow-ups: outlier contamination, per-hemisphere null correlations,
roundness-SFD with cleaned data, hemisphere/knobbiness confound."""
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv('/tmp/europa/work/blocks_mills_metrics.csv')
reg = pd.read_csv('/agent/repos/ConorNixon/europa-chaos/data/regions20_full.csv')
slopes = reg.set_index('region')['sfd_slope']
LEAD = list('ABCDEFGHI')

# --- degenerate geometry check in I and hh ---
for r_ in ['I', 'hh']:
    sub = df[df.region == r_]
    bad = sub[sub.J1 > 10]
    print(f'{r_}: n={len(sub)}, J1>10: {len(bad)}, '
          f'their L range {bad.L_km.min():.3f}-{bad.L_km.max():.3f} km, '
          f'J1 median {sub.J1.median():.2f}')

# clean: drop degenerate slivers
clean = df[(df.J1 < 10) & (df.angularity < 5000) & (df.L_km > 0.05)].copy()
print('\ncleaned blocks:', len(clean), 'removed:', len(df) - len(clean))

tm = clean.groupby('region').agg(roundness=('roundness', 'mean'),
                                 angularity=('angularity', 'mean'),
                                 J1=('J1', 'mean'), medL=('L_km', 'median'))
tm['sfd'] = slopes
for col in ['roundness', 'angularity', 'J1']:
    rho, p = stats.spearmanr(tm['sfd'], tm[col])
    print(f'CLEAN Spearman terrain-mean {col} vs SFD slope: rho={rho:+.3f} p={p:.3f}')

# roundness vs knobbiness within hemisphere (confound check)
tm['hemi'] = np.where(tm.index.isin(LEAD), 'leading', 'trailing')
for h in ['leading', 'trailing']:
    s = tm[tm.hemi == h]
    rho, p = stats.spearmanr(s['sfd'], s['roundness'])
    print(f'  {h}: roundness vs sfd rho={rho:+.3f} p={p:.3f} (n={len(s)})')

# partial: does hemisphere difference in terrain roundness survive controlling SFD?
import statsmodels.api as sm
X = pd.DataFrame({'sfd': tm.sfd, 'lead': (tm.hemi == 'leading').astype(float)})
X = sm.add_constant(X)
m = sm.OLS(tm.roundness, X).fit()
print('\nterrain roundness ~ const + sfd + leading:')
print(m.params.round(4).to_dict())
print({k: round(v, 4) for k, v in m.pvalues.to_dict().items()})

# --- per-hemisphere circle-null jaggedness-slope correlations ---
def jagg_slope_null(sub):
    P_circ = 2 * np.sqrt(np.pi * sub.area_km2)
    J = P_circ / (4 * np.pi * sub.area_km2)
    m, b = np.polyfit(sub.L_km, np.log10(J), 1)
    return m

def jagg_slope_real(sub):
    J = sub.perim_km / (4 * np.pi * sub.area_km2)
    m, b = np.polyfit(sub.L_km, np.log10(J), 1)
    return m

js = clean.groupby('region').apply(jagg_slope_null, include_groups=False).rename('null')
jr = clean.groupby('region').apply(jagg_slope_real, include_groups=False).rename('real')
j = pd.concat([js, jr], axis=1)
j['sfd'] = slopes
j['hemi'] = np.where(j.index.isin(LEAD), 'leading', 'trailing')
for h in ['leading', 'trailing']:
    s = j[j.hemi == h]
    rn, pn = stats.spearmanr(s.sfd, s['null'])
    rr, pr = stats.spearmanr(s.sfd, s['real'])
    print(f'\n{h} (n={len(s)}): jagg-slope vs SFD  real rho={rr:+.3f} p={pr:.3f} | '
          f'CIRCLE-NULL rho={rn:+.3f} p={pn:.3f}')
rall_n, pall_n = stats.spearmanr(j.sfd, j['null'])
rall_r, pall_r = stats.spearmanr(j.sfd, j['real'])
print(f'all 20: real rho={rall_r:+.3f} p={pall_r:.3f} | null rho={rall_n:+.3f} p={pall_n:.3f}')

# --- why: jaggedness slope is ~ -k*log10(e)/harmonic-mean-L ---
j['predicted_null'] = clean.groupby('region').apply(
    lambda s: -0.5 * np.log10(np.e) * (1 / s.L_km).mean() * 2, include_groups=False)
rho, p = stats.spearmanr(j['null'], 1 / clean.groupby('region').L_km.mean())
print(f'\nnull jagg-slope vs 1/meanL: rho={rho:+.3f} p={p:.4f}')
rho, p = stats.spearmanr(slopes, clean.groupby('region').L_km.mean())
print(f'SFD slope vs mean block L: rho={rho:+.3f} p={p:.4f}')
