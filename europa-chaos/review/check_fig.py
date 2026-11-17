"""Verification figure for the Mills draft review."""
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

df = pd.read_csv('/tmp/europa/work/blocks_mills_metrics.csv')
df = df[(df.J1 < 10) & (df.angularity < 5000) & (df.L_km > 0.05)]
reg = pd.read_csv('/agent/repos/ConorNixon/europa-chaos/data/regions20_full.csv')
slopes = reg.set_index('region')['sfd_slope']
LEAD = list('ABCDEFGHI')

fig, axes = plt.subplots(1, 3, figsize=(16.5, 5))

# (a) Conamara: Eq.3 jaggedness vs the dimensional variant
ax = axes[0]
co = df[df.region == 'Co']
ax.scatter(co.L_km, np.log10(co.J1), s=18, c='k', label=r'Eq. 3: $P^2/4\pi A$ (dimensionless)')
Jdim = co.J1 / co.area_km2
ax.scatter(co.L_km, np.log10(Jdim), s=18, c='crimson', marker='^',
           label=r'dimensional variant $\propto 1/A$ [km$^{-2}$]')
m, b = np.polyfit(co.L_km, np.log10(Jdim), 1)
xx = np.linspace(co.L_km.min(), co.L_km.max(), 10)
ax.plot(xx, m * xx + b, 'r--', lw=1.2, label=f'fit: {m:.2f}x+{b:.2f}  (draft: -0.19x+0.91)')
ax.axhline(0, color='gray', lw=0.8, ls=':')
ax.annotate('isoperimetric bound: Eq.3 $\\geq 1$\n(log $\\geq$ 0); draft Fig. 5 values\nbelow 0 are impossible under Eq. 3',
            xy=(6.5, 0.12), fontsize=8.5, color='0.3')
ax.set_xlabel('characteristic length $\\sqrt{A}$ [km]')
ax.set_ylabel('log$_{10}$(jaggedness)')
ax.set_title('(a) Conamara: Eq. 3 is scale-free;\nthe size trend needs a dimensional variant')
ax.legend(fontsize=8, loc='lower left')

# (b) jaggedness slope vs SFD slope: real shapes vs circle null
ax = axes[1]
def jslope(sub, null):
    P = 2 * np.sqrt(np.pi * sub.area_km2) if null else sub.perim_km
    J = P / (4 * np.pi * sub.area_km2)
    return np.polyfit(sub.L_km, np.log10(J), 1)[0]
rows = []
for r_, sub in df.groupby('region'):
    rows.append(dict(region=r_, real=jslope(sub, False), null=jslope(sub, True),
                     sfd=slopes[r_]))
j = pd.DataFrame(rows)
rr, pr = stats.spearmanr(j.sfd, j.real)
rn, pn = stats.spearmanr(j.sfd, j.null)
ax.scatter(j.sfd, j.real, c='k', s=40, label=f'real block shapes  $\\rho$={rr:+.2f}, p={pr:.3f}')
ax.scatter(j.sfd, j.null, facecolors='none', edgecolors='crimson', s=55, marker='o',
           label=f'circles of same areas  $\\rho$={rn:+.2f}, p={pn:.3f}')
for _, row in j.iterrows():
    ax.plot([row.sfd, row.sfd], [row.real, row.null], color='0.8', lw=0.6, zorder=0)
ax.set_xlabel('block size distribution slope [km$^{-1}$]')
ax.set_ylabel('fitted jaggedness slope')
ax.set_title('(b) The jaggedness-slope correlation survives\nwith ALL shape information erased')
ax.legend(fontsize=8.5, loc='lower right')

# (c) terrain-mean roundness vs SFD slope, colored by hemisphere
ax = axes[2]
tm = df.groupby('region').agg(roundness=('roundness', 'mean'))
tm['sfd'] = slopes
tm['lead'] = tm.index.isin(LEAD)
for lead, c, lab in [(True, 'crimson', 'leading'), (False, 'royalblue', 'trailing')]:
    s = tm[tm.lead == lead]
    ax.scatter(s.sfd, s.roundness, c=c, s=45, label=lab)
    for r_, row in s.iterrows():
        ax.annotate(r_, (row.sfd, row.roundness), fontsize=7.5,
                    xytext=(3, 3), textcoords='offset points', color=c)
rho, p = stats.spearmanr(tm.sfd, tm.roundness)
ax.set_xlabel('block size distribution slope [km$^{-1}$]')
ax.set_ylabel('terrain mean roundness  $\\pi r_{ins}^2/A$')
ax.set_title(f'(c) Max-inscribed-circle roundness:\nmean $\\approx$0.5 (not 0.25-0.35); hemispheres differ')
ax.legend(fontsize=9)

plt.tight_layout()
out = '/cursor/stores/bc-0959e656-639f-4f36-9cde-b9d3406f110a/media/europa-chaos/mills-draft-check.png'
plt.savefig(out, dpi=170)
print('saved', out)
