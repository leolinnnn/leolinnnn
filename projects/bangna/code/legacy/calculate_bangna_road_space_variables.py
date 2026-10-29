from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import networkx as nx
import pandas as pd


ROOT = Path.cwd()
OSM_DIR = ROOT / "data" / "bangna_osm"
GVI_DIR = ROOT / "data" / "gvi_deeplab_cityscapes"
TYPOLOGY_GEOJSON = ROOT / "data" / "qgis_typology" / "bangna_residential_typology_export.geojson"
SAMPLING_CSV = ROOT / "data" / "gsv_sampling" / "bangna_gsv_sampling_candidates.csv"
ROADS_GEOJSON = OSM_DIR / "bangna_road_edges_1300m.geojson"
GRAPHML = OSM_DIR / "bangna_walk_network_1300m.graphml"
STATION_GEOJSON = OSM_DIR / "bts_bang_na_station.geojson"
GVI_POINT_CSV = GVI_DIR / "bangna_gvi_point_results_deeplab_cityscapes.csv"
GVI_AREA_CSV = GVI_DIR / "bangna_gvi_area_results_deeplab_cityscapes.csv"

OUT_DIR = ROOT / "data" / "road_variables"
POINT_ROAD_CSV = OUT_DIR / "bangna_road_space_variables_points.csv"
AREA_ROAD_CSV = OUT_DIR / "bangna_road_space_variables_areas.csv"
POINT_ANALYSIS_CSV = OUT_DIR / "bangna_point_gvi_road_variables_for_mapping.csv"
AREA_ANALYSIS_CSV = OUT_DIR / "bangna_area_gvi_road_variables_for_analysis.csv"
POINT_GEOJSON = OUT_DIR / "bangna_point_gvi_road_variables.geojson"
SUMMARY_JSON = OUT_DIR / "road_space_variables_summary.json"
README = OUT_DIR / "README.md"

