from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any

import mxnet as mx
import numpy as np
import pandas as pd
from gluoncv.data.transforms.presets.segmentation import test_transform
from gluoncv.utils.viz import get_color_pallete
from PIL import Image


ROOT = Path.cwd()
INPUT_MANIFEST = ROOT / "data" / "gsv_images" / "bangna_gvi_image_input_manifest.csv"
VALID_POINTS_GEOJSON = ROOT / "data" / "gsv_images" / "bangna_gvi_valid_points.geojson"
OUT_DIR = ROOT / "data" / "gvi_deeplab_cityscapes"
QA_DIR = OUT_DIR / "qa_overlays"

IMAGE_RESULTS = OUT_DIR / "bangna_gvi_image_results_deeplab_cityscapes.csv"
POINT_RESULTS = OUT_DIR / "bangna_gvi_point_results_deeplab_cityscapes.csv"
AREA_RESULTS = OUT_DIR / "bangna_gvi_area_results_deeplab_cityscapes.csv"
TYPE_RESULTS = OUT_DIR / "bangna_gvi_type_results_deeplab_cityscapes.csv"
POINTS_GEOJSON = OUT_DIR / "bangna_gvi_points_with_values.geojson"
SUMMARY_JSON = OUT_DIR / "bangna_gvi_summary.json"
README = OUT_DIR / "README.md"

MODEL_NAME = "deeplab_resnet101_citys"
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


def choose_context(ctx_arg: str) -> mx.context.Context:
    if ctx_arg == "cpu":
        return mx.cpu()
    if ctx_arg.startswith("gpu"):
        gpu_id = int(ctx_arg.replace("gpu", "") or "0")
        return mx.gpu(gpu_id)
    if mx.context.num_gpus() > 0:
        return mx.gpu(0)
    return mx.cpu()


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


