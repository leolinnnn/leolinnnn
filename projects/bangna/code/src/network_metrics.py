"""Research functions from calculate_bangna_road_space_variables.py. See ../PROVENANCE.md."""

from __future__ import annotations

import math
from typing import Any



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
