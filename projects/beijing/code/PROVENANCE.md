# Beijing code provenance

[← Code and commands](README.md)

The modules preserve selected computation routines from the supplied research
archive. [source-manifest.json](source-manifest.json) records each original
filename, SHA-256, function line range and whether its body changed during extraction.

| Public module | Original research source | Packaging changes |
| --- | --- | --- |
| `spatial_statistics.py` | `analyze_fixed_osm_pairs.py`, Step 7 OSM analysis | Four functions copied unchanged; imports and metric-column constants retained |
| `road_aggregation.py` | `build_existing_gvi_osm.py`, release `code/street_view/` | Removed two automatic CSV writes; GeoDataFrame annotations generalized to DataFrame; computation retained |
| `ndvi_reflectance.py` | `rebuild_native_c2_ndvi.py`, release `code/remote_sensing/` | Numerical block copied from `main()` into a callable function; verified coefficients, shape check and return added |
| `ndvi_aggregation.py` | `pair_native_ndvi_roads.py`, release `code/remote_sensing/` | Intersection-area summary function copied unchanged; raster loading omitted |

The Step 7 statistical helpers were reused by the corrected C2 L2 analysis in
`analyze_corrected_pairs.py`. This repository uses the **corrected release's**
fixed paired values and the Step 11 specification dated 13 September 2026:
seed `20260913`, 4,999 resamples, 1/2/4 km grids and 999 Moran permutations.
The older Step 7 input data are not used.

`run_analysis.py`, the tests and this packaging were added for the portfolio on
29 October 2026. They are distinct from the original research routines.
The original archive was not modified. No claim is made that these selected
modules are the complete street-view and remote-sensing pipeline.
