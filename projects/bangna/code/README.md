# Bang Na research code

[← Research summary](../README.md)

Original research functions for interface aggregation, robust regression,
sensitivity analysis, street-view measurement and spatial variables. A portable
runner connects the numerical workflow to a small extract of the study tables.

## Run

From the repository root, using Python 3.12:

```sh
python -m pip install -r projects/bangna/code/requirements.txt
python projects/bangna/code/run_analysis.py --output outputs/bangna
```

The runner starts with **289 street-view points**, including **267 valid interface
observations**, aggregates them to **25 residential areas**, and fits:

- M2 and M2-I, using sample-SD standardisation and HC3 covariance.
- Seven area-level sensitivity specifications: median IO; exclusion of low-confidence,
  boundary or intersection points; and each of the three IO components separately.
- The auxiliary point-level model with area-clustered CR1 covariance.

It also produces type comparisons, Dunn tests with Benjamini–Hochberg adjustment,
Spearman associations, VIFs and influence diagnostics. CSVs and `verification.json`
are written to the requested new directory. Choose a different directory to rerun.

## Implementation

| File | Research computation |
| --- | --- |
| [interface_analysis.py](src/interface_analysis.py) | Point-to-area aggregation, model design, type comparisons, seven sensitivity models and clustered point model |
| [regression.py](src/regression.py) | OLS, leverage-adjusted HC3 covariance, t-based intervals, model summaries and VIF |
| [segmentation_metrics.py](src/segmentation_metrics.py) | Cityscapes class fractions, 40-pixel bottom exclusion and image → point → area aggregation |
| [network_metrics.py](src/network_metrics.py) | Reachable-node selection, exact line–circle lengths and buffered road context |
| [poi_diversity.py](src/poi_diversity.py) | Category-based POI Shannon diversity, evenness and buffer summaries |

The [historical scripts](legacy/README.md) additionally contain the full original
DeepLab/MXNet inference loop, NetworkX routing workflow and POI-processing workflow.
They retain their original input conventions and require external project inputs.
The modern numerical runner does not import MXNet or download images or models.

## Data and validation

The [input schema](data/README.md) describes the included point and area extracts.
Interface scores are the study's final manual observations; the runner checks
their arithmetic but does not independently re-code the images. The model is
cross-sectional and describes conditional associations.

Validated on **29 October 2026**, Python 3.12.14: the two main models, seven
sensitivity models and clustered point model match all numeric fields in six
archived model/coefficients tables (`rtol=1e-8, atol=1e-9`). Main adjusted R² values
are **0.4876908** and **0.7097321**; M2-I's IO coefficient is **5.5145202** percentage
points per SD, with HC3 95% CI **[2.2749648, 8.7540757]**.

Five kernel tests check class definitions and cropping, aggregation order, an
analytical HC3 case, disconnected-node fallback, road-buffer geometry and POI
diversity:

```sh
python -m unittest discover -s projects/bangna/code/tests -v
```

See [provenance and changes](PROVENANCE.md). The compact
[verification example](../../../examples/verify_bangna.py) remains available.
Study authors: **Zihao Lin and Lei Shao**. This package does not introduce a new
blanket license for the research materials or third-party imagery/software.
