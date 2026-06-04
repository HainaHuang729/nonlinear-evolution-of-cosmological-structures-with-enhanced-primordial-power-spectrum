# 修改前/修改后对照（中文说明版）

说明：

- 这个文件对应英文版 `overleaf_before_after_review.md`。
- TeX 代码片段保持原文，方便直接复制或对照论文。
- 中文部分解释每条到底改了什么、解决了老板哪类评论、以及还剩什么问题。

## A 部分：当前本地稿件里已经实际改过的内容

### A1. 添加蓝色修改命令和表格换行命令

修改前：

```tex
\usepackage{xcolor}
\usepackage{hyperref}
```

修改后：

```tex
\usepackage{xcolor}
\newcommand{\revisionblue}[1]{\textcolor{blue}{#1}}
\newcommand{\tabcell}[2]{\parbox[t]{#1}{\raggedright #2}}
\usepackage{hyperref}
```

中文说明：  
新增 `\revisionblue{...}`，让后续改动能显示为蓝色；新增 `\tabcell{...}{...}`，用于解决表格列宽和换行导致的编译/排版问题。

### A2. 摘要：把 nonlinear matter power spectrum 的结论量化

修改前：

```tex
While the blue-tilted model significantly boosts the non-linear matter power spectrum for $k> k_p$, the enhancement diminishes significantly at low redshift. {\color{red} quantify}
```

修改后：

```tex
\revisionblue{For the field-level statistic, the nonlinear matter-power response is more modest but measurable: in the fiducial \(25\,h^{-1}{\rm Mpc}\) box at \(z=0\), BT\_soft reaches \(P_{\rm BT}/P_{\rm PL}=1.17\) at \(k=20\,h\,{\rm Mpc}^{-1}\) and \(1.34\) at \(k=40\,h\,{\rm Mpc}^{-1}\), whereas BT\_deep remains close to unity at both wavenumbers.}
```

中文说明：  
老板红字要求 `quantify`，所以这里把原来笼统的 “significantly boosts” 改成具体数值：BT_soft 在 `z=0`、`k=20` 和 `40 h/Mpc` 处分别是 1.17 和 1.34。  
剩余问题：这里的 `field-level statistic` 之后还需要改，因为老板后来指出 power spectrum 不是 field-level，而是 summary statistic。

### A3. Introduction：替换旧的小尺度 tension 表述，加入 JWST 高红移动机

修改前：

```tex
The standard cosmological model, combining a nearly power-law primordial power spectrum with the $\Lambda$ Cold Dark Matter ($\Lambda$CDM) paradigm, provides an accurate description of the Universe on large scales ($>1 {\rm Mpc})$. Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-$\alpha$ forest are consistent with the standard cosmological model \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On the other hand, the constraints on small scales are weaker. For example, there are potential small-scale tensions in cosmology model such as the missing-satellites, core-cusp, and too-big-to-fail problems \citep{Bullock17smallscalechallenges,Sales22challenges}, although they are subject to the uncertainties in baryonic physics \citep{Benson2002reionization,Chan2015corecusp}. At the same time, early JWST measurements have revealed unexpectedly abundant and potentially massive galaxy candidates at $z\gtrsim 8$--$10$ \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \cite{Parashari23JWSTPPS,Hira24bluetilt},but high redshift baryonic physics is also potential solutions, e.g., evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.
```

修改后：

```tex
\revisionblue{The standard cosmological model, combining a nearly power-law primordial power spectrum with the \(\Lambda\) Cold Dark Matter (\(\Lambda\)CDM) paradigm, provides an accurate description of the Universe on large scales (\(>1\,{\rm Mpc}\)). Measurements of the cosmic microwave background, galaxy clustering, and the Lyman-\(\alpha\) forest are consistent with this picture \citep{Planck20CMB,Blanton17SDSSsurvey,Chabanier19LyalphaPS}. On smaller scales, however, constraints are weaker. Potential small-scale tensions such as the missing-satellites, core-cusp, and too-big-to-fail problems have motivated departures from the simplest cold-dark-matter picture \citep{Bullock17smallscalechallenges,Sales22challenges}, although baryonic physics can substantially affect these comparisons \citep{Benson2002reionization,Chan2015corecusp}. Early JWST measurements have also revealed unexpectedly abundant and potentially massive galaxy candidates at \(z\gtrsim 8\)--\(10\) \citep{Labbe23MassiveGalaxies,Donnan23UVLF}. These observations have motivated renewed interest in enhanced small-scale primordial matter power \citep{Parashari23JWSTPPS,Hira24bluetilt}; however, high-redshift baryonic physics and observational effects remain plausible explanations, including evolving star-formation efficiency, weak feedback, dust, UV emission efficiency, and selection effects \citep{Lovell23JWSTExtreme}.}
```

