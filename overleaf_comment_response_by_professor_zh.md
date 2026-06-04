# 按老板评论逐条说明修改内容

说明：

- 这个版本的逻辑不是“修改前/修改后”，而是“老板每条评论 -> 我们做了什么 -> 改在什么地方”。
- 行号基于当前本地稿件 `main.tex`。
- `已修改` 表示正文里已经有对应改动；`部分修改` 表示已经处理了一部分但还不够；`未修改` 表示正文还没有按该评论改；`需要数据/图` 表示不能只靠文字修改解决；`需原文锚点` 表示导出的 Overleaf 评论没有包含原高亮位置，无法准确判断。

## 原文和修改后正文对照

注意：Overleaf 导出的评论文本没有保留每条评论对应的原始高亮范围。因此，下面分两类：

- **已可精确恢复**：能从当前 Git diff 或红字占位中确定原文和修改后文本。
- **建议下一轮修改**：正文当前还没改，但我根据老板评论列出“当前原文”和“建议修改后”。

### 评论 3 / 红字 `quantify`：摘要中量化 nonlinear matter-power response

老板评论：

```text
I think these can be more qualitative in the abstract
```

后续红字要求：

```text
quantify
```

原文：

```tex
While the blue-tilted model significantly boosts the non-linear matter power spectrum for $k> k_p$, the enhancement diminishes significantly at low redshift. {\color{red} quantify}
```

修改后：

```tex
\revisionreplace{For the field-level statistic, the nonlinear matter-power response is more modest but measurable: in the fiducial \(25\,h^{-1}{\rm Mpc}\) box at \(z=0\), BT\_soft reaches \(P_{\rm BT}/P_{\rm PL}=1.17\) at \(k=20\,h\,{\rm Mpc}^{-1}\) and \(1.34\) at \(k=40\,h\,{\rm Mpc}^{-1}\), whereas BT\_deep remains close to unity at both wavenumbers.}{While the blue-tilted model significantly boosts the non-linear matter power spectrum for \(k>k_p\), the enhancement diminishes significantly at low redshift.}
```

位置：`main.tex:111`。  
剩余问题：`field-level statistic` 仍需按评论 53-54 改成 summary-statistic 表达。

### 评论 4-6：Introduction 高红移/JWST 动机重写

老板评论：

```text
these are obsoletes. But there are new higher redshift tensions.
Add more relevant reference.
need rewrite
```

原文：

```tex
The standard cosmological model, combining a nearly power-law primordial power spectrum with the $\Lambda$ Cold Dark Matter ($\Lambda$CDM) paradigm, provides an accurate description of the Universe on large scales ($>1 {\rm Mpc})$. Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-$\alpha$ forest are consistent with the standard cosmological model \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On the other hand, the constraints on small scales are weaker. For example, there are potential small-scale tensions in cosmology model such as the missing-satellites, core-cusp, and too-big-to-fail problems \citep{Bullock17smallscalechallenges,Sales22challenges}, although they are subject to the uncertainties in baryonic physics \citep{Benson2002reionization,Chan2015corecusp}. At the same time, early JWST measurements have revealed unexpectedly abundant and potentially massive galaxy candidates at $z\gtrsim 8$--$10$ \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \cite{Parashari23JWSTPPS,Hira24bluetilt},but high redshift baryonic physics is also potential solutions, e.g., evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.
```

修改后：

```tex
\revisionblue{The standard cosmological model, combining a nearly power-law primordial power spectrum with the \(\Lambda\) Cold Dark Matter (\(\Lambda\)CDM) paradigm, provides an accurate description of the Universe on large scales (\(>1\,{\rm Mpc}\)). Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-\(\alpha\) forest are consistent with this picture \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On smaller scales, however, constraints are weaker. Potential small-scale tensions such as the missing-satellites, core-cusp, and too-big-to-fail problems have motivated departures from the simplest cold-dark-matter picture \citep{Bullock17smallscalechallenges,Sales22challenges}, although baryonic physics can substantially affect these comparisons \citep{Benson2002reionization,Chan2015corecusp}. Early JWST measurements have also revealed unexpectedly abundant and potentially massive galaxy candidates at \(z\gtrsim 8\)--\(10\) \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \citep{Parashari23JWSTPPS,Hira24bluetilt}; however, high-redshift baryonic physics and observational effects remain plausible explanations, including evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.}
```

位置：`main.tex:126`。

### 评论 5：补充 enhanced small-scale power 的理论来源和引用

老板红字原文：

