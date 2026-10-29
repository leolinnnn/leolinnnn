"""Research functions from run_bangna_gvi_regression_analysis.py. See ../PROVENANCE.md."""

from __future__ import annotations

from typing import Any
import numpy as np
import pandas as pd
from scipy import stats



def ols_fit(x: pd.DataFrame, y: pd.Series) -> dict[str, np.ndarray | float | int]:
    x_np = x.to_numpy(float)
    y_np = y.to_numpy(float)
    n, p = x_np.shape
    xtx_inv = np.linalg.pinv(x_np.T @ x_np)
    beta = xtx_inv @ x_np.T @ y_np
    fitted = x_np @ beta
    resid = y_np - fitted
    sse = float(np.sum(resid**2))
    sst = float(np.sum((y_np - np.mean(y_np)) ** 2))
    df_resid = n - p
    mse = sse / df_resid if df_resid > 0 else np.nan
    rmse = float(np.sqrt(np.mean(resid**2)))
    r2 = 1 - sse / sst if sst else np.nan
    adj_r2 = 1 - (1 - r2) * (n - 1) / df_resid if df_resid > 0 and not pd.isna(r2) else np.nan
    hat = np.sum((x_np @ xtx_inv) * x_np, axis=1)
    sigma2 = mse
    cov_classic = sigma2 * xtx_inv
    se_classic = np.sqrt(np.diag(cov_classic))
    robust_scale = (resid / np.clip(1 - hat, 1e-12, None)) ** 2
    meat = x_np.T @ (x_np * robust_scale[:, None])
    cov_hc3 = xtx_inv @ meat @ xtx_inv
    se_hc3 = np.sqrt(np.clip(np.diag(cov_hc3), 0, None))
    loglik = -0.5 * n * (np.log(2 * np.pi) + 1 + np.log(sse / n)) if sse > 0 else np.nan
    aic = 2 * p - 2 * loglik if not pd.isna(loglik) else np.nan
    bic = np.log(n) * p - 2 * loglik if not pd.isna(loglik) else np.nan
    f_stat = ((sst - sse) / (p - 1)) / (sse / df_resid) if p > 1 and df_resid > 0 and sse > 0 else np.nan
    f_p = stats.f.sf(f_stat, p - 1, df_resid) if not pd.isna(f_stat) else np.nan
    cooks = (resid**2 / (p * mse)) * (hat / np.clip((1 - hat) ** 2, 1e-12, None)) if mse and not pd.isna(mse) else np.full(n, np.nan)
    condition_number = float(np.linalg.cond(x_np))
    return {
        "n": n,
        "p": p,
        "df_resid": df_resid,
        "beta": beta,
        "fitted": fitted,
        "resid": resid,
        "hat": hat,
        "cooks": cooks,
        "se_classic": se_classic,
        "se_hc3": se_hc3,
        "sse": sse,
        "sst": sst,
        "r2": float(r2),
        "adj_r2": float(adj_r2),
        "rmse": rmse,
        "mse": float(mse),
        "aic": float(aic),
        "bic": float(bic),
        "f_stat": float(f_stat) if not pd.isna(f_stat) else np.nan,
        "f_p": float(f_p) if not pd.isna(f_p) else np.nan,
        "condition_number": condition_number,
    }


def p_from_t(t_value: float, df: int) -> float:
    if pd.isna(t_value) or df <= 0:
        return np.nan
    return float(2 * stats.t.sf(abs(t_value), df))


def format_p(p_value: float | None) -> str:
    if p_value is None or pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "<0.001"
    return f"{p_value:.3f}"


def significance(p_value: float | None) -> str:
    if p_value is None or pd.isna(p_value):
        return ""
    if p_value < 0.001:
        return "***"
    if p_value < 0.01:
        return "**"
    if p_value < 0.05:
        return "*"
    return "ns"


def coefficient_table(spec: Any, x: pd.DataFrame, fit: dict, metadata: pd.DataFrame) -> pd.DataFrame:
    rows = []
    df_resid = int(fit["df_resid"])
    for i, term in enumerate(x.columns):
        beta = float(fit["beta"][i])
        se = float(fit["se_hc3"][i])
        t_value = beta / se if se else np.nan
        p_value = p_from_t(t_value, df_resid)
        ci_low = beta - stats.t.ppf(0.975, df_resid) * se if df_resid > 0 and not pd.isna(se) else np.nan
        ci_high = beta + stats.t.ppf(0.975, df_resid) * se if df_resid > 0 and not pd.isna(se) else np.nan
        meta = metadata[metadata["term"] == term].iloc[0].to_dict()
        rows.append(
            {
                "model_id": spec.model_id,
                "model_name": spec.model_name,
                "role": spec.role,
                "term": term,
                "source_field": meta.get("source_field", ""),
                "label_zh": meta.get("label_zh", ""),
                "label_en": meta.get("label_en", ""),
                "term_type": meta.get("term_type", ""),
                "estimate_pctpt": beta,
                "se_hc3": se,
                "t_hc3": t_value,
                "p_hc3": p_value,
                "p_hc3_formatted": format_p(p_value),
                "significance_hc3": significance(p_value),
                "ci95_low_hc3": ci_low,
                "ci95_high_hc3": ci_high,
                "se_classic": float(fit["se_classic"][i]),
                "transform": meta.get("transform", ""),
                "unit": meta.get("unit", ""),
                "interpretation": meta.get("interpretation", ""),
            }
        )
    return pd.DataFrame(rows)


def model_summary(spec: Any, fit: dict) -> dict:
    return {
        "model_id": spec.model_id,
        "model_name": spec.model_name,
        "role": spec.role,
        "analysis_unit": spec.analysis_unit,
        "subset": spec.subset,
        "n": int(fit["n"]),
        "parameters_including_intercept": int(fit["p"]),
        "df_resid": int(fit["df_resid"]),
        "r2": float(fit["r2"]),
        "adj_r2": float(fit["adj_r2"]),
        "rmse_pctpt": float(fit["rmse"]),
        "aic": float(fit["aic"]),
        "bic": float(fit["bic"]),
        "f_stat": float(fit["f_stat"]) if not pd.isna(fit["f_stat"]) else np.nan,
        "f_p": float(fit["f_p"]) if not pd.isna(fit["f_p"]) else np.nan,
        "f_p_formatted": format_p(float(fit["f_p"]) if not pd.isna(fit["f_p"]) else np.nan),
        "f_significance": significance(float(fit["f_p"]) if not pd.isna(fit["f_p"]) else np.nan),
        "condition_number": float(fit["condition_number"]),
        "include_type": spec.include_type,
        "predictors": "; ".join(spec.predictors),
        "note": spec.note,
    }


def vif_table(spec: Any, x: pd.DataFrame) -> pd.DataFrame:
    rows = []
    predictors = [col for col in x.columns if col != "Intercept"]
    for col in predictors:
        others = [c for c in predictors if c != col]
        if not others:
            vif = 1.0
            r2 = 0.0
        else:
            x_aux = pd.concat([pd.Series(1.0, index=x.index, name="Intercept"), x[others]], axis=1)
            y_aux = x[col]
            fit_aux = ols_fit(x_aux, y_aux)
            r2 = float(fit_aux["r2"])
            vif = float(1 / (1 - r2)) if r2 < 1 else np.inf
        rows.append(
            {
                "model_id": spec.model_id,
                "term": col,
                "vif": vif,
                "auxiliary_r2": r2,
                "vif_flag": "high" if vif >= 10 else ("moderate" if vif >= 5 else "ok"),
            }
        )
    return pd.DataFrame(rows)
