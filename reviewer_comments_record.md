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

## TK-02: Acknowledge previous simulation studies

- **Reviewer:** TK
- **Location:** `main.tex`, Introduction, after the opening paragraph
- **Status:** Addressed in blue text; comment retained in the manuscript for confirmation

### Original comment

> For simulations, We have Jianhao paper and \cite{Nadler2025enhanced} (but for zoom-in) and \cite{Hirano15BlueTiltedPPS} (for high redshift) also has simulations, although they are not looking into halo statistics in detail.

### 中文翻译

已有一些相关模拟工作，包括 Jianhao 的论文、采用 zoom-in 模拟的 \(\texttt{Nadler2025enhanced}\)，以及研究高红移结构的 \(\texttt{Hirano15BlueTiltedPPS}\)。虽然这些工作没有详细研究本文所关注的整套晕统计量，但正文仍应承认它们的存在。

### Comment intent

不能笼统地说增强小尺度功率的数值模拟仍然有限，而应先说明已有高红移宇宙学模拟和银河系质量环境的 zoom-in 模拟，再准确指出现有研究尚未系统比较本文使用的多种晕统计量。

### Implemented response

Introduction 现已引用 `Hirano15BlueTiltedPPS`、`Wu25BT` 和 `Nadler2025enhanced`，并将研究空缺限定为：在匹配相位的宇宙学体积中，对晕丰度、形成历史、内部结构和非线性物质功率进行系统比较的工作仍然有限。

## TK-03: Change the input-power-spectrum legend

- **Reviewer:** TK
- **Location:** `main.tex`, caption of Fig. `fig:power_spectrum_comparison`
- **Status:** Deferred at the author's request; figure unchanged

### Original comment

> change the legend.

### 中文翻译

修改图例。

### Comment intent

当前图例中的 `BT(soft)` 和 `BT(deep)` 与正文统一采用的模型名称不一致。预期应改为按 pivot scale 区分的 BT 模型名称。

### Current response

暂不修改 `input-power-spectrum.png` 或其绘图脚本，评论继续保留在正文中。

## JC comments

当前 `main.tex` 中没有保留活动的 `\\Jc{...}` 评论。此前 JC 评论对应的修改已并入正文；如需完整保存历史 JC 评论，应再从 Git 历史或旧版 Overleaf 导出文件中恢复。
