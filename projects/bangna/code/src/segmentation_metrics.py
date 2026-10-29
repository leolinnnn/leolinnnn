"""Research functions from calculate_bangna_gvi_deeplab_cityscapes.py. See ../PROVENANCE.md."""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd

CITYSCAPES_CLASSES = {
    0: "road",
    1: "sidewalk",
    2: "building",
    3: "wall",
    4: "fence",
    5: "pole",
    6: "traffic_light",
    7: "traffic_sign",
    8: "vegetation",
    9: "terrain",
    10: "sky",
    11: "person",
    12: "rider",
    13: "car",
    14: "truck",
    15: "bus",
    16: "train",
    17: "motorcycle",
    18: "bicycle",
}

def ratios_for_mask(mask: np.ndarray, ignore_bottom_px: int) -> dict[str, Any]:
    h, w = mask.shape
    full_pixels = int(h * w)
    scene_h = max(1, h - ignore_bottom_px)
    scene_mask = mask[:scene_h, :]
    scene_pixels = int(scene_mask.size)

    out: dict[str, Any] = {
        "mask_width": int(w),
        "mask_height": int(h),
        "full_pixel_count": full_pixels,
        "scene_pixel_count": scene_pixels,
        "ignore_bottom_px": int(ignore_bottom_px),
    }

    for class_id, class_name in CITYSCAPES_CLASSES.items():
        full_count = int((mask == class_id).sum())
        scene_count = int((scene_mask == class_id).sum())
        out[f"{class_name}_full"] = full_count / full_pixels
        out[f"{class_name}_scene"] = scene_count / scene_pixels

    out["gvi_vegetation_full"] = out["vegetation_full"]
    out["gvi_vegetation_scene"] = out["vegetation_scene"]
    out["gvi_vegetation_terrain_full"] = out["vegetation_full"] + out["terrain_full"]
    out["gvi_vegetation_terrain_scene"] = out["vegetation_scene"] + out["terrain_scene"]
    return out


def metric_summary(series: pd.Series, prefix: str) -> dict[str, Any]:
    return {
        f"{prefix}_mean": series.mean(),
        f"{prefix}_median": series.median(),
        f"{prefix}_std": series.std(ddof=1) if len(series) > 1 else 0.0,
        f"{prefix}_min": series.min(),
        f"{prefix}_max": series.max(),
    }


def aggregate_results(image_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    metric_cols = [
        "gvi_vegetation_full",
        "gvi_vegetation_scene",
        "gvi_vegetation_terrain_full",
        "gvi_vegetation_terrain_scene",
        "vegetation_scene",
        "terrain_scene",
        "sky_scene",
        "building_scene",
        "road_scene",
        "sidewalk_scene",
    ]

    point_rows: list[dict[str, Any]] = []
    for candidate_id, group in image_df.groupby("candidate_id", sort=True):
        first = group.iloc[0]
        row: dict[str, Any] = {
            "candidate_id": candidate_id,
            "area_id": first["area_id"],
            "res_type": first["res_type"],
            "type_name": first["type_name"],
            "lat": first["lat"],
            "lon": first["lon"],
            "pano_id": first.get("pano_id", ""),
            "pano_date": first.get("pano_date", ""),
            "n_images": len(group),
            "headings": ",".join(str(int(v)) for v in sorted(group["heading"].astype(int).tolist())),
        }
        for col in metric_cols:
            row[col] = group[col].astype(float).mean()
        point_rows.append(row)
    point_df = pd.DataFrame(point_rows)

    area_rows: list[dict[str, Any]] = []
    for area_id, group in point_df.groupby("area_id", sort=True):
        first = group.iloc[0]
        row = {
            "area_id": area_id,
            "res_type": first["res_type"],
            "type_name": first["type_name"],
            "n_points": len(group),
            "n_images": int(group["n_images"].sum()),
        }
        for col in metric_cols[:4]:
            row.update(metric_summary(group[col].astype(float), col))
        area_rows.append(row)
    area_df = pd.DataFrame(area_rows)

    type_rows: list[dict[str, Any]] = []
    for res_type, group in area_df.groupby("res_type", sort=True):
        first = group.iloc[0]
        row = {
            "res_type": res_type,
            "type_name": first["type_name"],
            "n_areas": len(group),
            "n_points": int(group["n_points"].sum()),
            "n_images": int(group["n_images"].sum()),
        }
        # Main inferential unit is area_id, so type summaries average area-level means.
        for col in metric_cols[:4]:
            area_mean_col = f"{col}_mean"
            row.update(metric_summary(group[area_mean_col].astype(float), area_mean_col))
        type_rows.append(row)
    type_df = pd.DataFrame(type_rows)
    return point_df, area_df, type_df
