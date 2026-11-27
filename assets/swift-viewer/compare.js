'use strict';
const statusEl=document.getElementById('comparison-status'),controls=[...document.querySelectorAll('button')],left=document.getElementById('left'),right=document.getElementById('right');
const windows=()=>[left.contentWindow,right.contentWindow];let ready=false,busy=false,generation=0;
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
function lock(on){busy=on;controls.forEach(b=>b.disabled=on);}
lock(true);
(async()=>{try{const start=performance.now();while(!windows().every(w=>w.swiftCompare&&w.swiftState?.loaded===56)){if(performance.now()-start>120000)throw Error('视图加载超时，请刷新重试。');await sleep(100);}
ready=true;for(const b of document.querySelectorAll('[data-snap]')){const f=windows()[0].swiftCompare.meta.frames[+b.dataset.snap];b.textContent=b.textContent.split(' · ')[0]+` · z = ${f.z.toFixed(2)}`;}
lock(false);statusEl.textContent='已就绪 · 拖动任一窗口，两边同步';}catch(e){statusEl.textContent=e.message;}})();
window.addEventListener('message',e=>{if(!ready||busy||e.origin!==location.origin||e.data?.type!=='swift-camera')return;if(e.source===left.contentWindow)right.contentWindow.swiftCompare.setCamera(e.data.camera);if(e.source===right.contentWindow)left.contentWindow.swiftCompare.setCamera(e.data.camera);});
async function seekBoth(t){await Promise.all(windows().map(w=>w.swiftCompare.seek(t)));}
for(const button of document.querySelectorAll('[data-snap]'))button.onclick=async()=>{generation++;lock(true);statusEl.textContent='加载匹配快照…';try{await seekBoth(+button.dataset.snap);statusEl.textContent='同一快照、相机、输出大小与配色';}catch(e){statusEl.textContent=e.message;}finally{lock(false);}};
document.getElementById('clip').onclick=async()=>{const serial=++generation;lock(true);try{await seekBoth(55);const start=performance.now();let f=0;while(f<1&&serial===generation){await new Promise(r=>requestAnimationFrame(r));f=Math.min(1,(performance.now()-start)/6000);await seekBoth(55+f);statusEl.textContent='snapshot 0055 → 0056 · 6 秒 · 周期插值';}}catch(e){statusEl.textContent=e.message;}finally{lock(false);}};
document.getElementById('benchmark').onclick=async()=>{generation++;lock(true);const results=[];const pose=windows()[0].swiftCompare.camera();
try{await seekBoth(55.5);for(let k=0;k<2;k++){
const w=windows()[k];windows().forEach((v,i)=>v.swiftCompare.setActive(i===k));w.swiftCompare.setCamera(pose);statusEl.textContent=`测试 ${k?'500k':'100k'}：另一窗口已暂停…`;await sleep(600);
const start=performance.now(),before=w.swiftCompare.metrics().renderedFrames;const samples=[];
for(let n=0;n<60;n++){w.swiftCompare.setCamera({...pose,yaw:pose.yaw+n*.003});await new Promise(r=>requestAnimationFrame(r));}
const elapsed=performance.now()-start,metrics=w.swiftCompare.metrics();
for(const t of [55.1,55.3,55.5,55.7,55.9]){const begin=performance.now();await w.swiftCompare.seek(t);await new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));samples.push(performance.now()-begin);}
results.push({cohort:k?500000:100000,fps:(metrics.renderedFrames-before)*1000/elapsed,frame_change_ms:samples,resolution:metrics.resolution,dpr:metrics.dpr,renderer:metrics.renderer,gpu_ms:null});w.swiftCompare.setCamera(pose);
}document.getElementById('results').textContent=results.map(r=>`${r.cohort.toLocaleString()} 粒子：${r.fps.toFixed(1)} FPS；缓存换帧（含绘制等待） ${Math.min(...r.frame_change_ms).toFixed(2)}–${Math.max(...r.frame_change_ms).toFixed(2)} ms；${r.resolution.join('×')} px`).join('\n');window.swiftBenchmark=results;statusEl.textContent='本机测试完成；GPU 耗时与显存未测';
}catch(e){statusEl.textContent=e.message;}finally{windows().forEach(w=>w.swiftCompare.setActive(true));await seekBoth(56);lock(false);}};
