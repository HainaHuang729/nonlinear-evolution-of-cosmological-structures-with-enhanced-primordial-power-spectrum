/* Multi-redshift sculptural visualizations for #statistics (5 bespoke styles, zero deps). */
(() => {
  'use strict';
  const D = window.ARTICLE_DATA;
  if (!D) return;

  const STYLE_CSS = `
    .msv-card{margin-top:20px;border:1px solid var(--border,#cfd5cc);border-radius:4px;overflow:hidden;background:var(--surface,#fff)}
    .msv-head{display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px 18px;padding:12px 16px;border-bottom:1px solid var(--border,#d8ddd5);background:rgba(17,19,17,.025)}
    .msv-head-left{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}
    .msv-badge{font:600 10px/1.2 ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.08em;text-transform:uppercase;padding:3px 7px;border-radius:3px;border:1px solid currentColor;opacity:.85}
    .msv-title{margin:0;font-size:15px;font-weight:600;letter-spacing:-.01em}
    .msv-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap;font-size:12px}
    .msv-btn{appearance:none;border:1px solid var(--border,#bfc7bc);background:var(--surface,#fff);color:inherit;padding:4px 10px;border-radius:3px;font-size:12px;cursor:pointer}
    .msv-btn[aria-pressed="true"]{background:#1c2530;color:#fff;border-color:#1c2530}
    .msv-canvas-wrap{position:relative;width:100%;line-height:0}
    .msv-canvas{display:block;width:100%;height:340px;cursor:crosshair}
    .msv-readout{position:absolute;right:12px;top:10px;pointer-events:none;font:11px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace;padding:5px 9px;border-radius:3px;background:rgba(15,20,29,.84);color:#f3f4f6;max-width:340px;white-space:pre-line;opacity:0;transition:opacity .12s}
    .msv-readout.is-on{opacity:1}
    .msv-foot{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;padding:9px 16px;font-size:12px;color:var(--ink-secondary,#525a52);border-top:1px solid var(--border,#e0e4dd)}
    .msv-card.msv-dark{border-color:#263042;background:#0f141d;color:#e5eaf2}
    .msv-card.msv-dark .msv-head{background:#141b27;border-color:#263042}
    .msv-card.msv-dark .msv-foot{background:#111722;border-color:#263042;color:#9aa7bd}
    .msv-card.msv-dark .msv-btn{background:#1a2232;border-color:#32405a;color:#dce4f2}
    .msv-card.msv-dark .msv-btn[aria-pressed="true"]{background:#d9624c;border-color:#d9624c;color:#fff}
    @media(max-width:720px){.msv-canvas{height:270px}}
  `;
  const st = document.createElement('style');
  st.textContent = STYLE_CSS;
  document.head.append(st);

  const zFmt = z => Math.abs(z) < 0.005 ? 'z = 0' : 'z = ' + Number(z).toFixed(2);
  const uniqueDesc = arr => [...new Set(arr.map(v => Number(v.toFixed(4))))].sort((a, b) => b - a);
  const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, t) => a + (b - a) * t;

  function fitCanvas(canvas, cssH = 340) {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const w = Math.max(300, Math.round(canvas.clientWidth || 760));
    const h = Math.round(canvas.clientHeight || cssH);
    if (canvas.width !== Math.round(w * dpr) || canvas.height !== Math.round(h * dpr)) {
      canvas.width = Math.round(w * dpr);
      canvas.height = Math.round(h * dpr);
    }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    return { ctx, w, h };
  }

  function interpLogX(pts, logX) {
    if (!pts.length) return NaN;
    if (logX < pts[0].lx || logX > pts[pts.length - 1].lx) return NaN;
    for (let i = 0; i < pts.length - 1; i++) {
      const a = pts[i], b = pts[i + 1];
      if (logX >= a.lx && logX <= b.lx) {
        const t = b.lx === a.lx ? 0 : (logX - a.lx) / (b.lx - a.lx);
        return lerp(a.y, b.y, t);
      }
    }
    return pts[pts.length - 1].y;
  }

  function bipolarColor(val, low = 0.7, mid = 1.0, high = 2.0, dark = false) {
    if (!Number.isFinite(val)) return dark ? '#18202e' : '#ecebe4';
    if (val >= mid) {
      const t = clamp(Math.log(val / mid) / Math.log(high / mid), 0, 1);
      const r = Math.round(lerp(dark ? 34 : 238, 214, t));
      const g = Math.round(lerp(dark ? 45 : 235, 86, t));
      const b = Math.round(lerp(dark ? 64 : 225, 68, t));
      return `rgb(${r},${g},${b})`;
    }
    const t = clamp(Math.log(mid / Math.max(val, 1e-3)) / Math.log(mid / low), 0, 1);
    const r = Math.round(lerp(dark ? 34 : 238, 42, t));
    const g = Math.round(lerp(dark ? 45 : 235, 118, t));
    const b = Math.round(lerp(dark ? 64 : 225, 168, t));
    return `rgb(${r},${g},${b})`;
  }

  function mountCard(topicId, cfg) {
    const host = document.getElementById(topicId);
    if (!host) return null;
    const panel = host.querySelector('[data-local-id="chart-panel"]') || host;
    const card = document.createElement('article');
    card.className = 'msv-card' + (cfg.dark ? ' msv-dark' : '');
    card.innerHTML = `
      <div class="msv-head">
        <div class="msv-head-left">
          <span class="msv-badge" style="color:${cfg.accent}">${cfg.styleTag}</span>
          <h4 class="msv-title">${cfg.title}</h4>
        </div>
        <div class="msv-controls"></div>
      </div>
      <div class="msv-canvas-wrap">
        <canvas class="msv-canvas" role="img" aria-label="${cfg.title}"></canvas>
        <div class="msv-readout"></div>
      </div>
      <div class="msv-foot"><span>${cfg.caption}</span><span class="msv-meta">${cfg.meta || ''}</span></div>
    `;
    panel.append(card);
    const controls = card.querySelector('.msv-controls');
    const canvas = card.querySelector('canvas');
    const readout = card.querySelector('.msv-readout');
    const metaEl = card.querySelector('.msv-meta');
    const state = { model: 'kp1' };

    if (cfg.modelToggle !== false) {
      for (const [key, label] of [['kp1', 'BT kₚ = 1'], ['kp10', 'BT kₚ = 10']]) {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'msv-btn';
        b.textContent = label;
        b.setAttribute('aria-pressed', String(state.model === key));
        b.addEventListener('click', () => {
          state.model = key;
          controls.querySelectorAll('.msv-btn').forEach(btn => btn.setAttribute('aria-pressed', String(btn === b)));
          redraw();
        });
        controls.append(b);
      }
    }

    let hitTest = null;
    function redraw() {
      const { ctx, w, h } = fitCanvas(canvas);
      hitTest = cfg.draw({ ctx, w, h, state, host, metaEl }) || null;
    }

    canvas.addEventListener('mousemove', e => {
      if (!hitTest) return;
      const r = canvas.getBoundingClientRect();
      const text = hitTest(e.clientX - r.left, e.clientY - r.top);
      if (text) { readout.textContent = text; readout.classList.add('is-on'); }
      else readout.classList.remove('is-on');
    });
    canvas.addEventListener('mouseleave', () => readout.classList.remove('is-on'));

    // Sync with existing topic dropdown controls
    host.querySelectorAll('select').forEach(sel => sel.addEventListener('change', () => requestAnimationFrame(redraw)));
    new ResizeObserver(redraw).observe(canvas);
    redraw();
    return { redraw };
  }

  /* 1. HMF — 01 Indigo Ridges (暖纸底 + 2.5D 靛蓝立体山脊) */
  function initHmf() {
    mountCard('topic-hmf', {
      styleTag: 'STYLE 01 · INDIGO RIDGES',
      title: '多红移质量函数增量地形（靛蓝山谱）',
      accent: '#2c4a9a',
      caption: '暖纸底 + 2.5D 靛蓝等密山脊：每道山脊对应一个红移的 log₁₀(n_BT / n_PL)，高红移低质量端骤然耸起的先发成晕峰群一览无余。',
      draw({ ctx, w, h, state, host, metaEl }) {
        const defSel = host.querySelector('[data-local-id="mass-definition"]');
        const def = defSel ? defSel.value : 'fof';
        const rows = (D.hmfRatios[def] || []).filter(r => r.model === state.model && r.x > 0 && r.y > 0);
        const zs = uniqueDesc(rows.map(r => r.z));
        metaEl.textContent = `${def.toUpperCase()} · ${zs.length} 个红移 · ${state.model === 'kp1' ? 'BT kₚ=1' : 'BT kₚ=10'} / PL`;

        // Warm paper background with subtle radial vignette
        const bg = ctx.createRadialGradient(w * 0.45, h * 0.35, 20, w * 0.5, h * 0.5, w * 0.72);
        bg.addColorStop(0, '#f7f4ea');
        bg.addColorStop(1, '#ebe6d6');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, w, h);

        if (!zs.length) return null;
        const lxs = rows.map(r => Math.log10(r.x));
        const minX = Math.min(...lxs), maxX = Math.max(...lxs);
        const maxH = Math.max(0.6, ...rows.map(r => Math.max(0, Math.log10(r.y))));

        const padL = 74, padR = 32, topBase = 58, botBase = h - 42;
        const n = zs.length;
        const ridgeGap = n > 1 ? (botBase - topBase) / (n - 1) : 0;
        const amp = Math.min(110, h * 0.34);
        const skew = 22;

        const bands = [];
        zs.forEach((z, idx) => {
          const pts = rows.filter(r => Math.abs(r.z - z) < 0.02)
            .map(r => ({ lx: Math.log10(r.x), y: r.y, x: r.x }))
            .sort((a, b) => a.lx - b.lx);
          const baseY = topBase + idx * ridgeGap;
          const xOff = (idx - (n - 1) / 2) * (skew / Math.max(1, n - 1));
          const xMap = lx => padL + xOff + ((lx - minX) / Math.max(1e-6, maxX - minX)) * (w - padL - padR - Math.abs(skew));

          // Sample dense ridge curve
          const samples = [];
          const N = 96;
          for (let i = 0; i <= N; i++) {
            const lx = lerp(minX, maxX, i / N);
            const val = interpLogX(pts, lx);
            const ly = Number.isFinite(val) ? Math.max(0, Math.log10(Math.max(val, 1))) : 0;
            samples.push({ px: xMap(lx), py: baseY - (ly / maxH) * amp, lx, val });
          }

          // Fill mountain body with indigo depth gradient
          const depthT = idx / Math.max(1, n - 1);
          const grad = ctx.createLinearGradient(0, baseY - amp, 0, baseY + 6);
          grad.addColorStop(0, `rgba(${Math.round(lerp(24, 42, depthT))},${Math.round(lerp(56, 86, depthT))},${Math.round(lerp(148, 178, depthT))},0.94)`);
          grad.addColorStop(0.6, `rgba(${Math.round(lerp(18, 30, depthT))},${Math.round(lerp(38, 62, depthT))},${Math.round(lerp(110, 146, depthT))},0.92)`);
          grad.addColorStop(1, `rgba(14,28,78,0.88)`);

          ctx.beginPath();
          ctx.moveTo(samples[0].px, baseY);
          samples.forEach(p => ctx.lineTo(p.px, p.py));
          ctx.lineTo(samples[samples.length - 1].px, baseY);
          ctx.closePath();
          ctx.fillStyle = grad;
          ctx.fill();

          // Pale ice contour crest line (signature 07-ridges detail)
          ctx.beginPath();
          samples.forEach((p, i) => i ? ctx.lineTo(p.px, p.py) : ctx.moveTo(p.px, p.py));
          ctx.strokeStyle = `rgba(216,232,255,${lerp(0.55, 0.92, depthT).toFixed(2)})`;
          ctx.lineWidth = idx === n - 1 ? 1.5 : 1.05;
          ctx.stroke();

          // Redshift label on left
          ctx.fillStyle = '#2c3d6b';
          ctx.font = '600 10px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.textAlign = 'right';
          ctx.fillText(zFmt(z), padL - 10 + xOff, baseY + 3);
          bands.push({ z, baseY, samples });
        });

        // Mass axis ticks along bottom
        ctx.fillStyle = '#47536b';
        ctx.font = '11px ui-monospace, SFMono-Regular, Menlo, monospace';
        ctx.textAlign = 'center';
        for (let p = Math.ceil(minX); p <= Math.floor(maxX); p++) {
          const px = padL + ((p - minX) / Math.max(1e-6, maxX - minX)) * (w - padL - padR - Math.abs(skew));
          ctx.fillText(`10^${p}`, px, h - 14);
        }
        ctx.textAlign = 'right';
        ctx.fillText(`log₁₀(M / M☉) · 峰高 = log₁₀(n_BT/n_PL) [max ${Math.pow(10, maxH).toFixed(1)}×]`, w - 16, 22);

        return (mx, my) => {
          let best = null, bd = 1e9;
          for (const b of bands) {
            const dy = Math.abs(my - b.baseY);
            if (dy < ridgeGap * 0.75 + 24) {
              for (const s of b.samples) {
                if (!Number.isFinite(s.val)) continue;
                const d = Math.hypot(mx - s.px, (my - s.py) * 0.6);
                if (d < bd) { bd = d; best = { z: b.z, lx: s.lx, val: s.val }; }
              }
            }
          }
          if (!best || bd > 42) return '';
          return `${zFmt(best.z)} · M ≈ 10^${best.lx.toFixed(2)} M☉\nn_BT / n_PL = ${best.val.toFixed(2)}×`;
        };
      }
    });
  }

  /* 2. Power Spectrum — 05 Swiss Survey Contours (冷灰测绘底 + (k,z) 等高擦除面) */
  function initPower() {
    mountCard('topic-power', {
      styleTag: 'STYLE 02 · SWISS SURVEY CONTOURS',
      title: '(k, z) 非线性功率谱擦除等高面',
      accent: '#b4432c',
      caption: '瑞士测绘工程底 + 连续 (k, z) 增量热图与等值脊线：清晰追踪高红移小尺度功率增强峰向 z=0 逐步被非线性耦合抹平的过程。',
      draw({ ctx, w, h, state, host, metaEl }) {
        const boxSel = host.querySelector('[data-local-id="box-size"]');
        const box = boxSel ? Number(boxSel.value) : 25;
        const rows = (D.powerRatios || []).filter(r => r.model === state.model && r.box === box && r.x > 0 && r.y > 0);
        const zs = uniqueDesc(rows.map(r => r.z));
        metaEl.textContent = `${box} h⁻¹ Mpc · ${zs.length} 个红移 · ${state.model === 'kp1' ? 'BT kₚ=1' : 'BT kₚ=10'} / PL`;

        ctx.fillStyle = '#f4f6f8';
        ctx.fillRect(0, 0, w, h);
        if (!zs.length) return null;

        const padL = 68, padR = 88, padT = 30, padB = 46;
        const pw = w - padL - padR, ph = h - padT - padB;
        const lks = rows.map(r => Math.log10(r.x));
        const minK = Math.min(...lks), maxK = Math.max(...lks);
        const byZ = zs.map(z => ({
          z,
          pts: rows.filter(r => Math.abs(r.z - z) < 0.02).map(r => ({ lx: Math.log10(r.x), y: r.y })).sort((a, b) => a.lx - b.lx)
        }));

        const cols = 64, rowH = ph / zs.length;
        const grid = [];
        for (let r = 0; r < zs.length; r++) {
          const rowVals = [];
          for (let c = 0; c < cols; c++) {
            const lk = lerp(minK, maxK, (c + 0.5) / cols);
            const v = interpLogX(byZ[r].pts, lk);
            rowVals.push({ lk, v });
            if (Number.isFinite(v)) {
              const t = clamp((v - 0.95) / 1.45, 0, 1);
              // Swiss survey ramp: cool steel -> pale ivory -> ochre -> vermilion
              const R = Math.round(t < 0.35 ? lerp(218, 240, t / 0.35) : lerp(240, 196, (t - 0.35) / 0.65));
              const G = Math.round(t < 0.35 ? lerp(228, 232, t / 0.35) : lerp(232, 64, (t - 0.35) / 0.65));
              const B = Math.round(t < 0.35 ? lerp(235, 200, t / 0.35) : lerp(200, 46, (t - 0.35) / 0.65));
              ctx.fillStyle = `rgb(${R},${G},${B})`;
              ctx.fillRect(padL + (c / cols) * pw, padT + r * rowH, pw / cols + 0.7, rowH + 0.7);
            }
          }
          grid.push(rowVals);
        }

        // Contour threshold ticks (1.1x, 1.3x, 1.6x, 2.0x)
        const levels = [1.1, 1.3, 1.6, 2.0];
        ctx.strokeStyle = 'rgba(22,28,36,0.55)';
        ctx.lineWidth = 1;
        for (const lv of levels) {
          ctx.beginPath();
          let started = false;
          for (let r = 0; r < zs.length; r++) {
            const cy = padT + (r + 0.5) * rowH;
            for (let c = 0; c < cols - 1; c++) {
              const a = grid[r][c].v, b = grid[r][c + 1].v;
              if (Number.isFinite(a) && Number.isFinite(b) && ((a <= lv && b >= lv) || (a >= lv && b <= lv))) {
                const t = b === a ? 0.5 : (lv - a) / (b - a);
                const cx = padL + ((c + t + 0.5) / cols) * pw;
                if (!started) { ctx.moveTo(cx, cy); started = true; } else ctx.lineTo(cx, cy);
                break;
              }
            }
          }
          ctx.stroke();
        }

        // Crisp Swiss grid lines & labels
        ctx.strokeStyle = 'rgba(30,41,59,0.16)';
        ctx.strokeRect(padL, padT, pw, ph);
        ctx.fillStyle = '#334155';
        ctx.font = '10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
        ctx.textAlign = 'right';
        zs.forEach((z, r) => {
          if (zs.length <= 10 || r % 2 === 0 || r === zs.length - 1) {
            ctx.fillText(zFmt(z), padL - 8, padT + (r + 0.5) * rowH + 3.5);
          }
        });
        ctx.textAlign = 'center';
        for (let p = Math.ceil(minK); p <= Math.floor(maxK); p++) {
          const px = padL + ((p - minK) / Math.max(1e-6, maxK - minK)) * pw;
          ctx.beginPath(); ctx.moveTo(px, padT); ctx.lineTo(px, padT + ph); ctx.stroke();
          ctx.fillText(`10^${p}`, px, h - 16);
        }
        ctx.fillText('波数 k [h Mpc⁻¹] · 等值脊线 1.1× / 1.3× / 1.6× / 2.0×', padL + pw / 2, padT - 10);

        // Colorbar on right
        const cbX = w - padR + 18, cbW = 12;
        for (let i = 0; i < ph; i++) {
          const t = 1 - i / ph;
          const R = Math.round(t < 0.35 ? lerp(218, 240, t / 0.35) : lerp(240, 196, (t - 0.35) / 0.65));
          const G = Math.round(t < 0.35 ? lerp(228, 232, t / 0.35) : lerp(232, 64, (t - 0.35) / 0.65));
          const B = Math.round(t < 0.35 ? lerp(235, 200, t / 0.35) : lerp(200, 46, (t - 0.35) / 0.65));
          ctx.fillStyle = `rgb(${R},${G},${B})`;
          ctx.fillRect(cbX, padT + i, cbW, 1.5);
        }
        ctx.strokeStyle = 'rgba(30,41,59,0.3)';
        ctx.strokeRect(cbX, padT, cbW, ph);
        ctx.textAlign = 'left';
        ctx.fillStyle = '#334155';
        ctx.fillText('2.4×', cbX + 16, padT + 8);
        ctx.fillText('1.5×', cbX + 16, padT + ph * 0.62);
        ctx.fillText('1.0×', cbX + 16, padT + ph);

        return (mx, my) => {
          if (mx < padL || mx > padL + pw || my < padT || my > padT + ph) return '';
          const r = clamp(Math.floor((my - padT) / rowH), 0, zs.length - 1);
          const c = clamp(Math.floor(((mx - padL) / pw) * cols), 0, cols - 1);
          const cell = grid[r][c];
          if (!Number.isFinite(cell.v)) return '';
          return `${zFmt(zs[r])} · k ≈ ${Math.pow(10, cell.lk).toFixed(2)} h/Mpc\nP_BT / P_PL = ${cell.v.toFixed(3)}×`;
        };
      }
    });
  }

  /* 3. Assembly — 03 Evolutionary Ribbons (暖羊皮纸 + 6 质量箱同屏吸积流带) */
  function initAssembly() {
    mountCard('topic-assembly', {
      styleTag: 'STYLE 03 · EVOLUTIONARY RIBBONS',
      title: '全 6 质量箱演化丝流带（BT vs PL 同屏对照）',
      accent: '#236954',
      caption: '暖羊皮纸底 + 6 个最终质量箱（10⁹ → 3×10¹¹ M☉）的 16–84% 渐宽置信丝流带同屏叠绘：实色流带为 BT，虚线为 PL 基准，直观呈现蓝倾谱的早成晕提前走廊。',
      draw({ ctx, w, h, state, metaEl }) {
        const masses = [...new Set((D.assembly || []).map(r => r.mass))].sort((a, b) => a - b);
        metaEl.textContent = `${masses.length} 个质量箱 · ${state.model === 'kp1' ? 'BT kₚ=1' : 'BT kₚ=10'} (实带) vs PL (虚线)`;
        ctx.fillStyle = '#f5f0e5';
        ctx.fillRect(0, 0, w, h);
        if (!masses.length) return null;

        const padL = 68, padR = 96, padT = 28, padB = 42;
        const pw = w - padL - padR, ph = h - padT - padB;
        const maxZ = Math.max(...D.assembly.map(r => r.x));
        const minM = Math.min(...D.assembly.filter(r => r.lo > 0).map(r => Math.log10(r.lo)));
        const maxM = Math.max(...D.assembly.filter(r => r.hi > 0).map(r => Math.log10(r.hi)));

        // High redshift on left -> z=0 on right (natural cosmic time flow!)
        const xMap = z => padL + ((maxZ - z) / Math.max(1e-6, maxZ)) * pw;
        const yMap = m => padT + ((maxM - Math.log10(Math.max(m, 1e6))) / Math.max(1e-6, maxM - minM)) * ph;

        // Subtle grid
        ctx.strokeStyle = 'rgba(92,84,68,0.14)';
        ctx.lineWidth = 1;
        for (let z = 0; z <= Math.ceil(maxZ); z += 2) {
          const px = xMap(z);
          ctx.beginPath(); ctx.moveTo(px, padT); ctx.lineTo(px, padT + ph); ctx.stroke();
        }
        for (let p = Math.ceil(minM); p <= Math.floor(maxM); p++) {
          const py = yMap(10 ** p);
          ctx.beginPath(); ctx.moveTo(padL, py); ctx.lineTo(padL + pw, py); ctx.stroke();
        }

        const palette = ['#2a6f6b', '#337b87', '#3f6899', '#5a5496', '#8d4c73', '#b34c3a'];
        const curves = [];
        masses.forEach((mass, idx) => {
          const col = palette[idx % palette.length];
          const bt = D.assembly.filter(r => r.mass === mass && r.model === state.model).sort((a, b) => b.x - a.x);
          const pl = D.assembly.filter(r => r.mass === mass && r.model === 'PL').sort((a, b) => b.x - a.x);
          if (!bt.length) return;

          // Confidence ribbon for BT
          ctx.beginPath();
          bt.forEach((p, i) => i ? ctx.lineTo(xMap(p.x), yMap(p.hi || p.y)) : ctx.moveTo(xMap(p.x), yMap(p.hi || p.y)));
          for (let i = bt.length - 1; i >= 0; i--) ctx.lineTo(xMap(bt[i].x), yMap(bt[i].lo || bt[i].y));
          ctx.closePath();
          ctx.fillStyle = col + '2e';
          ctx.fill();

          // Median BT solid
          ctx.beginPath();
          bt.forEach((p, i) => i ? ctx.lineTo(xMap(p.x), yMap(p.y)) : ctx.moveTo(xMap(p.x), yMap(p.y)));
          ctx.strokeStyle = col;
          ctx.lineWidth = 2.1;
          ctx.stroke();

          // Median PL dashed
          if (pl.length) {
            ctx.save();
            ctx.setLineDash([4, 4]);
            ctx.beginPath();
            pl.forEach((p, i) => i ? ctx.lineTo(xMap(p.x), yMap(p.y)) : ctx.moveTo(xMap(p.x), yMap(p.y)));
            ctx.strokeStyle = '#3b3f3b';
            ctx.lineWidth = 1.25;
            ctx.stroke();
            ctx.restore();
          }

          // Right end label
          const last = bt[bt.length - 1];
          ctx.fillStyle = col;
          ctx.font = '600 10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.textAlign = 'left';
          const exp = Math.log10(mass);
          ctx.fillText(`10^${exp.toFixed(1)} M☉`, padL + pw + 8, yMap(last.y) + 3);
          curves.push({ mass, bt, pl });
        });

        // Axes labels
        ctx.fillStyle = '#4e493d';
        ctx.font = '10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
        ctx.textAlign = 'center';
        for (let z = 0; z <= Math.ceil(maxZ); z += 2) ctx.fillText(`z=${z}`, xMap(z), h - 16);
        ctx.textAlign = 'right';
        for (let p = Math.ceil(minM); p <= Math.floor(maxM); p++) ctx.fillText(`10^${p}`, padL - 8, yMap(10 ** p) + 3.5);
        ctx.textAlign = 'left';
        ctx.fillText('时间推进方向（高红移 → z=0） · 实带 BT / 虚线 PL', padL, 17);

        return (mx, my) => {
          if (mx < padL || mx > padL + pw || my < padT || my > padT + ph) return '';
          let best = null, bd = 1e9;
          for (const c of curves) {
            for (const p of c.bt) {
              const d = Math.hypot(mx - xMap(p.x), my - yMap(p.y));
              if (d < bd) { bd = d; best = { mass: c.mass, z: p.x, bt: p.y, pl: c.pl.find(q => Math.abs(q.x - p.x) < 0.05)?.y }; }
            }
          }
          if (!best || bd > 36) return '';
          const ratio = best.pl ? ` (BT/PL = ${(best.bt / best.pl).toFixed(2)}×)` : '';
          return `M₀ = 10^${Math.log10(best.mass).toFixed(1)} M☉ · ${zFmt(best.z)}\nM_BT = ${best.bt.toExponential(2)} M☉${ratio}`;
        };
      }
    });
  }

  /* 4. Internal Structure — 04 Obsidian Bipolar Phase Space (深曜石底 + 珊瑚/钴蓝双极增强) */
  function initStructure() {
    mountCard('topic-structure', {
      styleTag: 'STYLE 04 · OBSIDIAN BIPOLAR',
      title: '暗夜双极内部结构：多红移浓度增强 × z=0 内核密度比',
      accent: '#e07a5f',
      dark: true,
      caption: '深曜石底 + 珊瑚红（BT 致密增强）vs 钴青蓝（压低）：左幅为多红移 c₂₀₀c(BT)/c₂₀₀c(PL) 双极矩阵，右幅为 z=0 各质量箱径向密度比 ρ_BT/ρ_PL 发光内核剖面。',
      draw({ ctx, w, h, state, metaEl }) {
        const cRows = D.concentration || [];
        const pRows = (D.profileRatios || []).filter(r => r.model === state.model && r.x > 0 && r.y > 0);
        metaEl.textContent = `${state.model === 'kp1' ? 'BT kₚ=1' : 'BT kₚ=10'} / PL · 双极编码（珊瑚 > 1× · 钴蓝 < 1×）`;

        ctx.fillStyle = '#0f141d';
        ctx.fillRect(0, 0, w, h);

        const midX = Math.round(w * 0.52);
        // Left panel: c200c(BT) / c200c(PL) heatmap across (M200c, z)
        const zs = uniqueDesc(cRows.filter(r => r.model === state.model).map(r => r.z));
        const lpL = 62, lpR = midX - 18, lpT = 34, lpB = h - 42;
        const lw = lpR - lpL, lh = lpB - lpT;
        const cells = [];

        if (zs.length) {
          const allM = cRows.filter(r => r.x > 0).map(r => Math.log10(r.x));
          const minM = Math.min(...allM), maxM = Math.max(...allM);
          const cols = 14, rowH = lh / zs.length, colW = lw / cols;
          zs.forEach((z, ri) => {
            const btPts = cRows.filter(r => r.model === state.model && Math.abs(r.z - z) < 0.02).map(r => ({ lx: Math.log10(r.x), y: r.y })).sort((a, b) => a.lx - b.lx);
            const plPts = cRows.filter(r => r.model === 'PL' && Math.abs(r.z - z) < 0.02).map(r => ({ lx: Math.log10(r.x), y: r.y })).sort((a, b) => a.lx - b.lx);
            for (let ci = 0; ci < cols; ci++) {
              const lx = lerp(minM, maxM, (ci + 0.5) / cols);
              const vb = interpLogX(btPts, lx), vp = interpLogX(plPts, lx);
              if (Number.isFinite(vb) && Number.isFinite(vp) && vp > 0) {
                const ratio = vb / vp;
                const x0 = lpL + ci * colW, y0 = lpT + ri * rowH;
                ctx.fillStyle = bipolarColor(ratio, 0.85, 1.0, 1.8, true);
                ctx.fillRect(x0 + 1, y0 + 1, colW - 2, rowH - 2);
                cells.push({ x0, y0, w: colW, h: rowH, z, lx, ratio });
              }
            }
            ctx.fillStyle = '#9aa7bd';
            ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, monospace';
            ctx.textAlign = 'right';
            ctx.fillText(zFmt(z), lpL - 7, lpT + (ri + 0.5) * rowH + 3.5);
          });
          ctx.textAlign = 'center';
          ctx.fillStyle = '#9aa7bd';
          for (let p = Math.ceil(minM); p <= Math.floor(maxM); p++) {
            const px = lpL + ((p - minM) / Math.max(1e-6, maxM - minM)) * lw;
            ctx.fillText(`10^${p}`, px, h - 16);
          }
          ctx.textAlign = 'left';
          ctx.fillStyle = '#e5eaf2';
          ctx.font = '600 11px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.fillText('多红移浓度比 c_BT / c_PL (M₂₀₀c)', lpL, 20);
        }

        // Right panel: z=0 radial density ratio glowing profiles
        const rpL = midX + 36, rpR = w - 22, rpT = 34, rpB = h - 42;
        const rw = rpR - rpL, rh = rpB - rpT;
        const pmasses = [...new Set(pRows.map(r => r.mass))].sort((a, b) => a - b);
        const rPts = [];
        if (pmasses.length) {
          const minR = Math.log10(Math.min(...pRows.map(r => r.x)));
          const maxR = Math.log10(Math.max(...pRows.map(r => r.x)));
          const minY = 0.8, maxY = Math.max(2.2, ...pRows.map(r => r.y) * 1.05 || [2.5]);
          const maxVal = Math.max(2.2, ...pRows.map(r => r.y));
          const xM = r => rpL + ((Math.log10(r) - minR) / Math.max(1e-6, maxR - minR)) * rw;
          const yM = v => rpB - ((v - minY) / Math.max(1e-6, maxVal * 1.08 - minY)) * rh;

          // Baseline 1.0
          ctx.strokeStyle = 'rgba(154,167,189,0.35)';
          ctx.setLineDash([4, 4]);
          ctx.beginPath(); ctx.moveTo(rpL, yM(1)); ctx.lineTo(rpR, yM(1)); ctx.stroke();
          ctx.setLineDash([]);

          const glowCols = ['#f28466', '#e9a959', '#67b7d1', '#9a8cf2'];
          pmasses.forEach((m, idx) => {
            const pts = pRows.filter(r => r.mass === m).sort((a, b) => a.x - b.x);
            const col = glowCols[idx % glowCols.length];
            ctx.save();
            ctx.shadowColor = col;
            ctx.shadowBlur = 8;
            ctx.beginPath();
            pts.forEach((p, i) => i ? ctx.lineTo(xM(p.x), yM(p.y)) : ctx.moveTo(xM(p.x), yM(p.y)));
            ctx.strokeStyle = col;
            ctx.lineWidth = 2.2;
            ctx.stroke();
            ctx.restore();
            pts.forEach(p => rPts.push({ px: xM(p.x), py: yM(p.y), m, r: p.x, y: p.y }));
          });

          ctx.fillStyle = '#9aa7bd';
          ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.textAlign = 'center';
          for (const rv of [0.02, 0.05, 0.1, 0.3, 1.0]) {
            if (Math.log10(rv) >= minR && Math.log10(rv) <= maxR) ctx.fillText(String(rv), xM(rv), h - 16);
          }
          ctx.textAlign = 'right';
          for (const yv of [1.0, 1.5, 2.0, 2.5]) {
            if (yv <= maxVal * 1.05) ctx.fillText(`${yv.toFixed(1)}×`, rpL - 6, yM(yv) + 3);
          }
          ctx.textAlign = 'left';
          ctx.fillStyle = '#e5eaf2';
          ctx.font = '600 11px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.fillText('z=0 径向内核密度比 ρ_BT / ρ_PL (r / R₂₀₀m)', rpL, 20);
        }

        return (mx, my) => {
          for (const c of cells) {
            if (mx >= c.x0 && mx <= c.x0 + c.w && my >= c.y0 && my <= c.y0 + c.h) {
              return `${zFmt(c.z)} · M₂₀₀c ≈ 10^${c.lx.toFixed(2)} M☉\nc_BT / c_PL = ${c.ratio.toFixed(3)}×`;
            }
          }
          let best = null, bd = 1e9;
          for (const p of rPts) {
            const d = Math.hypot(mx - p.px, my - p.py);
            if (d < bd) { bd = d; best = p; }
          }
          if (best && bd < 26) return `z=0 · M₂₀₀m = 10^${Math.log10(best.m).toFixed(1)} M☉ · r/R₂₀₀m = ${best.r.toFixed(3)}\nρ_BT / ρ_PL = ${best.y.toFixed(3)}×`;
          return '';
        };
      }
    });
  }

  /* 5. Halo Bias — 05 Glass Terraces (柔和暖白 + 宝石色阶梯对照砖格) */
  function initBias() {
    mountCard('topic-bias', {
      styleTag: 'STYLE 05 · GLASS TERRACES',
      title: '多红移 × 跨盒晕偏置双极阶梯（b_BT / b_PL）',
      accent: '#276b70',
      caption: '彩窗阶梯风格：按红移 × 质量箱排布配对分箱偏置比 b_BT / b_PL（深青压低 < 1× · 暖珀抬升 > 1×），实框为 256 h⁻¹ Mpc 大盒，虚框为 25 h⁻¹ Mpc 小盒。',
      draw({ ctx, w, h, state, host, metaEl }) {
        const defSel = host.querySelector('[data-local-id="bias-definition"]');
        const boxSel = host.querySelector('[data-local-id="bias-box"]');
        const def = defSel ? defSel.value : 'M200m';
        const boxFilter = boxSel ? boxSel.value : 'all';
        const rows = (D.biasRatios || []).filter(r =>
          r.model === state.model &&
          r.massDefinition === def &&
          (boxFilter === 'all' || String(r.box) === boxFilter) &&
          r.x > 0 && r.y > 0
        );
        const zs = uniqueDesc(rows.map(r => r.z));
        metaEl.textContent = `${def} · ${boxFilter === 'all' ? '25 + 256' : boxFilter} h⁻¹ Mpc · ${zs.length} 个红移`;

        ctx.fillStyle = '#f8f7f2';
        ctx.fillRect(0, 0, w, h);
        if (!zs.length) return null;

        const padL = 72, padR = 26, padT = 30, padB = 44;
        const pw = w - padL - padR, ph = h - padT - padB;
        const lxs = rows.map(r => Math.log10(r.x));
        const minX = Math.min(...lxs) - 0.15, maxX = Math.max(...lxs) + 0.15;
        const rowH = ph / zs.length;
        const tiles = [];

        zs.forEach((z, ri) => {
          const zRows = rows.filter(r => Math.abs(r.z - z) < 0.02).sort((a, b) => a.x - b.x);
          const y0 = padT + ri * rowH;
          ctx.strokeStyle = 'rgba(40,60,62,0.1)';
          ctx.beginPath(); ctx.moveTo(padL, y0 + rowH); ctx.lineTo(padL + pw, y0 + rowH); ctx.stroke();

          zRows.forEach(r => {
            const cx = padL + ((Math.log10(r.x) - minX) / Math.max(1e-6, maxX - minX)) * pw;
            const tw = Math.max(20, Math.min(46, pw / Math.max(8, zRows.length + 2)));
            const th = Math.max(14, rowH - 8);
            const x0 = cx - tw / 2, ty0 = y0 + (rowH - th) / 2;

            ctx.fillStyle = bipolarColor(r.y, 0.72, 1.0, 1.25, false);
            ctx.fillRect(x0, ty0, tw, th);
            ctx.save();
            if (r.box === 25) ctx.setLineDash([3, 2]);
            ctx.strokeStyle = r.box === 256 ? '#1f4e52' : '#8a5a36';
            ctx.lineWidth = r.box === 256 ? 1.4 : 1.1;
            ctx.strokeRect(x0, ty0, tw, th);
            ctx.restore();

            if (tw >= 28 && th >= 16) {
              ctx.fillStyle = r.y < 0.84 ? '#fff' : '#1b2628';
              ctx.font = '600 9.5px ui-monospace, SFMono-Regular, Menlo, monospace';
              ctx.textAlign = 'center';
              ctx.fillText(r.y.toFixed(2), cx, ty0 + th / 2 + 3.5);
            }
            tiles.push({ x0, y0: ty0, w: tw, h: th, r });
          });

          ctx.fillStyle = '#2c4244';
          ctx.font = '600 10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
          ctx.textAlign = 'right';
          ctx.fillText(zFmt(z), padL - 10, y0 + rowH / 2 + 3.5);
        });

        ctx.fillStyle = '#475b5c';
        ctx.font = '10.5px ui-monospace, SFMono-Regular, Menlo, monospace';
        ctx.textAlign = 'center';
        for (let p = Math.ceil(minX); p <= Math.floor(maxX); p++) {
          const px = padL + ((p - minX) / Math.max(1e-6, maxX - minX)) * pw;
          ctx.fillText(`10^${p}`, px, h - 16);
        }
        ctx.textAlign = 'left';
        ctx.fillText('质量 M [M☉] · 实框 256 h⁻¹ Mpc / 虚框 25 h⁻¹ Mpc · 青色偏置压低 (<1×)', padL, 18);

        return (mx, my) => {
          for (const t of tiles) {
            if (mx >= t.x0 && mx <= t.x0 + t.w && my >= t.y0 && my <= t.y0 + t.h) {
              return `${zFmt(t.r.z)} · ${t.r.box} h⁻¹ Mpc (${t.r.massDefinition})\nM ≈ 10^${Math.log10(t.r.x).toFixed(2)} M☉ · b_BT / b_PL = ${t.r.y.toFixed(3)} ± ${(t.r.err || 0).toFixed(3)}`;
            }
          }
          return '';
        };
      }
    });
  }

  function boot() {
    if (!document.getElementById('topic-hmf')) {
      setTimeout(boot, 60);
      return;
    }
    initHmf();
    initBias();
    initAssembly();
    initStructure();
    initPower();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