```tex
{\color{red} add motivations for enhanced power spectrum: e.g. ``the enhanced small-scale power spectrum can stem from a wide range of alternative cosmological theories, including warm inflation \citep{Arya20WarmInflation}, axion models with hyperbolic field-space geometry \cite{Sai26BlueTilt}, and multi-field hybrid inflation models that can naturally generate a broken power-law, blue-tilted spectrum \citep{Linde94Hybridinflation, Wang24BTinflationtheory, Wang25HybridInflation}. The discreteness of primordial black holes can also induce an isocurvature term that enhances especially the small-scale spectrum \cite{Inman2019PBHBT}.'' need rephase. }
```

修改后：

```tex
\revisionblue{Enhanced small-scale power can arise in several classes of beyond-minimal early-Universe scenarios. Examples include warm-inflation models that amplify curvature perturbations \citep{Arya20WarmInflation}, axion models with nontrivial field-space geometry that can generate blue spectra \citep{Sai26BlueTilt}, and multi-field or hybrid-inflation constructions capable of producing broken-power-law enhancements \citep{Linde94Hybridinflation,Wang24BTinflationtheory,Wang25HybridInflation}. A distinct route is provided by a discrete population of primordial black holes (PBHs), whose Poisson fluctuations source an isocurvature contribution to the small-scale matter power spectrum \citep{Inman2019PBHBT}. In this work we do not attempt to distinguish among these mechanisms; instead, we use the blue-tilted spectrum as a phenomenological input model for testing the gravitational response to enhanced small-scale power.}
```

位置：`main.tex:133`；新增参考文献：`main.bib` 中 `Inman2019PBHBT`。

### 评论 6：解释 blue-tilted 是什么

老板红字原文：

```tex
We use a blue-tilted (BT) power spectrum following the previous literatures \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}. {\color{red} need to describe what blue tilted is.} Note that the BT models are phenomenological models instead of directly deriving from, e.g., any inflationary model.
```

修改后：

```tex
\revisionblue{Following previous literature \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}, we use ``blue-tilted'' (BT) to denote a broken-power-law input spectrum whose large-scale part follows the standard nearly scale-invariant slope, while above a pivot wavenumber \(k_p\) the effective high-\(k\) slope is increased to \(m_s>n_s\). In this sense the tilt is ``blue'' because power is shifted toward shorter wavelengths, or larger \(k\), increasing the small-scale primordial matter power relative to PL. The BT models are phenomenological benchmarks rather than direct fits to any one inflationary model.}
```

位置：`main.tex:138`。

### 红字：补充论文结构 roadmap

原文：

```tex
{\color{red} State what we do in different sections}
```

修改后：

```tex
\revisionblue{The rest of this paper is organized as follows. Section~\ref{sec:theory} defines the PL and BT input spectra and explains how the pivot scale changes the initial matter field. Section~\ref{sec:numerical} describes the simulation suite, halo catalog construction, analysis definitions, and numerical interpretation ranges. Section~\ref{sec:results} presents the halo abundance, assembly, concentration, and nonlinear-power responses. Section~\ref{sec:discussion} discusses the main numerical and modeling limitations and connects the benchmark diagnostics to observations. Section~\ref{sec:conclusion} summarizes the quantitative trends and the analytic ingredients that should be carried forward.}
```

位置：`main.tex:151`。

### 表格命名：修正 `Blue-tiled`

原文：

```tex
Blue-tiled Soft (BT\_soft) & 1 & 1.5 \\
Blue-tiled Deep (BT\_deep) & 10 & 1.5 \\
```

修改后：

```tex
\revisionreplace{Blue-tilted Soft (BT\_soft)}{Blue-tiled Soft (BT\_soft)} & 1 & 1.5 \\
\revisionreplace{Blue-tilted Deep (BT\_deep)}{Blue-tiled Deep (BT\_deep)} & 10 & 1.5 \\
```

位置：`main.tex:223-224`。

### 评论 10-11：sigma8 是否相同

当前原文：

```tex
The BT spectra use the same background cosmology and large-scale normalization as PL; their matter power differs only above the pivot scale \(k_p\). Thus, \(\sigma_8\) is quoted here as the baseline normalization rather than as an independently refitted parameter for each BT spectrum.
```

建议修改后：

```tex
\revisionreplace{The PL and BT initial conditions use the same \(\sigma_8=0.8111\) normalization and the same background cosmology; the BT runs differ from PL only through the transfer-function modification above \(k_p\). Thus, \(\sigma_8\) is held fixed across the compared models rather than independently refitted for each BT spectrum.}{The BT spectra use the same background cosmology and large-scale normalization as PL; their matter power differs only above the pivot scale \(k_p\). Thus, \(\sigma_8\) is quoted here as the baseline normalization rather than as an independently refitted parameter for each BT spectrum.}
```