中文说明：  
老板说旧的 small-scale tensions 有些过时，但现在有新的高红移 tension。所以这段把重点转向 JWST 观测到的高红移星系候选体，同时保留 missing satellites/core-cusp/too-big-to-fail 作为背景，并明确 baryonic physics 可能解释这些现象。  
这条基本已处理。

### A4. Introduction：增加 enhanced small-scale power 的理论动机

修改前：

```tex
{\color{red} add motivations for enhanced power spectrum: e.g. ``the enhanced small-scale power spectrum can stem from a wide range of alternative cosmological theories, including warm inflation \citep{Arya20WarmInflation}, axion models with hyperbolic field-space geometry \cite{Sai26BlueTilt}, and multi-field hybrid inflation models that can naturally generate a broken power-law, blue-tilted spectrum \citep{Linde94Hybridinflation, Wang24BTinflationtheory, Wang25HybridInflation}. The discreteness of primordial black holes can also induce an isocurvature term that enhances especially the small-scale spectrum \cite{Inman2019PBHBT}.'' need rephase. }
```

修改后：

```tex
\revisionblue{Enhanced small-scale power can arise in several classes of beyond-minimal early-Universe scenarios. Examples include warm-inflation models that amplify curvature perturbations \citep{Arya20WarmInflation}, axion models with nontrivial field-space geometry that can generate blue spectra \citep{Sai26BlueTilt}, and multi-field or hybrid-inflation constructions capable of producing broken-power-law enhancements \citep{Linde94Hybridinflation,Wang24BTinflationtheory,Wang25HybridInflation}. A distinct route is provided by a discrete population of primordial black holes (PBHs), whose Poisson fluctuations source an isocurvature contribution to the small-scale matter power spectrum \citep{Inman2019PBHBT}. In this work we do not attempt to distinguish among these mechanisms; instead, we use the blue-tilted spectrum as a phenomenological input model for testing the gravitational response to enhanced small-scale power.}
```

中文说明：  
原来只是红字备注，让我们补充 enhanced power spectrum 的理论来源。修改后加入 warm inflation、axion 模型、hybrid/multi-field inflation，以及 PBH Poisson fluctuation 的动机。  
同时强调本文不是要区分这些理论机制，而是把 blue-tilted spectrum 当作 phenomenological benchmark。  
这条基本已处理。

### A5. Introduction：定义什么是 blue-tilted

修改前：

```tex
We use a blue-tilted (BT) power spectrum following the previous literatures \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}. {\color{red} need to describe what blue tilted is.} Note that the BT models are phenomenological models instead of directly deriving from, e.g., any inflationary model.
```

修改后：

```tex
\revisionblue{Following previous literature \citep[e.g.][]{Hirano15BlueTiltedPPS,Parashari23JWSTPPS,Hira24bluetilt,Tkac24BumpyPPS,deKruijf25DarkAges,Dekker25DwarfPPS,Wu25BT}, we use ``blue-tilted'' (BT) to denote a broken-power-law input spectrum whose large-scale part follows the standard nearly scale-invariant slope, while above a pivot wavenumber \(k_p\) the effective high-\(k\) slope is increased to \(m_s>n_s\). In this sense the tilt is ``blue'' because power is shifted toward shorter wavelengths, or larger \(k\), increasing the small-scale primordial matter power relative to PL. The BT models are phenomenological benchmarks rather than direct fits to any one inflationary model.}
```

中文说明：  
老板要求解释 blue-tilted 是什么。修改后明确：大尺度保持接近 scale-invariant，小尺度在 pivot `k_p` 之后 slope 变大，power 向更短波长/更大 `k` 偏移，所以叫 blue-tilted。  
这条已处理。

### A6. Introduction：删除重复 pivot 解释并修正拼写

修改前：

```tex
The large-scale power spectrum follows the standard power-law form $P(k)\propto k^{n_s}$ with $n_s\simeq0.965$,

but the primordial matter power spectrum is enhanced above a pivot wavenumber $k_p$. The pivot therefore separates the well-measured large scales from the more weakly constrained small scales, preserving the successful large-scale predictions of $\Lambda$CDM while directly changing the abundance and collapse history of small halos.
Several recent studies ... can be degenerate with the priomordial power spectrum.
```

修改后：

```tex
Several recent studies ... can be degenerate with the primordial power spectrum.
```