def load_existing_results(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def segment_image(model: Any, path: Path, ctx: mx.context.Context) -> np.ndarray:
    with Image.open(path) as pil_img:
        rgb = np.array(pil_img.convert("RGB"))
    img = mx.nd.array(rgb)
    transformed = test_transform(img, ctx=ctx)
    output = model.predict(transformed)
    pred = mx.nd.squeeze(mx.nd.argmax(output, 1)).asnumpy().astype(np.uint8)
    return pred


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


def make_overlay(image_path: Path, mask: np.ndarray, out_path: Path, alpha: float = 0.55) -> None:
    base = Image.open(image_path).convert("RGB").resize((mask.shape[1], mask.shape[0]))
    palette = get_color_pallete(mask, "citys").convert("RGB")
    overlay = Image.blend(base, palette, alpha)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    overlay.save(out_path, "JPEG", quality=92)


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


def write_points_geojson(point_df: pd.DataFrame) -> None:
    if not VALID_POINTS_GEOJSON.exists():
        return
    source = json.loads(VALID_POINTS_GEOJSON.read_text(encoding="utf-8"))
    lookup = {row["candidate_id"]: row for row in point_df.to_dict("records")}
    features = []
    for feature in source.get("features", []):
        props = feature.get("properties") or {}
        candidate_id = props.get("candidate_id")
        if candidate_id not in lookup:
            continue
        merged = dict(props)
        for key, value in lookup[candidate_id].items():
            if pd.isna(value):
                value = None
            merged[key] = value
        feature["properties"] = merged
        features.append(feature)
    out = {
        "type": "FeatureCollection",
        "name": "bangna_gvi_points_with_values",
        "crs": source.get("crs"),
        "features": features,
    }
    POINTS_GEOJSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def write_readme(args: argparse.Namespace, summary: dict[str, Any]) -> None:
    README.write_text(
        "\n".join(
            [
                "# Bang Na GVI: DeepLab Cityscapes",
                "",
                "本目录保存基于 GluonCV `deeplab_resnet101_citys` 的街景绿视率计算结果。",
                "",
                "## 主指标",
                "",
                "- `gvi_vegetation_scene`：Cityscapes `vegetation` 类像素占比，去除图像底部 40 px 水印区域后计算。",
                "- `gvi_vegetation_full`：同一指标，但使用完整 640x640 图像。",
                "- `gvi_vegetation_terrain_scene`：`vegetation + terrain`，作为可能包含草地/裸地的敏感性指标。",
                "",
                "## 输出文件",
                "",
                "- `bangna_gvi_image_results_deeplab_cityscapes.csv`：每张街景图像的语义类别比例与 GVI。",
                "- `bangna_gvi_point_results_deeplab_cityscapes.csv`：每个采样点四方向平均 GVI。",
                "- `bangna_gvi_area_results_deeplab_cityscapes.csv`：每个住宅片区的 GVI 汇总。",
                "- `bangna_gvi_type_results_deeplab_cityscapes.csv`：四类住宅的 GVI 汇总；统计单位为住宅片区。",
                "- `bangna_gvi_points_with_values.geojson/gpkg`：可在 QGIS 中制图的点级 GVI。",
                "- `qa_overlays/`：少量分割叠加图，用于人工核验。",
                "",
                "## 本次运行",
                "",
                f"- 模型：`{MODEL_NAME}`",
                f"- 上下文：`{summary.get('context')}`",
                f"- 输入图像：`{summary.get('input_image_count')}`",
                f"- 已计算图像：`{summary.get('image_result_count')}`",
                f"- 点级样本：`{summary.get('point_count')}`",
                f"- 片区样本：`{summary.get('area_count')}`",
                f"- 底部忽略像素：`{args.ignore_bottom_px}`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    global OUT_DIR, QA_DIR, IMAGE_RESULTS, POINT_RESULTS, AREA_RESULTS, TYPE_RESULTS, POINTS_GEOJSON, SUMMARY_JSON, README

    parser = argparse.ArgumentParser(description="Calculate Bang Na GVI with DeepLab ResNet101 Cityscapes.")
    parser.add_argument("--input", type=Path, default=INPUT_MANIFEST)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--ctx", default="auto", choices=["auto", "cpu", "gpu0"])
    parser.add_argument("--ignore-bottom-px", type=int, default=40)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--max-new-images", type=int, default=None, help="Process at most N images not already present in the result CSV.")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--flush-every", type=int, default=20)
    parser.add_argument("--qa-overlays-per-type", type=int, default=2)
    args = parser.parse_args()

    OUT_DIR = args.out_dir
    QA_DIR = OUT_DIR / "qa_overlays"
    IMAGE_RESULTS = OUT_DIR / "bangna_gvi_image_results_deeplab_cityscapes.csv"
    POINT_RESULTS = OUT_DIR / "bangna_gvi_point_results_deeplab_cityscapes.csv"
    AREA_RESULTS = OUT_DIR / "bangna_gvi_area_results_deeplab_cityscapes.csv"
    TYPE_RESULTS = OUT_DIR / "bangna_gvi_type_results_deeplab_cityscapes.csv"
    POINTS_GEOJSON = OUT_DIR / "bangna_gvi_points_with_values.geojson"
    SUMMARY_JSON = OUT_DIR / "bangna_gvi_summary.json"
    README = OUT_DIR / "README.md"

    if not args.input.exists():
        print(f"Missing input manifest: {args.input}", file=sys.stderr)
        return 2

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(args.input)
    if args.limit:
        manifest = manifest.head(args.limit)

    existing_rows = [] if args.force else load_existing_results(IMAGE_RESULTS)
    completed_ids = {row["image_id"] for row in existing_rows}
    rows = existing_rows[:]

    ctx = choose_context(args.ctx)
    print(f"loading model {MODEL_NAME} on {ctx}")
    from gluoncv import model_zoo

    model = model_zoo.get_model(MODEL_NAME, ctx=ctx, pretrained=True)

    qa_counts: dict[str, int] = {}
    start = time.time()
    fieldnames: list[str] | None = None
    pending = manifest[~manifest["image_id"].isin(completed_ids)].copy()
    if args.max_new_images is not None:
        pending = pending.head(args.max_new_images)
    print(f"input images: {len(manifest)}")
    print(f"already completed: {len(completed_ids)}")
    print(f"to process: {len(pending)}")

    for idx, (_, item) in enumerate(pending.iterrows(), start=1):
        image_path = Path(item["processed_abspath"])
        image_id = item["image_id"]
        if not image_path.exists():
            print(f"missing image: {image_path}", file=sys.stderr)
            continue

        mask = segment_image(model, image_path, ctx)
        ratios = ratios_for_mask(mask, args.ignore_bottom_px)

        row = item.to_dict()
        row.update(ratios)
        row["model_name"] = MODEL_NAME
        row["context"] = str(ctx)
        rows.append(row)
        if fieldnames is None:
            fieldnames = list(row.keys())

        res_type = str(item["res_type"])
        qa_counts.setdefault(res_type, 0)
        if qa_counts[res_type] < args.qa_overlays_per_type:
            overlay_path = QA_DIR / res_type / f"{image_id}_overlay.jpg"
            make_overlay(image_path, mask, overlay_path)
            qa_counts[res_type] += 1

        if idx % args.flush_every == 0:
            write_csv(IMAGE_RESULTS, sorted(rows, key=lambda r: r["image_id"]), fieldnames)
            elapsed = time.time() - start
            print(f"processed {idx}/{len(pending)} new images; total rows {len(rows)}; elapsed {elapsed:.1f}s")

    if rows:
        if fieldnames is None:
            fieldnames = list(rows[0].keys())
        write_csv(IMAGE_RESULTS, sorted(rows, key=lambda r: r["image_id"]), fieldnames)

    image_df = pd.read_csv(IMAGE_RESULTS)
    point_df, area_df, type_df = aggregate_results(image_df)
    point_df.to_csv(POINT_RESULTS, index=False, encoding="utf-8-sig")
    area_df.to_csv(AREA_RESULTS, index=False, encoding="utf-8-sig")
    type_df.to_csv(TYPE_RESULTS, index=False, encoding="utf-8-sig")
    write_points_geojson(point_df)

    summary = {
        "model_name": MODEL_NAME,
        "context": str(ctx),
        "input_manifest": str(args.input),
        "input_image_count": int(len(manifest)),
        "image_result_count": int(len(image_df)),
        "point_count": int(len(point_df)),
        "area_count": int(len(area_df)),
        "type_count": int(len(type_df)),
        "ignore_bottom_px": int(args.ignore_bottom_px),
        "main_metric": "gvi_vegetation_scene",
        "qa_overlay_count": int(sum(qa_counts.values())),
        "image_results": str(IMAGE_RESULTS),
        "point_results": str(POINT_RESULTS),
        "area_results": str(AREA_RESULTS),
        "type_results": str(TYPE_RESULTS),
        "points_geojson": str(POINTS_GEOJSON),
    }
    SUMMARY_JSON.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_readme(args, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
