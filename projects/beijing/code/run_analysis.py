"""Portable entry point added for this repository; calculations use archived functions."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.spatial_statistics import GVI_COL, NDVI_COLS, block_bootstrap, moran_global, type_labels

HERE = Path(__file__).resolve().parent
SEED = 20260913


def validate_input(table):
    if len(table) != 13943 or table.segment_id.isna().any() or table.segment_id.duplicated().any():
        raise ValueError("Expected 13,943 distinct fixed paired roads")
    columns = [GVI_COL, *NDVI_COLS, "centroid_x_m", "centroid_y_m"]
    if not np.isfinite(table[columns].to_numpy(float)).all():
        raise ValueError("Input contains missing or non-finite values")
    if not table[GVI_COL].between(0, 1).all() or not table[NDVI_COLS].map(lambda x: -1 <= x <= 1).all().all():
        raise ValueError("GVI or NDVI outside its measurement range")


def compare_reference(actual, filename, keys):
    expected = pd.read_csv(HERE / "reference" / filename).set_index(keys).sort_index()
    observed = actual.set_index(keys).sort_index()
    pd.testing.assert_index_equal(observed.index, expected.index)
    for column in expected.select_dtypes(include="number"):
        np.testing.assert_allclose(observed[column], expected[column], rtol=1e-9, atol=1e-10,
                                   err_msg=f"Archived result mismatch: {filename}/{column}")


def main():
    parser = argparse.ArgumentParser(description="Recompute Beijing spatial uncertainty from 13,943 fixed roads.")
    parser.add_argument("--output", type=Path, required=True, help="New directory for generated tables")
    parser.add_argument("--skip-moran", action="store_true", help="Omit the 999-permutation spatial diagnostic")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new directory")
    roads = pd.read_csv(HERE / "data" / "roads.csv")
    validate_input(roads)
    frames = []
    for grid in (2000, 1000, 4000):
        frame, _ = block_bootstrap(roads, grid, 4999, SEED)
        frames.append(frame)
    bootstrap = pd.concat(frames, ignore_index=True)
    compare_reference(bootstrap, "block_bootstrap_ci.csv", ["grid_m", "statistic"])
    rank_gvi = roads[GVI_COL].rank(method="average", pct=True)
    types = pd.DataFrame({"segment_id": roads.segment_id})
    for radius in (30, 50, 100):
        ndvi = roads[f"ndvi_{radius}m"]
        types[f"type_{radius}m"] = np.char.add(
            np.where(roads[GVI_COL] >= roads[GVI_COL].median(), "H", "L"),
            np.where(ndvi >= ndvi.median(), "H", "L"))
    types["type_p40p60_100m"] = type_labels(roads[GVI_COL].to_numpy(), roads.ndvi_100m.to_numpy(), .4, .6)
    moran = None
    if not args.skip_moran:
        discordance = rank_gvi - roads.ndvi_100m.rank(method="average", pct=True)
        moran = moran_global(discordance.to_numpy(), roads[["centroid_x_m", "centroid_y_m"]].to_numpy(),
                             [8, 4, 12], 999, SEED)
        compare_reference(moran, "moran_rank_discordance.csv", ["knn_k"])
    summary = {
        "status": "PASS", "roads": len(roads), "seed": SEED,
        "bootstrap_replicates_per_grid": 4999, "grids_m": [2000, 1000, 4000],
        "discordant_roads_100m": int(types.type_100m.isin(["HL", "LH"]).sum()),
        "category_changes_30_to_100m": int((types.type_30m != types.type_100m).sum()),
        "moran_checked": moran is not None,
        "verification": "All computed bootstrap and requested Moran numeric fields match archived results within 1e-9 relative / 1e-10 absolute tolerance."
    }
    if summary["discordant_roads_100m"] != 5400 or summary["category_changes_30_to_100m"] != 2810:
        raise AssertionError("Classification counts differ from archived results")
    args.output.mkdir(parents=True)
    bootstrap.to_csv(args.output / "block_bootstrap_ci.csv", index=False)
    types.to_csv(args.output / "road_categories.csv", index=False)
    if moran is not None:
        moran.to_csv(args.output / "moran_rank_discordance.csv", index=False)
    (args.output / "verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
