# Adding projects / 新增项目指南

[← Research overview](../README.md)

The homepage uses repeatable Markdown project blocks. Each project has its own
directory, so new work can be added without changing the page layout or existing
project links. No website build, JavaScript framework or fixed project count is
required.

## 统一版式

每个主页项目块保持相同顺序：**标题 → 一句研究问题 → 三条证据 → 工具 → 材料链接**。
三条证据依次说明研究对象或个人工作、方法或实现、结果或交付物。
英文块以约 70–110 词为宜。没有定量结果的项目可写可核查的系统、数据或设计成果。
标题不编号，因此新增、排序或调整精选项目都不需要重排编号。

```markdown
### Project title

One sentence stating the research question or technical problem.

- Describe the study scope or your concrete contribution.
- Explain the key method or implementation.
- State a verified result or deliverable, with its scope.

**Tool or method · Tool or method · Tool or method**

[Research summary](projects/project-slug/README.md) · [Code](projects/project-slug/src/analysis.py)
```

模板中的名称、路径和内容需要替换；只保留已经存在的材料链接。

## 添加步骤

1. 在 `projects/` 下创建简短的英文小写连字符目录，例如 `urban-heat`。
2. 复制 [项目说明模板](../templates/project/README.md) 到新目录，命名为 `README.md`，
   填入问题、贡献、方法、成果、运行方式和研究状态。
3. 在英文主页 `Selected research` 的注释标记之间插入一个上述项目块；同步更新中文主页。
   项目顺序由研究相关性决定，无须改变其他项目。
4. 代码可放在新项目的 `src/`，轻量示例数据放在 `data/`，图片放在 `assets/`。
   若代码已经维护在独立仓库，直接链接该仓库。当前共享的 `examples/` 目录仍可继续使用。
5. 在 [研究与复现说明](RESEARCH_NOTES.md) 中补充作者、成果状态和复现范围。
   只有新增项目实际使用了新方法时，才扩展主页的工具表。
6. 在 GitHub 的 Markdown 预览中检查链接、图片和段落；运行该项目提供的示例，再提交修改。

```text
README.md                    English overview
README.zh-CN.md              Chinese overview
projects/
  beijing/README.md
  bangna/README.md
  vr-climbing/README.md
  project-slug/              Future project; create when ready
    README.md
    src/                    Optional implementation
    data/                   Optional shareable example data
    assets/                 Optional figures
templates/project/README.md  Reusable detail-page template
docs/                       Research notes and this guide
```

## 保持主页简洁

暂未完成的项目不用预留空卡片或写 “Coming soon”。完成后直接添加同版式项目块。
当项目明显增多时，可将主页保留为 4–6 个精选项目，再新建 `projects/README.md` 作为完整索引；
现有项目路径保持不变。发表状态变化时更新对应项目说明和研究记录，不需要重做主页。

论文、合作开发和个人实现分别注明实际贡献；研究稿、预印本与正式发表分别标明。
复现链接应说明从哪一步开始以及能复现什么。发布素材延续各项目已有的来源与许可说明。
