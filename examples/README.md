# Recomputing selected urban-greenness results

Two small, portable examples accompany Zihao Lin's research portfolio. These use
the actual numerical outputs of the Beijing and Bang Na projects, not simulated data.
The examples reproduce selected statistical results from existing tables. They do
not recreate image acquisition, semantic segmentation, satellite processing, manual
coding or spatial bootstrap confidence intervals.

For the original research routines and more extensive runnable analyses, see
[Beijing research code](../projects/beijing/code/README.md) and
[Bang Na research code](../projects/bangna/code/README.md). These add spatial
bootstrap/Moran analysis and the full set of archived interface model checks.

## Beijing — Python standard library

```sh
python verify_beijing.py
```

Input: `data/beijing-pairs.csv`, 13,943 rows. `svvt` is the street-view vegetation +
terrain proportion; NDVI is summarized in 30, 50 and 100 m road buffers. `review_row`
is a row index, not a location identifier. This table contains no geometry or raw images.

Expected Pearson r: 0.5445584033 / 0.4508014493 / 0.3124452569.
At 100 m, 5,400 roads have discordant median-based categories (HL or LH).
Between 30 and 100 m, 2,810 roads change category. H means at or above the sample
median. These categories express relative positions in this sample.

The script is adapted from the project's existing verification code with only its
default input path changed. See `BEIJING_SOURCE_LICENSES.md` for the source terms
and OpenStreetMap/USGS attribution. Beijing data and original source code follow
the existing release's CC BY 4.0 terms to the extent of the author's rights.

## Bang Na — NumPy, pandas and SciPy

```sh
python -m pip install -r requirements.txt
python verify_bangna.py
```

Input: `data/bangna-areas.csv`, a nine-column extract of the existing 25-area table.
Types: A condominium, B house, C shophouse, D informal settlement. `gvi_pct` is
vegetation-only GVI in percent. `interface_openness_mean` is IO on a 0–100 scale;
larger values indicate greater interface openness. The original IO formula is
100 × (SET + VIS + (2 − VEH)) / 6, with each coded component in {0,1,2}.

The remaining predictors are mean network distance to Bang Na BTS (metres),
major-road share (fraction), and mean POI Shannon diversity in 400 m buffers.
`gvi_point_count` and `n_images` are sample counts. No property-price fields,
raw imagery or individual records are included.

The model uses shophouse (C) as the reference category, sample-SD standardization
(ddof=1), OLS, HC3 covariance and a t reference distribution with n − k degrees of
freedom. M2 has residential types and three spatial controls; M2-I adds IO.
Expected adjusted R²: 0.4876908 / 0.7097321. IO: 5.5145202 percentage points per SD,
95% CI [2.2749648, 8.7540757]. This is an association in 25 areas, not a causal estimate.

This compact script is newly prepared for the portfolio and independently recomputes
the stored main-model results. The research manuscript is by Zihao Lin and Lei Shao;
manuscript publication status and a separate Bang Na public data license are not
asserted here. Retain attribution; contact the authors for reuse beyond inspection.

## Verification

`expected-results.json` records the outputs checked during preparation. Python
3.12.14, NumPy 2.3.5, pandas 2.3.3 and SciPy 1.16.3 were used for the local check.
See [the research overview](../README.md) and project notes for the analytical context.
