# Zihao Lin | 林子豪

**Computational urban research · Spatial analysis · Human–environment interaction**

I study how built environments shape what people see and do. My work combines
Python-based spatial analysis, street-view computer vision and VR experiments
with architectural research and design.

[简体中文](README.zh-CN.md)

## Selected research

<!-- Add projects using docs/ADDING_PROJECTS.md; keep each block independent. -->
<!-- selected-research:start -->

### Street-view and satellite greenness in Beijing

How does measurement scale change the relationship between visible greenery and
satellite greenness?

- Compared **13,943 fixed paired road segments** at 30, 50 and 100 m buffer radii.
- Combined image deduplication, road matching, area-weighted NDVI aggregation
  and spatial block bootstrap analysis.
- Pearson correlation decreased from **0.545 to 0.312** between 30 and 100 m;
  **20.15%** of roads changed their median-based category.

**Python · GIS · Remote sensing · Spatial statistics**

[Research summary](projects/beijing/README.md) · [Research code & run instructions](projects/beijing/code/README.md) · [Quick check](examples/verify_beijing.py)

### Residential types, street interfaces and greenery in Bang Na

How do residential types and street interfaces relate to visible greenery along
public streets in a peripheral Bangkok station area?

- Analysed **1,156 images, 289 GVI points and 25 residential areas**.
- Combined pretrained segmentation, interface coding, road-network variables
  and regression with HC3 uncertainty estimates.
- Adding interface openness increased adjusted R² from **0.488 to 0.710**;
  the findings describe conditional associations.

**Computer vision · Urban morphology · Statistical modelling**

[Research summary](projects/bangna/README.md) · [Research code & run instructions](projects/bangna/code/README.md) · [Quick check](examples/verify_bangna.py)

### Architectural enclosure and VR climbing decisions

How can a VR climbing task reveal the relationship between architectural
enclosure and route-following decisions?

- Developed a **four-condition VR climbing experiment**, combining Rhino
  scene models, Unreal Engine 5.4 and a Pico headset.
- **Independently implemented the climbing interaction and grip-error
  counting Blueprints**, including route-index comparison and trial completion.
- Connected the experiment to the design of *Twin Cliff* (岩双阙), a climbing
  centre in Chongli, Zhangjiakou.

**Unreal Engine Blueprints · VR interaction · Experimental design · Rhino**

[Thesis & design](projects/vr-climbing/README.md) · [UE implementation & Blueprint evidence](projects/vr-climbing/IMPLEMENTATION.md)

<!-- selected-research:end -->

## Methods and tools

| Area | Tools and practice |
| --- | --- |
| Scientific computing | Python, NumPy, pandas, SciPy; data processing and numerical verification |
| Geospatial analysis | GeoPandas, Shapely, rasterio/GDAL, NetworkX, QGIS |
| Image-based measurement | Pretrained DeepLabV3 / Cityscapes, GluonCV / MXNet |
| VR and spatial prototyping | Unreal Engine 5.4, Blueprints, OpenXR, Rhino 8, Datasmith |
| Research methods | Spatial resampling, robust regression, sensitivity analysis, behavioural experiments |

## Research interests

Urban greenery and environmental perception; residential morphology and street
interfaces; immersive methods for studying human–environment interaction.

The Beijing and Bang Na projects are research manuscripts. The VR project is an
undergraduate thesis in Architecture at Tsinghua University (2025).
See [research and reproducibility notes](docs/RESEARCH_NOTES.md) for definitions,
authorship and the scope of the included code and examples.

[Repository maintenance guide](docs/ADDING_PROJECTS.md)

