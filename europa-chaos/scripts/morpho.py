"""Compute per-feature morphometrics for Europa chaos polygons.

All polygons are in geographic coords on the Europa 2000 sphere (R = 1562.09 km).
Each feature is projected to a local Lambert azimuthal equal-area projection
centered on its centroid before measuring, so areas/lengths are in true km.
"""
import numpy as np
import geopandas as gpd
import pandas as pd
from shapely.ops import transform as shp_transform
from pyproj import Transformer

R_EUROPA = 1562090.0  # m

def local_laea(lon0, lat0):
    return Transformer.from_crs(
        f"+proj=longlat +R={R_EUROPA} +no_defs",
        f"+proj=laea +lat_0={lat0} +lon_0={lon0} +R={R_EUROPA} +no_defs",
        always_xy=True).transform

def morphometrics(geom):
    """geom: shapely (Multi)Polygon in lon/lat degrees."""
    c = geom.representative_point()
    lon0, lat0 = c.x, c.y
    g = shp_transform(local_laea(lon0, lat0), geom)
    g = g.buffer(0)  # fix slivers
    A = g.area                      # m^2
    P = g.length                    # m (exterior + interior rings)
    hull = g.convex_hull
    rect = g.minimum_rotated_rectangle
    rc = np.array(rect.exterior.coords)
    edges = np.hypot(*(rc[1:] - rc[:-1]).T)
    L, W = max(edges[0], edges[1]), min(edges[0], edges[1])
    n_parts = len(g.geoms) if g.geom_type == 'MultiPolygon' else 1
    if g.geom_type == 'MultiPolygon':
        n_holes = sum(len(p.interiors) for p in g.geoms)
    else:
        n_holes = len(g.interiors)
    A_km2 = A / 1e6
    P_km = P / 1e3
    return dict(
        lon=lon0, lat=lat0,
        area_km2=A_km2, perim_km=P_km,
        circularity=4 * np.pi * A / P**2 if P > 0 else np.nan,
        solidity=A / hull.area if hull.area > 0 else np.nan,
        aspect=L / W if W > 0 else np.nan,
        eff_diam_km=2 * np.sqrt(A_km2 / np.pi),
        shape_complexity=P / (2 * np.sqrt(np.pi * A)) if A > 0 else np.nan,  # 1=circle
        n_parts=n_parts, n_holes=n_holes,
    )

def run(gdf, label):
    rows = []
    for i, row in gdf.iterrows():
        geom = row.geometry
        if geom is None or geom.is_empty:
            continue
        try:
            m = morphometrics(geom)
        except Exception as e:
            print(f"skip {label} {i}: {e}")
            continue
        m['src_index'] = i
        rows.append(m)
    df = pd.DataFrame(rows)
    df['dataset'] = label
    return df

if __name__ == '__main__':
    out = []

    borders = gpd.read_file('/tmp/europa/zenodo/borders/ChaosBorders.shp')
    df_b = run(borders, 'Leonard22_borders')
    out.append(df_b)

    sim = gpd.read_file('/tmp/europa/usgs/sim3513/sim3513_Europa_GIS/shapefiles/GeoUnits_FINAL.shp')
    sim['Geounits'] = sim['Geounits'].replace({'chM': 'chm'})
    chaos_units = sim[sim['Geounits'].isin(['chh', 'chl', 'chm'])].copy()
    df_s = run(chaos_units, 'SIM3513_chaos')
    df_s = df_s.merge(chaos_units[['Geounits']].reset_index().rename(
        columns={'index': 'src_index'}), on='src_index')
    out.append(df_s)

    allf = pd.concat(out, ignore_index=True)
    allf.to_csv('/tmp/europa/work/chaos_morphometrics.csv', index=False)
    print(allf.groupby(['dataset', allf.get('Geounits')], dropna=False)
          [['area_km2', 'circularity', 'solidity', 'aspect']].describe().T.head(40))
    print("\ncounts:", allf.groupby('dataset').size().to_dict())
    print("Geounits:", df_s['Geounits'].value_counts().to_dict())
    print("saved chaos_morphometrics.csv", len(allf))
