---
cursor:
  subagentId: "bc-7b8fc683-5fed-5314-917e-50b5565e397f"
---

# Draft co-author feedback on "Quantifying Chaos Block Morphology on Europa: Constraints on Chaos Evolution"

*Prepared for Conor Nixon to edit and send to Alyssa Mills. A Word version
(`mills-draft-coauthor-feedback.docx`) with the verification figure embedded
accompanies this file.*

---

Hi Alyssa,

Thanks for sending the draft — this is shaping up well. The question is
exactly the right follow-on to Leonard et al. (2022): if the platy→knobby
continuum is an evolutionary sequence, block shape should record it, and
testing that with objective sedimentology-style metrics is a nice, clean
idea. The core negative result (roundness and angularity do not track the
size-distribution slope) looks right to me, and I think the hemispheric
asymmetry is the most interesting positive finding in the paper — possibly
worth promoting further.

Before circulating more widely, I ran an independent check of the analysis
using the public block outlines (the Leonard et al. Zenodo record 12775125
and your record 10162452 — 2,665 unique blocks re-measured across the same 20
regions, with local equal-area projection on the Europa sphere, after
deduplicating the overlapping all-blocks and plate-subset GeoJSON files). Most of the
paper replicates well, but the check turned up one problem in the jaggedness
analysis that I think we need to fix before submission, plus a few smaller
statistical points. Details below; I'm happy to share the scripts and the
attached verification figure, and to help rework the relevant section.

## What replicates well

- **Roundness and angularity nulls.** With the standard
  max-inscribed-circle definition I get the same answer: no relationship
  with SFD slope once hemisphere is accounted for (a regression of terrain
  roundness on slope + hemisphere puts all the signal in the hemisphere term,
  p = 0.03, and none in slope, p = 0.81). Section 4's conclusion stands.
- **The hemispheric difference.** My independently computed Hotelling T² came
  out at 160 against your 121 — essentially the same — with the same
  direction (trailing blocks rounder, leading more angular/jagged). Even
  better, the roundness difference survives a conservative terrain-level
  Mann–Whitney test (p = 0.023 with n = 9 vs 11 terrains), which I'd suggest
  adding (see point 3).
- Angularity magnitudes, the long upper tail you describe, and the Fisher
  r-to-z arithmetic all check out.

## The one major issue: jaggedness

**1. The jaggedness definition, units, figure, and tabulated values are
mutually inconsistent, and I think the computed quantity differs from
Eq. 3.** As written, J = P²/4πA is dimensionless and scale-invariant, and the
isoperimetric inequality bounds it below by 1 (so log J ≥ 0 always). But the
text says J has units of inverse length; Fig. 5's y-axis is in −log(km) with
most Conamara points *below* zero; and the hemisphere means quoted in §3.4
(~1,414–1,570) are about three orders of magnitude above anything Eq. 3 can
produce for real blocks (across all 2,665 blocks I measure Eq. 3 values of
1.01–5.7, mean 1.63). Empirically, whatever was computed scales almost
exactly as 1/Area: a 1/A-type variant fitted to the Conamara blocks gives a
slope of −0.16 vs your −0.19, whereas Eq. 3 proper is flat (+0.015). Could
you check the ArcMap/script units here (my guess is a perimeter/area unit
mismatch, or a formula that divides by an extra factor of area)? Whichever
way it resolves, the equation, figure axes, and tabulated numbers need to end
up describing the same quantity.

**2. More fundamentally, the two significant jaggedness results are
reproduced exactly by shape-free circles — they restate the block size
distribution rather than measuring morphology.** Because the computed J
varies as ~1/A, both the per-terrain mean jaggedness and the fitted
"jaggedness slope" are controlled by each terrain's block sizes, and the SFD
slope is of course also a size-distribution summary — so the two axes of the
correlation are the same information measured twice. The decisive test: I
replaced every block with a perfect circle of the same area (erasing all
shape information) and re-ran the pipeline. The jaggedness-slope vs SFD-slope
correlation not only survives, it *strengthens* (circles: ρ = +0.67,
p = 0.001; real shapes: ρ = +0.54, p = 0.015; the same holds within each
hemisphere separately). Your §4.3 caveats already point in this direction,
but §4.4–4.5 and the Conclusions still read the correlation as potentially
informative about fragmentation — I don't think it can be, as constructed.

