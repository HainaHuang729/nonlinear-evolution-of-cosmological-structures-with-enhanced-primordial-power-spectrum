#!/usr/bin/env python3
"""Build an annotated manuscript from the unmodified Git HEAD version.

The Overleaf review export contains the comment text but not the exact
highlighted spans.  This script therefore anchors professor-intent notes to
nearby stable manuscript paragraphs and groups related comments together.
"""

from __future__ import annotations

import html
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_TEX = ROOT / "main_professor_intent_marked.tex"
OUT_MD = ROOT / "professor_intent_marked_original_zh.md"
OUT_HTML = ROOT / "professor_intent_marked_original_zh.html"


NOTES = [
    {
        "id": "C1,C2,C15,C16,C45",
        "title": "术语主线",
        "note": (
            "老板的核心想法是术语要先分层：理论动机处应说 ``primordial power spectrum'' "
            "或 ``the shape of primordial power spectrum''；具体到 MonofonIC 初始条件时，"
            "再说 z=200 的 input/linear matter power spectrum。不要把 CMB 后、z=200、"
            "以及代码输入谱混成一个概念。"
        ),
        "anchor": "\\maketitle",
        "after": True,
    },
    {
        "id": "C3",
        "title": "摘要写法",
        "note": (
            "老板认为摘要可以更定性一些，但同时红字要求 quantify。理解为：摘要开头不要堆过多细节，"
            "但关键结论必须给代表性数字，尤其是 halo abundance、formation redshift、concentration "
            "和 nonlinear power-spectrum ratio。"
        ),
        "anchor": (
            "While the blue-tilted model significantly boosts the non-linear matter power spectrum for $k> k_p$, "
            "the enhancement diminishes significantly at low redshift. {\\color{red} quantify}"
        ),
        "after": True,
    },
    {
        "id": "C4,C5,C6",
        "title": "引言动机",
        "note": (
            "老板觉得旧的 small-scale CDM tension 例子有些过时，应该加入更高红移的新 tension，"
            "例如 JWST high-redshift galaxy abundance，并补充更相关的新文献。这里还需要整体重写，"
            "让动机从“观测约束弱”自然过渡到“为什么研究 enhanced small-scale PPS”。"
        ),
        "anchor": (
            "At the same time, early JWST measurements have revealed unexpectedly abundant and potentially massive galaxy candidates"
        ),
        "mode": "paragraph",
    },
    {
        "id": "red-intro",
        "title": "理论动机补充",
        "note": (
            "老板红字的意思是：enhanced small-scale power spectrum 不能只说成一个任意参数化，"
            "需要给出可能来源，包括 warm inflation、axion/curved field-space、多场或 hybrid inflation、"
            "以及 primordial black holes 离散性诱导的小尺度 isocurvature 增强。"
        ),
        "anchor": (
            "{\\color{red} add motivations for enhanced power spectrum:"
        ),
        "mode": "paragraph",
    },
    {
        "id": "BT-definition",
        "title": "BT 定义",
        "note": (
            "老板要求先解释 blue-tilted 是什么。这里需要直接告诉读者：BT 表示在 pivot scale 以上，"
            "谱斜率变蓝，small-scale power 相对 PL 增强；同时强调本文只是 phenomenological benchmark，"
            "不是完整 inflation model。"
        ),
        "anchor": (
            "We use a blue-tilted (BT) power spectrum following the previous literatures"
        ),
        "mode": "paragraph",
    },
    {
        "id": "roadmap",
        "title": "论文结构",
        "note": (
            "老板要求写清楚各 section 做什么。这里应加一个短 roadmap：理论定义、数值设置、"
            "halo statistics、assembly/concentration、power spectrum、讨论和限制。"
        ),
        "anchor": "{\\color{red} State what we do in different sections}",
        "after": True,
    },
    {
        "id": "C10,C11",
        "title": "sigma8 归一化",
        "note": (
            "老板非常关心 PL 和 BT 是否保持同一个 sigma8。因为 sigma8 是观测约束的量，"
            "正确做法应是固定同一个 sigma8/large-scale normalization，再只改变 pivot 以上的 shape。"
            "正文必须明确说明实际 IC 是如何处理的。"
        ),
        "anchor": (
            "The BT spectra use the same background cosmology and large-scale normalization as PL;"
        ),
        "mode": "paragraph",
    },
    {
        "id": "C12",
        "title": "表格组织",
        "note": (
            "老板建议把 input-power model table 和 simulation table 合并，并参考 arXiv:1112.0330v2 "
            "的表格风格。原因是读者希望一眼看到 model、kp、ms、box、particle number、mass resolution "
            "等信息，而不是分散在两个表里。"
        ),
        "anchor": "\\begin{table}[t]\n\\caption{Input-power model parameters.",
        "after": False,
    },
    {
        "id": "C8,C9,C14,C18",
        "title": "初始条件逻辑",
        "note": (
            "老板认为这里原来的表达不够准确：不能简单说 power spectrum 是 linear 或只由一个函数决定，"
            "因为它经过 MonofonIC IC 生成，也依赖 random seed。应改成主动语态 ``we modify''，"
            "并明确说：在相同 initial phases 下测试 enhanced primordial power spectrum 的效应。"
        ),
        "anchor": (
            "We generate the initial conditions with \\textsc{Music2-MonofonIC}"
        ),
        "mode": "paragraph",
    },
    {
        "id": "C19",
        "title": "增强尺度与分辨率",
        "note": (
            "老板理解我们想说明增强尺度被分辨，但建议更直接：比较 particle/Nyquist scale 与 enhancement scale。"
            "也就是说，不只给 \\(\\Delta^2\\)，还要让读者看到 kp、增强区间和粒子网格分辨率之间的关系。"
        ),
        "anchor": (
            "As a basic consistency check on the initial conditions, we also evaluate the dimensionless input power"
        ),
        "mode": "paragraph",
    },
    {
        "id": "C20,C22,C23,C24,C25,C26",
        "title": "质量定义与重复信息",
        "note": (
            "老板提醒后文使用了多种 halo mass definition，所以需要集中定义 FOF、M200m、M200c，"
            "并且不要在表格已经给过 particle mass 后到处重复。M200c 必须在第一次出现前定义。"
        ),
        "anchor": (
            "Different statistics use different halo mass definitions."
        ),
        "mode": "paragraph",
    },
    {
        "id": "C27,C28,C29,C35",
        "title": "HMF 图和术语",
        "note": (
            "老板认为 ``direct model response'' 不清楚，应该明确说这是 BT 与 PL 的 ratio。"
            "B16/Reed07 之类缩写也要先定义。低粒子数区域需要阴影标出，避免读者过度解释不可靠 mass bin。"
        ),
        "anchor": "\\subsection{Halo Mass Function\\label{subsub:HMF}}",
        "after": True,
    },
    {
        "id": "C30,C31,C32,C33,C34",
        "title": "Assembly 与 accretion",
        "note": (
            "老板希望除了 half-mass redshift，还增加 mass accretion rate study。"
            "对于 BK09 比较，他的问题是：lower panel 到底和什么相减，为什么要和 BK09 比，"
            "以及是否更应该直接比较 BT 和 PL。细节可以放正文或 appendix。"
        ),
        "anchor": "\\subsection{Half-Mass Redshift\\label{subsub:HMR}}",
        "after": True,
    },
    {
        "id": "C36,C37,C38,C39,C40,C41,C42",
        "title": "NFW profile 解释",
        "note": (
            "老板认为 ``NFW-equivalent compactness curves'' 很奇怪，应该直接叫 dark matter halo density profile "
            "或 NFW profile。更重要的是，当前点和线容易让读者误以为点来自 simulated radial profile、线来自 fit；"
            "实际上它们是由 catalog concentration 重建的 NFW profile。若要回应更完整，还需要检验 NFW 对 BT halo "
            "的拟合准确性，并加 error bar 或 scatter。"
        ),
        "anchor": "\\subsubsection{NFW-Equivalent Compactness Diagnostic\\label{subsub:DensityProfile}}",
        "after": True,
    },
    {
        "id": "C43",
        "title": "模型缩写",
        "note": (
            "老板要求 D19 和 I21 不能直接出现，必须先写全名。类似 Reed07、B16 也最好在每个相关 section "
            "第一次出现时写成完整 citation/name，再决定是否使用缩写。"
        ),
        "anchor": "\\subsubsection{Concentration-Mass Relation\\label{subsub:concentration}}",
        "after": True,
    },
    {
        "id": "C21,C44,C53,C54",
        "title": "Power spectrum 表述",
        "note": (
            "老板指出 power spectrum 不是 field-level result，而是 summary statistic。这里应避免 ``field-level''，"
            "改成 nonlinear matter power-spectrum statistic 或 summary statistic measured from the particle density field。"
            "同时要说明 binning 方法和 shaded region 的含义。"
        ),
        "anchor": "\\subsection{Power Spectrum\\label{subsub:PS}}",
        "after": True,
    },
    {
        "id": "C47,C48,C49,C50,C51,C52",
        "title": "物理解释",
        "note": (
            "老板觉得 Discussion 开头的因果链不自然，而且 ``This earlier collapse first appears...'' 很别扭。"
            "他建议用更直接的逻辑：enhanced primordial power spectrum 先提高 early small-scale density fluctuations，"
            "这些早期涨落在高红移更早塌缩。对于 ``rescaling of nonlinear statistics'' 和 ``proved'' 这类说法，"
            "要改成更具体、更谨慎的解释。"
        ),
        "anchor": (
            "The results in Section~\\ref{sec:results} point to a single physical picture."
        ),
        "mode": "paragraph",
    },
    {
        "id": "C55,C56,C57,C58,C59,C78,C79,C84",
        "title": "优先级和限制",
        "note": (
            "老板希望论文优先强调 enhanced PPS 对 dark matter halos 的影响，而不是把重点过早转到观测 caveat。"
            "baryonic physics、selection、cosmic variance 应放在限制或结尾。还要诚实说明目前是一组 matched-seed "
            "dark-matter-only simulations，不是完整 resolution study；若老板要求 resolution study，需要新增分析。"
        ),
        "anchor": "\\subsection{Numerical and Modeling Limitations}",
        "after": True,
    },
    {
        "id": "C60,C61,C62,C64",
        "title": "Conclusion 结构",
        "note": (
            "老板觉得 response table 的形式不够清楚，建议把数值直接写入 conclusion bullet points。"
            "``collects representative response amplitudes'' 这类句子太绕，应让结论本身直接承载主要数字。"
        ),
        "anchor": "\\begin{table}[t]\n\\caption{Representative model responses relative to PL.",
        "after": False,
    },
    {
        "id": "C65,C66,C67,C68,C69,C70,C71,C72,C73,C74,C75,C76,C77,C80",
        "title": "Conclusion 语气和引用",
        "note": (
            "老板认为结论中有些内容像定义而不是结果，analytic model 的符号和引用也要更清楚。"
            "Eq. reference 不需要外层括号；Reed07/B16/D19/I21 等称呼要统一并在附近重新引用。"
            "同时最终句太弱，应以更积极的 future target 或 benchmark value 收束。"
        ),
        "anchor": (
            "The analytic ingredients that we recommend carrying forward from this benchmark are the tested"
        ),
        "mode": "paragraph",
    },
    {
        "id": "C81,C82,C83",
        "title": "Data availability",
        "note": (
            "老板要求给 GitHub address，并考虑 Zenodo，尤其是 halo catalogs 和 SOAP output。"
            "如果 full snapshots 太大不能公开，可以明确说无法提供 full snapshots，但 reduced data、scripts、"
            "catalog summaries 应给出可访问链接或 DOI placeholder。"
        ),
        "anchor": "\\section*{Data Availability}",
        "after": True,
    },
]