中文说明：  
原文这里重复解释了 pivot，而且有拼写错误 `priomordial`。修改后删除重复段落，只保留后面更自然的相关工作段，并修正拼写。  
这条已处理。

### A7. Introduction：补充论文结构说明

修改前：

```tex
{\color{red} State what we do in different sections}
```

修改后：

```tex
\revisionblue{The rest of this paper is organized as follows. Section~\ref{sec:theory} defines the PL and BT input spectra and explains how the pivot scale changes the initial matter field. Section~\ref{sec:numerical} describes the simulation suite, halo catalog construction, analysis definitions, and numerical interpretation ranges. Section~\ref{sec:results} presents the halo abundance, assembly, concentration, and nonlinear-power responses. Section~\ref{sec:discussion} discusses the main numerical and modeling limitations and connects the benchmark diagnostics to observations. Section~\ref{sec:conclusion} summarizes the quantitative trends and the analytic ingredients that should be carried forward.}
```

中文说明：  
老板要求说明各 section 做什么。修改后加了标准 roadmap：theory、numerical、results、discussion、conclusion 各自负责什么。  
这条已处理。

### A8. 参数表：修正 Blue-tiled 拼写错误

修改前：

```tex
Blue-tiled Soft (BT\_soft) & 1 & 1.5 \\
Blue-tiled Deep (BT\_deep) & 10 & 1.5 \\
```

修改后：

```tex
\revisionblue{Blue-tilted Soft (BT\_soft)} & 1 & 1.5 \\
\revisionblue{Blue-tilted Deep (BT\_deep)} & 10 & 1.5 \\
```

中文说明：  
把 `Blue-tiled` 改成正确的 `Blue-tilted`。  
剩余问题：老板还建议把这个表和 simulation table 合并，当前还没有处理。

### A9. trusted ranges 表格：改写表格实现，解决编译/排版问题

修改前：

```tex
\begin{ruledtabular}
\begin{tabular}{p{0.22\textwidth}p{0.22\textwidth}p{0.22\textwidth}p{0.26\textwidth}}
Diagnostic & Quantity & Quantitative range & Interpretation note \\
\colrule
...
\end{tabular}
\end{ruledtabular}
```

修改后：

```tex
\begingroup
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}llll@{}}
\toprule
\tabcell{0.18\textwidth}{Diagnostic} & \tabcell{0.17\textwidth}{Quantity} & \tabcell{0.20\textwidth}{Quantitative range} & \tabcell{0.36\textwidth}{Interpretation note} \\
\midrule
...
\bottomrule
\end{tabular}
\endgroup
```

中文说明：  
这主要是 LaTeX 技术修改。原来在 `revtex/ruledtabular` 里用 `p{}` 列容易编译或排版出问题。修改后用 `\tabcell` 控制每个格子的宽度和换行。  
这不是老板内容评论本身，只是保证 PDF 能正常编译。

### A10. Observation paragraph：修正冠词错误

修改前：

```tex
The main value of the present work is therefore to identify where an primordial-power signal is likely to be largest before those additional complications are introduced.
```

修改后：

```tex
The main value of the present work is therefore to identify where \revisionblue{a primordial-power signal} is likely to be largest before those additional complications are introduced.
```

中文说明：  
把 `an primordial-power signal` 改成 `a primordial-power signal`。  
剩余问题：老板关于 “final sentence 太弱”、“优先强调 dark matter halo effect” 的评论还没有完全处理。

### A11. response-summary table：改写表格实现，解决编译/排版问题

修改前：

```tex
\begin{ruledtabular}
\begin{tabular}{p{0.34\columnwidth}p{0.50\columnwidth}}
Diagnostic & Representative response \\
\colrule
...
\end{tabular}
\end{ruledtabular}
```

修改后：

```tex
\begin{tabular}{@{}ll@{}}
\toprule
\tabcell{0.28\columnwidth}{Diagnostic} & \tabcell{0.58\columnwidth}{Representative response} \\
\midrule
...
\bottomrule
\end{tabular}
```

中文说明：  
这也是 LaTeX 表格排版/编译修正。  
剩余问题：老板明确说这个 table 不容易懂，建议放到 conclusion bullet points 里。当前只是把表格修到能编译，还没有按照老板建议删除/合并到 bullet。

### A12. 参考文献：添加 PBH 相关引用

修改前：

```bibtex
% No Inman2019PBHBT entry.
```

修改后：