BUFFER_RADII_M = [100, 200]
MAJOR_ROADS = {"trunk", "primary", "secondary"}
LOCAL_ROADS = {"tertiary", "residential", "living_street", "unclassified"}
SERVICE_OR_PATH = {"service", "footway", "steps", "path", "pedestrian", "track", "cycleway"}
WALKABLE_ROADS = LOCAL_ROADS | SERVICE_OR_PATH
ROAD_HIERARCHY_SCORE = {
    "motorway": 6.0,
    "trunk": 5.0,
    "primary": 4.5,
    "secondary": 4.0,
    "tertiary": 3.0,
    "residential": 2.0,
    "living_street": 2.0,
    "unclassified": 2.0,
    "service": 1.0,
    "pedestrian": 1.0,
    "footway": 0.5,
    "steps": 0.3,
    "path": 0.5,
    "track": 0.5,
    "cycleway": 0.5,
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


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


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371008.8
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def point_segment_distance_m(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    qx = ax + t * dx
    qy = ay + t * dy
    return math.hypot(px - qx, py - qy)


def segment_circle_inside_length(
    ax: float,
    ay: float,
    bx: float,
    by: float,
    cx: float,
    cy: float,
    radius_m: float,
) -> float:
    dx = bx - ax
    dy = by - ay
    seg_len = math.hypot(dx, dy)
    if seg_len == 0:
        return 0.0

    fx = ax - cx
    fy = ay - cy
    a = dx * dx + dy * dy
    b = 2 * (fx * dx + fy * dy)
    c = fx * fx + fy * fy - radius_m * radius_m
    disc = b * b - 4 * a * c

    def inside(t: float) -> bool:
        x = ax + t * dx
        y = ay + t * dy
        return (x - cx) ** 2 + (y - cy) ** 2 <= radius_m * radius_m

    intervals = []
    if disc < 0:
        if inside(0.5):
            intervals.append((0.0, 1.0))
    else:
        s = math.sqrt(max(0.0, disc))
        t1 = (-b - s) / (2 * a)
        t2 = (-b + s) / (2 * a)
        cuts = [0.0, 1.0, max(0.0, min(1.0, t1)), max(0.0, min(1.0, t2))]
        cuts = sorted(set(round(t, 12) for t in cuts))
        for lo, hi in zip(cuts[:-1], cuts[1:]):
            if hi <= lo:
                continue
            mid = (lo + hi) / 2
            if inside(mid):
                intervals.append((lo, hi))
    return sum((hi - lo) * seg_len for lo, hi in intervals)


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


def polygon_centroid(parts: list[list[list[tuple[float, float]]]]) -> tuple[float, float]:
    xs = []
    ys = []
    for poly in parts:
        for ring in poly[:1]:
            for x, y in ring:
                xs.append(x)
                ys.append(y)
    return (sum(xs) / len(xs), sum(ys) / len(ys))


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


def line_coords(geometry: dict[str, Any]) -> list[list[list[float]]]:
    if geometry["type"] == "LineString":
        return [geometry["coordinates"]]
    if geometry["type"] == "MultiLineString":
        return geometry["coordinates"]
    return []


def road_class(highway: str) -> str:
    highway = str(highway)
    if highway in MAJOR_ROADS:
        return "major"
    if highway in LOCAL_ROADS:
        return "local"
    if highway in SERVICE_OR_PATH:
        return "service_or_path"
    return "other"


def load_road_segments(project) -> list[dict[str, Any]]:
    roads = load_json(ROADS_GEOJSON)
    segments: list[dict[str, Any]] = []
    for feature in roads["features"]:
        props = feature.get("properties") or {}
        highway = str(props.get("highway", ""))
        osmid = str(props.get("osmid", ""))
        name = props.get("name:en") or props.get("name") or props.get("alt_name:en") or ""
        for line in line_coords(feature["geometry"]):
            for a, b in zip(line[:-1], line[1:]):
                ax, ay = project(a[0], a[1])
                bx, by = project(b[0], b[1])
                length = math.hypot(bx - ax, by - ay)
                if length == 0:
                    continue
                segments.append(
                    {
                        "osmid": osmid,
                        "name": name,
                        "highway": highway,
                        "road_class": road_class(highway),
                        "hierarchy_score": ROAD_HIERARCHY_SCORE.get(highway, 1.0),
                        "ax": ax,
                        "ay": ay,
                        "bx": bx,
                        "by": by,
                        "mid_x": (ax + bx) / 2,
                        "mid_y": (ay + by) / 2,
                        "length_m": length,
                    }
                )
    return segments


def load_polygons(project) -> dict[str, dict[str, Any]]:
    data = load_json(TYPOLOGY_GEOJSON)
    out = {}
    for feature in data["features"]:
        props = feature.get("properties") or {}
        area_id = str(props.get("area_id", ""))
        parts = geometry_parts_projected(feature["geometry"], project)
        cx, cy = polygon_centroid(parts)
        out[area_id] = {
            "area_id": area_id,
            "res_type": props.get("res_type", ""),
            "type_name": props.get("type_name", ""),
            "confidence": props.get("confidence", ""),
            "parts": parts,
            "area_m2": polygon_area_m2(parts),
            "centroid_x": cx,
            "centroid_y": cy,
        }
    return out


def load_graph(project) -> tuple[nx.Graph, dict[str, tuple[float, float]]]:
    raw = nx.read_graphml(GRAPHML)
    graph = nx.Graph()
    coords = {}
    for node, attrs in raw.nodes(data=True):
        lat = float(attrs["lat"])
        lon = float(attrs["lon"])
        x, y = project(lon, lat)
        graph.add_node(node)
        coords[node] = (x, y)
    for u, v, attrs in raw.edges(data=True):
        length = float(attrs.get("length_m", 0) or 0)
        if graph.has_edge(u, v):
            if length < graph[u][v]["length_m"]:
                graph[u][v].update(length_m=length, highway=attrs.get("highway", ""), name=attrs.get("name", ""))
        else:
            graph.add_edge(u, v, length_m=length, highway=attrs.get("highway", ""), name=attrs.get("name", ""))
    return graph, coords


def nearest_node(x: float, y: float, coords: dict[str, tuple[float, float]]) -> tuple[str, float]:
    best_node = ""
    best_dist = float("inf")
    for node, (nx_, ny_) in coords.items():
        d = math.hypot(x - nx_, y - ny_)
        if d < best_dist:
            best_dist = d
            best_node = node
    return best_node, best_dist


def nearest_reachable_node(
    x: float,
    y: float,
    coords: dict[str, tuple[float, float]],
    reachable_nodes: set[str],
) -> tuple[str, float]:
    best_node = ""
    best_dist = float("inf")
    for node in reachable_nodes:
        nx_, ny_ = coords[node]
        d = math.hypot(x - nx_, y - ny_)
        if d < best_dist:
            best_dist = d
            best_node = node
    return best_node, best_dist


def nearest_road(x: float, y: float, segments: list[dict[str, Any]]) -> dict[str, Any]:
    best = None
    best_dist = float("inf")
    for seg in segments:
        d = point_segment_distance_m(x, y, seg["ax"], seg["ay"], seg["bx"], seg["by"])
        if d < best_dist:
            best_dist = d
            best = seg
    assert best is not None
    return {
        "nearest_road_osmid": best["osmid"],
        "nearest_road_name": best["name"],
        "nearest_road_highway": best["highway"],
        "nearest_road_class": best["road_class"],
        "nearest_road_hierarchy_score": best["hierarchy_score"],
        "nearest_road_distance_m": best_dist,
    }


def nearest_major_road_distance(x: float, y: float, segments: list[dict[str, Any]]) -> float:
    distances = [
        point_segment_distance_m(x, y, seg["ax"], seg["ay"], seg["bx"], seg["by"])
        for seg in segments
        if seg["road_class"] == "major"
    ]
    return min(distances) if distances else float("nan")


def buffer_road_context(x: float, y: float, radius_m: float, segments: list[dict[str, Any]], node_points: list[dict[str, Any]]) -> dict[str, Any]:
    context = {
        f"road_length_{int(radius_m)}m_m": 0.0,
        f"major_road_length_{int(radius_m)}m_m": 0.0,
        f"local_road_length_{int(radius_m)}m_m": 0.0,
        f"service_path_length_{int(radius_m)}m_m": 0.0,
        f"weighted_road_hierarchy_{int(radius_m)}m": 0.0,
    }
    weighted_sum = 0.0
    for seg in segments:
        inside_len = segment_circle_inside_length(seg["ax"], seg["ay"], seg["bx"], seg["by"], x, y, radius_m)
        if inside_len <= 0:
            continue
        context[f"road_length_{int(radius_m)}m_m"] += inside_len
        weighted_sum += inside_len * seg["hierarchy_score"]
        if seg["road_class"] == "major":
            context[f"major_road_length_{int(radius_m)}m_m"] += inside_len
        elif seg["road_class"] == "local":
            context[f"local_road_length_{int(radius_m)}m_m"] += inside_len
        elif seg["road_class"] == "service_or_path":
            context[f"service_path_length_{int(radius_m)}m_m"] += inside_len

    road_len = context[f"road_length_{int(radius_m)}m_m"]
    area_ha = math.pi * radius_m * radius_m / 10000
    context[f"road_density_{int(radius_m)}m_m_per_ha"] = road_len / area_ha
    context[f"major_road_share_{int(radius_m)}m"] = context[f"major_road_length_{int(radius_m)}m_m"] / road_len if road_len else 0.0
    context[f"local_road_share_{int(radius_m)}m"] = context[f"local_road_length_{int(radius_m)}m_m"] / road_len if road_len else 0.0
    context[f"service_path_share_{int(radius_m)}m"] = context[f"service_path_length_{int(radius_m)}m_m"] / road_len if road_len else 0.0
    context[f"weighted_road_hierarchy_{int(radius_m)}m"] = weighted_sum / road_len if road_len else float("nan")

    nodes_in = 0
    intersections_in = 0
    for node in node_points:
        if math.hypot(node["x"] - x, node["y"] - y) <= radius_m:
            nodes_in += 1
            if node["degree"] >= 3:
                intersections_in += 1
    context[f"node_count_{int(radius_m)}m"] = nodes_in
    context[f"intersection_count_{int(radius_m)}m"] = intersections_in
    context[f"intersection_density_{int(radius_m)}m_per_ha"] = intersections_in / area_ha
    return context


def approximate_segment_length_in_polygon(seg: dict[str, Any], parts: list[list[list[tuple[float, float]]]], step_m: float = 10.0) -> float:
    n = max(1, int(math.ceil(seg["length_m"] / step_m)))
    inside = 0
    for i in range(n):
        t = (i + 0.5) / n
        x = seg["ax"] + (seg["bx"] - seg["ax"]) * t
        y = seg["ay"] + (seg["by"] - seg["ay"]) * t
        if point_in_polygon_parts(x, y, parts):
            inside += 1
    return seg["length_m"] * inside / n


def area_road_metrics(
    area: dict[str, Any],
    segments: list[dict[str, Any]],
    node_points: list[dict[str, Any]],
    station_x: float,
    station_y: float,
    graph: nx.Graph,
    graph_coords: dict[str, tuple[float, float]],
    station_distances: dict[str, float],
) -> dict[str, Any]:
    parts = area["parts"]
    area_m2 = area["area_m2"]
    area_ha = area_m2 / 10000 if area_m2 else float("nan")
    road_length = 0.0
    major_length = 0.0
    local_length = 0.0
    service_length = 0.0
    hierarchy_weighted = 0.0
    for seg in segments:
        inside_len = approximate_segment_length_in_polygon(seg, parts)
        if inside_len <= 0:
            continue
        road_length += inside_len
        hierarchy_weighted += inside_len * seg["hierarchy_score"]
        if seg["road_class"] == "major":
            major_length += inside_len
        elif seg["road_class"] == "local":
            local_length += inside_len
        elif seg["road_class"] == "service_or_path":
            service_length += inside_len

    node_count = 0
    intersection_count = 0
    for node in node_points:
        if point_in_polygon_parts(node["x"], node["y"], parts):
            node_count += 1
            if node["degree"] >= 3:
                intersection_count += 1

    centroid_x = area["centroid_x"]
    centroid_y = area["centroid_y"]
    centroid_node, centroid_node_dist = nearest_node(centroid_x, centroid_y, graph_coords)
    reachable_nodes = set(station_distances.keys())
    routing_node, routing_node_dist = nearest_reachable_node(centroid_x, centroid_y, graph_coords, reachable_nodes)
    network_dist = station_distances.get(routing_node, float("nan")) + routing_node_dist
    return {
        "area_id": area["area_id"],
        "res_type": area["res_type"],
        "type_name": area["type_name"],
        "confidence": area["confidence"],
        "polygon_area_m2": area_m2,
        "polygon_area_ha": area_ha,
        "centroid_euclidean_dist_to_bts_m": math.hypot(centroid_x - station_x, centroid_y - station_y),
        "centroid_nearest_graph_node": centroid_node,
        "centroid_distance_to_nearest_graph_node_m": centroid_node_dist,
        "centroid_routing_graph_node": routing_node,
        "centroid_distance_to_routing_graph_node_m": routing_node_dist,
        "centroid_network_distance_status": "ok_nearest" if routing_node == centroid_node else "ok_reachable_fallback",
        "centroid_network_dist_to_bts_m": network_dist,
        "road_length_in_polygon_m": road_length,
        "road_density_in_polygon_m_per_ha": road_length / area_ha if area_ha else float("nan"),
        "major_road_length_in_polygon_m": major_length,
        "local_road_length_in_polygon_m": local_length,
        "service_path_length_in_polygon_m": service_length,
        "major_road_share_in_polygon": major_length / road_length if road_length else 0.0,
        "local_road_share_in_polygon": local_length / road_length if road_length else 0.0,
        "service_path_share_in_polygon": service_length / road_length if road_length else 0.0,
        "weighted_road_hierarchy_in_polygon": hierarchy_weighted / road_length if road_length else float("nan"),
        "node_count_in_polygon": node_count,
        "intersection_count_in_polygon": intersection_count,
        "intersection_density_in_polygon_per_ha": intersection_count / area_ha if area_ha else float("nan"),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    station_feature = load_json(STATION_GEOJSON)["features"][0]
    station_lon, station_lat = station_feature["geometry"]["coordinates"]
    gvi_points = pd.read_csv(GVI_POINT_CSV)
    lat0 = float(pd.concat([gvi_points["lat"], pd.Series([station_lat])]).mean())
    project = make_projector(lat0)
    station_x, station_y = project(station_lon, station_lat)

    segments = load_road_segments(project)
    polygons = load_polygons(project)
    graph, graph_coords = load_graph(project)
    station_node, station_node_dist = nearest_node(station_x, station_y, graph_coords)
    station_distances = nx.single_source_dijkstra_path_length(graph, station_node, weight="length_m")
    reachable_nodes = set(station_distances.keys())

    node_points = []
    degrees = dict(graph.degree())
    for node, (x, y) in graph_coords.items():
        node_points.append({"node": node, "x": x, "y": y, "degree": degrees.get(node, 0)})

    sampling = pd.read_csv(SAMPLING_CSV)
    sampling_cols = [
        "candidate_id",
        "match_method",
        "distance_to_polygon_m",
        "road_osmid",
        "road_name",
        "highway",
        "gsv_priority",
    ]
    points = gvi_points.merge(sampling[sampling_cols], on="candidate_id", how="left", suffixes=("", "_sample"))

    point_rows: list[dict[str, Any]] = []
    for _, row in points.iterrows():
        x, y = project(float(row["lon"]), float(row["lat"]))
        node, node_dist = nearest_node(x, y, graph_coords)
        routing_node, routing_node_dist = nearest_reachable_node(x, y, graph_coords, reachable_nodes)
        network_dist = station_distances.get(routing_node, float("nan")) + routing_node_dist
        nearest = nearest_road(x, y, segments)
        out: dict[str, Any] = {
            "candidate_id": row["candidate_id"],
            "area_id": row["area_id"],
            "res_type": row["res_type"],
            "type_name": row["type_name"],
            "lat": row["lat"],
            "lon": row["lon"],
            "gvi_vegetation_scene": row["gvi_vegetation_scene"],
            "gvi_vegetation_full": row["gvi_vegetation_full"],
            "pano_date": row.get("pano_date", ""),
            "match_method": row.get("match_method", ""),
            "sample_highway": row.get("highway", ""),
            "sample_gsv_priority": row.get("gsv_priority", ""),
            "euclidean_dist_to_bts_m": math.hypot(x - station_x, y - station_y),
            "nearest_graph_node": node,
            "distance_to_nearest_graph_node_m": node_dist,
            "routing_graph_node": routing_node,
            "distance_to_routing_graph_node_m": routing_node_dist,
            "network_dist_to_bts_m": network_dist,
            "network_distance_status": "ok_nearest" if routing_node == node else "ok_reachable_fallback",
            "nearest_major_road_dist_m": nearest_major_road_distance(x, y, segments),
        }
        out.update(nearest)
        for radius in BUFFER_RADII_M:
            out.update(buffer_road_context(x, y, radius, segments, node_points))
        point_rows.append(out)

    write_csv(POINT_ROAD_CSV, point_rows)
    point_analysis = pd.DataFrame(point_rows)
    point_analysis.to_csv(POINT_ANALYSIS_CSV, index=False, encoding="utf-8-sig")

    area_rows = [
        area_road_metrics(area, segments, node_points, station_x, station_y, graph, graph_coords, station_distances)
        for _, area in sorted(polygons.items())
    ]
    write_csv(AREA_ROAD_CSV, area_rows)

    area_road = pd.DataFrame(area_rows)
    area_gvi = pd.read_csv(GVI_AREA_CSV)
    area_analysis = area_gvi.merge(area_road, on=["area_id", "res_type", "type_name"], how="left", suffixes=("", "_road"))
    area_analysis.to_csv(AREA_ANALYSIS_CSV, index=False, encoding="utf-8-sig")

    # Point GeoJSON for QGIS.
    features = []
    for row in point_rows:
        props = {k: (None if pd.isna(v) else v) for k, v in row.items() if k not in {"lat", "lon"}}
        features.append(
            {
                "type": "Feature",
                "properties": props,
                "geometry": {"type": "Point", "coordinates": [float(row["lon"]), float(row["lat"])]},
            }
        )
    POINT_GEOJSON.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "name": "bangna_point_gvi_road_variables",
                "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                "features": features,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    summary = {
        "station_lat": station_lat,
        "station_lon": station_lon,
        "station_nearest_graph_node": station_node,
        "station_distance_to_graph_node_m": station_node_dist,
        "road_segment_count": len(segments),
        "graph_node_count": len(graph.nodes),
        "graph_edge_count": len(graph.edges),
        "point_count": len(point_rows),
        "area_count_all_typology": len(area_rows),
        "area_count_with_gvi": int(area_analysis["gvi_vegetation_scene_mean"].notna().sum())
        if "gvi_vegetation_scene_mean" in area_analysis.columns
        else len(area_analysis),
        "buffer_radii_m": BUFFER_RADII_M,
        "point_road_variables_csv": str(POINT_ROAD_CSV),
        "area_road_variables_csv": str(AREA_ROAD_CSV),
        "area_analysis_csv": str(AREA_ANALYSIS_CSV),
        "point_geojson": str(POINT_GEOJSON),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    README.write_text(
        "\n".join(
            [
                "# Bang Na Road Space Variables",
                "",
                "本目录保存第七步道路空间变量结果。变量主要来自 OSM 道路网络、BTS Bang Na 站点位置、GVI 有效采样点和住宅片区边界。",
                "",
                "## 已自动获取/计算的变量",
                "",
                "- 点到 BTS Bang Na 的欧氏距离与步行网络距离。",
                "- 最近道路的 OSM 道路等级、道路名称、道路层级评分。",
                "- 100 m 与 200 m 缓冲区内道路长度、道路密度、主干路比例、地方路比例、服务/步行路比例。",
                "- 100 m 与 200 m 缓冲区内路网节点数、交叉口数和交叉口密度。",
                "- 住宅片区内道路长度、道路密度、主干路比例、交叉口密度和片区质心到站距离。",
                "",
                "## 主要输出",
                "",
                "- `bangna_road_space_variables_points.csv`：点级道路变量。",
                "- `bangna_road_space_variables_areas.csv`：片区级道路变量。",
                "- `bangna_area_gvi_road_variables_for_analysis.csv`：片区 GVI 与道路变量合并表，建议用于相关分析。",
                "- `bangna_point_gvi_road_variables_for_mapping.csv`：点级 GVI 与道路变量合并表。",
                "- `bangna_point_gvi_road_variables.geojson/gpkg`：QGIS 制图图层。",
                "",
                "说明：本阶段仅保留可由 OSM 路网、采样点和住宅片区边界稳定计算的变量；道路宽度、车道数、建筑退界、围墙连续性等人工判读变量已从流程中删除。",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
