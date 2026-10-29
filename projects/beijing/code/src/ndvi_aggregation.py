"""Research functions from pair_native_ndvi_roads.py. See ../PROVENANCE.md."""

from __future__ import annotations

import math
import numpy as np
import shapely



def summarize_polygon(polygon, data: dict, gt: tuple, width: int, height: int,
                      variants: tuple[str, ...]) -> dict:
    out = {name: (np.nan, 0.0, 0) for name in variants}
    area = float(polygon.area)
    if polygon.is_empty or area <= 0:
        return {**{name: out[name] for name in variants}, "area_m2": 0.0, "intersecting_pixels": 0}
    col0 = max(0, math.floor((polygon.bounds[0] - gt[0]) / gt[1]))
    col1 = min(width, math.ceil((polygon.bounds[2] - gt[0]) / gt[1]))
    row0 = max(0, math.floor((gt[3] - polygon.bounds[3]) / -gt[5]))
    row1 = min(height, math.ceil((gt[3] - polygon.bounds[1]) / -gt[5]))
    if col1 <= col0 or row1 <= row0:
        return {**{name: out[name] for name in variants}, "area_m2": area, "intersecting_pixels": 0}
    rr, cc = np.meshgrid(np.arange(row0, row1), np.arange(col0, col1), indexing="ij")
    left = gt[0] + cc.ravel() * gt[1]
    top = gt[3] + rr.ravel() * gt[5]
    cells = shapely.box(left, top + gt[5], left + gt[1], top)
    overlap = shapely.area(shapely.intersection(cells, polygon))
    intersecting = overlap > 0
    if not np.any(intersecting):
        return {**{name: out[name] for name in variants}, "area_m2": area, "intersecting_pixels": 0}
    result = {"area_m2": area, "intersecting_pixels": int(intersecting.sum())}
    for name in variants:
        values = data[name][row0:row1, col0:col1].ravel()
        valid = intersecting & np.isfinite(values)
        valid_area = float(overlap[valid].sum())
        if valid_area > area * 1.000001:
            raise AssertionError("Valid pixel area exceeds clipped road-buffer area")
        mean = (float(np.dot(values[valid], overlap[valid]) / valid_area)
                if valid_area > 0 else np.nan)
        result[name] = (mean, min(valid_area / area, 1.0), int(valid.sum()))
    return result
