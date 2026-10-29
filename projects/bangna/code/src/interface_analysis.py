"""Research functions from analyze_bangna_interface.py. See ../PROVENANCE.md."""

from __future__ import annotations

import math
from itertools import combinations
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from .regression import coefficient_table, format_p, model_summary, ols_fit, significance, vif_table

AREA_DB = Path(__file__).resolve().parents[1] / "data" / "areas.csv"
TYPE_ORDER = ["A", "B", "C", "D"]
TYPE_LABELS = {"A": "Condo", "B": "House", "C": "Shophouse", "D": "Informal"}
TYPE_LABELS_ZH = {"A": "高层商品公寓", "B": "低层独户住宅", "C": "传统商住排屋", "D": "非正式住区"}

def area_aggregate(points: pd.DataFrame, value_method: str = "mean", filters: dict | None = None) -> pd.DataFrame:
    work = points.copy()
    if filters:
        for field, allowed in filters.items():
            if callable(allowed):
                work = work[allowed(work[field])]
            else:
                work = work[work[field].isin(allowed)]
    grouped = []
    for area_id, group in work.groupby("area_id", sort=True):
        valid = group[group["interface_openness"].notna()].copy()
        aggregation = np.nanmean if value_method == "mean" else np.nanmedian
        grouped.append(
            {
                "area_id": area_id,
                "interface_points_total": int(len(group)),
                "interface_points_valid": int(len(valid)),
                "interface_valid_share": float(len(valid) / len(group)) if len(group) else np.nan,
                "interface_low_confidence_n": int((group["coding_confidence"] == "low").sum()),
                "interface_low_confidence_share": float((group["coding_confidence"] == "low").mean()),
                "setback_mean": float(valid["setback"].mean()) if len(valid) else np.nan,
                "visual_permeability_mean": float(valid["visual_permeability"].mean()) if len(valid) else np.nan,
                "vehicle_occupation_mean": float(valid["vehicle_occupation"].mean()) if len(valid) else np.nan,
                "interface_openness_mean": float(valid["interface_openness"].mean()) if len(valid) else np.nan,
                "interface_openness_median": float(valid["interface_openness"].median()) if len(valid) else np.nan,
                "interface_openness_analysis": float(aggregation(valid["interface_openness"])) if len(valid) else np.nan,
            }
        )
    aggregate = pd.DataFrame(grouped)
    area = pd.read_csv(AREA_DB)
    merged = area.merge(aggregate, on="area_id", how="left", validate="one_to_one")
    if len(merged) != 25:
        raise ValueError("Area aggregation must produce 25 areas")
    return merged


def type_descriptives(area: pd.DataFrame) -> pd.DataFrame:
    rows = []
    fields = [
        ("setback_mean", "建筑退界"),
        ("visual_permeability_mean", "边界通透性"),
        ("vehicle_occupation_mean", "机动车界面占用"),
        ("interface_openness_mean", "界面开放度"),
    ]
    for res_type in TYPE_ORDER:
        group = area[area["res_type"] == res_type]
        for field, label in fields:
            series = group[field].dropna()
            rows.append(
                {
                    "res_type": res_type,
                    "type_label": TYPE_LABELS[res_type],
                    "type_label_zh": TYPE_LABELS_ZH[res_type],
                    "metric": field,
                    "metric_label_zh": label,
                    "area_n": int(len(series)),
                    "mean": float(series.mean()),
                    "sd": float(series.std(ddof=1)) if len(series) > 1 else np.nan,
                    "median": float(series.median()),
                    "q1": float(series.quantile(0.25)),
                    "q3": float(series.quantile(0.75)),
                    "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
                    "min": float(series.min()),
                    "max": float(series.max()),
                }
            )
    return pd.DataFrame(rows)


def bh_adjust(p_values: list[float]) -> list[float]:
    p = np.asarray(p_values, dtype=float)
    order = np.argsort(p)
    ranked = p[order]
    adjusted = ranked * len(p) / np.arange(1, len(p) + 1)
    adjusted = np.minimum.accumulate(adjusted[::-1])[::-1]
    adjusted = np.clip(adjusted, 0, 1)
    result = np.empty_like(adjusted)
    result[order] = adjusted
    return result.tolist()


