# Research and reproducibility notes

[← Research overview](../README.md)

## Authorship and status

- **Beijing:** research manuscript by Zihao Lin, summarised from the October 2026
  manuscript and associated numerical outputs.
- **Bang Na:** research manuscript by Zihao Lin and Lei Shao, summarised from the
  English v4 manuscript dated 22 October 2026 and associated analysis tables.
- **VR climbing:** Zihao Lin's undergraduate thesis and graduation design in
  Architecture at Tsinghua University, 2025, including independent development
  of the climbing interaction and grip-error counting Blueprints.

The profile's education, graduate GPA/rank and 2026 graduate scholarship follow
Zihao Lin's CV dated 24 October 2026. The M.Arch. is in progress, with graduation
expected in June 2027; the B.Arch. was completed in June 2025. Research interests
and experience in affective assessment are also summarised from that CV.

No journal acceptance or publication DOI is asserted by this repository.

## What can be reproduced here

The [Beijing research code](../projects/beijing/code/README.md) recomputes spatial
block-bootstrap intervals, Moran diagnostics and classifications from 13,943
paired roads. The [Bang Na research code](../projects/bangna/code/README.md)
recomputes point-to-area interface aggregation, two main models, seven sensitivity
models and the clustered point model. Both runners call original research
routines and compare their results with archived output tables. Their input
schemas, provenance and validation scope are documented with the code.

Selected upstream kernels and historical workflows are also supplied. The
portfolio update does not rerun image acquisition, semantic segmentation,
satellite preprocessing, full GIS data preparation or manual image coding.
The [compact examples](../examples/README.md) remain as smaller starting points.

The compact Beijing verification script is adapted from the existing research code by
making its input path portable. The compact Bang Na script was prepared for this
portfolio and checked against the original model outputs. Its preparation should
not be confused with the date or authorship of the original study.

The UE contribution is documented with the thesis's original Blueprint figure,
the stated workflow and the retained project structure. No claim is made that a
complete runnable VR application is included in this repository.

## Definitions that matter

- **Beijing GVI:** vegetation + terrain classes. Street-view observations span
  2013–2023; the Landsat scene is from 7 September 2021.
- **Bang Na GVI:** vegetation only, after excluding the bottom 40 pixels of each
  640 × 640 image. Area-level model coefficients are associations.
- **Climbing enclosure:** the experimental scene labels and visible-sky measure
  follow the thesis's operational definition. They should not be silently equated
  with a separately validated hemispherical urban-climate SVF measurement.
- **Climbing statistics:** the archived draft contains discrepancies between
  narrative statistics and its tables. This portfolio presents the design and
  technical contribution without adopting the disputed inferential results.

## Source materials and reuse

Beijing numerical data and the adapted script retain the source package's
[license and attribution notes](../examples/BEIJING_SOURCE_LICENSES.md), including
its CC BY 4.0 scope, OpenStreetMap attribution and USGS Landsat source.

Bang Na authorship is retained. A separate public-data license for those research
materials is not asserted here. The original providers' terms and the authors'
rights continue to apply.

The Beijing project reproduces **Figures 9 and 7** from the manuscript dated
**21 October 2026**, retaining the original Chinese figure labels and adding
English captions. The Bang Na project reproduces **Figures 2 and 5** from the
**22 October 2026 English v4 manuscript**. All four PNG files are unchanged
copies, verified against the images embedded in their respective manuscripts.
Their original legends, intervals and map credits are retained. README display
widths are limited for readability; linked images retain their full resolution.

The climbing-centre views, drawings and experimental-scene images come from the
final presentation set dated **25 May 2025** (`0525_layout`, boards 1–4), checked
against the four supplied PNG boards. The figures were extracted from the matching
PDF and proportionally resized or encoded for web display, without content
retouching. The [visual record](../projects/vr-climbing/VISUALS.md) identifies each
figure's source board. The Blueprint figure comes from the thesis.

The UE materials include Unreal starter content and third-party VR
plugins; those components are not claimed as original work.

This repository contains no participant photographs, participant-level VR records,
raw street-view images, full institutional forms, engine binaries or local
machine configuration files.
