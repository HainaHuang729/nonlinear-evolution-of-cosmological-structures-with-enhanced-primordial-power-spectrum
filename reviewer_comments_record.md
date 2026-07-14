# Reviewer Comments Record

本文档单独记录论文中的审稿评论，便于在正文接受修改、移除评论标记后继续追踪评论来源和处理状态。

## TK-01: Describe the projection figure

- **Reviewer:** TK
- **Location:** `main.tex`, Projection subsection, immediately before Fig. `fig:dark_matter_comparison`
- **Status:** Addressed in blue text; comment retained in the manuscript for confirmation

### Original comment

> We need to describe the figure. For example, we can see blue tilted has more structures, especially at higher redshift. "The present analysis does not measure a subhalo mass function, radial subhalo distribution, or subhalo survival statistic, so the projections are not used as quantitative evidence for subhalo abundance or concentration." is true but the readers understand that. We can say we will quantify these later.

### 中文翻译

需要对这幅图进行描述。例如，可以看出蓝倾模型中存在更多结构，尤其是在较高红移时。原文中关于“本文并未测量子晕质量函数、子晕径向分布或子晕存活统计，因此这些投影图不作为子晕丰度或集中程度的定量证据”的说明本身没有问题，但读者能够理解这一点，无需特别强调。可以改为说明，后文将对图中呈现的差异进行定量分析。

### Comment intent

TK 希望正文直接指出图中可见的物理差异：蓝倾模型具有更明显的小尺度结构，而且这种差异在高红移时更突出。同时，应删去过度防御性的限制说明，转而告诉读者后续章节将使用定量统计量检验这些趋势。

### Implemented response

Projection 小节现已说明：三个模型使用相同初始相位，因此大尺度结构在空间上对应；BT 模型呈现更强的小尺度密度反差和更多精细结构，其中该趋势在高红移、尤其是 \(z=8.52\) 的 BT \(k_p=1\) 模型中最明显。正文和图注还指出，后续将通过晕质量函数、形成历史、晕结构、浓度-质量关系和非线性物质功率谱进行定量比较。

## JC comments

当前 `main.tex` 中没有保留活动的 `\\Jc{...}` 评论。此前 JC 评论对应的修改已并入正文；如需完整保存历史 JC 评论，应再从 Git 历史或旧版 Overleaf 导出文件中恢复。
