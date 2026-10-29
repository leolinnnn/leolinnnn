"""Research functions from calculate_bangna_functional_variables.py. See ../PROVENANCE.md."""

from __future__ import annotations

import math
from typing import Any

MAIN_CATEGORIES = ["food_beverage", "retail", "education", "health", "public_service",
    "recreation_tourism", "transit", "auto_mobility", "office_production", "other_amenity"]
COMMERCIAL_CATEGORIES = {"food_beverage", "retail", "office_production"}
DAILY_SERVICE_CATEGORIES = {"food_beverage", "retail", "education", "health", "public_service"}

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
