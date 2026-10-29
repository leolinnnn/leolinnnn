"""Portable runner for the original Bang Na interface and regression functions."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.interface_analysis import (
    area_aggregate, cluster_robust_point_model, correlations, fit_area_model,
    robustness_models, type_descriptives, type_tests,
)

HERE = Path(__file__).resolve().parent


def validate_points(points):
    if len(points) != 289 or points.candidate_id.isna().any() or points.candidate_id.duplicated().any():
        raise ValueError("Expected 289 distinct street-view sampling points")
    if points.area_id.nunique() != 25 or points.interface_openness.notna().sum() != 267:
        raise ValueError("Expected 25 areas and 267 valid interface observations")
    for col in ["setback", "visual_permeability", "vehicle_occupation"]:
        if not points[col].dropna().between(0, 2).all():
            raise ValueError(f"Out-of-range interface component: {col}")
    computed = 100 * (points.setback + points.visual_permeability + 2 - points.vehicle_occupation) / 6
    np.testing.assert_allclose(points.interface_openness, computed, atol=1e-10, equal_nan=True)


def compare_reference(actual, filename, keys):
    expected = pd.read_csv(HERE / "reference" / filename).set_index(keys).sort_index()
    observed = actual.set_index(keys).sort_index()
    pd.testing.assert_index_equal(observed.index, expected.index)
    for column in expected.select_dtypes(include="number"):
        np.testing.assert_allclose(observed[column], expected[column], rtol=1e-8, atol=1e-9,
                                   equal_nan=True, err_msg=f"Archived result mismatch: {filename}/{column}")


def main():
    parser = argparse.ArgumentParser(description="Reproduce Bang Na area models, robustness and clustered point model.")
    parser.add_argument("--output", type=Path, required=True, help="New directory for generated tables")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output already exists; choose a new directory")
    points = pd.read_csv(HERE / "data" / "interface-points.csv")
    validate_points(points)
    areas = area_aggregate(points)
    fits = [fit_area_model(areas, "M2_replication", None),
            fit_area_model(areas, "M2-I", "interface_openness_mean")]
    outputs = dict(zip(
        ["model_summary", "model_coefficients_hc3", "model_vif", "model_predictions"],
        [pd.concat([f[i] for f in fits], ignore_index=True) for i in range(4)]))
    outputs["robustness_summary"], outputs["robustness_coefficients"] = robustness_models(points, areas)
    outputs["point_model_summary"], outputs["point_model_cluster_coefficients"] = cluster_robust_point_model(points)
    for name in ["model_summary", "model_coefficients_hc3", "robustness_summary", "robustness_coefficients",
                 "point_model_summary", "point_model_cluster_coefficients"]:
        keys = ["model_id", "term"] if "coefficients" in name else ["model_id"]
        compare_reference(outputs[name], name + ".csv", keys)
    outputs["type_kruskal_wallis"], outputs["type_dunn_bh"] = type_tests(areas)
    outputs["interface_gvi_correlations"] = correlations(areas)
    outputs["type_descriptives"] = type_descriptives(areas)
    outputs["area_summary"] = areas
    io = outputs["model_coefficients_hc3"].query("model_id == 'M2-I' and term == 'z_interface_openness_mean'").iloc[0]
    summary = {
        "status": "PASS", "areas": len(areas), "gvi_points": len(points), "valid_interface_points": 267,
        "area_models_checked": 9, "clustered_point_models_checked": 1,
        "adjusted_r2": dict(zip(outputs["model_summary"].model_id, outputs["model_summary"].adj_r2)),
        "io_coefficient_pctpt_per_sd": io.estimate_pctpt,
        "io_hc3_ci95": [io.ci95_low_hc3, io.ci95_high_hc3],
        "verification": "All numeric fields in six archived model/coefficients tables match within 1e-8 relative / 1e-9 absolute tolerance."
    }
    args.output.mkdir(parents=True)
    for name, frame in outputs.items():
        frame.to_csv(args.output / (name + ".csv"), index=False)
    (args.output / "verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