位置：`main.tex:209`。  
注意：应用前需要确认 MonofonIC 设置确实是 same sigma8。

### 评论 14：用主动语态 `we modify`

当前原文：

```tex
For the BT models, the implementation modifies the transfer function above \(k_p\), rather than introducing a separate explicitly normalized curvature-spectrum amplitude, so that the resulting input linear matter power spectrum at \(z_i=200\) follows the broken-power-law enhancement described in Section~\ref{sec:theory}.
```

建议修改后：

```tex
\revisionreplace{For the BT models, we modify the transfer function above \(k_p\), rather than introducing a separate explicitly normalized curvature-spectrum amplitude, so that the resulting input linear matter power spectrum at \(z_i=200\) follows the broken-power-law enhancement described in Section~\ref{sec:theory}.}{For the BT models, the implementation modifies the transfer function above \(k_p\), rather than introducing a separate explicitly normalized curvature-spectrum amplitude, so that the resulting input linear matter power spectrum at \(z_i=200\) follows the broken-power-law enhancement described in Section~\ref{sec:theory}.}
```

位置：`main.tex:235`。

### 评论 27：`direct model response` 不清楚

当前原文：

```tex
The lower ratio panels show the direct model response, \(f_{\rm BT}(M)/f_{\rm PL}(M)\), computed in the same FOF mass bins and plotted where both the BT and PL bins are populated.
```

建议修改后：

```tex
\revisionreplace{The lower ratio panels show the BT abundance relative to PL, \(f_{\rm BT}(M)/f_{\rm PL}(M)\), computed in the same FOF mass bins and plotted where both the BT and PL bins are populated.}{The lower ratio panels show the direct model response, \(f_{\rm BT}(M)/f_{\rm PL}(M)\), computed in the same FOF mass bins and plotted where both the BT and PL bins are populated.}
```

位置：`main.tex:337`。

### 评论 37-40：NFW diagnostic 名称和图注

当前原文：

```tex
\subsubsection{NFW-Equivalent Compactness Diagnostic\label{subsub:DensityProfile}}
```

建议修改后：

```tex
\subsubsection{Concentration-Derived NFW Density Profiles\label{subsub:DensityProfile}}
```

当前图注原文：

```tex
NFW-equivalent compactness curves reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and concentrations for the PL, BT\_soft, and BT\_deep models.
```

建议修改后：

```tex
\revisionreplace{Concentration-derived NFW density profiles reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and catalog concentrations for the PL, BT\_soft, and BT\_deep models.}{NFW-equivalent compactness curves reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and concentrations for the PL, BT\_soft, and BT\_deep models.}
```

位置：`main.tex:382`, `391`。

### 评论 47-50：Discussion physical interpretation 句子不自然

当前原文：

```tex
Increasing the small-scale input matter power at \(z_i=200\) raises the initial amplitude of low-mass density fluctuations, so these perturbations cross the collapse threshold earlier than in the PL model. This earlier collapse first appears as a high-redshift abundance excess and then leaves a lower-redshift structural imprint.
```

建议修改后：

```tex
\revisionreplace{The enhanced primordial power spectrum increases the amplitude of small-scale density fluctuations in the initial conditions. These early density fluctuations trigger earlier collapse at high redshift, producing an excess of low-mass halos first and leaving a later imprint on halo assembly histories and concentrations.}{Increasing the small-scale input matter power at \(z_i=200\) raises the initial amplitude of low-mass density fluctuations, so these perturbations cross the collapse threshold earlier than in the PL model. This earlier collapse first appears as a high-redshift abundance excess and then leaves a lower-redshift structural imprint.}
```

位置：`main.tex:447`。

### 评论 51：`uniform rescaling` 不清楚

当前原文：

```tex
The signal is not simply a uniform rescaling of all nonlinear statistics.
```

建议修改后：

```tex
\revisionreplace{The response is not the same for every diagnostic: it depends on pivot scale, redshift, halo mass, and whether the statistic measures abundance, assembly, concentration, or \(P(k)\).}{The signal is not simply a uniform rescaling of all nonlinear statistics.}
```

位置：`main.tex:449`。

### 评论 53-54：power spectrum 不是 field-level，而是 summary statistic

当前原文：

```tex
The nonlinear matter power spectrum provides a complementary field-level view.
```

建议修改后：

```tex
\revisionreplace{The nonlinear matter power spectrum provides a complementary summary statistic measured from the particle density field.}{The nonlinear matter power spectrum provides a complementary field-level view.}
```

