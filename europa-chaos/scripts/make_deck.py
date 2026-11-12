"""Build a slide deck from the Europa chaos sub-types report."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from PIL import Image
import os

STORE = "/cursor/stores/bc-0959e656-639f-4f36-9cde-b9d3406f110a"
FIGS = f"{STORE}/media/europa-chaos"
OUT = f"{STORE}/docs/europa-chaos-subtypes-slides.pptx"

NAVY = RGBColor(0x16, 0x2A, 0x44)
BLUE = RGBColor(0x1F, 0x6F, 0xB2)
SLATE = RGBColor(0x33, 0x3D, 0x4A)
GRAY = RGBColor(0x6B, 0x75, 0x82)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
ACCENT = RGBColor(0x2E, 0xA3, 0xC8)

SW, SH = Inches(13.333), Inches(7.5)

prs = Presentation()
prs.slide_width = SW
prs.slide_height = SH
BLANK = prs.slide_layouts[6]


def add_slide():
    return prs.slides.add_slide(BLANK)


def rect(slide, x, y, w, h, color):
    from pptx.enum.shapes import MSO_SHAPE
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    sh.shadow.inherit = False
    return sh


def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    """lines: list of (text, size_pt, bold, color, bullet_level_or_None, space_after_pt)"""
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    first = True
    for text, size, bold, color, level, space_after in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        p.space_after = Pt(space_after)
        if level is not None:
            p.level = level
            text = ("\u2022  " if level == 0 else "\u2013  ") + text
        # support **bold** inline segments
        segs = text.split("**")
        for i, seg in enumerate(segs):
            if seg == "":
                continue
            r = p.add_run()
            r.text = seg
            r.font.size = Pt(size)
            r.font.bold = bold or (i % 2 == 1)
            r.font.color.rgb = color
            r.font.name = "Calibri"
    return tb


def header(slide, title, number=None):
    rect(slide, 0, 0, SW, Inches(0.92), NAVY)
    textbox(slide, Inches(0.5), Inches(0.08), Inches(11.5), Inches(0.8),
            [(title, 26, True, WHITE, None, 0)], anchor=MSO_ANCHOR.MIDDLE)
    if number:
        textbox(slide, Inches(12.3), Inches(0.08), Inches(0.8), Inches(0.8),
                [(number, 16, False, ACCENT, None, 0)],
                align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)


def add_picture_fit(slide, path, x, y, max_w, max_h):
    w_px, h_px = Image.open(path).size
    ar = w_px / h_px
    box_ar = max_w / max_h
    if ar >= box_ar:
        w, h = max_w, int(max_w / ar)
    else:
        h, w = max_h, int(max_h * ar)
    slide.shapes.add_picture(path, int(x + (max_w - w) / 2),
                             int(y + (max_h - h) / 2), int(w), int(h))


def fig_slide(title, number, fig, bullets, fig_frac=0.62):
    """Figure on the left, takeaway bullets on the right."""
    s = add_slide()
    header(s, title, number)
    fw = Emu(int((SW - Inches(1.0)) * fig_frac))
    add_picture_fit(s, f"{FIGS}/{fig}", Inches(0.5), Inches(1.15), fw,
                    SH - Inches(1.65))
    bx = Inches(0.7) + fw
    lines = []
    for b in bullets:
        lines.append((b, 14, False, SLATE, 0, 10))
    textbox(s, bx, Inches(1.3), SW - bx - Inches(0.5), SH - Inches(1.8),
            lines)
    return s


# ---------------- Slide 1: title ----------------
s = add_slide()
rect(s, 0, 0, SW, SH, NAVY)
add_picture_fit(s, f"{FIGS}/fig1-global-chaos-map.png",
                Inches(0.9), Inches(3.6), SW - Inches(1.8), Inches(3.3))
textbox(s, Inches(0.9), Inches(0.9), SW - Inches(1.8), Inches(2.6), [
    ("Is Europa's \u201cchaos\u201d one geologic feature type \u2014 or several lumped together?", 36, True, WHITE, None, 14),
    ("Quantitative morphometrics of 2,643 mapped blocks, 20 block-mapped regions, and 114 global chaos polygons, plus literature synthesis", 18, False, ACCENT, None, 8),
    ("November 2026", 14, False, RGBColor(0x9F, 0xB3, 0xC8), None, 0),
])

# ---------------- Slide 2: answer up front ----------------
s = add_slide()
header(s, "The answer up front", "2")
textbox(s, Inches(0.6), Inches(1.15), SW - Inches(1.2), Inches(1.0), [
    ("Mostly one family \u2014 with a small number of genuine impostors.", 22, True, BLUE, None, 0),
])
textbox(s, Inches(0.6), Inches(2.0), SW - Inches(1.2), Inches(5.2), [
    ("Every quantitative test points the same way: canonical chaos forms a **single continuous morphological spectrum**, not discrete sub-populations.", 16, False, SLATE, 0, 12),
    ("Platy\u2192knobby block-size-distribution slope across 20 regions is **unimodal** (dip test p = 0.19; 1-component GMM beats 2 by BIC).", 16, False, SLATE, 0, 12),
    ("\u201cPlates\u201d and \u201cknobs\u201d are the large and small tails of **one log-normal block-size continuum**.", 16, False, SLATE, 0, 12),
    ("USGS map units chh / chl / chm are **indistinguishable in planform shape** (Kruskal\u2013Wallis p = 0.07\u20130.77) \u2014 they track radiation and sulfur implantation (hemisphere), not formation mechanism.", 16, False, SLATE, 0, 12),
    ("Microchaos (5\u201375 km) \u2192 regional chaos \u2192 giant units (>1,000 km): a **size hierarchy with no natural break**.", 16, False, SLATE, 0, 12),
    ("But a short list of look-alikes is probably **mechanistically distinct**: Murias Chaos (extrusive mega-diapir), Moytura Chaos (unique chM unit), and candidate impact-breach sites.", 16, False, SLATE, 0, 0),
])

# ---------------- Slide 3: data ----------------
s = add_slide()
header(s, "Data", "3")
rows = [
    ("Leonard et al. (2022) \u2014 Zenodo 12775125",
     "9 chaos terrain outlines (247 arc segments, reconstructed to closed polygons, areas match published to \u22640.9%) + 1,910 block polygons. Includes Conamara (TH_cc) and Murias (LH_E)."),
    ("Mills (2023) \u2014 Zenodo 10162452",
     "737 block polygons with knob/plate labels in 11 lower-RegMap regions (F\u2013I, ee\u2013kk)."),
    ("USGS SIM 3513 (Leonard, Patthoff & Senske 2024)",
     "Global geologic map GIS: 114 chaos polygons (chh / chl / chm / chM), 2,313 microchaos points, 500-m global mosaic basemap."),
    ("Dunn et al. (2023, NeurIPS ML4PS)",
     "Region metadata: plate/knob counts, areas, and centers for all 20 block-mapped regions."),
]
y = Inches(1.3)
for name, desc in rows:
    textbox(s, Inches(0.6), y, Inches(4.5), Inches(1.2),
            [(name, 15, True, BLUE, None, 0)])
    textbox(s, Inches(5.3), y, Inches(7.4), Inches(1.2),
            [(desc, 14, False, SLATE, None, 0)])
    y += Inches(1.3)
textbox(s, Inches(0.6), y + Inches(0.1), Inches(12.1), Inches(0.5), [
    ("All vector data on the Europa 2000 sphere (R = 1,562.09 km); all areas geodesic.", 13, False, GRAY, None, 0)])

# ---------------- Slide 4: methods ----------------
s = add_slide()
header(s, "Methods", "4")
textbox(s, Inches(0.6), Inches(1.3), SW - Inches(1.2), Inches(5.6), [
    ("**Morphometrics** \u2014 each polygon projected to a local Lambert azimuthal equal-area frame; geodesic area, perimeter, circularity (4\u03c0A/P\u00b2), solidity, aspect ratio, effective diameter, centroid.", 16, False, SLATE, 0, 14),
    ("**Block size-frequency distributions** \u2014 per region, ln(cumulative fractional block area above length scale x = \u221aarea) fit linearly; slope m is the platy (\u2248 \u22120.2) to knobby (\u2248 \u22121.2) metric. Re-derived slopes match Leonard et al. to ~0.07 km\u207b\u00b9; same procedure applied to the 11 Mills regions.", 16, False, SLATE, 0, 14),
    ("**Statistics** \u2014 Hartigan dip tests, 1D/4D Gaussian mixtures with BIC, k-means and Ward clustering with silhouettes, PCA, Kruskal\u2013Wallis / Mann\u2013Whitney / KS / \u03c7\u00b2 / Spearman.", 16, False, SLATE, 0, 14),
    ("**Cross-referencing** \u2014 each of the 20 block-mapped regions located in its containing SIM 3513 unit polygon; microchaos points spatially joined to units.", 16, False, SLATE, 0, 0),
])

# ---------------- Slides 5-10: figures ----------------
fig_slide("Global context: chaos covers ~40% of Europa", "5",
          "fig1-global-chaos-map.png", [
    "114 chaos polygons of USGS SIM 3513 over the 500-m global mosaic; 20 block-mapped regions marked.",
    "chl dominates the anti-Jovian hemisphere, chh the sub-Jovian \u2014 a pattern the mappers attribute to radiation processing and Iogenic sulfur implantation.",
    "**Exogenic overprint, not formation mechanism.**",
], fig_frac=0.66)

fig_slide("No planform separation among the map units", "6",
          "fig2-sim3513-morphometrics.png", [
    "Across 114 chaos polygons, chh / chl / chm do not differ in log-area (p = 0.068), circularity (p = 0.77), solidity (p = 0.45) or aspect (p = 0.35).",
    "Sizes form one log-normal-like continuum over 10\u00b2\u201310\u2076 km\u00b2 (dip p = 0.96).",
    "Only latitude is marginally distinct (p = 0.039) \u2014 geographic, not morphological.",
], fig_frac=0.62)

fig_slide("Clustering finds no natural sub-populations", "7",
          "fig3-clustering.png", [
    "GMM prefers k = 3 by BIC, but structure is weak: silhouettes peak at 0.41 (genuine clusters need \u2265 0.5); no deep gap in the Ward dendrogram.",
    "PCA shows one elongated cloud; dominant axis is the trivial size\u2013shape covariance.",
    "Statistical clusters are **independent of the geologic map classes** (\u03c7\u00b2 p = 0.57).",
], fig_frac=0.62)

fig_slide("The platy\u2013knobby axis is a continuum (n = 20)", "8",
          "fig4-platy-knobby-continuum.png", [
    "Slopes run continuously from \u22120.22 (platy) to \u22121.20 (knobby); unimodal (dip p = 0.19).",
    "No latitude correlation (\u03c1 = 0.03) \u2014 Leonard et al.'s sampling-artifact suspicion confirmed.",
    "Bigger chaos is platier (\u03c1 = 0.59, p = 0.006): a scale-dependence one mechanism predicts naturally.",
    "Conamara, the canonical type example, is the **least typical** region (4% knobs vs \u2265 43% elsewhere).",
], fig_frac=0.60)

fig_slide("Endmembers look different but connect continuously", "9",
          "fig5-endmember-closeups.png", [
    "Conamara (platy: rafts with preserved ridged-plains texture) vs Murias / LH_D (knobby: small rounded knobs, little texture).",
    "Regions like I, hh, gg populate every intermediate state; the SFD slope orders them all on one axis.",
], fig_frac=0.66)

fig_slide("Microchaos: the small end, not a separate species", "10",
          "fig6-microchaos.png", [
    "2,313 microchaos points (5\u201375 km), 95% in regional plains; same latitude distribution as chaos units (KS p = 0.34).",
    "The map itself invokes \u201cincomplete coalescence of microchaos\u201d as the origin of chm mottling.",
    "Consistent with one production process: small expressions = lenticulae-scale microchaos, large coalesced expressions = regional chaos.",
], fig_frac=0.62)

# ---------------- Slide 11: mechanisms ----------------
s = add_slide()
header(s, "Mechanisms vs. the observed continuum", "11")
mech = [
    ("Melt-through of the shell", "Carr 1998; Greenberg 1999",
     "Disfavored as the general mechanism (topography, pit/uplift morphometrics, thermodynamics) \u2014 but its descriptive core survives inside the sill/lens models."),
    ("Diapirism / solid-state convection", "Pappalardo 1998; Nimmo & Manga 2002",
     "Explains elevated/domed features and lenticula spacing; needs partial melt or brine to make true blocky chaos."),
    ("Brine mobilization", "Head & Pappalardo 1999; Fagents 2003",
     "A bridge between diapirism and melt lenses; favored for Thrace-type features."),
    ("Perched water / sill collapse", "Schmidt 2011; Michaut & Manga 2014",
     "**Best current fit**: naturally produces a continuum from microchaos (small sills) to giant chaos (large lenses); Thera Macula possibly active today."),
    ("Impact breach", "Cox 2008; Cox & Bauer 2015",
     "Plausible for individual features (Tyre, Callanish transitional); cannot produce 40% of the surface."),
]
y = Inches(1.2)
for name, refs, status in mech:
    textbox(s, Inches(0.6), y, Inches(3.3), Inches(1.0),
            [(name, 14, True, BLUE, None, 2), (refs, 11, False, GRAY, None, 0)])
    textbox(s, Inches(4.1), y, Inches(8.7), Inches(1.0),
            [(status, 13, False, SLATE, None, 0)])
    y += Inches(1.08)
textbox(s, Inches(0.6), y + Inches(0.05), Inches(12.1), Inches(0.6), [
    ("Collins & Nimmo (2009): the constraint list requires one mechanism with internal degrees of freedom (lens depth/size, melt fraction, maturity) \u2014 not two or more mechanisms.", 13, True, SLATE, None, 0)])

# ---------------- Slide 12: impostors ----------------
s = add_slide()
header(s, "The genuine impostors", "12")
imp = [
    ("Murias Chaos (\u201cthe Mitten\u201d, LH_E)",
     "Elevated, with flow lobes extending tens of km over the plains. Figueredo et al. (2002): \u201cdistinct from typical chaos terrain\u201d \u2014 the surface extrusion of a rare, large thermal diapir, effectively cryovolcanic. Sits at the knobby extreme (97% knobs) but its topographic signature is what sets it apart."),
    ("Moytura Chaos (chM)",
     "The USGS global map gives it its own unit: smooth material standing high, broken by curvilinear depressions, found at exactly one place on Europa. Flagged by the mappers as \u201ca unique morphology of chaos.\u201d"),
    ("Candidate impact-origin chaos",
     "Km-scale impactors must occasionally breach the shell, and breach sites should look like raft-filled chaos (Cox & Bauer 2015); Tyre and Callanish are transitional. Some individual patches may be impact scars \u2014 the global population cannot be."),
]
y = Inches(1.3)
for name, desc in imp:
    textbox(s, Inches(0.6), y, Inches(3.6), Inches(1.6),
            [(name, 16, True, BLUE, None, 0)])
    textbox(s, Inches(4.4), y, Inches(8.4), Inches(1.6),
            [(desc, 14, False, SLATE, None, 0)])
    y += Inches(1.85)

# ---------------- Slide 13: caveats ----------------
s = add_slide()
header(s, "Caveats", "13")
textbox(s, Inches(0.6), Inches(1.3), SW - Inches(1.2), Inches(5.6), [
    ("**Coverage / resolution bias** \u2014 only ~15% of Europa imaged at \u2264 250 m/px; the 20 regions sit in two longitude corridors. A real sub-population could hide in unimaged terrain.", 16, False, SLATE, 0, 13),
    ("**Small n** \u2014 20 regions limits power for region-level tests; marginal signals (knob fraction vs SIM unit p = 0.052, leading vs trailing p = 0.058) worth revisiting with Europa Clipper EIS (> 80% coverage at < 100 m/px).", 16, False, SLATE, 0, 13),
    ("**Planform \u2260 topography** \u2014 the known-distinct features (Murias, Moytura) distinguish themselves in elevation, which 2-D morphometrics cannot capture; stereo DEMs / Clipper altimetry are the natural next discriminator.", 16, False, SLATE, 0, 13),
    ("**Outline reconstruction** \u2014 the nine Leonard outlines were reassembled from unclosed arcs (validated to \u2264 0.9% in area).", 16, False, SLATE, 0, 13),
    ("**Area conventions** \u2014 published region areas are planar-equirectangular; ours are geodesic. Comparisons account for this.", 16, False, SLATE, 0, 0),
])

# ---------------- Slide 14: bottom line ----------------
s = add_slide()
rect(s, 0, 0, SW, SH, NAVY)
textbox(s, Inches(0.9), Inches(0.9), SW - Inches(1.8), Inches(0.8),
        [("Bottom line", 30, True, WHITE, None, 0)])
textbox(s, Inches(0.9), Inches(1.9), SW - Inches(1.8), Inches(4.9), [
    ("The core chaos population is **one genetic family** expressed along continuous axes:", 19, False, WHITE, None, 12),
    ("size (microchaos \u2192 Conamara-scale \u2192 giant chm/chl fields)", 17, False, ACCENT, 0, 8),
    ("fragmentation energy (platy \u2192 knobby)", 17, False, ACCENT, 0, 8),
    ("maturity (active Thera \u2192 refrozen Conamara \u2192 degraded low-albedo chaos)", 17, False, ACCENT, 0, 8),
    ("exogenic surface state (chh / chl brightness classes)", 17, False, ACCENT, 0, 16),
    ("Platy vs knobby and high- vs low-albedo are **coordinates, not categories**. The real mislabeling is narrow: a handful of elevated, extrusive features (Murias, Moytura) and possibly a few impact-breach scars carry the \u201cchaos\u201d name while their formation physics is likely different.", 18, False, WHITE, None, 14),
    ("Europa Clipper's global imaging and topography should make that short list definitive.", 18, True, WHITE, None, 0),
])

prs.save(OUT)
print("saved", OUT, os.path.getsize(OUT), "bytes,", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