def git_head_main() -> str:
    return subprocess.check_output(
        ["git", "show", "HEAD:main.tex"], cwd=ROOT, text=True
    )


def tex_escape_note(text: str) -> str:
    # Notes intentionally contain LaTeX commands such as ``...'', so only handle
    # characters that are accidental in prose.
    return text.replace("%", "\\%")


def make_macro() -> str:
    return r"""
\usepackage[UTF8,scheme=plain,fontset=fandol]{ctex}
\newcommand{\bossnote}[3]{%
  \par\smallskip
  \noindent{\color{blue}\footnotesize\textbf{[Boss note #1: #2]} #3}%
  \par\smallskip
}
\newcommand{\tabcell}[2]{\begin{minipage}[t]{#1}\raggedright\arraybackslash #2\end{minipage}}
"""


def boss_tex(note: dict[str, str]) -> str:
    return (
        "\n"
        + "\\bossnote{"
        + note["id"]
        + "}{"
        + note["title"]
        + "}{"
        + tex_escape_note(note["note"])
        + "}\n"
    )


def find_paragraph_end(text: str, start: int) -> int:
    pos = text.find("\n\n", start)
    if pos == -1:
        return start
    return pos


def insert_notes(tex: str) -> str:
    tex = tex.replace("\\usepackage{orcidlink}\n", "\\usepackage{orcidlink}\n" + make_macro(), 1)

    for note in NOTES:
        anchor = note["anchor"]
        idx = tex.find(anchor)
        if idx == -1:
            raise RuntimeError(f"Anchor not found for {note['id']}: {anchor[:80]}")

        if note.get("mode") == "paragraph":
            insert_at = find_paragraph_end(tex, idx)
        elif note.get("after", True):
            insert_at = idx + len(anchor)
        else:
            insert_at = idx
        tex = tex[:insert_at] + boss_tex(note) + tex[insert_at:]

    return fix_revtex_tables(tex)


