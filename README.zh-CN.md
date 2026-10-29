# 林子豪 | Zihao Lin

**清华大学建筑学硕士在读 · 计算城市研究**

我具有建筑学背景，研究高密度建成环境中的可见绿量与空间体验。研究方法结合 Python、街景计算机视觉、GIS 与空间统计，以及情感评价和沉浸式 VR 实验。

[English](README.md)

## 学术背景

| 学位 | 院校 | 时间 |
| --- | --- | --- |
| 建筑学硕士 | 清华大学 | 2025–2027（预计） |
| 建筑学学士 | 清华大学 | 2021–2025 |

硕士 GPA **4.00/4.00**，排名 **1/101**；获 **2026 年研究生国家奖学金**。以上信息依据 2026 年 10 月 CV。

## 代表项目

<!-- 按 docs/ADDING_PROJECTS.md 添加独立项目块；同步英文主页。 -->
<!-- selected-research:start -->

### 北京街景绿量与卫星绿量的尺度比较

测量尺度如何改变街景绿量与卫星绿量的关系？

- 在 **13,943 条固定配对道路**上比较 30、50、100 m 缓冲尺度。
- 结合影像去重、道路匹配、面积加权 NDVI 汇总和空间分块自助法。
- 30→100 m 时，Pearson 相关系数由 **0.545 降至 0.312**，**20.15%** 的道路发生基于样本中位数的分类转移。

**Python · GIS · 遥感 · 空间统计**

[研究说明](projects/beijing/README.md) · [研究代码与运行说明](projects/beijing/code/README.md) · [快速核验](examples/verify_beijing.py)

### Bang Na 住宅类型、街道界面与绿视率

曼谷外围轨道站区的住宅类型和街道界面如何与可见绿量关联？

- 分析 **1,156 张图像、289 个绿视率观测点和 25 个住宅片区**。
- 结合预训练语义分割、界面编码、路网变量与 HC3 回归。
- 加入界面开放度后，模型调整 R² 由 **0.488 增至 0.710**；结果表述为条件关联。

**计算机视觉 · 城市形态 · 统计建模**

[研究说明](projects/bangna/README.md) · [研究代码与运行说明](projects/bangna/code/README.md) · [快速核验](examples/verify_bangna.py)

### 建筑空间围合与 VR 攀岩决策

VR 攀岩任务如何帮助研究建筑空间围合与路线跟随决策的关系？

- 结合 Rhino 场景、Unreal Engine 5.4 与 Pico 头显，组织四条件 VR 攀岩实验。
- **独立实现攀岩交互与抓握错误计数蓝图**，包括路线编号比较和实验结束逻辑。
- 将实验与张家口崇礼“岩双阙”（Twin Cliff）攀岩中心设计相结合，完成清华大学建筑学本科论文与毕业设计（2025）。

**Unreal Engine 蓝图 · VR 交互 · 实验设计 · Rhino**

[论文与设计说明](projects/vr-climbing/README.md) · [UE 实现与蓝图证据](projects/vr-climbing/IMPLEMENTATION.md)

<!-- selected-research:end -->

## 方法与工具

| 方向 | 工具与方法 |
| --- | --- |
| 科学计算 | Python、NumPy、pandas、SciPy |
| 空间分析 | GeoPandas、Shapely、rasterio/GDAL、NetworkX、QGIS |
| 街景测量 | 预训练 DeepLabV3 / Cityscapes、GluonCV / MXNet |
| VR 与空间原型 | Unreal Engine 5.4、Blueprints、OpenXR、Rhino 8、Datasmith |
| 研究分析 | 空间重抽样、稳健回归、敏感性分析、行为实验 |

## 研究兴趣

植被配置与室内外视觉联系，以及高密度建成环境中的空间感知和情感体验。

北京与 Bang Na 项目目前按研究稿展示。数值、作者及复算范围见[研究说明](docs/RESEARCH_NOTES.md)。

[仓库维护与新增项目指南](docs/ADDING_PROJECTS.md)

