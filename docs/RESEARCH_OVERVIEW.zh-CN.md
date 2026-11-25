# 研究项目与计算方法

[← Profile](../README.md)

**清华大学建筑学硕士研究生 · 城市分析与科学计算**

我通过计算方法研究城市绿化、街道环境与空间体验。项目结合 Python 地理空间分析、
图像测量、统计建模，以及基于 Unreal Engine 的交互实验。

[English](RESEARCH_OVERVIEW.md) · [学术邮箱](mailto:zh-lin21@mails.tsinghua.edu.cn)

## 研究与代码

<!-- selected-research:start -->

### 北京：街景绿化与卫星绿度

空间尺度如何影响街道视角与卫星视角下的绿化测度关系？

- 固定 **13,943 条配对道路**，比较 30、50、100 m 缓冲区，进行空间分块 bootstrap 与空间诊断。
- 提供图像内容去重、NDVI 处理和像元面积加权实现，以及可直接运行的统计分析流程。
- 缓冲区增大时，相关系数由 **0.545 降至 0.312**；**20.15%** 的道路改变中位数分类。

**Python · 地理空间分析 · 空间统计**

[研究与仓库](https://github.com/leolinnnn/multiscale-urban-greenness) · [运行分析](https://github.com/leolinnnn/multiscale-urban-greenness#quick-start)

### Bang Na：街道界面与可见绿化

曼谷外围站点地区的住宅类型和街道界面，与公共街道上的可见绿化有何关系？

- 将 **1,156 张图像、289 个采样点和 25 个居住片区**连接到图像测量、界面编码和空间变量。
- 实现采样点到片区的聚合、HC3 回归、七组敏感性模型及片区聚类稳健的点层级模型。
- 加入界面开放度后，调整后 R² 由 **0.488 升至 0.710**；结果解释为条件关联。

**Python · 图像测量 · 统计建模**

[研究与仓库](https://github.com/leolinnnn/street-interface-greenery) · [运行分析](https://github.com/leolinnnn/street-interface-greenery#quick-start)

### VR 攀岩：建筑围合与决策表现

如何通过交互式攀岩任务研究空间围合与路线遵循决策的关系？

- 将 **四组实验场景**、Rhino 模型、Unreal Engine 5.4 和 Pico 头显组合为 VR 攀岩实验。
- 通过 Blueprint 连接控制器输入、手部与岩点交互、路线序号比较、错误计数和试次结束。
- 展示实验系统，以及研究在张家口崇礼“岩双阙”攀岩中心设计中的应用。

**Unreal Engine Blueprints · VR 交互 · 实验设计**

[仓库与蓝图资产](https://github.com/leolinnnn/ue-vr-climbing-experiment) · [系统实现](https://github.com/leolinnnn/ue-vr-climbing-experiment/blob/main/docs/IMPLEMENTATION.md) · [研究与设计](../projects/vr-climbing/README.md)

<!-- selected-research:end -->

## 计算方法

| 能力 | 实现入口 |
| --- | --- |
| 地理空间计算 | [NDVI 与像元面积加权](https://github.com/leolinnnn/multiscale-urban-greenness/blob/main/docs/IMPLEMENTATION.md)；[道路网络与 POI 变量](https://github.com/leolinnnn/street-interface-greenery/blob/main/docs/IMPLEMENTATION.md) |
| 统计计算 | [空间 bootstrap 与 Moran's I](https://github.com/leolinnnn/multiscale-urban-greenness/blob/main/src/spatial_statistics.py)；[OLS、HC3 与模型诊断](https://github.com/leolinnnn/street-interface-greenery/blob/main/src/regression.py) |
| 图像测量 | [类别比例、裁切与图像→采样点→片区聚合](https://github.com/leolinnnn/street-interface-greenery/blob/main/src/segmentation_metrics.py) |
| 交互系统 | [Blueprint 原始资产、交互与实验控制](https://github.com/leolinnnn/ue-vr-climbing-experiment/blob/main/docs/IMPLEMENTATION.md) |

## 教育与联系

**清华大学建筑学院**  
建筑学硕士，2025–2027（预计）· 建筑学学士，2021–2025。  
研究生 GPA **4.00/4.00**，排名 **1/101** · **2026 年研究生国家奖学金**。

[学术邮箱](mailto:zh-lin21@mails.tsinghua.edu.cn) · [研究记录](RESEARCH_NOTES.md)
