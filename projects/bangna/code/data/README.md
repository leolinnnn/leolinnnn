# Bang Na analysis inputs

[← Code and commands](../README.md)

Both CSVs are column subsets of the project's final analysis tables. All original
rows and missing observations are retained; no synthetic values were added.

| File | Rows | Source |
| --- | ---: | --- |
| [areas.csv](areas.csv) | 25 | `data/analysis_database/bangna_area_analysis_master.csv` |
| [interface-points.csv](interface-points.csv) | 289 | `data/interface_coding/bangna_interface_coding_points_final.csv` |

Area fields: `area_id`; `res_type` (A Condo, B House, C Shophouse, D Informal);
`type_label`; `gvi_pct` (vegetation-only GVI in percentage points);
`network_dist_to_bts_mean_m`; `major_road_share_in_polygon` (0–1);
`poi_shannon_400m_mean` (natural-log Shannon diversity).

Point fields: `candidate_id` (street sampling-point ID, not a person); `area_id`;
`res_type`; `gvi_pct`; `setback`, `visual_permeability`, `vehicle_occupation`
(means of assessable sides, each on a 0–2 scale); `interface_openness` (0–100);
`coding_confidence`; `boundary_25m_flag`; `intersection_flag`;
`network_dist_to_bts_m`; `major_road_share_200m`; `poi_shannon_400m`.

IO = 100 × (SET + VIS + (2 − VEH)) / 6. The 22 points with missing IO remain
missing; they are excluded from interface aggregation and the point-level model.
Area GVI and spatial controls retain their original study definitions when IO
sample restrictions change. C is the regression reference type. Continuous
covariates are standardised using the model sample's SD (`ddof=1`).

Files in `../reference/` are unchanged model-output CSVs from
`outputs/interface_analysis/csv/`, with the common `bangna_interface_` prefix
removed from their filenames. They are used after estimation to verify results.
The runner does not use stored coefficients to fit its models.

The extracts omit panorama IDs, image paths, coordinates and market-price fields.
Study authorship and original provider terms remain applicable; no separate
public-data license is asserted.
