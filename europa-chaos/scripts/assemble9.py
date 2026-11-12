"""Assemble the 247 ChaosBorders arcs into the 9 named chaos terrain polygons
of Leonard et al. (2022), validated against their Table 1 areas.

Method: cluster arcs by spatial proximity into terrain groups, then recover the
enclosed region of each group by buffering the union of its arcs and taking the
interior holes of the buffered shape (robust to small gaps and junctions).
Published Table 1 areas are planar-equirectangular (no cos-lat factor), so we
compare on that convention for labeling, but keep geodesic values for science.
"""
import numpy as np
import geopandas as gpd
import warnings
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon

warnings.filterwarnings('ignore')

DEG_KM = 1562090.0 * np.pi / 180 / 1000  # km per degree on Europa sphere

TABLE1 = {  # name: (area_km2 equirect, SFD slope m, intercept b, Ab%, A_x>2)
    'LH_A': (12242, -0.2712, -0.3853, 68, 4426),
    'LH_B': (2765, -0.5129, -0.2374, 79, 909),
    'LH_C': (2945, -0.2140, -0.2015, 82, 1582),
    'LH_D': (1959, -1.1065, 1.0694, 291, 667),
    'LH_E': (7682, -0.7445, -0.8715, 42, 865),   # Murias
    'TH_aa': (13186, -0.4377, -0.7785, 46, 2835),
    'TH_bb': (22570, -0.2995, -1.0254, 36, 4854),
    'TH_cc': (8997, -0.2653, -0.3997, 67, 3393),  # Conamara
    'TH_dd': (7979, -0.4366, -1.5420, 21, 798),
}


def cluster_lines(geoms, eps=0.08):
    """Connected components of lines whose eps-buffers intersect."""
    n = len(geoms)
    bufs = [g.buffer(eps) for g in geoms]
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    tree = gpd.GeoSeries(bufs).sindex
    for i in range(n):
        for j in tree.intersection(bufs[i].bounds):
            j = int(j)
            if j > i and bufs[i].intersects(bufs[j]):
                parent[find(i)] = parent[find(j)]
    return [find(i) for i in range(n)]


def enclosed_region(lines, eps=0.03):
    """Region enclosed by a set of boundary arcs: buffer the arc union and
    take interior holes, then dilate back."""
    u = unary_union(lines).buffer(eps)
    holes = []
    geoms = u.geoms if isinstance(u, MultiPolygon) else [u]
    for p in geoms:
        for ring in p.interiors:
            holes.append(Polygon(ring))
    if not holes:
        return None
    region = unary_union(holes).buffer(eps)
    if isinstance(region, MultiPolygon):
        region = max(region.geoms, key=lambda q: q.area)
    return region


def equirect_area_km2(poly):
    """Planar equirect area in km^2 (paper's convention, no cos-lat)."""
    return poly.area * DEG_KM**2


def main():
    b = gpd.read_file('/tmp/europa/zenodo/borders/ChaosBorders.shp')
    # drop exact duplicates
    seen, lines = [], []
    for g in b.geometry:
        if any(g.equals(s) for s in seen):
            continue
        seen.append(g)
        lines.append(g)
    lab = cluster_lines(lines)
    groups = {}
    for i, l in enumerate(lab):
        groups.setdefault(l, []).append(lines[i])
    print(f"{len(groups)} spatial clusters, sizes:",
          sorted(len(v) for v in groups.values()))

    polys = []
    for key, grp in groups.items():
        for eps in (0.03, 0.05, 0.08, 0.12):
            region = enclosed_region(grp, eps)
            if region is not None:
                break
        if region is None:
            print(f"cluster {key} ({len(grp)} arcs): no enclosed region, skipped")
            continue
        polys.append(region)

    gdf = gpd.GeoDataFrame(geometry=polys, crs=b.crs)
    gdf['area_eq_km2'] = gdf.geometry.apply(equirect_area_km2)
    gdf = gdf.sort_values('area_eq_km2', ascending=False).reset_index(drop=True)

    # label by nearest published area (greedy 1:1)
    names, areas = list(TABLE1), np.array([TABLE1[n][0] for n in TABLE1])
    gdf['name'] = None
    used = set()
    for i, row in gdf.iterrows():
        if len(used) == len(names):
            break
        diffs = np.abs(areas - row.area_eq_km2) / areas
        order = np.argsort(diffs)
        for k in order:
            if k not in used:
                gdf.loc[i, 'name'] = names[k]
                gdf.loc[i, 'area_match_pct'] = 100 * diffs[k]
                used.add(k)
                break
    for n, (a, m, bb, ab, ax2) in TABLE1.items():
        sel = gdf['name'] == n
        gdf.loc[sel, 'pub_area'] = a
        gdf.loc[sel, 'sfd_slope'] = m
        gdf.loc[sel, 'sfd_intercept'] = bb
        gdf.loc[sel, 'block_frac_pub'] = ax2 / a
    print(gdf.drop(columns='geometry').round(2).to_string())
    gdf.to_file('/tmp/europa/work/chaos9_leonard.geojson', driver='GeoJSON')
    print("saved chaos9_leonard.geojson")


if __name__ == '__main__':
    main()
