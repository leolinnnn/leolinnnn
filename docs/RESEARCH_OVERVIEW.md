# Research portfolio

[← Profile](../README.md)

**M.Arch. student at Tsinghua University · Urban analytics & scientific computing**

I develop computational workflows to study urban greenery, street environments
and spatial experience, alongside building-performance simulation. My projects
combine Python-based geospatial analysis, image-based measurement, statistical
modelling, EnergyPlus simulations and interactive experiments in Unreal Engine.

[简体中文](RESEARCH_OVERVIEW.zh-CN.md) · [Email](mailto:zh-lin21@mails.tsinghua.edu.cn)

## Selected research & code

<!-- selected-research:start -->

### Beijing — Street-view and satellite greenness

How does spatial scale affect the relationship between street-level and
satellite-based greenery?

- Analyses **13,943 paired road segments** across 30, 50 and 100 m buffers using
  spatial block bootstrap and spatial diagnostics.
- Provides implementations for content deduplication, NDVI processing and
  pixel-area weighting, alongside a runnable statistical workflow.
- Correlation decreases from **0.545 to 0.312** as buffer radius increases;
  **20.15%** of roads change their median-based category.

**Python · Geospatial analysis · Spatial statistics**

[Research & repository](https://github.com/leolinnnn/multiscale-urban-greenness) · [Run the analysis](https://github.com/leolinnnn/multiscale-urban-greenness#quick-start)

### Bang Na — Street interfaces and visible greenery

How do residential types and street interfaces relate to visible greenery along
public streets in a peripheral Bangkok station area?

- Connects **1,156 images, 289 sampling points and 25 residential areas** through
  image-based measurement, interface coding and spatial variables.
- Implements point-to-area aggregation, regression with HC3 uncertainty estimates,
  seven sensitivity models and an area-clustered point model.
- Adding interface openness increases adjusted R² from **0.488 to 0.710**;
  the models describe conditional associations.

**Python · Image-based measurement · Statistical modelling**

[Research & repository](https://github.com/leolinnnn/street-interface-greenery) · [Run the analysis](https://github.com/leolinnnn/street-interface-greenery#quick-start)

### Building energy — Simulation and sensitivity analysis

How stable are comparisons of heating and cooling demand when geometry
interpretations and shared operating assumptions change?

- Builds **four drawing-derived scenarios** with Python geometry processing,
  thermal-zone construction and EnergyPlus model generation.
- Provides **170 archived model inputs**, monthly numerical data and a batch
  runner, covering geometry branches, single-factor tests and three 2³ designs.
- Reproduces annual ideal thermal demand, pairwise rank reversals and factorial
  contrasts; four baseline models have also been regenerated and rerun.

**Python · EnergyPlus · Computational geometry · Sensitivity analysis**

[Research & repository](https://github.com/leolinnnn/building-energy-sensitivity) · [Run the analysis](https://github.com/leolinnnn/building-energy-sensitivity#quick-start)

### VR climbing — Architectural enclosure and decisions

How can an interactive climbing task investigate the relationship between spatial
enclosure and route-following decisions?

- Combines **four experimental scenes**, Rhino models, Unreal Engine 5.4 and a
  Pico headset in a VR climbing study.
- Links controller input and hand–hold interaction to route-index comparison,
  grip-error counting and trial completion through Blueprints.
- Documents the experiment and its architectural application in *Twin Cliff*,
  a climbing-centre design in Chongli, Zhangjiakou.

**Unreal Engine Blueprints · VR interaction · Experimental design**

[Repository & Blueprint assets](https://github.com/leolinnnn/ue-vr-climbing-experiment) · [System implementation](https://github.com/leolinnnn/ue-vr-climbing-experiment/blob/main/docs/IMPLEMENTATION.md) · [Research & design](../projects/vr-climbing/README.md)

<!-- selected-research:end -->

## Computational methods

| Area | Implementations |
| --- | --- |
| Geospatial computation | [NDVI and pixel-area weighting](https://github.com/leolinnnn/multiscale-urban-greenness/blob/main/docs/IMPLEMENTATION.md); [road-network and POI variables](https://github.com/leolinnnn/street-interface-greenery/blob/main/docs/IMPLEMENTATION.md) |
| Statistical computing | [Spatial bootstrap and Moran's I](https://github.com/leolinnnn/multiscale-urban-greenness/blob/main/src/spatial_statistics.py); [OLS, HC3 covariance and model diagnostics](https://github.com/leolinnnn/street-interface-greenery/blob/main/src/regression.py) |
| Image-based measurement | [Class fractions, cropping and image → point → area aggregation](https://github.com/leolinnnn/street-interface-greenery/blob/main/src/segmentation_metrics.py) |
| Building performance | [Geometry-to-IDF generation](https://github.com/leolinnnn/building-energy-sensitivity/blob/main/src/energy_model.py); [batch simulation](https://github.com/leolinnnn/building-energy-sensitivity/blob/main/run_simulations.py); [rank sensitivity and factorial contrasts](https://github.com/leolinnnn/building-energy-sensitivity/blob/main/src/sensitivity.py) |
| Interactive systems | [Blueprint assets, interaction and experiment control](https://github.com/leolinnnn/ue-vr-climbing-experiment/blob/main/docs/IMPLEMENTATION.md) |

## Education & contact

**Tsinghua University, School of Architecture**  
M.Arch., 2025–2027 (expected) · B.Arch., 2021–2025.  
Graduate GPA **4.00/4.00**, rank **1/101** · National Scholarship for Graduate Students, **2026**.

[Academic email](mailto:zh-lin21@mails.tsinghua.edu.cn) · [Research records](RESEARCH_NOTES.md)