def fix_revtex_tables(tex: str) -> str:
    """Keep the original table content but avoid RevTeX p-column failures."""
    replacements = {
        r"\begin{tabular}{p{0.22\textwidth}p{0.22\textwidth}p{0.22\textwidth}p{0.26\textwidth}}":
            r"\begin{tabular}{llll}",
        r"Diagnostic & Quantity & Quantitative range & Interpretation note \\":
            r"\tabcell{0.18\textwidth}{Diagnostic} & \tabcell{0.17\textwidth}{Quantity} & \tabcell{0.20\textwidth}{Quantitative range} & \tabcell{0.36\textwidth}{Interpretation note} \\",
        r"FOF halo mass function & \(M_{\rm FOF}\) & \(M_{\rm FOF}\ge10^8\,M_\odot\) & About 50 particles in the fiducial runs; the gray band marks the interval down to the nominal 20-particle threshold. \\":
            r"\tabcell{0.18\textwidth}{FOF halo mass function} & \tabcell{0.17\textwidth}{\(M_{\rm FOF}\)} & \tabcell{0.20\textwidth}{\(M_{\rm FOF}\ge10^8\,M_\odot\)} & \tabcell{0.36\textwidth}{About 50 particles in the fiducial runs; the gray band marks the interval down to the nominal 20-particle threshold.} \\",
        r"\(M_{200c}\) mass-function check & \(M_{200c}\) & \(M_{200c}\ge2.0\times10^8\,M_\odot\) & SOAP \texttt{SO/200\_crit} catalogs require \(N_{\rm DM}\ge100\), close to \(1.9\times10^8\,M_\odot\). \\":
            r"\tabcell{0.18\textwidth}{\(M_{200c}\) mass-function check} & \tabcell{0.17\textwidth}{\(M_{200c}\)} & \tabcell{0.20\textwidth}{\(M_{200c}\ge2.0\times10^8\,M_\odot\)} & \tabcell{0.36\textwidth}{SOAP \texttt{SO/200\_crit} catalogs require \(N_{\rm DM}\ge100\), close to \(1.9\times10^8\,M_\odot\).} \\",
        r"Half-mass assembly & \(M_{\rm FOF}(z=0)\), \(z_{1/2}\) & Quoted trends use \(M_{\rm FOF}(z=0)\gtrsim10^9\,M_\odot\) & Same-\texttt{TrackId} FOF histories are used without gap filling or cumulative-envelope smoothing; Appendix~\ref{app:fof_gap_stitching} brackets the temporary-FOF-reassignment systematic. \\":
            r"\tabcell{0.18\textwidth}{Half-mass assembly} & \tabcell{0.17\textwidth}{\(M_{\rm FOF}(z=0)\), \(z_{1/2}\)} & \tabcell{0.20\textwidth}{Quoted trends use \(M_{\rm FOF}(z=0)\gtrsim10^9\,M_\odot\)} & \tabcell{0.36\textwidth}{Same-\texttt{TrackId} FOF histories are used without gap filling or cumulative-envelope smoothing; Appendix~\ref{app:fof_gap_stitching} brackets the temporary-FOF-reassignment systematic.} \\",
        r"NFW-equivalent compactness & \texttt{SO/200\_mean} catalog \(M\), \(R\), and \(c\) & \(10^8\,M_\odot\) panel qualitative; stronger interpretation for \(\gtrsim10^9\,M_\odot\) & Profiles are reconstructed from catalog concentrations rather than direct particle-count radial stacks. \\":
            r"\tabcell{0.18\textwidth}{NFW-equivalent compactness} & \tabcell{0.17\textwidth}{\texttt{SO/200\_mean} catalog \(M\), \(R\), and \(c\)} & \tabcell{0.20\textwidth}{\(10^8\,M_\odot\) panel qualitative; stronger interpretation for \(\gtrsim10^9\,M_\odot\)} & \tabcell{0.36\textwidth}{Profiles are reconstructed from catalog concentrations rather than direct particle-count radial stacks.} \\",
        r"Concentration--mass relation & \(M_{200c}\), \(c_{200c}\) & Plotted points require \(N_{\rm DM}\ge100\); quoted low-mass ratios use \(10^9\)--\(10^{9.5}\,M_\odot\) & Concentrations must be finite and positive, with \(c_{200c}<500\); the quoted bin is near or above the \(\simeq500\)-particle scale. \\":
            r"\tabcell{0.18\textwidth}{Concentration--mass relation} & \tabcell{0.17\textwidth}{\(M_{200c}\), \(c_{200c}\)} & \tabcell{0.20\textwidth}{Plotted points require \(N_{\rm DM}\ge100\); quoted low-mass ratios use \(10^9\)--\(10^{9.5}\,M_\odot\)} & \tabcell{0.36\textwidth}{Concentrations must be finite and positive, with \(c_{200c}<500\); the quoted bin is near or above the \(\simeq500\)-particle scale.} \\",
        r"Nonlinear matter power spectrum & \(k\) & Matched-box ratios only; conservative mesh scales are \(k_{\rm Ny}\simeq129\) and \(12.6\,h\,{\rm Mpc}^{-1}\) for the 25 and \(256\,h^{-1}{\rm Mpc}\) boxes & Field-level statistic with no halo-particle cut; high-\(k\) ratios are not promoted to a calibrated nonlinear-power fitting formula. \\":
            r"\tabcell{0.18\textwidth}{Nonlinear matter power spectrum} & \tabcell{0.17\textwidth}{\(k\)} & \tabcell{0.20\textwidth}{Matched-box ratios only; conservative mesh scales are \(k_{\rm Ny}\simeq129\) and \(12.6\,h\,{\rm Mpc}^{-1}\) for the 25 and \(256\,h^{-1}{\rm Mpc}\) boxes} & \tabcell{0.36\textwidth}{Field-level statistic with no halo-particle cut; high-\(k\) ratios are not promoted to a calibrated nonlinear-power fitting formula.} \\",
        r"\begin{tabular}{p{0.34\columnwidth}p{0.50\columnwidth}}":
            r"\begin{tabular}{ll}",
        r"Diagnostic & Representative response \\":
            r"\tabcell{0.28\columnwidth}{Diagnostic} & \tabcell{0.58\columnwidth}{Representative response} \\",
        r"FOF HMF at \(z=8.52\) & At \(M_{\rm FOF}\simeq1.21\times10^9,\,1.21\times10^{10}\,M_\odot\): BT\_soft \(=4.81,\ 6.55\); BT\_deep \(=1.39,\ 1.05\). \\":
            r"\tabcell{0.28\columnwidth}{FOF HMF at \(z=8.52\)} & \tabcell{0.58\columnwidth}{At \(M_{\rm FOF}\simeq1.21\times10^9,\,1.21\times10^{10}\,M_\odot\): BT\_soft \(=4.81,\ 6.55\); BT\_deep \(=1.39,\ 1.05\).} \\",
        r"FOF HMF at \(z=0\) & Same mass bins: BT\_soft \(=1.42,\ 1.47\); BT\_deep \(=1.31,\ 1.08\). \\":
            r"\tabcell{0.28\columnwidth}{FOF HMF at \(z=0\)} & \tabcell{0.58\columnwidth}{Same mass bins: BT\_soft \(=1.42,\ 1.47\); BT\_deep \(=1.31,\ 1.08\).} \\",
        r"Half-mass assembly & At \(M_{z=0}\simeq1.25\times10^9\,M_\odot\): PL has \(z_{1/2}=2.28\), BT\_soft has \(4.24\), and BT\_deep has \(2.61\). \\":
            r"\tabcell{0.28\columnwidth}{Half-mass assembly} & \tabcell{0.58\columnwidth}{At \(M_{z=0}\simeq1.25\times10^9\,M_\odot\): PL has \(z_{1/2}=2.28\), BT\_soft has \(4.24\), and BT\_deep has \(2.61\).} \\",
        r"Concentration at \(z=0\) & In \(10^9\)--\(10^{9.5}\,M_\odot\): \(c_{200c}/c_{\rm PL}=3.20\) for BT\_soft and \(1.35\) for BT\_deep. \\":
            r"\tabcell{0.28\columnwidth}{Concentration at \(z=0\)} & \tabcell{0.58\columnwidth}{In \(10^9\)--\(10^{9.5}\,M_\odot\): \(c_{200c}/c_{\rm PL}=3.20\) for BT\_soft and \(1.35\) for BT\_deep.} \\",
        r"Nonlinear \(P(k)\) at \(z=0\) & In the \(25\,h^{-1}{\rm Mpc}\) box at \(k=20,\,40\,h\,{\rm Mpc}^{-1}\): BT\_soft/PL \(=1.17,\ 1.34\); BT\_deep/PL \(=1.00,\ 1.00\). \\":
            r"\tabcell{0.28\columnwidth}{Nonlinear \(P(k)\) at \(z=0\)} & \tabcell{0.58\columnwidth}{In the \(25\,h^{-1}{\rm Mpc}\) box at \(k=20,\,40\,h\,{\rm Mpc}^{-1}\): BT\_soft/PL \(=1.17,\ 1.34\); BT\_deep/PL \(=1.00,\ 1.00\).} \\",
    }
    for old, new in replacements.items():
        tex = tex.replace(old, new)
    return tex