def dunn_bh(area: pd.DataFrame, field: str) -> pd.DataFrame:
    work = area[["res_type", field]].dropna().copy()
    work["rank"] = stats.rankdata(work[field], method="average")
    n = len(work)
    _, counts = np.unique(work[field], return_counts=True)
    tie_correction = 1 - np.sum(counts**3 - counts) / (n**3 - n) if n > 1 else 1
    variance = n * (n + 1) / 12 * tie_correction
    rows = []
    for g1, g2 in combinations(TYPE_ORDER, 2):
        a, b = work[work["res_type"] == g1], work[work["res_type"] == g2]
        z = (a["rank"].mean() - b["rank"].mean()) / math.sqrt(variance * (1 / len(a) + 1 / len(b)))
        p = float(2 * stats.norm.sf(abs(z)))
        rows.append({"group_1": g1, "group_2": g2, "z": float(z), "p_raw": p})
    adjusted = bh_adjust([row["p_raw"] for row in rows])
    for row, p_adj in zip(rows, adjusted):
        row["p_bh"] = p_adj
        row["p_bh_formatted"] = format_p(p_adj)
        row["significance_bh"] = significance(p_adj)
    return pd.DataFrame(rows)


def type_tests(area: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows = []
    dunn_all = []
    for field, label in [
        ("setback_mean", "建筑退界"),
        ("visual_permeability_mean", "边界通透性"),
        ("vehicle_occupation_mean", "机动车界面占用"),
        ("interface_openness_mean", "界面开放度"),
    ]:
        groups = [area.loc[area["res_type"] == t, field].dropna().to_numpy() for t in TYPE_ORDER]
        h, p = stats.kruskal(*groups)
        rows.append(
            {
                "metric": field,
                "metric_label_zh": label,
                "test": "Kruskal-Wallis",
                "H": float(h),
                "df": 3,
                "p": float(p),
                "p_formatted": format_p(p),
                "significance": significance(p),
                "analysis_unit": "area",
                "n": int(sum(len(g) for g in groups)),
            }
        )
        if p < 0.05:
            posthoc = dunn_bh(area, field)
            posthoc.insert(0, "metric", field)
            posthoc.insert(1, "metric_label_zh", label)
            dunn_all.append(posthoc)
    return pd.DataFrame(rows), (pd.concat(dunn_all, ignore_index=True) if dunn_all else pd.DataFrame())


def correlations(area: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for field, label in [
        ("setback_mean", "建筑退界"),
        ("visual_permeability_mean", "边界通透性"),
        ("vehicle_occupation_mean", "机动车界面占用"),
        ("interface_openness_mean", "界面开放度"),
    ]:
        pair = area[[field, "gvi_pct"]].dropna()
        rho, p = stats.spearmanr(pair[field], pair["gvi_pct"])
        rows.append(
            {
                "interface_metric": field,
                "metric_label_zh": label,
                "outcome": "gvi_pct",
                "spearman_rho": float(rho),
                "p": float(p),
                "p_formatted": format_p(p),
                "significance": significance(p),
                "n": int(len(pair)),
                "analysis_unit": "area",
            }
        )
    return pd.DataFrame(rows)


def zscore(series: pd.Series) -> tuple[pd.Series, float, float]:
    numeric = pd.to_numeric(series, errors="coerce")
    mean = float(numeric.mean())
    sd = float(numeric.std(ddof=1))
    return (numeric - mean) / sd, mean, sd


def build_area_model(area: pd.DataFrame, interface_field: str | None) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    fields = [
        "network_dist_to_bts_mean_m",
        "major_road_share_in_polygon",
        "poi_shannon_400m_mean",
    ]
    if interface_field:
        fields.insert(0, interface_field)
    work = area[["area_id", "res_type", "type_label", "gvi_pct", *fields]].dropna().copy()
    parts = [pd.Series(1.0, index=work.index, name="Intercept")]
    meta = [
        {
            "term": "Intercept", "source_field": "", "label_zh": "截距", "label_en": "Intercept",
            "term_type": "intercept", "unit": "percentage point", "transform": "none",
            "mean_used": np.nan, "sd_used": np.nan,
            "interpretation": "Expected GVI for Shophouse at mean continuous predictors.",
        }
    ]
    for res_type in ["A", "B", "D"]:
        term = f"type_{res_type}_vs_C"
        parts.append((work["res_type"] == res_type).astype(float).rename(term))
        meta.append(
            {
                "term": term, "source_field": "res_type",
                "label_zh": f"{TYPE_LABELS_ZH[res_type]} 相对 {TYPE_LABELS_ZH['C']}",
                "label_en": f"{TYPE_LABELS[res_type]} vs Shophouse", "term_type": "type_dummy",
                "unit": "percentage point", "transform": "dummy", "mean_used": np.nan, "sd_used": np.nan,
                "interpretation": "Difference from Shophouse, conditional on included covariates.",
            }
        )
    label_map = {
        "interface_openness_mean": ("界面开放度（均值）", "Interface openness (mean)", "score"),
        "interface_openness_median": ("界面开放度（中位数）", "Interface openness (median)", "score"),
        "interface_openness_analysis": ("界面开放度（稳健性口径）", "Interface openness (robustness)", "score"),
        "setback_mean": ("建筑退界", "Setback", "ordinal mean"),
        "visual_permeability_mean": ("边界通透性", "Visual permeability", "ordinal mean"),
        "vehicle_occupation_mean": ("机动车界面占用", "Vehicle occupation", "ordinal mean"),
        "network_dist_to_bts_mean_m": ("至BTS站平均网络步行距离", "Mean network distance to BTS", "m"),
        "major_road_share_in_polygon": ("主干路长度占比", "Major road share", "ratio"),
        "poi_shannon_400m_mean": ("400m范围POI香农多样性", "POI Shannon diversity", "index"),
    }
    for field in fields:
        transformed, mean, sd = zscore(work[field])
        term = f"z_{field}"
        parts.append(transformed.rename(term))
        zh, en, unit = label_map[field]
        meta.append(
            {
                "term": term, "source_field": field, "label_zh": zh, "label_en": en,
                "term_type": "continuous", "unit": unit, "transform": "z-score",
                "mean_used": mean, "sd_used": sd,
                "interpretation": f"GVI percentage-point change per 1 SD increase in {en}.",
            }
        )
    x = pd.concat(parts, axis=1).astype(float)
    y = work["gvi_pct"].astype(float)
    model_data = work[["area_id", "res_type", "type_label", "gvi_pct"]].copy()
    return x, y, pd.DataFrame(meta), model_data


def fit_area_model(area: pd.DataFrame, model_id: str, interface_field: str | None) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    x, y, meta, model_data = build_area_model(area, interface_field)
    fit = ols_fit(x, y)

    class Spec:
        model_name = "Type plus core built environment" if interface_field is None else "M2 extended with street interface"
        role = "baseline_replication" if interface_field is None else "interface_extension"
        include_type = True
        subset = "all"
        analysis_unit = "area"
        predictors = tuple(meta.loc[meta["term_type"] == "continuous", "source_field"].tolist())
        note = "Cross-sectional explanatory OLS; no causal mediation claim."

    spec = Spec()
    spec.model_id = model_id
    coef = coefficient_table(spec, x, fit, meta)
    summary = pd.DataFrame([model_summary(spec, fit)])
    vif = vif_table(spec, x)
    predictions = model_data.copy()
    predictions["model_id"] = model_id
    predictions["fitted"] = fit["fitted"]
    predictions["residual"] = fit["resid"]
    predictions["leverage"] = fit["hat"]
    predictions["cooks_distance"] = fit["cooks"]
    return summary, coef, vif, predictions


def cluster_robust_point_model(points: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fields = ["interface_openness", "network_dist_to_bts_m", "major_road_share_200m", "poi_shannon_400m"]
    work = points[["candidate_id", "area_id", "res_type", "gvi_pct", *fields]].dropna().copy()
    parts = [pd.Series(1.0, index=work.index, name="Intercept")]
    for res_type in ["A", "B", "D"]:
        parts.append((work["res_type"] == res_type).astype(float).rename(f"type_{res_type}_vs_C"))
    for field in fields:
        z, _, _ = zscore(work[field])
        parts.append(z.rename(f"z_{field}"))
    x = pd.concat(parts, axis=1).to_numpy(float)
    y = work["gvi_pct"].to_numpy(float)
    beta = np.linalg.pinv(x.T @ x) @ x.T @ y
    resid = y - x @ beta
    bread = np.linalg.pinv(x.T @ x)
    groups = work["area_id"].astype(str).to_numpy()
    unique_groups = np.unique(groups)
    meat = np.zeros((x.shape[1], x.shape[1]))
    for group in unique_groups:
        mask = groups == group
        score = x[mask].T @ resid[mask]
        meat += np.outer(score, score)
    n, p, g = len(work), x.shape[1], len(unique_groups)
    correction = (g / (g - 1)) * ((n - 1) / (n - p))
    covariance = correction * bread @ meat @ bread
    se = np.sqrt(np.clip(np.diag(covariance), 0, None))
    t_values = beta / se
    p_values = 2 * stats.t.sf(np.abs(t_values), g - 1)
    critical = stats.t.ppf(0.975, g - 1)
    terms = [part.name for part in parts]
    coef = pd.DataFrame(
        {
            "model_id": "P1_cluster",
            "term": terms,
            "estimate_pctpt": beta,
            "se_cluster_area": se,
            "t_cluster": t_values,
            "p_cluster": p_values,
            "ci95_low_cluster": beta - critical * se,
            "ci95_high_cluster": beta + critical * se,
            "n_points": n,
            "clusters": g,
            "cluster_df": g - 1,
        }
    )
    sse = float(np.sum(resid**2))
    sst = float(np.sum((y - y.mean()) ** 2))
    summary = pd.DataFrame(
        [
            {
                "model_id": "P1_cluster", "n_points": n, "clusters": g, "parameters": p,
                "r2": 1 - sse / sst, "adj_r2": 1 - (1 - (1 - sse / sst)) * (n - 1) / (n - p),
                "rmse": math.sqrt(sse / n), "se_type": "area-cluster robust CR1",
                "interpretation": "Point-level auxiliary association; observations are not treated as independent within areas.",
            }
        ]
    )
    return summary, coef


def robustness_models(points: pd.DataFrame, area_base: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    scenarios = []
    scenario_areas = {
        "R1_area_median": area_aggregate(points, value_method="median"),
        "R2_exclude_low_confidence": area_aggregate(points, filters={"coding_confidence": ["high", "medium"]}),
        "R3_exclude_boundary": area_aggregate(points, filters={"boundary_25m_flag": [0]}),
        "R4_exclude_intersections": area_aggregate(points, filters={"intersection_flag": [0]}),
    }
    scenario_fields = {
        "R1_area_median": "interface_openness_analysis",
        "R2_exclude_low_confidence": "interface_openness_analysis",
        "R3_exclude_boundary": "interface_openness_analysis",
        "R4_exclude_intersections": "interface_openness_analysis",
        "R5_setback_only": "setback_mean",
        "R6_permeability_only": "visual_permeability_mean",
        "R7_vehicle_only": "vehicle_occupation_mean",
    }
    summaries, coefs = [], []
    for model_id, field in scenario_fields.items():
        data = scenario_areas.get(model_id, area_base)
        summary, coef, _, _ = fit_area_model(data, model_id, field)
        summaries.append(summary)
        coefs.append(coef)
        scenarios.append(
            {
                "model_id": model_id,
                "interface_field": field,
                "area_n": int(summary["n"].iloc[0]),
                "note": {
                    "R1_area_median": "Area median replaces area mean.",
                    "R2_exclude_low_confidence": "Low-confidence points excluded before aggregation.",
                    "R3_exclude_boundary": "Points outside polygons within the 25 m tolerance excluded.",
                    "R4_exclude_intersections": "Points within 20 m of an OSM network intersection excluded.",
                    "R5_setback_only": "Setback component replaces composite IO.",
                    "R6_permeability_only": "Visual permeability replaces composite IO.",
                    "R7_vehicle_only": "Vehicle occupation replaces composite IO; sign is expected to be opposite IO.",
                }[model_id],
            }
        )
    summary_all = pd.concat(summaries, ignore_index=True).merge(pd.DataFrame(scenarios), on="model_id")
    return summary_all, pd.concat(coefs, ignore_index=True)