Two ways to fix it, in order of preference: (a) keep the jaggedness section
but recast it against the size-matched null — compute each terrain's expected
jaggedness slope from circles (or any fixed shape) with the observed block
areas, and report the *residual*; in my run the residuals look like noise,
which is itself a publishable statement ("edge complexity shows no
terrain-level signal beyond block size"); or (b) replace jaggedness with a
scale-invariant edge-complexity metric from the start — Eq. 3 as actually
written is exactly that (it's 1/circularity), so the simplest fix may be to
compute it correctly in consistent units and redo §3.3.

## Smaller statistical points

3. **Hotelling's T² treats ~2,000 blocks as independent samples**, but they
   cluster within 20 terrains that differ in mapper, image geometry, and
   illumination — reviewers will flag this as pseudoreplication. Since the
   roundness difference also passes at terrain level (p = 0.010), I'd report
   the terrain-level test as primary (or a mixed model with a terrain random
   effect) and keep T² as supporting. The PCA panel shows the hemisphere
   clouds almost fully overlapping, so an effect-size statement would be more
   honest than the very small p-value, which is mostly a function of n.
4. **Hemisphere and knobbiness are collinear** (the leading hemisphere
   contains the knobbiest terrains: D, E, F, H), so the roundness–slope and
   roundness–hemisphere results are not independent. The regression above
   cleanly attributes the signal to hemisphere — worth stating explicitly,
   because it simultaneously sharpens the "no evolution signal" conclusion
   and strengthens the hemispheric result. It might even be the cleaner frame
   for the whole paper.
5. **The text calls the all-chaos jaggedness-slope correlation significant,
   but Table 1 gives p = 0.052**, which fails the paper's own α = 0.05. The
   wording in §4.3 and the Conclusions needs to match the table (this may
   become moot after point 2).
6. **Fisher r-to-z on Spearman coefficients** should use the
   Spearman-adjusted standard error (≈1.06/(n−3)) rather than the Pearson
   1/(n−3); with n = 9 and 11 the hemisphere contrasts are slightly
   anti-conservative. And the leading-hemisphere ρ = 0.833 (n = 9) deserves a
   confidence interval (roughly 0.4–0.96) so readers don't over-read it.
7. **A roundness-vs-size diagnostic would pre-empt the resolution worry**:
   in my re-measurement roundness is uncorrelated with block length
   (ρ = −0.02 across all blocks), which is reassuring for the null results
   and worth one sentence plus a supplementary panel.

## Housekeeping

8. §3.1 has some placeholder fragments to finish ("We find no statistically
   significant relationship where.", "(l)", "…as evident with the Spearman
   test ()"), and §3.1 says trailing terrains cluster at 0.30–0.34 while
   Fig. 3 shows dd at ≈0.254.
9. Key Points, Abstract, Plain Language Summary, Open Research, and the
   References list are still template text — in particular the data DOIs
   (Zenodo 12775125, 10162452, and a record for the new mappings) will be
   needed for the AGU availability statement, and I'd suggest depositing the
   metric scripts there too.
10. The PCA includes log area, log perimeter, *and* jaggedness, which (as
    computed) is nearly a deterministic function of the first two
    (r = −0.925) — PC1 and the "97% in three PCs" statement are partly
    built in. PCA on the shape variables alone might say more.
11. The GeoJSON release for regions I and hh contains a few degenerate
    sliver polygons (1–100 m across) that explode the angularity/jaggedness
    tails — worth filtering in both the analysis and the archive. Also, each
    region's `Chaos_X.json` (all blocks) and `Chaos_X_plates.json` (plate
    subset) share the same plate geometries, so concatenating the two double
    counts plates — I did exactly this on my first pass, and a README note
    would spare others the same mistake.
12. Typos I noticed: "its' ice shell" (§1), "trialing hemispheres" (§4.5),
    "a newer imagery" (§4.2), "smaller, roundness blocks" (Conclusions), and
    the duplicated mosaic credit in the Fig. 1 caption.

None of this undercuts the paper's main message — if anything, points 2 and
4 make the story cleaner: block shape carries no platy→knobby evolution
signal (now demonstrated against an explicit null), while the hemispheres
really do differ. Happy to send the scripts, run the size-matched null for
the final block set, or take a pass at §3.3/4.3 myself — just let me know.

Best,
Conor

*Attachment: verification figure (3 panels: (a) Eq. 3 vs the dimensional
variant on Conamara; (b) jaggedness-slope correlation with real shapes vs
area-matched circles; (c) terrain-mean roundness by hemisphere).*