def write_summary() -> None:
    lines = [
        "# 老板想法标注版说明",
        "",
        "底稿来源：`git show HEAD:main.tex`，即未应用本地蓝字/删除线修改前的版本。",
        "",
        "说明：Overleaf Review 导出的文本没有包含每条评论对应的高亮原句，所以这里按主题把评论锚定到最接近的段落、标题、表格或小节。正文内容保持原始底稿，只额外插入蓝色 `Boss note`。",
        "",
        "## 标注分组",
        "",
    ]
    for note in NOTES:
        lines.append(f"### {note['id']}：{note['title']}")
        lines.append("")
        lines.append(note["note"])
        lines.append("")
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    body = "\n".join(
        [
            "<!doctype html>",
            '<html lang="zh-Hans">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>老板想法标注版说明</title>",
            "<style>",
            "body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:920px;margin:40px auto;padding:0 24px;line-height:1.75;color:#1f2937}",
            "h1{font-size:28px} h2{font-size:21px;margin-top:30px} h3{font-size:17px;margin-top:22px;color:#1d4ed8}",
            "p{margin:8px 0 14px} code{background:#f3f4f6;padding:2px 5px;border-radius:4px}",
            ".note{border-left:3px solid #2563eb;padding-left:12px;color:#374151}",
            "</style>",
            "</head>",
            "<body>",
            "<h1>老板想法标注版说明</h1>",
            "<p class=\"note\">底稿来源：<code>git show HEAD:main.tex</code>，正文内容保持原始底稿，只额外插入蓝色 Boss note。由于 Overleaf Review 导出没有高亮原句，标注按主题锚定到最接近位置。</p>",
            "<h2>标注分组</h2>",
        ]
    )
    for note in NOTES:
        body += f"\n<h3>{html.escape(note['id'])}：{html.escape(note['title'])}</h3>"
        body += f"\n<p>{html.escape(note['note'])}</p>"
    body += "\n</body>\n</html>\n"
    OUT_HTML.write_text(body, encoding="utf-8")


def main() -> None:
    original = git_head_main()
    annotated = insert_notes(original)
    OUT_TEX.write_text(annotated, encoding="utf-8")
    write_summary()
    print(OUT_TEX)
    print(OUT_MD)
    print(OUT_HTML)


if __name__ == "__main__":
    main()