```bibtex
@ARTICLE{Inman2019PBHBT,
       author = {{Inman}, Derek and {Ali-Ha{\"i}moud}, Yacine},
        title = "{Early structure formation in primordial black hole cosmologies}",
      journal = {\prd},
         year = 2019,
        month = oct,
       volume = {100},
       number = {8},
          eid = {083528},
        pages = {083528},
          doi = {10.1103/PhysRevD.100.083528},
archivePrefix = {arXiv},
       eprint = {1907.08129},
 primaryClass = {astro-ph.CO}
}
```

中文说明：  
为了支持 Introduction 里 PBH discreteness/Poisson fluctuation 可以增强小尺度 power 的说法，添加了 Inman & Ali-Haimoud 2019 的 bib entry。  
这条已处理。

## B 部分：建议下一轮修改，但还没有应用到 `main.tex`

### B1. 把 power spectrum 的 `field-level` 改掉

修改前：

```tex
For the field-level statistic, the nonlinear matter-power response is more modest but measurable...
```

建议修改后：

```tex
For the matter-power summary statistic, the nonlinear response is more modest but measurable...
```

中文说明：  
老板说 power spectrum 不是 field-level，而是 summary statistic。所以应该把 `field-level statistic/view/signal` 这类表达统一改掉。

### B2. 修改 `particle-field statistic` 的说法

修改前：

```tex
The nonlinear matter power spectrum is a particle-field statistic and does not require a halo mass definition.
```

建议修改后：

```tex
The nonlinear matter power spectrum is measured from the particle density field and does not require a halo mass definition.
```

中文说明：  
这样更准确：power spectrum 是从 particle density field 测出来的统计量，不是 field-level 本身。

### B3. 澄清 HMF ratio panel 的含义

修改前：

```tex
The lower ratio panels show the direct model response, \(f_{\rm BT}(M)/f_{\rm PL}(M)\)...
```

建议修改后：

```tex
The lower ratio panels show the BT abundance relative to PL, \(f_{\rm BT}(M)/f_{\rm PL}(M)\)...
```

中文说明：  
老板说 `direct model response` 不清楚。这里直接说 lower panel 是 BT/PL abundance ratio，更明确。

### B4. 初始条件段落改成主动语态

修改前：

```tex
For the BT models, the implementation modifies the transfer function above \(k_p\)...
```

建议修改后：

```tex
For the BT models, we modify the transfer function above \(k_p\)...
```

中文说明：  
老板说不要写 `the implementation modifies`，应该直接写 `we modify`。

### B5. 明确 sigma8 是否相同

修改前：

```tex
The BT spectra use the same background cosmology and large-scale normalization as PL; their matter power differs only above the pivot scale \(k_p\).
```

建议修改后：

```tex
The PL and BT initial conditions use the same \(\sigma_8=0.8111\) normalization and the same background cosmology; the BT runs differ from PL only through the transfer-function modification above \(k_p\).
```

中文说明：  
老板问 PL 和 BT 是否用同一个 `sigma_8`。如果事实确实如此，就应该明确写出来。  
注意：这条需要确认 simulation/MonofonIC 的实际设置，不能只靠文字猜。

### B6. 统一 `primordial` 和 `input` 的术语

修改前：

```tex
The purpose of this paper is to isolate the gravitational, nonlinear response to enhanced small-scale power in the primordial matter spectrum ... comparing a standard power-law input matter spectrum with two transfer-function-modified BT benchmark models.
```

建议修改后：

```tex
The purpose of this paper is to isolate the gravitational, nonlinear response to an enhanced small-scale primordial power spectrum. In the simulations, this enhancement is implemented as a transfer-function modification of the input linear matter power spectrum at \(z_i=200\).
```

中文说明：  
老板指出 `input matter power spectrum` 用得不一致。建议规则是：  
物理动机层面用 `primordial power spectrum`；具体 simulation/MonofonIC 输入层面用 `input linear matter power spectrum at z_i=200`。  
另外你之前提醒过：不要过度使用 `primordial matter power spectrum`，所以要控制频率。

### B7. 重写 Discussion 的 physical interpretation

修改前：

```tex
Increasing the small-scale input matter power at \(z_i=200\) raises the initial amplitude of low-mass density fluctuations, so these perturbations cross the collapse threshold earlier than in the PL model. This earlier collapse first appears as a high-redshift abundance excess and then leaves a lower-redshift structural imprint.
```

建议修改后：

```tex
The enhanced primordial power spectrum increases the amplitude of small-scale density fluctuations in the initial conditions. These early density fluctuations trigger earlier collapse at high redshift, producing an excess of low-mass halos first and leaving a later imprint on halo assembly histories and concentrations.
```

中文说明：  
老板明确说原句 clumsy，并建议用 “These early density fluctuations trigger earlier collapse at high redshift” 这种更直接的表达。  
这条建议优先改。

