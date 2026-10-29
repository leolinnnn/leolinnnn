# Beijing research code

[← Research summary](../README.md)

Selected implementations from the original Beijing research archive, with a
portable runner and the numerical inputs needed to reproduce the spatial analysis.
The computation modules cover road-content deduplication, physical NDVI, exact
pixel-area weighting and spatial uncertainty.

## Run

From the repository root, using Python 3.12:

```sh
python -m pip install -r projects/beijing/code/requirements.txt
python projects/beijing/code/run_analysis.py --output outputs/beijing
```

The runner reads **13,943 fixed paired roads**, then recomputes:

- Pearson correlations and paired scale differences with **4,999 bootstrap
  resamples** at each of the 1, 2 and 4 km grids; seed `20260913`.
- Global Moran's I of the 100 m signed rank difference, with k = 4, 8 and 12
  neighbours and **999 permutations**.
- Median-based categories, the 5,400 discordant roads at 100 m and the 2,810
  roads whose categories change between 30 and 100 m.

Generated CSVs and `verification.json` go into the requested new output directory.
Choose a different directory for a subsequent run. The runner compares its results
against the archived tables and exits with an error if they differ. Use
`--skip-moran` to run only the bootstrap and classification calculations.

## Implementation

| File | Research computation | Input |
| --- | --- | --- |
| [spatial_statistics.py](src/spatial_statistics.py) | Block bootstrap from per-block moments, rank categories and k-nearest-neighbour Moran test | Included road measures and projected centroids |
| [road_aggregation.py](src/road_aggregation.py) | Remove nearest-road ties and ambiguous content assignments; retain one observation per content hash; aggregate to the full road frame | Request-to-road crosswalk, image scores and road attributes |
| [ndvi_reflectance.py](src/ndvi_reflectance.py) | Landsat C2 L2 scale/offset, spectral constraints, cloud/saturation/aerosol/water masks | Aligned red, NIR and QA arrays |
| [ndvi_aggregation.py](src/ndvi_aggregation.py) | Exact pixel–polygon intersection-area weighted NDVI and valid-area fraction | NDVI arrays and clipped road-buffer polygons |

The first module is exercised on the included study data. The other three expose
upstream research functions for inspection and reuse; they are checked with small
analytical fixtures. Road assignment uses the archived nearest-road crosswalk;
this module does not construct that crosswalk. Its coverage denominator remains
the study's 32,992 unique panorama contents.

The raster kernel expects a north-up, unrotated 30 m grid in **EPSG:32650**, matching
the study. Valid area is measured relative to the clipped road buffer; the study's
paired sample requires at least 80% valid area at all three radii. These kernels
do not include image downloads, model weights, raster I/O or the complete GIS
preprocessing workflow.

## Data and validation

See the [input schema](data/README.md) and [code provenance](PROVENANCE.md).
The included values are research-derived observations, not synthetic examples.
The existing [standard-library check](../../../examples/verify_beijing.py) remains
available for a smaller correlation/classification-only demonstration.

Validated on **29 October 2026**, Python 3.12.14: all 12 bootstrap rows and the
three Moran diagnostic rows match their archived numerical fields within
`rtol=1e-9, atol=1e-10`. The four kernel tests cover QA variants, physical
reflectance, partial-pixel weighting, ambiguous road assignment and correlation
moments.

```sh
python -m pip install -r projects/beijing/code/requirements-kernels.txt
python -m unittest discover -s projects/beijing/code/tests -v
```

The source package's [license and attribution notes](../../../examples/BEIJING_SOURCE_LICENSES.md)
apply, including © OpenStreetMap contributors and USGS Landsat credit.
