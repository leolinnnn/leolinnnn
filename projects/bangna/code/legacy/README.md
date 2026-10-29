# Historical upstream workflows

[← Code and validated numerical workflow](../README.md)

These are complete original scripts copied from the project archive. Their
research computation is preserved; file discovery still follows the historical
project layout. They are separate from the Python 3.12 numerical runner.

| Script | Dependencies and required inputs | Outputs |
| --- | --- | --- |
| [Street-view segmentation](calculate_bangna_gvi_deeplab_cityscapes.py) | Compatible MXNet/GluonCV environment, NumPy, pandas, Pillow; pretrained `deeplab_resnet101_citys`; image manifest with `image_id`, `processed_abspath`, point/area/type IDs, heading and coordinates; corresponding locally available images | Class fractions, vegetation-only GVI, image/point/area/type CSVs and optional QA overlays |
| [Road and network variables](calculate_bangna_road_space_variables.py) | NetworkX and pandas; OSM road GeoJSON, walking GraphML, station GeoJSON, residential polygons, GVI point/area tables and sampling crosswalk | Shortest-path distance plus the point-to-reachable-node connector, buffer road metrics and area road variables |
| [Functional variables](calculate_bangna_functional_variables.py) | pandas; classified OSM POI table, residential polygons and GVI point/area tables | POI category counts, density, diversity and distance variables |

Run the two spatial scripts from a separate copy of the original project root:
their constants list the required paths under `data/`, and their outputs also go
under `data/`. The network workflow makes an undirected walking graph, preserves
the shortest length among parallel edges and flags reachable-node fallback. The
area road-length calculation uses the original sampling approximation; circular
buffer lengths use exact line–circle intersections. The local projection is the
original equirectangular approximation.

The segmentation script accepts `--input`, `--out-dir`, `--ctx` and
`--ignore-bottom-px`. It loads pretrained weights and may fetch them if absent.
Its `processed_abspath` manifest field must point to images on the current machine;
the original user's image paths are not included. The default bottom exclusion
is 40 pixels. The modern requirements file does **not** install the historical
MXNet/GluonCV stack; its compatibility and image inference have not been retested
in this update.

Raw street-view images, weights, complete OSM input layers and API credentials
are not bundled here. Image providers' terms, pretrained-model licenses and
© [OpenStreetMap contributors](https://www.openstreetmap.org/copyright) attribution
remain applicable. For a fully runnable numerical example, use the parent
directory's documented command.