位置：`main.tex:451`。  
同类位置还包括：`main.tex:111`, `289`, `294`, `429`, `438`, `467`, `505`。

### 评论 60-62：response table 应放入 conclusion bullet points

当前原文：

```tex
Table~\ref{tab:main_response_summary} collects representative response amplitudes for the same trends. The main conclusions, with the corresponding result sections and figures, are as follows:
```

建议修改后：

```tex
\revisionreplace{The main conclusions, with representative response amplitudes and the corresponding result sections and figures, are as follows:}{Table~\ref{tab:main_response_summary} collects representative response amplitudes for the same trends. The main conclusions, with the corresponding result sections and figures, are as follows:}
```

位置：`main.tex:500`。  
还需要删除或注释掉 `tab:main_response_summary` 表格：`main.tex:477-493`，并把表里的数值合并进 bullet points。

### 评论 66：equation reference 不要括号

当前原文：

```tex
Eq.~(\ref{eq:bt_input_power})
```

建议修改后：

```tex
Eq.~\ref{eq:bt_input_power}
```

位置：`main.tex:508` 及全文所有类似位置。

### 评论 80：final sentence 太弱

当前原文：

```tex
They are relevant to JWST-era high-redshift galaxy studies, dwarf-galaxy structure, strong-lensing probes of low-mass structure, 21 cm forecasts, and small-scale clustering measurements, but each application requires additional modeling of baryons, reionization, galaxy selection, and survey response.
```

建议修改后：

```tex
\revisionreplace{By identifying the halo masses, redshifts, and wavenumbers where the dark-matter response is largest, these simulations provide a concrete target set for future hydrodynamic simulations, semi-analytic modeling, and multi-probe tests of enhanced small-scale primordial power.}{They are relevant to JWST-era high-redshift galaxy studies, dwarf-galaxy structure, strong-lensing probes of low-mass structure, 21 cm forecasts, and small-scale clustering measurements, but each application requires additional modeling of baryons, reionization, galaxy selection, and survey response.}
```

位置：`main.tex:510`。

### 评论 81-82：Data Availability 加 GitHub/Zenodo

当前原文：

```tex
The reduced data products supporting the figures and quantitative comparisons in this article are openly available in the \texttt{public\_data/} directory accompanying this manuscript.
```

建议修改后：

```tex
\revisionreplace{The reduced data products supporting the figures and quantitative comparisons in this article are available in the project GitHub repository at \url{<GITHUB_URL>} and will be archived on Zenodo at \url{<ZENODO_URL>} if a DOI is assigned.}{The reduced data products supporting the figures and quantitative comparisons in this article are openly available in the \texttt{public\_data/} directory accompanying this manuscript.}
```

位置：`main.tex:514`。  
需要你提供真实 GitHub/Zenodo 地址，或者先使用占位符。

## 快速总览

