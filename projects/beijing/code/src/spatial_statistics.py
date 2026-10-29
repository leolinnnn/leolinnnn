"""Research functions from analyze_fixed_osm_pairs.py. See ../PROVENANCE.md."""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

GVI_COL = "gvi_vt_25m_mean"
NDVI_COLS = ["ndvi_30m", "ndvi_50m", "ndvi_100m"]

def type_labels(gvi: np.ndarray, ndvi: np.ndarray, low: float, high: float) -> np.ndarray:
    gl, gh = np.quantile(gvi, [low, high])
    nl, nh = np.quantile(ndvi, [low, high])
    labels = np.full(len(gvi), "MIDDLE", dtype="<U6")
    labels[(gvi >= gh) & (ndvi >= nh)] = "HH"
    labels[(gvi >= gh) & (ndvi <= nl)] = "HL"
    labels[(gvi <= gl) & (ndvi >= nh)] = "LH"
    labels[(gvi <= gl) & (ndvi <= nl)] = "LL"
    return labels


def pearson_from_moments(m: np.ndarray) -> np.ndarray:
    """Moments per replicate: n,sx,sx2,sy,sy2,sxy."""
    n, sx, sx2, sy, sy2, sxy = [m[..., i] for i in range(6)]
    numerator = n * sxy - sx * sy
    denominator = np.sqrt(np.maximum(n * sx2 - sx * sx, 0) * np.maximum(n * sy2 - sy * sy, 0))
    return np.divide(numerator, denominator, out=np.full_like(numerator, np.nan), where=denominator > 0)


def block_bootstrap(table: pd.DataFrame, grid_m: int, resamples: int, seed: int) -> tuple[pd.DataFrame, dict]:
    x = table[GVI_COL].to_numpy(dtype=float)
    y = table[NDVI_COLS].to_numpy(dtype=float)
    bx = np.floor(table.centroid_x_m.to_numpy(dtype=float) / grid_m).astype(int)
    by = np.floor(table.centroid_y_m.to_numpy(dtype=float) / grid_m).astype(int)
    block_code, unique_blocks = pd.factorize(pd.MultiIndex.from_arrays([bx, by]), sort=True)
    b = len(unique_blocks)
    if b < 20:
        raise AssertionError(f"Only {b} nonempty {grid_m} m blocks")

    # One row per block with six Pearson moments for each NDVI radius.
    moments = np.zeros((b, len(NDVI_COLS), 6), dtype=float)
    for j in range(len(NDVI_COLS)):
        yy = y[:, j]
        for k, values in enumerate((np.ones(len(x)), x, x * x, yy, yy * yy, x * yy)):
            moments[:, j, k] = np.bincount(block_code, weights=values, minlength=b)

    rng = np.random.default_rng(seed + grid_m)
    rows = []
    delta_samples = []
    for start in range(0, resamples, 250):
        take = min(250, resamples - start)
        sampled = rng.integers(0, b, size=(take, b))
        replicate_moments = moments[sampled].sum(axis=1)
        vals = pearson_from_moments(replicate_moments)
        rows.append(vals)
        delta_samples.append(vals[:, 0] - vals[:, 2])
    reps = np.concatenate(rows)
    delta = np.concatenate(delta_samples)
    if not np.isfinite(reps).all() or not np.isfinite(delta).all():
        raise AssertionError("Non-finite bootstrap statistic")

    output = []
    for j, radius in enumerate((30, 50, 100)):
        output.append({
            "grid_m": grid_m,
            "statistic": f"pearson_r_ndvi_{radius}m",
            "estimate": float(np.corrcoef(x, y[:, j])[0, 1]),
            "ci_2p5": float(np.quantile(reps[:, j], 0.025)),
            "ci_97p5": float(np.quantile(reps[:, j], 0.975)),
            "nonempty_blocks": b,
            "resamples": resamples,
        })
    output.append({
        "grid_m": grid_m,
        "statistic": "delta_r_30m_minus_100m",
        "estimate": float(np.corrcoef(x, y[:, 0])[0, 1] - np.corrcoef(x, y[:, 2])[0, 1]),
        "ci_2p5": float(np.quantile(delta, 0.025)),
        "ci_97p5": float(np.quantile(delta, 0.975)),
        "nonempty_blocks": b,
        "resamples": resamples,
    })
    profile = {
        "grid_m": grid_m,
        "nonempty_blocks": b,
        "roads_per_block_min": int(np.bincount(block_code).min()),
        "roads_per_block_median": float(np.median(np.bincount(block_code))),
        "roads_per_block_max": int(np.bincount(block_code).max()),
    }
    return pd.DataFrame(output), profile


def moran_global(d: np.ndarray, coordinates: np.ndarray, k_values: list[int], permutations: int, seed: int) -> pd.DataFrame:
    max_k = max(k_values)
    candidates = cKDTree(coordinates).query(coordinates, k=max_k + 2, workers=-1)[1]
    if candidates.ndim != 2:
        raise AssertionError("Unexpected neighbor shape")
    neighbors = np.empty((len(d), max_k), dtype=int)
    for i, candidate in enumerate(candidates):
        valid = candidate[candidate != i]
        if len(valid) < max_k:
            raise AssertionError("Insufficient non-self neighbors")
        neighbors[i] = valid[:max_k]
    z = d - np.mean(d)
    denominator = float(np.dot(z, z))
    if denominator <= 0:
        raise AssertionError("Constant rank discordance")
    observed = {k: float(np.dot(z, z[neighbors[:, :k]].mean(axis=1)) / denominator) for k in k_values}
    simulated = {k: np.empty(permutations) for k in k_values}
    rng = np.random.default_rng(seed)
    for i in range(permutations):
        shuffled = rng.permutation(z)
        for k in k_values:
            simulated[k][i] = np.dot(shuffled, shuffled[neighbors[:, :k]].mean(axis=1)) / denominator
    expected = -1 / (len(d) - 1)
    return pd.DataFrame([{
        "knn_k": k,
        "moran_i": observed[k],
        "randomization_expected_i": expected,
        "permutation_p_two_sided": float((1 + np.count_nonzero(np.abs(simulated[k] - expected) >= abs(observed[k] - expected))) / (permutations + 1)),
        "permutation_null_2p5": float(np.quantile(simulated[k], 0.025)),
        "permutation_null_97p5": float(np.quantile(simulated[k], 0.975)),
        "permutations": permutations,
        "n_roads": len(d),
    } for k in k_values])