### B8. 替换 `uniform rescaling` 句子

修改前：

```tex
The signal is not simply a uniform rescaling of all nonlinear statistics.
```

建议修改后：

```tex
The response is not the same for every diagnostic: it depends on pivot scale, redshift, halo mass, and whether the statistic measures abundance, assembly, concentration, or \(P(k)\).
```

中文说明：  
老板说 `rescaling of all nonlinear statistics` 不清楚。新句子直接说明不同 diagnostic 的 response 不一样，避免抽象表述。

### B9. 重命名 NFW diagnostic

修改前：

```tex
\subsubsection{NFW-Equivalent Compactness Diagnostic}
```

建议修改后：

```tex
\subsubsection{Concentration-Derived NFW Density Profiles}
```

中文说明：  
老板说 `NFW-equivalent compactness curves` 很奇怪，而且容易让读者误以为是直接测出来的 radial profiles。  
建议改成更朴素、更准确的 “由 concentration 推出来的 NFW density profiles”。

### B10. 澄清 NFW 图注

修改前：

```tex
NFW-equivalent compactness curves reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and concentrations...
```

建议修改后：

```tex
Concentration-derived NFW density profiles reconstructed from \textsc{SOAP} \texttt{SO/200\_mean} masses, radii, and catalog concentrations...
```

中文说明：  
这样能明确说明图里的曲线不是直接 particle-count radial profile，而是根据 catalog concentration 重建出来的 NFW profile。

### B11. 删除/合并 response-summary table 到 conclusion bullet points

修改前：

```tex
Table~\ref{tab:main_response_summary} collects representative response amplitudes for the same trends. The main conclusions, with the corresponding result sections and figures, are as follows:
```

建议修改后：

```tex
The main conclusions, with representative response amplitudes and the corresponding result sections and figures, are as follows:
```

中文说明：  
老板说 table form 不容易懂，建议放到 conclusion bullet points 里。  
所以推荐删除 `tab:main_response_summary`，把里面的数值直接合并进 conclusion 的 bullet。

### B12. Equation reference 去掉括号

修改前：

```tex
Eq.~(\ref{eq:bt_input_power})
```

建议修改后：

```tex
Eq.~\ref{eq:bt_input_power}
```

中文说明：  
老板说 equation 引用不需要括号。应该全文统一改。

### B13. Data Availability 加 GitHub/Zenodo

修改前：

```tex
The reduced data products supporting the figures and quantitative comparisons in this article are openly available in the \texttt{public\_data/} directory accompanying this manuscript.
```

建议修改后：

```tex
The reduced data products supporting the figures and quantitative comparisons in this article are available in the project GitHub repository at \url{<GITHUB_URL>} and will be archived on Zenodo at \url{<ZENODO_URL>} if a DOI is assigned.
```

中文说明：  
老板说可以给 GitHub 地址，也可以考虑 Zenodo。  
这条需要你提供真实 GitHub/Zenodo 链接，或者我先放占位符。

### B14. 加强 conclusion 最后一句

修改前：

```tex
They are relevant to JWST-era high-redshift galaxy studies, dwarf-galaxy structure, strong-lensing probes of low-mass structure, 21 cm forecasts, and small-scale clustering measurements, but each application requires additional modeling of baryons, reionization, galaxy selection, and survey response.
```

建议修改后：

```tex
By identifying the halo masses, redshifts, and wavenumbers where the dark-matter response is largest, these simulations provide a concrete target set for future hydrodynamic simulations, semi-analytic modeling, and multi-probe tests of enhanced small-scale primordial power.
```

中文说明：  
老板说最后一句太弱。新句子更积极，强调本文提供了未来 hydrodynamic simulations、semi-analytic modeling、多探针检验可以直接使用的 target set。

### B15. 需要新数据/新图，不能只靠文字解决的两条

Mass accretion rate：

```text
Comment 30 asks for a mass-accretion-rate study. This cannot be fixed honestly by prose alone; it needs a new diagnostic from merger histories.
```

中文说明：  
老板要求加 mass accretion rate study。这需要从 merger history 里算新的量，比如 `dM/dz` 或 `d ln M / d ln a`，不能靠改一句话解决。

Resolution study：

```text
Comment 84 asks for a resolution study. Current text only gives trusted numerical ranges. A real response needs a resolution/volume comparison if the needed runs exist.
```

中文说明：  
老板要求加 resolution study。当前稿件只是写了 trusted ranges 和 particle threshold，不是真正的 resolution study。  
如果有不同 resolution/box size 的可比 runs，就应该加图或 appendix；如果没有，只能诚实写成 limitation。