| 编号 | 老板评论 | 状态 | 已经修改了什么 | 位置 | 下一步 |
|---:|---|---|---|---|---|
| 1 | `primordial matter power spectrum` | 部分修改 | 文中保留并使用了该概念，但和 `primordial power spectrum`、`input matter power spectrum` 仍混用 | `main.tex:109`, `126`, `147`, `149` | 做术语统一 pass |
| 2 | `primordial power spectrum` | 部分修改 | Introduction 和理论部分已有该表达 | `main.tex:109`, `126`, `147` | 明确何时用 `primordial power spectrum`，何时用 simulation input |
| 3 | abstract 可更 qualitative | 备注 | 后续又有 `quantify` 要求，目前摘要改成带数值 | `main.tex:111` | 不建议删数值；可把第一句写得更 qualitative |
| 4 | 旧 tension 过时，需要高红移 tension | 已修改 | Introduction 改为突出 JWST 高红移星系候选体，同时保留小尺度问题背景 | `main.tex:126` | 无 |
| 5 | Add more relevant reference | 已修改 | 增加 JWST、BT/PPS、baryonic caveat、PBH、观测探针等引用 | `main.tex:126`, `133`, `138`, `147`；`main.bib` | 无 |
| 6 | need rewrite | 部分修改 | Introduction 多段已重写为蓝色；但 Discussion/Conclusion 还有不自然句子 | `main.tex:126`, `133`, `138`, `151` | 继续改评论 47-52、60-62、80 |
| 7 | We haven't shown these in our paper | 部分修改 | 已补充说明 projection map 只作视觉比较，不用来声称 subhalo abundance/concentration | `main.tex:322`, `327` | 如果原锚点不是 subhalo，需要回 Overleaf 确认 |
| 8 | MonofonIC 后 matter spectrum/seed 表述不准确 | 部分修改 | IC 段说明通过 MonofonIC/transfer function，且 matched seed/same phases | `main.tex:235` | 还需更谨慎地区分 primordial PPS 和 `z_i=200` input |
| 9 | need rewrite | 部分修改 | IC 段已加长说明，但仍略笨重 | `main.tex:235` | 重写为更直接版本 |
| 10 | sigma8 是否相同 | 部分修改 | 写了 PL baseline `sigma_8=0.8111`，BT 与 PL 同背景和大尺度归一化 | `main.tex:207-209` | 需明确写 “PL 和 BT 使用同一 sigma8”，前提是确认事实 |
| 11 | 正确做法是 PL/BT same sigma8 | 部分修改 | 同上 | `main.tex:207-209` | 同上 |
| 12 | 表格可和 simulation table 合并，参考 arXiv:1112.0330v2 | 未修改 | 只修了模型表拼写，未合并表格 | `main.tex:213-227` | 合并 input-power model table 和 simulation table |
| 13 | 句子 clumsy/strange | 部分修改 | 若指 Introduction，已有重写；若指后文，仍有 clumsy 句子 | 多处 | 需要 prose pass |
| 14 | 用 “we modify”，不要 “implementation modifies” | 未修改 | 当前仍写 `the implementation modifies` | `main.tex:235` | 改为 `For the BT models, we modify...` |
| 15 | `input matter power spectrum` 用法不一致 | 未修改 | 当前仍多处混用 | `main.tex:149`, `214`, `235`, `337`, `447` | 做全文术语统一 |
| 16 | `the shape of primordial power spectrum` 更好 | 部分修改 | 相关概念已出现，但还没按该规则统一替换 | `main.tex:147`, `149` | 结合评论 15/45 一起改 |
| 17 | 句子 strange，需要更直接 | 部分修改 | 部分段落已经更直接，但缺原锚点 | 可能是 `main.tex:235` 或 `149` | 需按原锚点确认 |
| 18 | “test the effect of enhanced primordial power spectrum, given same initial phases” | 部分修改 | 已说明 same random seed/same phases，控制变量是 input spectrum shape | `main.tex:235` | 可把这句话直接并入 IC 段 |
| 19 | 比较 particle scale 和 enhancement scale | 部分修改 | 已加 Nyquist scale 和 `Delta^2` consistency check | `main.tex:237`, figure caption near `240` | 需要更直接比较 enhancement scale 与分辨率 |
| 20 | 后面用了其他 mass definitions | 已修改 | 增加 mass-definition 总说明，区分 FOF、M200m、M200c、power spectrum | `main.tex:289` | 无 |
| 21 | discuss binning | 已修改 | power-spectrum 方法段加入 mesh、binning、median/log-bin 说明 | `main.tex:429` | 无 |
| 22 | No need to mention | 需原文锚点 | 无法确定原高亮文字 | 不明 | 需回 Overleaf 看锚点 |
| 23 | particle mass 已在表中显示 | 需原文锚点 | 当前正文/图注仍多次重复 particle mass | `main.tex:287`, `333`, `355`, `359`, `423` | 删除冗余处，但保留 threshold 解释 |
| 24 | This is mentioned already | 需原文锚点 | 不确定重复对象 | 不明 | 需回 Overleaf 看锚点 |
| 25 | mentioned already, wording strange | 需原文锚点 | 不确定重复对象 | 不明 | 需回 Overleaf 看锚点 |
| 26 | define M200c | 已修改 | 定义并说明 M200c/R200c/c200c 与 SOAP SO/200crit | `main.tex:287`, `289`, `359`, `397-412` | 无 |
| 27 | ratio between PL and BT，`direct model response` 不清楚 | 未修改 | 当前仍写 `direct model response` | `main.tex:337`, `355`, `364`, `438` | 改成 `BT abundance relative to PL` / `BT/PL ratio` |
| 28 | define B16 in text | 已修改 | B16 定义为 Bocquet et al. fitting function | `main.tex:335`, `359` | 无 |
| 29 | Not defined yet | 已修改 | likely 指 B16/M200c，当前均已定义 | `main.tex:335`, `359` | 无 |
| 30 | Add mass accretion rate study | 需要数据/图 | 正文还没有 mass-accretion-rate study | 无 | 需要从 merger history 新算诊断 |
| 31 | details can go in text or appendix | 部分修改 | HMR 细节已写清，并把 gap-stitching 系统误差放 Appendix | `main.tex:369`, Appendix | 可再压缩 caption/method 细节 |
| 32 | between what and BK09 | 部分修改 | 图注说明 lower panel 是 relative to BK09 | `main.tex:376` | 仍需解释为什么和 BK09 比 |
| 33 | why compare to BK09 | 未修改 | 当前仍缺少比较 BK09 的理由 | `main.tex:376` | 加一句 BK09/COCO 是外部 reference relation 的理由，或删去 lower panel |
| 34 | 应比较 BT to PL | 部分修改 | 文中有 BT 相对 PL 的数值，但图 lower panel 仍是相对 BK09 | `main.tex:371`, `376` | 改图或图注，突出 BT-PL comparison |
| 35 | 加 too-few-particles shaded region | 已修改 | HMF 图注解释 gray band 是 20-particle 到 adopted cut 区域 | `main.tex:355` | 无 |
| 36 | 这只是 DM halo density profile 和 NFW profile | 部分修改 | 已说明是 concentration-derived/reconstructed NFW profiles | `main.tex:383`, `391` | section title 仍需改名 |
| 37 | `NFW-equivalent compactness curves` strange | 未修改 | 该说法仍出现在标题、表格、图注、结论 | `main.tex:309`, `382`, `391`, `504`, `514` | 改为 `Concentration-derived NFW density profiles` |
| 38 | 不是 radial profiles，是 fitted concentration 的 NFW profile | 已修改 | 已明确不是 direct particle-count radial stacks | `main.tex:383`, `391` | 无 |
| 39 | 容易误导 points/lines 含义 | 部分修改 | 图注说明 markers 不是 individual halos，line/marker 都由 catalog concentration 重建 | `main.tex:391` | 图本身 label 可能还要改 |
| 40 | 读者想看 NFW 描述 BT 准确性 | 部分修改 | 当前只解释不是直接 profile-fit accuracy test | `main.tex:383`, `391` | 若要真正回应，需新增 profile residual/fit accuracy |
| 41 | figures 加 error bar | 已修改 | HMF 有 Poisson；HMR/concentration 有 16-84 percentile scatter | `main.tex:333`, `369`, `395`, `423` | NFW reconstructed profile 图若需 uncertainty band 另算 |
| 42 | add scatter in concentration | 部分修改 | concentration 图用 16-84 percentile scatter | `main.tex:395`, `423` | 还没有单独讨论 scatter 结果 |
| 43 | define D19 and I21 | 已修改 | 已用 full names Diemer & Joyce、Ishiyama et al. | `main.tex:395` | 无 |
| 44 | shaded region represented? | 已修改 | power-spectrum 图注说明 gray high-k region 和 unity shaded band | `main.tex:438` | 无 |
| 45 | most input matter power -> primordial power spectrum | 未修改 | 仍有大量 `input matter/input linear matter` 表达 | `main.tex:149`, `214`, `235`, `337`, `447`, `451` | 全文术语 pass |
| 46 | This is right | 备注 | 正面评论，无需修改 | 无 | 无 |
| 47 | sentences unnatural | 未修改 | Discussion 物理解释仍不自然 | `main.tex:447` | 改写 physical interpretation |
| 48 | issue is not direct | 未修改 | 当前 causal chain 仍写得比较直接 | `main.tex:447` | 软化为 “enhanced PPS -> IC fluctuations -> earlier collapse” |
| 49 | `This earlier collapse first appears...` clumsy | 未修改 | 原句仍在 | `main.tex:447` | 用评论 50 的思路替换 |
| 50 | “These early density fluctuations...” clearer | 未修改 | 建议句还未采用 | `main.tex:447` | 直接替换 |
| 51 | `rescaling of all nonlinear statistics` unclear | 部分修改 | 当前仍保留该句，但后一句解释了 redshift/mass/diagnostic dependence | `main.tex:449` | 改成更具体的 diagnostic-dependent response |
| 52 | This is not proved? | 部分修改 | 当前用 `supports the interpretation`，但仍可能偏强 | `main.tex:451` | 进一步软化为 interpretation，不说 proof |
| 53 | power spectrum 不是 field-level | 未修改 | `field-level` 仍多处出现，包括新增 abstract 句 | `main.tex:111`, `289`, `294`, `429`, `438`, `451`, `505` | 全部改为 summary statistic / measured from density field |
| 54 | 它是 summary statistics | 未修改 | 同评论 53 | 同上 | 同上 |
| 55 | True but strange | 部分修改 | observational connection 有改善，但表达仍偏散 | `main.tex:455-475`, `510` | 结合评论 56-59、80 改 |
| 56 | priority first: effect of enhanced PPS | 部分修改 | 正文有暗示，但 Discussion/Conclusion 仍分散到多个观测方向 | `main.tex:455-475`, `498-510` | 先强调 enhanced PPS 对 DM halo statistics 的影响 |
| 57 | on dark matter halo | 部分修改 | HMF、assembly、concentration 是核心结果，但结论可更直接 | `main.tex:498-505` | Conclusion 首句/最后一句强化 halo effect |
| 58 | baryonic physics/galaxy formation/selection 放 conclusion 最后 | 部分修改 | caveat 出现在 Introduction、Limitations、Observation、Conclusion 多处 | 多处 | 保留必要 caveat，但不要抢主线 |
| 59 | DM halos 是最 dominant effect | 部分修改 | 当前写 strongest responses include halo abundance/assembly/concentration | `main.tex:475`, `502-505` | 更明确写 halo statistics 是首要结果 |
| 60 | table 放进 conclusion bullet points | 未修改 | response table 仍保留 | `main.tex:477-493`, `500` | 删除表或合并到 conclusion bullets |
| 61 | `collects representative response amplitudes...` 不清楚 | 未修改 | 该句仍在 | `main.tex:500` | 删除表后该句也删除 |
| 62 | clumsy | 未修改 | 同评论 61 | `main.tex:500` | 同上 |
| 63 | This is a good paragraph | 备注 | 正面评论，无需修改 | 无 | 无 |
| 64 | use bullet points here | 已修改 | Conclusion 已用 enumerate bullet list | `main.tex:501-506` | 无 |
| 65 | 这是 definition，不是 result | 部分修改 | analytic ingredients 段仍混合 definitions 和 recommendations | `main.tex:508` | 缩短或移到前文/appendix |
| 66 | equation references 不要括号 | 未修改 | 仍有 `Eq.~(\ref{...})` | `main.tex:508` | 全文改为 `Eq.~\ref{...}` |
| 67 | cite reference again here | 需原文锚点 | 不知道具体指哪处 | 不明 | 回 Overleaf 看锚点 |
| 68 | use full name | 部分修改 | D19/I21 已改 full names；Reed07/B16 shorthand 仍在 | `main.tex:335`, `355`, `359`, `395`, `508` | 统一 first mention 用 full names |
| 69 | Reed07/B16/D19 不一致 | 部分修改 | D19/I21 改善；Reed07/B16 仍混用 shorthand/full citation | 多处 | 建 notation rule |
| 70 | need absolutely clear | 部分修改 | mass definitions 和 model definitions 更清楚，但 notation 仍可统一 | `main.tex:289`, `335`, `359`, `395` | 同评论 69/71 |
| 71 | 每节早定义 consistent notation | 部分修改 | 有定义但不够系统 | 多处 | 每个 section 首次出现都 full name + shorthand |
| 72 | cite reference again here | 需原文锚点 | 不知道具体指哪处 | 不明 | 回 Overleaf 看锚点 |
| 73 | 不懂，是否不是用 project plots 里的 counted halos? | 需原文锚点 | 可能指 analytic ingredients 或 projected maps，但不确定 | `main.tex:508` 或 `327` | 需原锚点 |
| 74 | 本文不提供 nonlinear power fitting formula | 已修改 | 明确说不推荐 standalone nonlinear-power fitting formula | `main.tex:431`, `438`, `508` | 无 |
| 75 | 没有 analytic model for nonlinear power spectrum? | 已修改 | 写了 theory curves only for orientation/no calibrated formula | `main.tex:431`, `438`, `508` | 无 |
| 76 | should mention earlier in conclusions | 部分修改 | 目前在 analytic ingredients 段提到 | `main.tex:508` | 可移入 nonlinear-power bullet |
| 77 | It sounds strange | 需原文锚点 | 不知道具体句子 | 不明 | 回 Overleaf 看锚点 |
| 78 | one simulation, no cosmic variance，只提一次 | 已修改 | Limitations 明确 one matched-seed realization；无 cosmic variance/realization scatter | `main.tex:465` | 无 |
| 79 | 不能提供 direct observational constraints，主要不是 cosmic variance | 部分修改 | Conclusion 说不是 direct observational constraints，需 baryon/selection/survey modeling | `main.tex:510` | 避免把限制归因过多放在 cosmic variance |
| 80 | final sentence 太弱 | 未修改 | 结尾仍以 caveat 收尾 | `main.tex:510` | 改成更积极的 future target statement |
| 81 | give a GitHub address | 未修改 | Data Availability 没有 GitHub URL | `main.tex:514` | 补真实 GitHub 地址或占位符 |
| 82 | consider Zenodo for halo catalogs/SOAP output | 未修改 | Data Availability 没有 Zenodo/DOI | `main.tex:514` | 补 Zenodo DOI/占位符 |
| 83 | full snapshots not possible | 已修改 | Data Availability 说明 raw snapshots 和完整 catalogs 太大 | `main.tex:514` | 无 |
| 84 | Add resolution study | 需要数据/图 | 当前只有 trusted ranges，不是真正 resolution study | `main.tex:296-315`, `465-467` | 需要已有 resolution/volume runs 支持，否则写 limitation |

