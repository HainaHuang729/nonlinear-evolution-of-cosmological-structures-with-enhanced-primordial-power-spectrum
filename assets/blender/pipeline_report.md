# Dataset used

MVP 实施与交付内容验收完成（2026-09-20 至 2026-09-21）。仅处理 bluetilted/kp_10_ms_1.5_25_1024 的正式输出；未重新扫描全项目。
原始文件只读。57 snapshots，每帧 1,073,741,824 个 PartType1 暗物质粒子。
实测细节以 output/*/metadata.json、验证 JSON 与本目录 Slurm 日志为依据。

# Particle cohort method

完整扫描末帧全部 uint64 ParticleID，以 SplitMix64(ID xor seed) 排名选最小 1M，
seed=20260920。100k/500k 为排名前缀，三个 cohort 均以 ID 升序保存。
主缓存只存 1M，小 cohort 使用 uint32 索引映射。首次 cohort 扫描耗时 46.01 秒。
扫描按 1,048,576 行块处理，内存不随十亿粒子数量增长。

# ParticleID matching verification

每帧独立扫描全体 ID，通过 canonical ID searchsorted 匹配，记录 selected-ID 的缺失、重复、命中率。
此检查不宣称验证全体十亿 ID 的唯一性。遇到异常不发布 metadata.json 完成标记。
不得将 source row index 作为时间身份。
0055 和 0056 的 1M selected IDs 均命中 100%，缺失/重复均 0。
现已扩展到全部 57 帧：每帧 1M IDs 命中 100%，缺失/重复均 0；全部相邻帧的最小镜像位移统计保存在 sequence_validation.json。
额外 fixture 验证了 >2^60 的 uint64 ID、反转行顺序、缺失/重复拒绝，以及 speed=(3²+4²)^0.5=5。

# Coordinate/unit conversion

BoxSize=[37.11401426970295]*3 comoving Mpc，输出 mod(x,L)/L-0.5 float32。
各帧保留 Header、Units、Coordinates/Velocities 属性及实际 scale factor/redshift。
坐标不再除 h。speed 用 float64 求速度模，再存 float32。
这里采用 comoving 展示；不会通过放大盒子来表现 Hubble expansion。已诊断 h=0.6736，BoxSize 约 25 Mpc/h。

# Periodic interpolation

单位盒中 delta=p1-p0；delta-=round(delta)；p=(p0+alpha*delta+0.5)%1-0.5。
0055→0056 验证包含真实跨边界计数、端点重建误差与位移分位数。
实测 11,123 个粒子发生至少一轴跨边界，参考公式端点重建误差上限 8.94e-8 单位盒。
Blender 改用等价的单次条件回卷减少求余成本；重新打开后的两端点与缓存逐元素一致。
插值依据最小镜像假设，端点本身不能证明两帧之间没有多次绕盒。
中间时间按 a 线性插值，z=1/a-1，并标注 interpolated；未用 snapshot 编号猜物理时间。

# Blender particle representation

Blender 4.5.3 LTS 独立安装；实测 bpy.data.pointclouds.new 可建空对象，
但 points 没有 add，因此采用单个 vertex-only mesh 转 Geometry Nodes points。
没有逐粒子 Object，没有球体实例，也没有百万粒子普通 keyframes。

# Geometry Nodes setup

Mesh to Points → Set Material。点半径为单位盒比例；speed 属性经固定范围映射到 Color Ramp → Emission。
固定色标避免逐帧自动拉伸造成颜色含义变化；原始 uint64 ID 保留在外部 cache。

# Volume deposition

0000、0028、0056 的全部粒子质量参与周期 CIC，128³；0056 增加 256³ 成本测试。
float64 网格累加，严格检查沉积总质量；科学密度输出 float32，单位为源质量/comoving Mpc³。
单个数组 axis order=xyz，体素中心在 (i+0.5)/n-0.5。
overdensity 文件实际上为 rho/mean(rho)，不是 delta=rho/mean(rho)-1。

# OpenVDB workflow

科学 density 和 rho/mean(rho) 分别存 mass_density、overdensity grids。
显示 density=max(log1p(rho/mean(rho))-log(2),0)，阈值/映射在所有时刻固定。
显示转换不会覆盖科学网格。三个 volume 帧离散切换；不是 57 帧完整 volume 动画。
OpenVDB 13 文件版本 225 曾被 Blender 4.5.3 报不支持；已固定 OpenVDB 12 转换环境。
四个 VDB 均通过科学网格无损往返、首末体素中心位置检查；Blender 实际加载三个网格并完成纯 volume 渲染。
128³ 文件分别为 18.656、18.726、18.131 MB；晚期 256³ 为 143.830 MB。
四次全粒子 CIC 耗时分别为 258.05、248.29、230.67、234.07 秒，质量相对误差最大 1.15e-15。
该质量误差指 float64 沉积阶段；float32 输出允许舍入，另检查 rho/mean(rho) 的均值偏差小于 1e-6。
[OpenVDB Python 官方文档](https://www.openvdb.org/documentation/doxygen/python.html) 描述 NumPy 复制与变换接口，实际安装可用性仍由运行验证。

# Animation caching strategy

采用 raw little-endian float32 + JSON metadata。1M 每帧 position=12 MB，speed=4 MB；
57 帧载荷 912 MB，独立 uint64 主 ID=8 MB。两个帧的基础粒子缓存=32 MB，另有 Blender 几何、属性、插值临时数组和 GPU 副本。
三个嵌套 cohort 的 ID 文件合计 12.8 MB，三个索引映射合计 6.4 MB。

| 格式 | MVP 评价 |
|---|---|
| raw float32 + metadata | 无解压、精确布局、Web 可复用，需自带完整性与 shape 检查；首选 |
| NPZ | 自描述方便，压缩会增加换帧解码成本；两帧实验测量 |
| binary PLY | 静态点云互通，但时间/单位/ID/scalar 属性导入兼容性需额外处理 |
| Alembic/USD | 可封装动画，但 Blender 实际 point 属性及百万点流式行为需要另行验证；不凭格式规格直接采用 |

外部 current/next cache + frame_change handler；场景重开需可信 Python bootstrap。
保存的 .blend 必须随 output/ 和 blender/ 脚本目录一起分发。

# Performance results

100k、500k、1M 均通过导入、保存、重开换帧验证。优化后 1M 换帧 0.108–0.126 s；这不是 viewport FPS。
GPU 尚未获分配，实测渲染使用 CPU 软件 Eevee。640×360、64 samples 的 1M points 约 150.87 s。
低成本三角形实例约 121.81 s，但累计进程峰值从约 1.88 GiB 上升到 5.12 GiB，且实例 speed 属性尚未验收。
点与三角形像素覆盖不同，存在 shader cache/顺序影响，不将此单次渲染当同等质量速度排名。
详细口径、机器、原始记录与局限见 blender_performance_report.md。

# Recommended Blender architecture

```text
Raw SWIFT HDF5 (read-only)
    ↓ Slurm streaming: fixed uint64 ID cohort + full-particle mass CIC
canonical float32 position/speed + scientific 128³ density
    ↓ periodic interpolation metadata / OpenVDB conversion
external Blender cache
    ↓ current/next loader + Geometry Nodes points + Principled Volume
Blender rendering
```

# Recommended visual style

黑背景、细小 speed 着色发光粒子、淡蓝低强度体发光、慢速 orbit/push-in/pullback。
默认不加景物；避免强 glow 淹没丝状结构。Particles/Volume collection 可分别开关。
实际测试了半径 0.00045/0.0008、发光强度 2/4、FOG_GLOW 和 f/2.8 景深。
默认选小半径、强度 2、关闭额外 glow/景深；后者会模糊相机前的时间文字。
纯体预览原先偏暗，显示 emission 增至 3，density scale 仍为 0.8；屏幕体采样块从默认值降为 2 像素以减少伪影。

# Current limitations

GPU 尚未分配，VRAM 与真实桌面 viewport FPS 未测；没有将 CPU handler 耗时或离屏渲染速度替代 FPS。
未测试 2M/5M、4K 成片、Alembic/USD 百万点完整序列。原生 PointCloud Python 直接批量填充路线未实现；采用已验证的 GN points。
只生成三个时间的 volume；播放时选择与当前粒子 a 最近的离散 volume，并单独标记其红移。不能把该预览解读为 57 帧连续密度演化。
粒子插值采用最小镜像直线近似；没有用动力学积分重建帧间轨迹。点半径、颜色与体发光都是显示参数。
外部缓存与可信 Python handler 是播放依赖；单独复制 .blend 不能得到完整动画。当前 handler 针对单个 simulation，双模拟模式尚未实现。
Scene 的 19 fps 是时间轴设置，不是实测交互帧率。预览视频为 100k、640×360、5 fps；1M 主场景和全部缓存仍在交付包中。

# Next step

下一步在目标桌面 GPU 测 viewport 与 4K 短片段，再决定更高粒子数和全序列 volume 的预算。

## 已交付与验证证据

- `output/metadata.json`、`sequence_validation.json`：57 帧、每帧 1M ID 完整匹配、912 MB position/speed、56 对相邻帧位移检查。
- `output/cohorts/`：三个嵌套 uint64 cohort 和 canonical uint32 索引。
- `output/density_validation.json`、`vdb_validation.json`：全粒子 CIC、质量守恒、float32 VDB 往返、非对称 xyz 探针和体素中心变换。
- `output/preview/cosmic_evolution_demo.blend`：1M 主场景；重开后首尾帧坐标准确，并通过 100k/500k/1M 切换检查。
- `output/camera_validation.json`：修正开场裁切后，起止帧八个盒角均处于画幅内，至少保留 2% 边界。
- `output/preview/demo/`：early/middle/late × particles/volume/hybrid 九张图；71 帧、5 fps、640×360、14.2 秒 MP4。
- `output/delivery_validation.json`：实际读取视频与 .blend 后的最终验收记录；视频大小 1,416,449 bytes。

[最终 Hybrid 静帧](../output/preview/demo/late_hybrid.png) · [预览视频](../output/preview/demo/cosmic_evolution_preview.mp4) · [性能报告](blender_performance_report.md)。

## 交付架构的明确建议

1. **粒子数量**：100k 用于交互预览，500k 作为折中，1M 用于高质量场景和离线渲染。未测试 2M/5M，不默认升级。
2. **Volume 的角色**：远景以全粒子密度体为主。128³ 的单格边长约 0.290 Mpc，适合全盒结构；256³ 约 0.145 Mpc，可增加细节，但均不等同于 halo 内部高分辨率解析。
3. **Hybrid**：推荐，用 full-particle density 保留质量分布，用固定 cohort 展示可追踪运动。三帧体缓存只作 MVP，字幕明确显示其离散红移。
4. **57 snapshots 的 cache**：推荐当前 raw float32 + metadata + uint64 cohort + current/next loader。不要把全部粒子动画写成普通 keyframes；Alembic/USD 要先做实际导入、属性和内存测试再考虑替换。
5. **4K 视频**：推荐 Cycles 作为最终离线成片路线，Eevee 用于交互和预览。在本次 CPU 节点，同一 960×540、1M Hybrid 镜头，Cycles 32 samples 为 12.71 s，软件 Eevee 16 samples 为 43.49 s；采样设置并非等质量标定。4K 与目标 GPU 尚未实测，正式成片前应先验证短片段成本，不能把这些 CPU 数字直接外推。MVP .blend 仍按要求默认 Eevee。
6. **与 Three.js 共用**：共享 canonical IDs、归一化 float32 positions、speed、a/z/BoxSize/units、科学 CIC 网格。网页更小 overview 可以直接从主 cache 和索引抽取，无须再读原始 HDF5；VDB、节点、材质和 .blend 留给 Blender。

第二阶段再增加：目标 GPU/真实 viewport benchmark、全 57 帧 volume、全局一致 transfer-function 调节、经过实测的更快插值/cache、2M/5M 测试、双模拟按物理时间对齐。
目前不做：十亿粒子进 Blender、逐粒子 Object/球体、1024³ VDB、全部坐标 keyframes、无 ID 的 row-index 插值，以及没有测量依据的 4K 性能承诺。
