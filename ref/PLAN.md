# Brown-Correa 与本文关系总结记录

## Summary

在当前 Plan Mode 下，不直接写入文件。建议新建 Markdown 文件：

`/Users/amadeus/overleaf/nonlinear-evolution-of-cosmological-structures-with-enhanced-primordial-power-spectrum/brown_correa_comparison_notes.md`

该文件用于记录 Brown et al. 2020、Correa et al. 2015 与本文工作的关系、相同点、差异和可新增分析方向。

## Markdown 内容

```markdown
# Brown et al. 2020、Correa et al. 2015 与本文工作的关系总结

## 1. 核心物理链条

本文研究的是修改早期/原初功率谱后，非线性结构形成如何响应。相关物理链条可以概括为：

```text
Primordial power spectrum P(k)
→ linear matter power spectrum
→ variance S(M) or sigma(M)
→ halo collapse / mass accretion history
→ formation time / half-mass redshift
→ concentration and internal density profile
→ nonlinear matter power spectrum
```

因此，halo mass function、half-mass redshift、concentration、density profile 和 nonlinear matter power spectrum 并不是彼此孤立的结果，而是同一条物理链条的不同表现。

## 2. Correa et al. 2015 的作用

Correa et al. 2015a,b,c 提供的是理论和半解析框架。

### Paper I

Correa et al. 2015a 从 extended Press-Schechter 理论出发，说明 halo mass accretion history 可以写成：

```text
M(z) = M0 (1 + z)^alpha exp(beta z)
```

其中 alpha 和 beta 与线性增长因子以及由线性功率谱得到的质量方差 S(M) 有关。

核心关系是：

```text
P(k) → S(M) → alpha, beta → M(z)
```

### Paper II

Correa et al. 2015b 进一步用模拟说明 halo formation time、mass accretion history 和 concentration 之间有紧密联系。

其物理图像是：

```text
mass accretion history → formation redshift → concentration
```

早形成的 halo 在更高宇宙背景密度下建立内部结构，因此具有更高的 characteristic density 和 concentration。

### 对本文的意义

Correa et al. 为本文结果提供理论解释：

```text
修改早期功率谱
→ 改变 S(M)
→ 改变 halo assembly history
→ 改变 half-mass redshift 和 concentration
```

但 Correa et al. 并不是直接研究本文的 blue-tilted PPS 模型，而是提供普适的理论框架。

## 3. Brown et al. 2020 的作用

Brown et al. 2020 的文章题目是：

```text
Connecting the structure of dark matter haloes to the primordial power spectrum
```

它用 collisionless N-body simulations 系统改变 primordial power spectrum 的 amplitude、spectral index 和 pivot scale，研究 halo structure 是否保留 initial conditions 的记忆。

其核心结论是：

```text
dark matter halo structure retains memory of the primordial power spectrum
```

具体来说：

```text
increased initial fluctuation amplitude → higher halo concentration
decreased initial fluctuation amplitude → lower halo concentration
strong deviations from standard initial conditions → possible breakdown of NFW universality
```

Brown et al. 更像是基础物理数值实验：它问的是 halo structure 的普适性是否成立，以及这种普适性是否只是标准 CMB-normalized initial conditions 附近的结果。

## 4. 本文与 Brown et al. 的相同点

本文与 Brown et al. 在物理问题上高度重合：

```text
modified primordial power spectrum
→ dark-matter-only / collisionless N-body simulations
→ halo assembly and internal structure response
```

共同结果包括：

```text
enhanced small-scale power → earlier halo assembly
enhanced small-scale power → higher concentration
enhanced small-scale power → denser inner halo profiles
halo structure retains memory of initial conditions
```

因此，本文不能把“enhanced PPS increases concentration”作为主要新发现，因为 Brown et al. 已经证明了相近的 general conclusion。

## 5. 本文与 Brown et al. 的不同点

本文仍然可以与 Brown et al. 区分开来，关键是改变文章定位。

Brown et al. 的重点是：

```text
general variations of primordial amplitude, spectral index, and pivot scale
→ test universality of halo profiles and PPSD
```

本文的重点应定位为：

```text
blue-tilted small-scale PPS models motivated by current observational probes
→ joint response of halo abundance, assembly time, concentration, density profile, and nonlinear clustering
```

本文更接近一个 controlled simulation benchmark，服务于 JWST、dwarf galaxies、strong lensing、21 cm 和 small-scale clustering 等观测方向。

## 6. 当前文章的潜在创新不足

如果当前文章只强调：

```text
enhanced small-scale PPS changes halo structure
```

创新性较弱，因为 Brown et al. 2020 已经做过 general demonstration。

更好的定位是：

```text
We apply the Brown et al. physical picture to blue-tilted small-scale primordial spectra and quantify how the signal appears simultaneously in halo abundance, half-mass assembly redshift, concentration, density profiles, and nonlinear matter power.
```

也就是说，本文的创新不应是“首次发现 PPS 影响 halo structure”，而应是：

```text
specific BT model
+ multi-diagnostic response
+ observationally motivated mass/redshift/k ranges
+ connection between assembly history and concentration
```

## 7. 建议新增分析量

为了增强本文独立性，建议加入以下分析。

### 7.1 c 与 z_half 的关系

这是最重要的新增分析。

当前文章分别展示了 half-mass redshift 和 concentration，但还没有直接证明二者之间的联系。

建议画：

```text
c vs z_1/2 at fixed mass bins
c(M) colored by z_1/2
BT/PL concentration comparison at fixed M and fixed z_1/2
```

关键问题：

```text
BT halos are more concentrated because they assemble earlier?
```

如果固定 z_1/2 后，BT 和 PL 的 concentration 差异明显减小，就说明 concentration enhancement 很大程度上由 earlier assembly mediated。

### 7.2 完整 mass accretion history

half-mass redshift 是 assembly history 的一个摘要量；mass accretion history 是完整信息。

建议新增：

```text
median M_main(z) / M0 vs z
```

按 z=0 halo mass bin 分组，比较 PL、BT_soft、BT_deep。

这可以展示 BT halo 在哪些红移阶段更早增长。

### 7.3 吸积率或 specific accretion rate

吸积率图是 half-mass redshift 的升级版，但不是完全等价。

关系是：

```text
M(z) = full assembly history
dM/dt = slope of M(z)
z_1/2 = one characteristic point on M(z)
```

推荐使用无量纲形式：

```text
d ln M / d ln a
```

这样更适合跨质量比较。

### 7.4 拟合 Correa 的 MAH 参数

可以从 merger tree 的 median M(z) 拟合：

```text
M(z) = M0 (1+z)^alpha exp(beta z)
```

然后比较：

```text
alpha(M), beta(M)
c vs alpha
c vs beta
z_1/2 vs beta
```

这样可以直接把本文结果和 Correa et al. 的理论框架连接起来。

### 7.5 用 sigma(M) 或 peak height nu 重画结果

Brown 和 Correa 都强调功率谱主要通过 sigma(M) 或 peak height 进入 halo formation。

建议把部分结果从 M 轴改成：

```text
sigma(M)
nu = delta_c / sigma(M,z)
```

如果 PL 和 BT 在 nu 空间中部分 collapse 到同一关系，说明差异主要由 initial variance 控制。

如果不能 collapse，则说明 BT 模型导致了额外的 non-universality，这也有物理价值。

### 7.6 NFW 拟合质量 / profile shape

Brown et al. 讨论了 NFW universality 的可能 breakdown。本文可以检查：

```text
NFW fit residuals
chi^2_NFW(M)
Einasto alpha
inner slope d ln rho / d ln r
```

这可以回答：

```text
Does BT only increase concentration, or does it change profile shape?
```

## 8. 建议文章中加入的表述

### Relation to Previous Work

```text
Our results are closely related to Brown et al. (2020), who showed using collisionless N-body simulations that dark matter haloes retain memory of the primordial power spectrum. In particular, they found that increasing the amplitude of the initial fluctuations increases halo concentrations and can lead to departures from the apparent universality of halo density profiles. Our findings are consistent with this picture, but focus on blue-tilted small-scale primordial spectra and quantify the response through halo abundance, half-mass assembly redshift, internal structure, and nonlinear clustering.
```

### Correa 物理解释

```text
This interpretation is also consistent with the physical framework of Correa et al. (2015a,b,c), in which the linear matter power spectrum determines the halo mass accretion history through the variance of the initial density field, and the resulting assembly history is linked to halo concentration.
```

### 本文定位

```text
Rather than revisiting the general question of whether halo structure depends on the primordial power spectrum, we focus on blue-tilted small-scale spectra motivated by recent observational probes and provide a controlled benchmark of their joint imprint on halo abundance, assembly history, internal structure, and nonlinear clustering.
```

## 9. 需要注意的问题

当前 manuscript 中 BT 命名和单位需要统一。

发现的问题包括：

```text
BT_soft / BT_deep / BT_hard 命名不完全一致
k_p = 1, 10 h Mpc^-1 与 k_p = 0.702, 3.51 cMpc^-1 的表述需要解释或统一
```

在和 Brown et al. 对比时，模型定义必须清楚，否则读者会难以判断本文相对已有工作的区别。

## 10. 推荐最小新增工作

如果时间有限，建议优先完成三件事：

```text
1. c - z_1/2 relation at fixed mass
2. median M_main(z)/M0 and optionally d ln M / d ln a
3. fit Correa MAH parameters alpha and beta
```

这三项可以把文章从“验证 Brown et al.”提升为：

```text
quantitative mechanism test in blue-tilted PPS models
```

即本文不是简单重复 Brown 的结论，而是在具体 BT 模型中定量展示：

```text
enhanced PPS → earlier MAH → higher concentration
```

并把 Brown 的 initial-condition memory picture 和 Correa 的 MAH-concentration framework 连接起来。
```

## Assumptions

- 文件放在你的论文项目根目录，便于和 `main.tex`、`main.bib` 一起管理。
- Markdown 内容使用中英混合，保留英文句子方便后续直接改写进论文。
- 只记录讨论总结，不修改 `main.tex` 或 `main.bib`。
