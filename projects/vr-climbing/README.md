# Architectural enclosure and VR climbing decisions

[← Research overview](../../README.md)

**Zihao Lin · Undergraduate thesis and graduation design · 2025**  
School of Architecture, Tsinghua University. Supervisor: 张利 (Zhang Li).

## Research question

How can a VR climbing task help investigate the relationship between architectural
enclosure and route-following decisions?

The project connects an architectural proposal, *Twin Cliff* (岩双阙 / Yan Shuang Que), in
Chongli, Zhangjiakou, with a behavioural experiment. A relatively enclosed training
hall and an open competition hall provide the spatial basis for the study.

## My contribution

- Architectural design and Rhino modelling of the climbing-centre proposal and
  experimental scenes.
- Independent development of the Unreal Engine climbing interaction and
  grip-error counting Blueprints.
- Experiment design linking scene conditions, a reference route and observable
  grip errors.
- Organisation of the VR study, analysis of the recorded results and integration
  of the research with architectural design development.

## Experimental design

| Component | Implementation |
| --- | --- |
| Scene conditions | Three competition-space conditions labelled 10%, 40% and 70% visible sky, plus a training-space condition |
| Environment | Rhino 8 models, Unreal Engine 5.4, Pico headset and PC streaming |
| Task | Follow a reference climbing route, with up to 30 grip events per trial |
| Behavioural measure | Grip error count, operationalised through route-index comparison |
| Analysis materials | Recorded observations, Jamovi output, thesis and defence presentation |

The thesis reports 20 recruited participants; its displayed result table contains
16 participant records per condition. This is an exploratory study of a virtual
task. It does not establish performance improvements in real or elite climbing.

| Competition-space scene | Training-space scene |
| --- | --- |
| ![UE competition-space scene with a glazed roof and climbing wall](../../assets/vr-climbing/scene-competition-a.jpg) | ![UE training-space scene enclosed by tall walls with a roof opening](../../assets/vr-climbing/scene-training.jpg) |

Experimental environments reproduced from the final presentation board.
[View all four scenes and the reference-route display](VISUALS.md#experimental-scenes).

## Programming evidence

The implementation links controller input, hand/hold interaction, route labels,
error accumulation and trial completion.

[Read the implementation note and view the original Blueprint figure](IMPLEMENTATION.md).

## Architectural outcome

![Final exterior of Twin Cliff: a faceted training hall and glazed competition hall connected by a landscape platform](../../assets/vr-climbing/final-exterior.jpg)

**Twin Cliff — final design, 25 May 2025.** Exterior perspective from board 1 of
the final drawing set. The proposal combines contrasting training and competition
spaces with a landscape platform in Zhangjiakou's Winter Olympic venue context.

[View the final site plan, section and interior perspectives](VISUALS.md).

## Research record

**Thesis:** 建筑空间围合度对攀岩决策表现的影响研究  
*Architectural enclosure and climbing decision performance* (English descriptive title).

**Design:** 岩双阙——基于空间形态–攀岩决策表现耦合模型的张家口攀岩中心设计.

This summary focuses on the experimental design, implemented system and
architectural outcome. See the [research notes](../../docs/RESEARCH_NOTES.md)
for the scope of the archived statistical results.
