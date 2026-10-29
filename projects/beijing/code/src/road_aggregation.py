"""Research functions from build_existing_gvi_osm.py. See ../PROVENANCE.md."""

from __future__ import annotations

import pandas as pd



def assert_unique(frame: pd.DataFrame, key: str, label: str) -> None:
    if frame[key].isna().any() or frame[key].duplicated().any():
        raise AssertionError(f"{label}: {key} must be unique and non-null")


def choose_unique_content(requests: pd.DataFrame, threshold_m: float) -> tuple[pd.DataFrame, dict]:
    close = requests.loc[requests.nearest_osm_road_distance_m <= threshold_m].copy()
    tied = close.loc[close.nearest_tie_count > 1]
    close = close.loc[close.nearest_tie_count == 1].copy()
    candidate_segment_count = close.groupby("content_id_sha256").nearest_segment_id.nunique()
    ambiguous_hashes = set(candidate_segment_count[candidate_segment_count > 1].index)
    eligible = close.loc[~close.content_id_sha256.isin(ambiguous_hashes)].copy()
    eligible = eligible.sort_values(
        ["content_id_sha256", "nearest_osm_road_distance_m", "image_id"],
        kind="mergesort",
    )
    selected = eligible.drop_duplicates("content_id_sha256", keep="first").copy()
    assert_unique(selected, "content_id_sha256", "selected panorama content")
    selected = selected.rename(
        columns={"nearest_segment_id": "segment_id", "nearest_osm_road_distance_m": "road_distance_m"}
    )
    selected["gvi_formula"] = "Cityscapes vegetation + terrain / all pixels"
    selected["assignment_threshold_m"] = threshold_m
    summary = {
        "threshold_m": threshold_m,
        "request_rows_within_threshold": int(len(tied) + len(close)),
        "request_rows_with_nearest_road_tie_excluded": int(len(tied)),
        "distinct_content_with_non_tied_near_request": int(len(candidate_segment_count)),
        "content_groups_with_multiple_candidate_segments_excluded": int(len(ambiguous_hashes)),
        "selected_unique_content_count": int(len(selected)),
        "selected_fraction_of_all_unique_contents": float(len(selected) / 32_992),
        "selected_capture_year_month_min": str(selected.capture_year_month.min()),
        "selected_capture_year_month_max": str(selected.capture_year_month.max()),
        "selected_gvi_vt_mean_unweighted": float(selected.gvi_vt_existing.mean()),
    }
    columns = [
        "content_id_sha256", "image_id", "segment_id", "gvi_vt_existing",
        "road_distance_m", "capture_year_month", "nearest_highway", "nearest_osm_way_id",
        "assignment_threshold_m", "gvi_formula",
    ]
    return selected, summary


def segment_aggregate(roads: pd.DataFrame, selected: pd.DataFrame, threshold_m: int) -> tuple[pd.DataFrame, dict]:
    aggregate = selected.groupby("segment_id", as_index=False).agg(
        panorama_n=("content_id_sha256", "size"),
        gvi_vt_mean=("gvi_vt_existing", "mean"),
        gvi_vt_median=("gvi_vt_existing", "median"),
        gvi_vt_std=("gvi_vt_existing", "std"),
        gvi_vt_min=("gvi_vt_existing", "min"),
        gvi_vt_max=("gvi_vt_existing", "max"),
        road_distance_mean_m=("road_distance_m", "mean"),
        road_distance_max_m=("road_distance_m", "max"),
        capture_year_month_min=("capture_year_month", "min"),
        capture_year_month_max=("capture_year_month", "max"),
    )
    assert_unique(aggregate, "segment_id", "road aggregate")
    result = roads.merge(aggregate, on="segment_id", how="left", validate="one_to_one")
    if len(result) != len(roads):
        raise AssertionError("Road merge changed the OSM support")
    result["panorama_n"] = result.panorama_n.fillna(0).astype("int32")
    result["has_gvi_vt"] = result.panorama_n.gt(0).astype("int8")
    result["gvi_assignment_threshold_m"] = threshold_m
    result["gvi_metric_definition"] = "precomputed Cityscapes vegetation+terrain pixel share"
    result["capture_year_month_min"] = result.capture_year_month_min.astype("string")
    result["capture_year_month_max"] = result.capture_year_month_max.astype("string")
    observed = result.has_gvi_vt.eq(1)
    summary = {
        "osm_road_segment_count": int(len(result)),
        "segments_with_existing_gvi_vt": int(observed.sum()),
        "segment_coverage_fraction": float(observed.mean()),
        "road_length_coverage_fraction": float(result.loc[observed, "length_m"].sum() / result.length_m.sum()),
        "image_observation_count_after_deduplication": int(result.panorama_n.sum()),
        "segments_with_one_observation": int(result.panorama_n.eq(1).sum()),
        "segments_with_two_or_more_observations": int(result.panorama_n.ge(2).sum()),
        "unweighted_mean_of_observed_segment_means": float(result.loc[observed, "gvi_vt_mean"].mean()),
    }
    export_columns = [
        "segment_id", "osm_way_id", "highway", "name", "length_m", "panorama_n",
        "has_gvi_vt", "gvi_vt_mean", "gvi_vt_median", "gvi_vt_std",
        "gvi_vt_min", "gvi_vt_max", "road_distance_mean_m", "road_distance_max_m",
        "capture_year_month_min", "capture_year_month_max",
        "gvi_assignment_threshold_m", "gvi_metric_definition",
    ]
    return result, summary
