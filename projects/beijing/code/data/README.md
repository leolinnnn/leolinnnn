# Beijing analysis inputs

[← Code and commands](../README.md)

[roads.csv](roads.csv) contains seven columns from
`zenodo_release_v1.0.0/data/road_level/fixed_pair_road_metrics.csv`.
All 13,943 fixed paired rows are retained in their original order; no observations
were generated, imputed or resampled to construct this input.

| Column | Definition |
| --- | --- |
| `segment_id` | Unique road-segment key in the rebuilt OSM frame |
| `gvi_vt_25m_mean` | Road mean of deduplicated vegetation + terrain pixel fractions, assigned within 25 m; range 0–1 |
| `ndvi_30m`, `ndvi_50m`, `ndvi_100m` | QA-screened, intersection-area weighted Landsat C2 L2 NDVI at each road-buffer radius |
| `centroid_x_m`, `centroid_y_m` | Road geometry centroids, EPSG:32650, metres; used for spatial blocks and neighbours |

The [bootstrap reference](../reference/block_bootstrap_ci.csv) and
[Moran reference](../reference/moran_rank_discordance.csv) are copied from the
release's `results/core/` directory. They are comparison targets, not inputs to
the estimators. The original percentile-rank and median rules operate within
this fixed road sample.

These are derived numerical and OSM-based spatial records. The
[source terms and attribution](../../../../examples/BEIJING_SOURCE_LICENSES.md)
remain applicable.
