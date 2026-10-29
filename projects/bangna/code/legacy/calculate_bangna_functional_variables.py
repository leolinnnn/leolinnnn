from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path.cwd()
FUNCTIONAL_DIR = ROOT / "data" / "functional_osm"
GVI_DIR = ROOT / "data" / "gvi_deeplab_cityscapes"
TYPOLOGY_GEOJSON = ROOT / "data" / "qgis_typology" / "bangna_residential_typology_export.geojson"
FEATURES_CSV = FUNCTIONAL_DIR / "bangna_osm_functional_features_1800m.csv"
GVI_POINT_CSV = GVI_DIR / "bangna_gvi_point_results_deeplab_cityscapes.csv"
GVI_AREA_CSV = GVI_DIR / "bangna_gvi_area_results_deeplab_cityscapes.csv"

OUT_DIR = ROOT / "data" / "functional_variables"
POINT_FUNCTION_CSV = OUT_DIR / "bangna_functional_variables_points.csv"
AREA_FUNCTION_CSV = OUT_DIR / "bangna_functional_variables_areas.csv"
POINT_ANALYSIS_CSV = OUT_DIR / "bangna_point_gvi_functional_variables_for_mapping.csv"
AREA_ANALYSIS_CSV = OUT_DIR / "bangna_area_gvi_functional_variables_for_analysis.csv"
POINT_GEOJSON = OUT_DIR / "bangna_point_gvi_functional_variables.geojson"
SUMMARY_JSON = OUT_DIR / "functional_variables_summary.json"
README = OUT_DIR / "README.md"

BUFFER_RADII_M = [200, 400]
MAIN_CATEGORIES = [
    "food_beverage",
    "retail",
    "education",
    "health",
    "public_service",
    "recreation_tourism",
    "transit",
    "auto_mobility",
    "office_production",
    "other_amenity",
]
COMMERCIAL_CATEGORIES = {"food_beverage", "retail", "office_production"}
DAILY_SERVICE_CATEGORIES = {"food_beverage", "retail", "education", "health", "public_service"}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows and not fieldnames:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def make_projector(lat0: float):
    radius = 6371008.8
    cos0 = math.cos(math.radians(lat0))

    def project(lon: float, lat: float) -> tuple[float, float]:
        return (math.radians(lon) * radius * cos0, math.radians(lat) * radius)

    return project


def point_in_ring(x: float, y: float, ring: list[tuple[float, float]]) -> bool:
    inside = False
    j = len(ring) - 1
    for i, (xi, yi) in enumerate(ring):
        xj, yj = ring[j]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def point_in_polygon_parts(x: float, y: float, parts: list[list[list[tuple[float, float]]]]) -> bool:
    for poly in parts:
        if not poly:
            continue
        if not point_in_ring(x, y, poly[0]):
            continue
        if any(point_in_ring(x, y, hole) for hole in poly[1:]):
            continue
        return True
    return False


def ring_area_m2(ring: list[tuple[float, float]]) -> float:
    area = 0.0
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        area += x1 * y2 - x2 * y1
    return abs(area) / 2


def polygon_area_m2(parts: list[list[list[tuple[float, float]]]]) -> float:
    total = 0.0
    for poly in parts:
        if not poly:
            continue
        total += ring_area_m2(poly[0])
        for hole in poly[1:]:
            total -= ring_area_m2(hole)
    return max(0.0, total)


def geometry_parts_projected(geometry: dict[str, Any], project) -> list[list[list[tuple[float, float]]]]:
    if geometry["type"] == "Polygon":
        coords = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        coords = geometry["coordinates"]
    else:
        return []
    parts = []
    for poly in coords:
        rings = []
        for ring in poly:
            rings.append([project(lon, lat) for lon, lat in ring])
        parts.append(rings)
    return parts


def load_polygons(project) -> dict[str, dict[str, Any]]:
    data = json.loads(TYPOLOGY_GEOJSON.read_text(encoding="utf-8"))
    out = {}
    for feature in data["features"]:
        props = feature.get("properties") or {}
        area_id = str(props.get("area_id", ""))
        parts = geometry_parts_projected(feature["geometry"], project)
        out[area_id] = {
            "area_id": area_id,
            "res_type": props.get("res_type", ""),
            "type_name": props.get("type_name", ""),
            "parts": parts,
            "area_m2": polygon_area_m2(parts),
        }
    return out


def shannon_evenness(counts: list[int]) -> tuple[float, float, int]:
    total = sum(counts)
    active = sum(1 for c in counts if c > 0)
    if total <= 0 or active <= 1:
        return 0.0, 0.0, active
    entropy = 0.0
    for count in counts:
        if count <= 0:
            continue
        p = count / total
        entropy -= p * math.log(p)
    evenness = entropy / math.log(active)
    return entropy, evenness, active


