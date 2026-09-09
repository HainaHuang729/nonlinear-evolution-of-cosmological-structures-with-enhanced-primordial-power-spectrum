/* Offline article explorer. No network requests or runtime dependencies. */
(() => {
  'use strict';
  const D = window.ARTICLE_DATA;
  const $ = id => document.getElementById(id);
  if (!D) {
    $('load-error').hidden = false;
    $('load-error').textContent = '数值数据未加载。请保留 data.js、app.js 和 assets 目录与 index.html 的相对位置。';
    $('play').disabled = true;
    return;
  }
  const MODELS = ['PL', 'kp1', 'kp10'];
  const LABELS = {PL:'PL', kp1:'BT kₚ = 1', kp10:'BT kₚ = 10'};
  const COLORS = {PL:'#53657e', kp1:'#377caf', kp10:'#298773'};
  const S = {frame:0, tab:'hmf', statsZ:8.52, definition:'fof', box:25, mass:1e10, profileMass:1e10, zoom:1, panX:0, panY:0};
  let timer = null;
  let downloadRows = [];
  const nearly = (a,b) => Math.abs(a-b)<0.015;
  const ztext = z => Math.abs(z)<0.005 ? '0' : Number(z).toFixed(2);
  const unique = a => [...new Set(a.map(v=>Number(v.toFixed(5))))].sort((a,b)=>b-a);
  const fmt = (n, precision=3) => {
    if (!Number.isFinite(n)) return '—';
    if (n===0) return '0';
    if (Math.abs(n)>=1e4 || Math.abs(n)<0.01) return n.toExponential(precision-1);
    return Number(n.toPrecision(precision)).toString();
  };
  const elem = (tag, attrs={}, text) => {
    const el=document.createElementNS('http://www.w3.org/2000/svg',tag);
    Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,String(v)));
    if(text!==undefined) el.textContent=text;
    return el;
  };
  function grouped(rows, options={}) {
    return MODELS.map(model=>({model,label:LABELS[model],color:COLORS[model],points:rows.filter(r=>r.model===model).sort((a,b)=>a.x-b.x),...options})).filter(s=>s.points.length);
  }
  function tooltip(text, target, event) {
    const el=$('tooltip');
    el.textContent=text; el.hidden=false;
    const rect=target.getBoundingClientRect();
    const x=event?.clientX ?? rect.right;
    const y=event?.clientY ?? rect.top;
    el.style.left=Math.min(Math.max(8,x+14),window.innerWidth-el.offsetWidth-8)+'px';
    el.style.top=Math.min(Math.max(8,y+12),window.innerHeight-el.offsetHeight-8)+'px';
  }
  function chart(id, series, config={}) {
    const host=$(id); host.replaceChildren();
    const W=620,H=338,L=70,R=20,T=25,B=53;
    const xLog=config.xLog!==false, yLog=config.yLog!==false;
    const good = p=>Number.isFinite(p.x)&&Number.isFinite(p.y)&&(!xLog||p.x>0)&&(!yLog||p.y>0);
    const all=series.flatMap(s=>s.points.filter(good));
    if(!all.length) { empty(id,config.available??[]); return; }
    const tx=n=>xLog?Math.log10(n):n, ty=n=>yLog?Math.log10(n):n;
    const xs=all.map(p=>tx(p.x));
    const ys=all.flatMap(p=>[p.y,p.lo,p.hi].filter(v=>Number.isFinite(v)&&(!yLog||v>0)).map(ty));
    let xmin=config.xDomain?tx(config.xDomain[0]):Math.min(...xs), xmax=config.xDomain?tx(config.xDomain[1]):Math.max(...xs);
    let ymin=config.yDomain?ty(config.yDomain[0]):Math.min(...ys), ymax=config.yDomain?ty(config.yDomain[1]):Math.max(...ys);
    if (config.baseline!==undefined) { ymin=Math.min(ymin,ty(config.baseline));ymax=Math.max(ymax,ty(config.baseline)); }
    if(xmin===xmax){xmin-=.5;xmax+=.5;}
    if(ymin===ymax){ymin-=.5;ymax+=.5;}
    if(!config.yDomain){const pad=(ymax-ymin)*.09;ymin-=pad;ymax+=pad;}
    const x=n=>L+(tx(n)-xmin)/(xmax-xmin)*(W-L-R);
    const y=n=>H-B-(ty(n)-ymin)/(ymax-ymin)*(H-T-B);
    const svg=elem('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':`${config.title}. 横轴 ${config.xLabel}；纵轴 ${config.yLabel}`});
    const title=elem('title',{},config.title);svg.append(title);
    const defs=elem('defs');const clip=elem('clipPath',{id:`clip-${id}`});clip.append(elem('rect',{x:L,y:T,width:W-L-R,height:H-T-B}));defs.append(clip);svg.append(defs);
    const plot=elem('g',{'clip-path':`url(#clip-${id})`});
    const ticks=(min,max,log)=>{
      if(log){const arr=[];for(let p=Math.ceil(min);p<=Math.floor(max);p++)arr.push(p);if(arr.length>6)return arr.filter((_,i)=>i%Math.ceil(arr.length/6)===0);if(arr.length>=2)return arr;}
      const raw=(max-min)/4, pow=10**Math.floor(Math.log10(raw));
      const step=[1,2,2.5,5,10].find(s=>s*pow>=raw)*pow;
      const arr=[];for(let v=Math.ceil(min/step)*step;v<=max+step*1e-6;v+=step)arr.push(v);return arr;
    };
    const superdigits=n=>String(n).split('').map(c=>({'-':'⁻','0':'⁰','1':'¹','2':'²','3':'³','4':'⁴','5':'⁵','6':'⁶','7':'⁷','8':'⁸','9':'⁹'}[c]??c)).join('');
    const tickLabel=(v,log)=>log&&Math.abs(v-Math.round(v))<1e-7?'10'+superdigits(Math.round(v)):fmt(log?10**v:v,2);
    ticks(ymin,ymax,yLog).forEach(v=>{const py=H-B-(v-ymin)/(ymax-ymin)*(H-T-B);svg.append(elem('line',{x1:L,y1:py,x2:W-R,y2:py,stroke:'#e8ece5','stroke-width':.7}));svg.append(elem('text',{x:L-12,y:py+4,'text-anchor':'end',fill:'#899285','font-size':11},tickLabel(v,yLog)));});
    ticks(xmin,xmax,xLog).forEach(v=>{const px=L+(v-xmin)/(xmax-xmin)*(W-L-R);svg.append(elem('line',{x1:px,y1:H-B,x2:px,y2:H-B+5,stroke:'#bcc6b6'}));svg.append(elem('text',{x:px,y:H-B+22,'text-anchor':'middle',fill:'#899285','font-size':11},tickLabel(v,xLog)));});
    if(config.trusted){const [lo,hi]=config.trusted;
      for(const [a,b] of [[L,Math.min(W-R,x(lo))],[Math.max(L,x(hi)),W-R]])if(b>a)plot.append(elem('rect',{x:a,y:T,width:b-a,height:H-T-B,fill:'#e9eae5',opacity:.75}));
      [lo,hi].forEach(v=>plot.append(elem('line',{x1:x(v),y1:T,x2:x(v),y2:H-B,stroke:'#a2ad9c','stroke-dasharray':'3 4','stroke-width':.8})));
    }
    if(config.baseline!==undefined)plot.append(elem('line',{x1:L,y1:y(config.baseline),x2:W-R,y2:y(config.baseline),stroke:'#abb5a3','stroke-dasharray':'4 4'}));
    if(config.marker!==undefined&&config.marker>= (xLog?10**xmin:xmin)&&config.marker<=(xLog?10**xmax:xmax)) {
      plot.append(elem('line',{x1:x(config.marker),y1:T,x2:x(config.marker),y2:H-B,stroke:'#b48b50','stroke-dasharray':'4 4'}));
      plot.append(elem('text',{x:x(config.marker)+5,y:T+11,fill:'#9b783e','font-size':10},'投影 z='+ztext(config.marker)));
    }
    series.forEach(s=>{
      const points=s.points.filter(good).sort((a,b)=>a.x-b.x);
      if(!points.length)return;
      const color=s.color||COLORS[s.model];
      const band=points.filter(p=>Number.isFinite(p.lo)&&Number.isFinite(p.hi)&&p.hi>0);
      if(config.bands && band.length>1){
        const floor=yLog?10**ymin:ymin;
        const coords=band.map(p=>`${x(p.x)},${y(Math.max(floor,p.hi))}`).concat([...band].reverse().map(p=>`${x(p.x)},${y(Math.max(floor,p.lo))}`)).join(' ');
        plot.append(elem('polygon',{points:coords,fill:color,opacity:.10}));
      }
      const path=points.map((p,i)=>`${i?'L':'M'}${x(p.x).toFixed(2)},${y(p.y).toFixed(2)}`).join(' ');
      plot.append(elem('path',{d:path,fill:'none',stroke:color,'stroke-width':s.dash?1.2:1.65,'stroke-dasharray':s.dash?'5 4':'','data-series':s.label,opacity:s.dash?.65:1}));
      if(s.dash)return;
      const stride=Math.max(1,Math.ceil(points.length/55));
      points.forEach((p,i)=>{
        if(i%stride!==0&&i!==points.length-1)return;
        const outside=config.trusted&&(p.x<config.trusted[0]||p.x>config.trusted[1]);
        if(config.errors&&Number.isFinite(p.lo)&&Number.isFinite(p.hi)) {
          const low=yLog?Math.max(10**ymin,p.lo):p.lo;
          plot.append(elem('line',{x1:x(p.x),y1:y(low),x2:x(p.x),y2:y(p.hi),stroke:color,'stroke-width':.8,opacity:.5}));
        }
        let tip=`${s.label}\n${config.xLabel}: ${fmt(p.x,5)}\n${config.yLabel}: ${fmt(p.y,5)}`;
        if(Number.isFinite(p.lo)&&Number.isFinite(p.hi))tip+=`\n${config.intervalLabel||'区间'}: ${fmt(p.lo,4)} – ${fmt(p.hi,4)}`;
        if(p.count!==undefined)tip+=`\nN = ${p.count.toLocaleString('en-US')}`;
        if(p.countPL!==undefined)tip+=`；N(PL) = ${p.countPL.toLocaleString('en-US')}`;
        if(outside)tip+='\n在采用的定量解释区间之外';
        const dot=elem('circle',{cx:x(p.x),cy:y(p.y),r:2.4,fill:outside?'#fff':color,stroke:color,'stroke-width':.9,opacity:outside?.5:1,tabindex:0,class:'point','aria-label':tip,'data-x':p.x,'data-y':p.y,'data-model':s.model});
        dot.append(elem('title',{},tip));
        dot.addEventListener('pointerenter',event=>tooltip(tip,dot,event));
        dot.addEventListener('pointermove',event=>tooltip(tip,dot,event));
        dot.addEventListener('pointerleave',()=>{$('tooltip').hidden=true;});
        dot.addEventListener('focus',()=>tooltip(tip,dot));
        dot.addEventListener('blur',()=>{$('tooltip').hidden=true;});
        plot.append(dot);
      });
    });
    svg.append(plot);
    svg.append(elem('line',{x1:L,y1:H-B,x2:W-R,y2:H-B,stroke:'#aeb9a7','stroke-width':.8}));
    svg.append(elem('text',{x:(L+W-R)/2,y:H-9,'text-anchor':'middle',fill:'#65765e','font-size':12},config.xLabel));
    svg.append(elem('text',{x:16,y:(T+H-B)/2,transform:`rotate(-90 16 ${(T+H-B)/2})`,'text-anchor':'middle',fill:'#65765e','font-size':12},config.yLabel));
    host.append(svg);
  }
  function empty(id,available) {
    const box=document.createElement('div');box.className='chart-empty';
    const icon=document.createElement('span');icon.className='empty-icon';icon.textContent='◌';
    const title=document.createElement('strong');title.textContent=`z = ${ztext(S.statsZ)} 暂无对应数值表`;
    const note=document.createElement('span');note.textContent='选择已有红移查看；投影继续保留当前帧。';
    const choices=document.createElement('div');choices.className='choices';
    available.forEach(z=>{const b=document.createElement('button');b.type='button';b.textContent='z = '+ztext(z);b.addEventListener('click',()=>{S.statsZ=z;renderStats();});choices.append(b);});
    box.append(icon,title,note,choices);$(id).replaceChildren(box);
  }
  function refs(files) {
    $('reference-figures').replaceChildren(...files.map(([file,label])=>{
      const a=document.createElement('a');a.href='assets/'+file;a.target='_blank';a.rel='noopener';
      const figure=document.createElement('figure');const img=document.createElement('img');img.src=a.href;img.alt=label;img.loading='lazy';
      const caption=document.createElement('figcaption');caption.textContent=label+' · 点击查看原图';figure.append(img,caption);a.append(figure);return a;
    }));
  }
  function setHeading(side,title,meta,caption) {
    $('chart-title-'+side).textContent=title;$('chart-meta-'+side).textContent=meta;$('chart-caption-'+side).textContent=caption;
  }
  function renderStats() {
    $('tooltip').hidden=true;
    const projectionZ=D.projection.frames[S.frame].z;
    ['hmf','power','assembly','structure'].forEach(tab=>{
      $('tab-'+tab).setAttribute('aria-selected',String(S.tab===tab));$('tab-'+tab).tabIndex=S.tab===tab?0:-1;
      $(tab+'-control').hidden=S.tab!==tab;
    });
    $('chart-panel').setAttribute('aria-labelledby','tab-'+S.tab);
    $('redshift-control').hidden=S.tab==='assembly';
    const source=S.tab==='hmf'?D.hmf[S.definition]:S.tab==='power'?D.power:D.concentration;
    const available=unique(source.map(r=>r.z));
    const choices=available.some(z=>nearly(z,S.statsZ))?available:[S.statsZ,...available].sort((a,b)=>b-a);
    $('stats-redshift').replaceChildren(...choices.map(z=>{
      const option=document.createElement('option');option.value=z;option.textContent='z = '+ztext(z)+(available.some(a=>nearly(a,z))?'':' · 暂无统计');option.selected=nearly(z,S.statsZ);return option;
    }));
    const matching=nearly(S.statsZ,projectionZ);
    $('sync-status').classList.toggle('is-independent',!matching);
    $('sync-status').textContent=S.tab==='assembly'?'完整形成历史 · 选定最终质量样本':matching?'与投影红移一致':`统计 z = ${ztext(S.statsZ)} · 投影 z = ${ztext(projectionZ)}`;
    $('legend-note').textContent='';
    const atZ=rows=>rows.filter(r=>nearly(r.z,S.statsZ));
    const zr='z = '+ztext(S.statsZ);
    if(S.tab==='hmf') {
      const rows=atZ(D.hmf[S.definition]),ratio=atZ(D.hmfRatios[S.definition]);
      const theory=S.definition==='fof'?atZ(D.hmfReference):[];
      const massLabel=S.definition==='fof'?'M_FOF [M☉]':'M₂₀₀c [M☉]';
      const threshold=S.definition==='fof'?1e8:2e8;
      $('science-question').textContent='小尺度功率增强后，同一质量范围内的 halo 数量如何变化？';
      $('legend-note').textContent=S.definition==='fof'?'虚线：Reed07 理论参考；误差：Poisson':'误差：Poisson 计数不确定性';
      setHeading('a',S.definition==='fof'?'FOF halo 质量函数':'M₂₀₀c halo 质量函数',zr,`直接读取论文中的质量函数点。质量下限 ${fmt(threshold)} M☉；横轴保留源表中的质量坐标。`);
      setHeading('b','相对于 PL 的丰度',zr,'将论文配套逐 halo 目录按相同固定质量区间重新分箱后计算 BT/PL；误差由双方 Poisson 计数传播。该交互面板采用统一分箱，论文原图见下方。');
      chart('chart-a',[...grouped(rows),...grouped(theory,{dash:true}).map(s=>({...s,label:s.label+' · Reed07'}))],{title:'Halo 质量函数',xLabel:massLabel,yLabel:'dn / dlog₁₀M [Mpc⁻³]',errors:true,intervalLabel:'Poisson ±1σ',available});
      chart('chart-b',grouped(ratio),{title:'共同质量分箱的 BT/PL 丰度比',xLabel:massLabel,yLabel:'n_BT / n_PL',baseline:1,errors:true,intervalLabel:'传播的 Poisson ±1σ',available:unique(D.hmfRatios[S.definition].map(r=>r.z))});
      refs([[S.definition==='fof'?'mass-function.png':'mass-function-m200c-bocquet16.png','论文质量函数图']]);
      downloadRows=[...rows.map(r=>({...r,series:'published_hmf'})),...ratio.map(r=>({...r,series:'shared_bin_BT_over_PL'}))];
    } else if(S.tab==='power') {
      const rows=atZ(D.power).filter(r=>r.box===S.box),ratio=atZ(D.powerRatios).filter(r=>r.box===S.box);
      const trusted=[4*2*Math.PI/S.box,.25*Math.PI*1024/S.box];
      $('science-question').textContent='初始的小尺度功率增强，在非线性演化后保留在哪些尺度？';
      $('legend-note').textContent='虚线：HMcode2020；灰区：采用范围之外';
      setHeading('a','非线性物质功率谱',`${zr} · L = ${S.box}`,`L = ${S.box} h⁻¹ Mpc。采用区间 ${trusted[0].toFixed(2)} ≤ k ≤ ${trusted[1].toFixed(2)} h Mpc⁻¹；HMcode2020 曲线为理论参考。`);
      setHeading('b','相对于 PL 的功率',zr,'直接使用论文发布的同盒子 BT/PL 数据。灰区外保留原始趋势供查看；不跨盒子计算比值。');
      chart('chart-a',[...grouped(rows),...grouped(rows.map(r=>({...r,y:r.theory})),{dash:true}).map(s=>({...s,label:s.label+' · HMcode2020'}))],{title:'非线性物质功率谱',xLabel:'k [h Mpc⁻¹]',yLabel:'P(k) [(Mpc/h)³]',trusted,available});
      chart('chart-b',grouped(ratio),{title:'同盒子 BT/PL 功率比',xLabel:'k [h Mpc⁻¹]',yLabel:'P_BT / P_PL',baseline:1,trusted,available});
      refs([['power-spectrum_finite_box.png','论文非线性功率谱图'],['input-power-spectrum.png','输入线性物质功率谱']]);
      downloadRows=[...rows.map(r=>({...r,series:'power'})),...ratio.map(r=>({...r,series:'BT_over_PL'}))];
    } else if(S.tab==='assembly') {
      const rows=D.assembly.filter(r=>r.mass===S.mass);
      $('science-question').textContent='今天质量相近的 halo，过去怎样组装，又在何时达到一半质量？';
      $('legend-note').textContent='阴影：halo 间 16–84% 分位区间';
      setHeading('a','质量组装历史',`M₀ ≈ ${fmt(S.mass)} M☉`,'PL 与 BT kₚ=1 的相同最终质量窗口样本；显示逐 halo 的 M(z)/M₀ 中位数和散布。保留 same-TrackId 的原始历史口径。');
      setHeading('b','半质量形成红移','z = 0 选样','按最终 FOF 质量分组，显示 z₁/₂ 中位数与 halo 间 16–84% 分位数。该面板不随当前投影红移改写样本。');
      chart('chart-a',grouped(rows),{title:'质量组装历史',xLabel:'红移 z',yLabel:'median[M(z) / M₀]',xLog:false,bands:true,marker:projectionZ,intervalLabel:'halo 16–84%'});
      chart('chart-b',grouped(D.halfmass),{title:'半质量形成红移',xLabel:'最终 M_FOF [M☉]',yLabel:'z₁/₂',yLog:false,bands:true,intervalLabel:'halo 16–84%'});
      refs([['mass-assembly-history-correa.png','论文质量组装历史图'],['halfmass-redshift-trackid-no-envelope.png','论文半质量形成红移图']]);
      downloadRows=[...rows.map(r=>({...r,series:'assembly'})),...D.halfmass.map(r=>({...r,series:'half_mass_redshift'}))];
    } else {
      const rows=atZ(D.concentration),profiles=D.profiles.filter(r=>r.mass===S.profileMass);
      const convergence=Math.max(...profiles.map(r=>r.convergence));
      $('science-question').textContent='halo 的内部密度分布与浓度，是否随输入功率模型改变？';
      $('legend-note').textContent='浓度阴影：halo 散布；剖面阴影：bootstrap';
      setHeading('a','浓度–质量关系',zr,'SOAP c₂₀₀c 的中位数及 halo 间 16–84% 散布。保留源表的浓度质量筛选；灰区标出 1000 粒子尺度以下。');
      setHeading('b','直接粒子密度剖面',`固定 z = 0 · ${fmt(S.profileMass)} M☉`,'粒子计数得到的中位径向密度；阴影为中位数的 bootstrap 16–84% 区间。左侧灰区采用三个模型中最大的 Power 收敛半径。');
      chart('chart-a',grouped(rows),{title:'浓度与质量',xLabel:'M₂₀₀c [M☉]',yLabel:'c₂₀₀c',bands:true,trusted:[1.89e9,1e15],available,intervalLabel:'halo 16–84%'});
      chart('chart-b',grouped(profiles),{title:'z=0 直接粒子密度剖面',xLabel:'r / R₂₀₀m',yLabel:'ρ [M☉ kpc⁻³]',bands:true,trusted:[convergence,10],intervalLabel:'bootstrap 16–84%'});
      refs([['concentration-qc-i21-fit.png','论文浓度–质量关系'],['halo-density-radial-n100-power.png','论文直接粒子密度剖面']]);
      downloadRows=[...rows.map(r=>({...r,series:'concentration'})),...profiles.map(r=>({...r,series:'density_profile'}))];
    }
    $('download-data').textContent=downloadRows.length?'下载当前数据 ↓':'当前无可下载数据';
    $('download-data').setAttribute('aria-disabled',String(!downloadRows.length));
  }
  function renderProjection() {
    const f=D.projection.frames[S.frame];
    $('redshift').value=S.frame;
    $('redshift-output').textContent='z = '+ztext(f.z);
    $('redshift').setAttribute('aria-valuetext','红移 '+ztext(f.z));
    document.querySelectorAll('.frame-z').forEach(el=>{el.textContent='z = '+ztext(f.z);});
    document.querySelectorAll('[data-frame]').forEach(el=>el.classList.toggle('active',Number(el.dataset.frame)===S.frame));
    document.querySelectorAll('.projection-viewport').forEach(view=>{
      const sprite=view.querySelector('.projection-sprite');
      sprite.style.backgroundPosition=`${Number(view.dataset.col)*50}% ${f.row*50}%`;
      sprite.style.transform=`translate(${S.panX*100}%,${S.panY*100}%) scale(${S.zoom})`;
      view.classList.toggle('is-zoomed',S.zoom>1);
    });
  }
  function chooseFrame(frame, pause=true) {
    S.frame=Math.max(0,Math.min(2,Number(frame)));
    if(pause)stop();
    S.statsZ=D.projection.frames[S.frame].z;
    renderProjection();renderStats();
  }
  function stop(){if(timer)clearInterval(timer);timer=null;$('play').textContent='▶';$('play').setAttribute('aria-label','播放红移演化');$('play').setAttribute('aria-pressed','false');}
  function start(){stop();timer=setInterval(()=>chooseFrame((S.frame+1)%3,false),Number($('speed').value));$('play').textContent='Ⅱ';$('play').setAttribute('aria-label','暂停红移演化');$('play').setAttribute('aria-pressed','true');}
  $('play').addEventListener('click',()=>timer?stop():start());
  $('speed').addEventListener('change',()=>{if(timer)start();});
  $('redshift').addEventListener('input',event=>chooseFrame(event.target.value));
  document.querySelectorAll('[data-frame]').forEach(button=>button.addEventListener('click',()=>chooseFrame(button.dataset.frame)));
  document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
  window.addEventListener('scroll',()=>{$('tooltip').hidden=true;},{passive:true});
  $('zoom').addEventListener('change',event=>{S.zoom=Number(event.target.value);S.panX=0;S.panY=0;renderProjection();});
  $('reset-view').addEventListener('click',()=>{S.zoom=1;S.panX=0;S.panY=0;$('zoom').value='1';renderProjection();});
  const clampPan=()=>{const limit=(S.zoom-1)/2;S.panX=Math.max(-limit,Math.min(limit,S.panX));S.panY=Math.max(-limit,Math.min(limit,S.panY));};
  document.querySelectorAll('.projection-viewport').forEach(view=>{
    let drag=null;
    view.addEventListener('pointerdown',event=>{if(S.zoom<=1||event.button!==0)return;drag={x:event.clientX,y:event.clientY,panX:S.panX,panY:S.panY};view.setPointerCapture(event.pointerId);view.classList.add('is-dragging');});
    view.addEventListener('pointermove',event=>{if(!drag)return;S.panX=drag.panX+(event.clientX-drag.x)/view.clientWidth;S.panY=drag.panY+(event.clientY-drag.y)/view.clientHeight;clampPan();renderProjection();});
    const finish=()=>{drag=null;view.classList.remove('is-dragging');};
    view.addEventListener('pointerup',finish);view.addEventListener('pointercancel',finish);
    view.addEventListener('keydown',event=>{if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(event.key)||S.zoom<=1)return;event.preventDefault();S.panX+=event.key==='ArrowLeft'?.05:event.key==='ArrowRight'?-.05:0;S.panY+=event.key==='ArrowUp'?.05:event.key==='ArrowDown'?-.05:0;clampPan();renderProjection();});
  });
  const tabButtons=[...document.querySelectorAll('[role=tab]')];
  tabButtons.forEach((button,i)=>{
    button.addEventListener('click',()=>{S.tab=button.dataset.tab;renderStats();});
    button.addEventListener('keydown',event=>{let index;if(event.key==='ArrowRight')index=(i+1)%tabButtons.length;if(event.key==='ArrowLeft')index=(i+tabButtons.length-1)%tabButtons.length;if(event.key==='Home')index=0;if(event.key==='End')index=tabButtons.length-1;if(index!==undefined){event.preventDefault();tabButtons[index].click();tabButtons[index].focus();}});
  });
  $('stats-redshift').addEventListener('change',event=>{stop();S.statsZ=Number(event.target.value);renderStats();});
  $('follow-projection').addEventListener('click',()=>{S.statsZ=D.projection.frames[S.frame].z;renderStats();});
  $('mass-definition').addEventListener('change',event=>{S.definition=event.target.value;renderStats();});
  $('box-size').addEventListener('change',event=>{S.box=Number(event.target.value);renderStats();});
  for(const [id,rows,key,stateKey] of [['final-mass',D.assembly,'mass','mass'],['profile-mass',D.profiles,'mass','profileMass']]) {
    $(id).replaceChildren(...[...new Set(rows.map(r=>r[key]))].sort((a,b)=>a-b).map(m=>{const option=document.createElement('option');option.value=m;option.textContent=fmt(m)+' M☉';option.selected=m===S[stateKey];return option;}));
    $(id).addEventListener('change',event=>{S[stateKey]=Number(event.target.value);renderStats();});
  }
  $('download-data').addEventListener('click',event=>{
    event.preventDefault();
    if(!downloadRows.length)return;
    const keys=[...new Set(downloadRows.flatMap(r=>Object.keys(r)))];
    const quote=value=>'"'+String(value??'').replaceAll('"','""')+'"';
    const csv='\uFEFF'+[keys.map(quote).join(','),...downloadRows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');
    const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));
    const a=document.createElement('a');a.href=url;a.download=`article-${S.tab}-${S.tab==='assembly'?'history':'z'+ztext(S.statsZ)}.csv`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  $('download-data').href='#';
  $('build-date').textContent='数据打包 '+D.built.slice(0,10)+' · 离线可用';
  const image=new Image();image.src='assets/projection-clean.png';
  image.onerror=()=>{$('load-error').hidden=false;$('load-error').textContent='投影图片未加载，请确认 assets/projection-clean.png 与页面一同保存。';};
  renderProjection();renderStats();
})();
