# Residential types, street interfaces and greenery in Bang Na

[← Research overview](../../README.md)

**Zihao Lin and Lei Shao · Research manuscript · Bangkok, Thailand**

## Research question

How do residential types and the interface between buildings and public streets
relate to visible greenery in a peripheral transit-oriented development station area?

## Research workflow

- Process **1,156 directional images at 289 points** across **25 residential areas**.
- Measure vegetation-only GVI after removing the bottom 40 pixels of each
  640 × 640 image, using pretrained semantic segmentation.
- Combine setback, visual permeability and reversed vehicle occupation in an
  interface-openness index; 267 points have valid interface observations.
- Derive network distance, major-road share and POI diversity variables.
- Compare residential types, estimate area-level models with HC3 covariance,
  and examine alternative aggregation and sample rules.

## Selected results

| Model | Adjusted R² |
| --- | ---: |
| Residential types + three spatial controls (M2) | 0.488 |
| M2 + interface openness (M2-I) | 0.710 |

In M2-I, one SD higher interface openness is associated with **5.51 percentage
points higher GVI** (HC3 95% CI 2.27–8.75; 25 areas). The controls are mean
network distance to the BTS station, major-road share and mean POI Shannon
diversity in 400 m buffers.

## Code and reproducibility

[verify_bangna.py](../../examples/verify_bangna.py) makes the design matrix,
sample-SD standardisation, OLS and HC3 covariance calculation explicit.
It uses a [nine-column extract of the 25-area table](../../examples/data/bangna-areas.csv).

```sh
cd examples
python -m pip install -r requirements.txt
python verify_bangna.py
```

The portable example was checked against the stored main-model results. It does
not repeat raw image inference or manual interface coding.

## Interpretation

The model describes conditional associations. Equal-area and point-weighted
summaries answer different questions. The sample uses an 800 m Euclidean station
buffer to select intersecting residential polygons; it is not an 800 m walking
catchment. Unlike Beijing, the main Bang Na GVI includes vegetation only.

**Tools:** Python, NumPy, pandas, SciPy, NetworkX, GluonCV/MXNet, Matplotlib.

**Manuscript:** *Residential types, street interfaces and variation in the green
view index along public streets in a peripheral TOD station area: Bang Na, Bangkok*.

[Authorship and research notes](../../docs/RESEARCH_NOTES.md)