def nearest_distance(x: float, y: float, pois: list[dict[str, Any]], categories: set[str] | None = None) -> float:
    distances = []
    for poi in pois:
        if categories is not None and poi["functional_category"] not in categories:
            continue
        distances.append(math.hypot(poi["x"] - x, poi["y"] - y))
    return min(distances) if distances else float("nan")


def buffer_function_context(x: float, y: float, radius_m: float, pois: list[dict[str, Any]]) -> dict[str, Any]:
    inside = []
    for poi in pois:
        if math.hypot(poi["x"] - x, poi["y"] - y) <= radius_m:
            inside.append(poi)
    counts = {cat: 0 for cat in MAIN_CATEGORIES}
    for poi in inside:
        category = poi["functional_category"]
        if category in counts:
            counts[category] += 1

    area_ha = math.pi * radius_m * radius_m / 10000
    category_counts = [counts[cat] for cat in MAIN_CATEGORIES]
    entropy, evenness, active_category_count = shannon_evenness(category_counts)
    poi_count = len(inside)
    commercial_count = sum(counts[cat] for cat in COMMERCIAL_CATEGORIES)
    daily_service_count = sum(counts[cat] for cat in DAILY_SERVICE_CATEGORIES)

    prefix = f"{int(radius_m)}m"
    out: dict[str, Any] = {
        f"poi_count_{prefix}": poi_count,
        f"poi_density_{prefix}_per_ha": poi_count / area_ha,
        f"active_poi_category_count_{prefix}": active_category_count,
        f"poi_shannon_{prefix}": entropy,
        f"poi_evenness_{prefix}": evenness,
        f"commercial_poi_count_{prefix}": commercial_count,
        f"commercial_poi_density_{prefix}_per_ha": commercial_count / area_ha,
        f"daily_service_poi_count_{prefix}": daily_service_count,
        f"daily_service_poi_density_{prefix}_per_ha": daily_service_count / area_ha,
    }
    for cat, count in counts.items():
        out[f"{cat}_count_{prefix}"] = count
        out[f"{cat}_density_{prefix}_per_ha"] = count / area_ha
    return out


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    features = pd.read_csv(FEATURES_CSV).fillna("")
    gvi_points = pd.read_csv(GVI_POINT_CSV)
    lat0 = pd.concat([features["lat"], gvi_points["lat"]]).astype(float).mean()
    project = make_projector(lat0)
    polygons = load_polygons(project)

    pois = []
    landuse_features = []
    for _, row in features.iterrows():
        x, y = project(float(row["lon"]), float(row["lat"]))
        item = {
            "feature_id": row["feature_id"],
            "x": x,
            "y": y,
            "lon": float(row["lon"]),
            "lat": float(row["lat"]),
            "feature_role": row["feature_role"],
            "functional_category": row["functional_category"],
            "name": row.get("name", ""),
        }
        if row["feature_role"] == "poi":
            pois.append(item)
        else:
            landuse_features.append(item)

    point_rows: list[dict[str, Any]] = []
    for _, row in gvi_points.iterrows():
        x, y = project(float(row["lon"]), float(row["lat"]))
        out: dict[str, Any] = {
            "candidate_id": row["candidate_id"],
            "area_id": row["area_id"],
            "res_type": row["res_type"],
            "type_name": row["type_name"],
            "lat": row["lat"],
            "lon": row["lon"],
            "gvi_vegetation_scene": row["gvi_vegetation_scene"],
            "nearest_poi_dist_m": nearest_distance(x, y, pois),
            "nearest_food_beverage_dist_m": nearest_distance(x, y, pois, {"food_beverage"}),
            "nearest_retail_dist_m": nearest_distance(x, y, pois, {"retail"}),
            "nearest_transit_dist_m": nearest_distance(x, y, pois, {"transit"}),
            "nearest_public_service_dist_m": nearest_distance(x, y, pois, {"public_service"}),
            "nearest_recreation_tourism_dist_m": nearest_distance(x, y, pois, {"recreation_tourism"}),
        }
        for radius in BUFFER_RADII_M:
            out.update(buffer_function_context(x, y, radius, pois))
        point_rows.append(out)

    write_csv(POINT_FUNCTION_CSV, point_rows)
    pd.DataFrame(point_rows).to_csv(POINT_ANALYSIS_CSV, index=False, encoding="utf-8-sig")

    features_geojson = []
    for row in point_rows:
        props = {k: (None if pd.isna(v) else v) for k, v in row.items() if k not in {"lat", "lon"}}
        features_geojson.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])]},
                "properties": props,
            }
        )
    POINT_GEOJSON.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "name": "bangna_point_gvi_functional_variables",
                "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                "features": features_geojson,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    point_df = pd.DataFrame(point_rows)
    agg_dict: dict[str, tuple[str, str]] = {
        "n_points": ("candidate_id", "count"),
        "nearest_poi_dist_mean_m": ("nearest_poi_dist_m", "mean"),
        "nearest_food_beverage_dist_mean_m": ("nearest_food_beverage_dist_m", "mean"),
        "nearest_retail_dist_mean_m": ("nearest_retail_dist_m", "mean"),
        "nearest_transit_dist_mean_m": ("nearest_transit_dist_m", "mean"),
        "nearest_public_service_dist_mean_m": ("nearest_public_service_dist_m", "mean"),
    }
    for radius in BUFFER_RADII_M:
        prefix = f"{radius}m"
        for col in [
            f"poi_count_{prefix}",
            f"poi_density_{prefix}_per_ha",
            f"active_poi_category_count_{prefix}",
            f"poi_shannon_{prefix}",
            f"poi_evenness_{prefix}",
            f"commercial_poi_count_{prefix}",
            f"commercial_poi_density_{prefix}_per_ha",
            f"daily_service_poi_count_{prefix}",
            f"daily_service_poi_density_{prefix}_per_ha",
            f"food_beverage_count_{prefix}",
            f"retail_count_{prefix}",
            f"transit_count_{prefix}",
            f"recreation_tourism_count_{prefix}",
            f"public_service_count_{prefix}",
        ]:
            agg_dict[f"{col}_mean"] = (col, "mean")

    area_from_points = point_df.groupby(["area_id", "res_type", "type_name"], as_index=False).agg(**agg_dict)

    area_inside_rows = []
    for area_id, area in sorted(polygons.items()):
        parts = area["parts"]
        area_ha = area["area_m2"] / 10000 if area["area_m2"] else float("nan")
        inside = [poi for poi in pois if point_in_polygon_parts(poi["x"], poi["y"], parts)]
        counts = {cat: 0 for cat in MAIN_CATEGORIES}
        for poi in inside:
            category = poi["functional_category"]
            if category in counts:
                counts[category] += 1
        entropy, evenness, active_category_count = shannon_evenness([counts[cat] for cat in MAIN_CATEGORIES])
        row: dict[str, Any] = {
            "area_id": area_id,
            "poi_count_inside_polygon": len(inside),
            "poi_density_inside_polygon_per_ha": len(inside) / area_ha if area_ha else float("nan"),
            "active_poi_category_count_inside_polygon": active_category_count,
            "poi_shannon_inside_polygon": entropy,
            "poi_evenness_inside_polygon": evenness,
        }
        for cat, count in counts.items():
            row[f"{cat}_count_inside_polygon"] = count
            row[f"{cat}_density_inside_polygon_per_ha"] = count / area_ha if area_ha else float("nan")
        area_inside_rows.append(row)

    area_function = area_from_points.merge(pd.DataFrame(area_inside_rows), on="area_id", how="left")
    area_function.to_csv(AREA_FUNCTION_CSV, index=False, encoding="utf-8-sig")

    area_gvi = pd.read_csv(GVI_AREA_CSV)
    area_analysis = area_gvi.merge(
        area_function,
        on=["area_id", "res_type", "type_name"],
        how="left",
        suffixes=("_gvi", "_functional"),
    )
    area_analysis = area_analysis.rename(
        columns={
            "n_points_gvi": "gvi_point_count",
            "n_points_functional": "functional_point_count",
        }
    )
    area_analysis.to_csv(AREA_ANALYSIS_CSV, index=False, encoding="utf-8-sig")

    summary = {
        "poi_count": len(pois),
        "landuse_feature_count": len(landuse_features),
        "point_count": len(point_rows),
        "area_count": len(area_function),
        "buffer_radii_m": BUFFER_RADII_M,
        "point_functional_variables_csv": str(POINT_FUNCTION_CSV),
        "area_functional_variables_csv": str(AREA_FUNCTION_CSV),
        "area_analysis_csv": str(AREA_ANALYSIS_CSV),
        "point_geojson": str(POINT_GEOJSON),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    README.write_text(
        "\n".join(
            [
                "# Bang Na Functional Variables",
                "",
                "本目录保存第 9 步功能变量。数据来自 OpenStreetMap Overpass API，不使用 Google Places API。",
                "",
                "## 主变量",
                "",
                "- 点级 200 m / 400 m POI 数量与密度。",
                "- 点级 POI 功能类别数、Shannon 多样性指数、均匀度。",
                "- 餐饮、零售、公共服务、休闲旅游、交通设施等类别计数与密度。",
                "- 最近 POI、最近餐饮、最近零售、最近公交/轨道设施距离。",
                "- 片区级变量采用点级功能暴露的均值，并补充片区边界内 POI 数。",
                "",
                "## 输出",
                "",
                "- `bangna_functional_variables_points.csv`：点级功能变量。",
                "- `bangna_functional_variables_areas.csv`：片区级功能变量。",
                "- `bangna_area_gvi_functional_variables_for_analysis.csv`：片区 GVI 与功能变量合并表。",
                "- `bangna_point_gvi_functional_variables_for_mapping.csv`：点级 GVI 与功能变量合并表。",
                "- `bangna_point_gvi_functional_variables.geojson/gpkg`：QGIS 点图层。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
