# Street-view and satellite greenness in Beijing

[← Research overview](../../README.md)

**Zihao Lin · Research manuscript · Beijing, China**

## Research question

How does the spatial extent of satellite measurement change its relationship
with street-view greenery on the same roads?

## Research workflow

- Curate street-view observations through content deduplication and road matching.
- Apply pretrained semantic segmentation and aggregate the vegetation + terrain
  fraction to roads.
- Summarise native-grid Landsat NDVI with pixel–buffer intersection-area weights.
- Keep **13,943 paired road segments** fixed when comparing 30, 50 and 100 m buffers.
- Examine correlations, within-sample ranks, median-based categories and spatial
  block-bootstrap uncertainty.

## Selected results

| Road-buffer radius | Pearson r | 95% spatial-block bootstrap CI |
| --- | ---: | --- |
| 30 m | 0.545 | 0.525–0.564 |
| 50 m | 0.451 | 0.427–0.474 |
| 100 m | 0.312 | 0.283–0.342 |

At 100 m, 5,400 roads (38.73%) have discordant high/low classifications. Between
30 and 100 m, 2,810 roads (20.15%) change category. “High” means at or above the
corresponding fixed-sample median. Intervals use 2 km blocks and 4,999 resamples.

## Code and reproducibility

[verify_beijing.py](../../examples/verify_beijing.py) uses only Python's standard
library and the [included paired values](../../examples/data/beijing-pairs.csv).
It recomputes the three correlations, category counts and transition matrix.

```sh
cd examples
python verify_beijing.py
```

This check starts from numerical tables. It does not repeat image inference,
satellite processing or spatial bootstrap resampling.

## Measurement scope

The Beijing street-view metric combines the Cityscapes vegetation and terrain
classes. Street-view dates span 2013–2023; the Landsat scene is from 7 September
2021. Category transitions describe measurement sensitivity, not changes in real
vegetation or model accuracy.

**Tools:** Python, NumPy, GeoPandas, Shapely, rasterio/GDAL, GluonCV/MXNet.

**Manuscript:** *A Road-Segment Comparison of Street-View GVI and NDVI:
Scale-Dependent Associations and Classification Differences within Beijing's
Fifth Ring Road*.

[Source and license notes](../../docs/RESEARCH_NOTES.md)