## 已经真正落到正文里的主要修改

1. **摘要 power-spectrum 结论量化**  
   对应评论：3 及红字 `quantify`。  
   修改位置：`main.tex:111`。  
   当前用 `changes` 包标记为 `\revisionreplace{新句}{旧句}`，PDF 里旧句会被划线，新句为蓝色。

2. **Introduction 高红移/JWST motivation 重写**  
   对应评论：4、5、6。  
   修改位置：`main.tex:126`。  
   修改内容：从旧的小尺度 tension 叙述，改成大尺度约束可靠、小尺度约束较弱、JWST 高红移星系候选体引出 enhanced small-scale primordial matter power，同时保留 baryonic caveat。

3. **新增 enhanced power 的理论来源**  
   对应评论：5。  
   修改位置：`main.tex:133`，`main.bib` 中新增 `Inman2019PBHBT`。  
   修改内容：加入 warm inflation、axion、multi-field/hybrid inflation、PBH Poisson fluctuation 等动机。

4. **定义 blue-tilted**  
   对应评论：6 以及 “need to describe what blue tilted is”。  
   修改位置：`main.tex:138`。  
   修改内容：解释 BT 是 broken-power-law input spectrum，`k>k_p` 后有效 high-k slope 增大，power 向短波长/大 k 偏移。

