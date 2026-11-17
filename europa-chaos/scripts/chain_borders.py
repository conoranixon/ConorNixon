"""Chain the Leonard et al. ChaosBorders arc segments into closed polygons.

Endpoints of consecutive arcs meet within ~0.01 deg; cluster endpoints with a
union-find at TOL deg, walk the resulting multigraph into cycles, and build a
polygon per cycle (force-closing any residual gap with a chord).
"""
import numpy as np
import geopandas as gpd
import warnings
from shapely.geometry import Polygon
from shapely.validation import make_valid
from scipy.spatial import cKDTree

warnings.filterwarnings('ignore')
TOL = 0.12  # deg


def main():
    b = gpd.read_file('/tmp/europa/zenodo/borders/ChaosBorders.shp')
    # drop exact duplicate geometries
    keep, seen = [], []
    for i, g in enumerate(b.geometry):
        if any(g.equals(s) for s in seen):
            continue
        seen.append(g)
        keep.append(i)
    lines = [np.array(b.geometry.iloc[i].coords) for i in keep]
    print(f"{len(lines)} unique lines")

    # cluster endpoints (union-find)
    pts = np.array([c for ln in lines for c in (ln[0], ln[-1])])
    parent = list(range(len(pts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, c):
        parent[find(a)] = find(c)

    tree = cKDTree(pts)
    for a, c in tree.query_pairs(TOL):
        union(a, c)
    node = [find(k) for k in range(len(pts))]

    # multigraph: line i connects node[2i] -- node[2i+1]
    incident = {}
    for i in range(len(lines)):
        for n in (node[2 * i], node[2 * i + 1]):
            incident.setdefault(n, set()).add(i)

    used = set()
    polys = []
    for start in range(len(lines)):
        if start in used:
            continue
        chain = [lines[start]]
        used.add(start)
        start_node, cur = node[2 * start], node[2 * start + 1]
        while cur != start_node:
            cand = [j for j in incident.get(cur, ()) if j not in used]
            if not cand:
                break
            # pick candidate whose endpoint is closest to current chain end
            tail = chain[-1][-1]
            best, bj, brev = None, None, False
            for j in cand:
                for rev, end in ((False, lines[j][0]), (True, lines[j][-1])):
                    d = np.hypot(*(end - tail))
                    if best is None or d < best:
                        best, bj, brev = d, j, rev
            seg = lines[bj][::-1] if brev else lines[bj]
            chain.append(seg)
            used.add(bj)
            cur = node[2 * bj] if brev else node[2 * bj + 1]
        coords = np.vstack(chain)
        if len(coords) < 4:
            continue
        p = Polygon(coords)
        if not p.is_valid:
            p = make_valid(p)
            parts = [q for q in getattr(p, 'geoms', [p]) if q.geom_type == 'Polygon']
            if not parts:
                continue
            p = max(parts, key=lambda q: q.area)
        polys.append((len(chain), p))

    print(f"{len(polys)} polygons (from chains of lengths "
          f"{np.bincount([n for n, _ in polys]).tolist()})")
    gdf = gpd.GeoDataFrame({'n_arcs': [n for n, _ in polys]},
                           geometry=[p for _, p in polys], crs=b.crs)
    # drop polygons nested inside / duplicating another (keep larger)
    drop = set()
    sidx = gdf.sindex
    for i in range(len(gdf)):
        gi = gdf.geometry.iloc[i]
        for j in sidx.intersection(gi.bounds):
            j = int(j)
            if j <= i or j in drop or i in drop:
                continue
            gj = gdf.geometry.iloc[j]
            inter = gi.intersection(gj).area
            if inter > 0.8 * min(gi.area, gj.area):
                drop.add(i if gi.area < gj.area else j)
    print("dropping", len(drop), "near-duplicate/nested")
    gdf = gdf.drop(gdf.index[list(drop)]).reset_index(drop=True)
    gdf.to_file('/tmp/europa/work/chaos_polys_leonard.geojson', driver='GeoJSON')
    print("final:", len(gdf), "chaos polygons saved")


if __name__ == '__main__':
    main()
