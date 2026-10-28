"""Independently recompute the three headline statistics from paired values.

Run after extracting Supplementary Data S1. By default, read pair_values.csv. This script
does not need road IDs, exact locations, image IDs, or capture dates.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path


def pearson(x: list[float], y: list[float]) -> float:
    mx, my = statistics.mean(x), statistics.mean(y)
    xy = math.fsum((a - mx) * (b - my) for a, b in zip(x, y))
    xx = math.fsum((a - mx) ** 2 for a in x)
    yy = math.fsum((b - my) ** 2 for b in y)
    return xy / math.sqrt(xx * yy)


def classify(svvt: float, ndvi: float, svvt_median: float, ndvi_median: float) -> str:
    return ("H" if svvt >= svvt_median else "L") + ("H" if ndvi >= ndvi_median else "L")


def main(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    required = {"svvt", "ndvi_30m", "ndvi_50m", "ndvi_100m"}
    if not rows or not required <= rows[0].keys():
        raise ValueError("Missing paired values or required columns")
    values = {key: [float(row[key]) for row in rows] for key in required}
    medians = {key: statistics.median(vals) for key, vals in values.items()}
    r = {radius: pearson(values["svvt"], values[f"ndvi_{radius}m"]) for radius in (30, 50, 100)}
    labels30 = [
        classify(svvt, ndvi, medians["svvt"], medians["ndvi_30m"])
        for svvt, ndvi in zip(values["svvt"], values["ndvi_30m"])
    ]
    labels100 = [
        classify(svvt, ndvi, medians["svvt"], medians["ndvi_100m"])
        for svvt, ndvi in zip(values["svvt"], values["ndvi_100m"])
    ]
    n = len(rows)
    return {
        "n_fixed_pair_roads": n,
        "r_30m": r[30],
        "r_50m": r[50],
        "r_100m": r[100],
        "delta_r_30m_minus_100m": r[30] - r[100],
        "discordant_100m_n": sum(label in {"HL", "LH"} for label in labels100),
        "discordant_100m_fraction": sum(label in {"HL", "LH"} for label in labels100) / n,
        "transition_30m_to_100m_n": sum(a != b for a, b in zip(labels30, labels100)),
        "transition_30m_to_100m_fraction": sum(a != b for a, b in zip(labels30, labels100)) / n,
        "threshold_rule": "H iff value >= the corresponding fixed-sample median; ties are H",
        "transition_matrix": {
            before: {after: sum(a == before and b == after for a, b in zip(labels30, labels100))
                     for after in ("HH", "HL", "LH", "LL")}
            for before in ("HH", "HL", "LH", "LL")
        },
    }


if __name__ == "__main__":
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent / "data" / "beijing-pairs.csv"
    print(json.dumps(main(input_path), ensure_ascii=False, indent=2))