5. **增加论文 roadmap**  
   对应评论：`State what we do in different sections`。  
   修改位置：`main.tex:151`。  
   修改内容：逐节说明 theory、numerical、results、discussion、conclusion 做什么。

6. **修正模型表拼写**  
   对应评论：表格/命名问题。  
   修改位置：`main.tex:223-224`。  
   修改内容：`Blue-tiled` 改为 `Blue-tilted`，并用 `\revisionreplace` 标记。

7. **质量定义和 M200c/B16 说明**  
   对应评论：20、26、28、29、69-71。  
   修改位置：`main.tex:287-289`, `335`, `359`, `397-412`。  
   修改内容：区分 FOF、M200c、M200m、SO/200crit、SO/200mean，并定义 B16 和 concentration model。

8. **HMF 低粒子数 gray band 说明**  
   对应评论：35。  
   修改位置：`main.tex:355`。  
   修改内容：图注说明 gray band 是 20-particle threshold 到 adopted catalog cut 的区域。

9. **HMR、concentration、power spectrum 的 error/scatter/binning 说明**  
   对应评论：21、41、42、44。  
   修改位置：`main.tex:369`, `395`, `423`, `429`, `438`。  
   修改内容：写明 HMR/concentration scatter，power-spectrum mesh/binning，shaded regions 含义。

10. **NFW profile 来源澄清**  
    对应评论：36、38、39。  
    修改位置：`main.tex:383`, `391`。  
    修改内容：说明这些不是 direct particle-count radial stacks，而是由 SOAP catalog concentration 重建的 NFW profile。

11. **single realization / cosmic variance limitation**  
    对应评论：78。  
    修改位置：`main.tex:465`。  
    修改内容：说明每个模型一个 matched-seed realization，误差条不含 cosmic variance 或 realization-to-realization scatter。

12. **Data Availability 对 full snapshots 的限制**  
    对应评论：83。  
    修改位置：`main.tex:514`。  
    修改内容：说明 raw snapshots 和完整 HBT-HERONS/SOAP catalogs 太大，当前提供 reduced products。

## 仍然最需要下一步改的评论

1. 术语统一：评论 1、2、15、16、45。
2. `field-level` 全文替换：评论 53、54。
3. Discussion physical interpretation 重写：评论 47-52。
4. NFW diagnostic 改名：评论 36-40，尤其 37。
5. response table 合并到 conclusion bullets：评论 60-62。
6. sigma8/MonofonIC 表述更精确：评论 8、10、11、14、18。
7. GitHub/Zenodo 数据可用性：评论 81、82。
8. 需要新分析的项目：mass accretion rate study（评论 30）和 resolution study（评论 84）。
