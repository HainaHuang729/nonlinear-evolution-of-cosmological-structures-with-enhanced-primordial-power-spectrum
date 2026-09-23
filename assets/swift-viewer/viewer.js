(async()=>{'use strict';
const $=id=>document.getElementById(id),canvas=$('view'),gl=canvas.getContext('webgl2',{antialias:true,alpha:false});
function fail(e){$('error').hidden=false;$('error').textContent=e.message||String(e);playing=false;$('play').textContent='播放';}
let playing=false,buffering=false,playTicket=0;
try{
if(!gl)throw Error('此浏览器无法建立 WebGL2。请启用硬件加速或尝试其他浏览器。');
const vs=`#version 300 es
precision highp float;
layout(location=0) in vec4 first;layout(location=1) in vec4 second;
uniform float alpha,threshold,pointSize,aspect;uniform vec3 eye,right,up,forward;uniform bool line;
out float speed;out float visible;
void main(){vec3 d=second.xyz-first.xyz;d-=roundEven(d);vec3 p=line?first.xyz:mod(first.xyz+alpha*d+0.5,1.)-0.5;
speed=mix(first.w,second.w,alpha);visible=(line||speed>=threshold)?1.:0.;
vec3 v=p-eye;float z=dot(v,forward);gl_Position=vec4(dot(v,right)*2.414/aspect,dot(v,up)*2.414,1.0002*z-0.020002,z);gl_PointSize=pointSize;}`;
const fs=`#version 300 es
precision highp float;in float speed;in float visible;uniform bool line,colored;out vec4 color;
void main(){if(visible<.5)discard;if(line){color=vec4(.22,.32,.43,.65);return;}float r=length(gl_PointCoord-.5);if(r>.5)discard;vec3 c=colored?mix(vec3(.05,.16,.45),vec3(1.,.55,.12),clamp(speed/1000.,0.,1.)):vec3(.55,.72,.95);color=vec4(c,.8*(1.-smoothstep(.3,.5,r)));}`;
function shader(type,src){const s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s;}
const program=gl.createProgram();gl.attachShader(program,shader(gl.VERTEX_SHADER,vs));gl.attachShader(program,shader(gl.FRAGMENT_SHADER,fs));gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw Error(gl.getProgramInfoLog(program));gl.useProgram(program);
const U={};for(const name of ['alpha','threshold','pointSize','aspect','eye','right','up','forward','line','colored'])U[name]=gl.getUniformLocation(program,name);
const gpuCache=new Map();const boxBuffer=gl.createBuffer(),edges=[];
for(let axis=0;axis<3;axis++)for(let b=0;b<2;b++)for(let c=0;c<2;c++)for(let end=0;end<2;end++){let p=[];p[axis]=end-.5;p[(axis+1)%3]=b-.5;p[(axis+2)%3]=c-.5;edges.push(...p,0);}
gl.bindBuffer(gl.ARRAY_BUFFER,boxBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(edges),gl.STATIC_DRAW);
const comparison=new URLSearchParams(location.search).get('compare')==='1';
const quality500=comparison&&new URLSearchParams(location.search).get('quality')==='500k';
if(comparison){document.querySelector('header').style.display='none';document.querySelector('aside').style.display='none';document.querySelector('main').style.cssText='display:block;height:100dvh';canvas.style.height='100dvh';}
const res=await fetch(quality500?'metadata500.json':'metadata.json');if(!res.ok)throw Error('metadata 加载失败');const meta=await res.json();
const minA=meta.frames[0].a,maxA=meta.frames[56].a,rateA=(maxA-minA)/14;
if(!meta.frames.every((f,i)=>Number.isFinite(f.a)&&f.a>0&&(!i||f.a>meta.frames[i-1].a)))throw Error('Scale factor metadata must increase strictly');
function scaleAt(index){const i=Math.floor(index),t=index-i;return meta.frames[i].a*(1-t)+meta.frames[Math.min(i+1,56)].a*t;}
function indexAt(a){a=Math.max(minA,Math.min(maxA,a));if(a>=maxA-1e-12)return 56;if(a<=minA+1e-12)return 0;let lo=0,hi=56;while(hi-lo>1){const mid=(lo+hi)>>1;if(meta.frames[mid].a<=a)lo=mid;else hi=mid;}return lo+(a-meta.frames[lo].a)/(meta.frames[hi].a-meta.frames[lo].a);}
$('timeline').min=minA;$('timeline').max=maxA;$('timeline').step='any';$('timeline').value=maxA;
window.swiftTimeline={scaleAt,indexAt,minA,maxA,rateA};
let target=56,display=56,loaded=-1,version=0,controller=null,fetching=false,yaw=-.9,pitch=.42,distance=2.6,center=[0,0,0],frames=0,lastPerf=performance.now(),fps=0;
const cache=new Map(),pending=new Map(),queue=[];let visible=0,fullCache=false,activeLoads=0,requestId=0,countId=0,lastCount=0,lastUI=0,glError=0,bufferWaits=0,uploads=0;
const worker=new Worker('cache-worker.js?rev=smooth1');
worker.onerror=()=>fail(Error('缓存 Worker 出错，请刷新页面。'));
worker.onmessage=({data:m})=>{
 if(m.type==='counted'){if(m.id===countId)visible=m.visible;return;}
 const item=pending.get(m.index??m.id);if(!item)return;
 pending.delete(item.index);activeLoads--;
 if(m.type==='error')item.reject(Error(m.message));
 else{cache.set(item.index,new Float32Array(m.bytes));prune();item.resolve(cache.get(item.index));}
 pump();
};
function pump(){while(activeLoads<4&&queue.length){const item=queue.shift();activeLoads++;worker.postMessage({type:'load',id:item.index,index:item.index,url:new URL(meta.frames[item.index].file,location.href).href,count:meta.count});}}
function load(i,priority=false){if(cache.has(i))return Promise.resolve(cache.get(i));if(pending.has(i)){
 const item=pending.get(i),at=queue.indexOf(item);if(priority&&at>=0){queue.splice(at,1);queue.unshift(item);}return item.promise;}
 let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});const item={index:i,promise,resolve,reject};pending.set(i,item);priority?queue.unshift(item):queue.push(item);pump();return promise;}
function prune(){const i=Math.floor(target),limit=fullCache?57:16,protect=new Set([i,Math.min(i+1,56),loaded,Math.min(loaded+1,56)]);
 const candidates=[...cache.keys()].filter(k=>!protect.has(k)).sort((a,b)=>Math.abs(b-i)-Math.abs(a-i));
 while(cache.size>limit&&candidates.length){const k=candidates.shift();cache.delete(k);worker.postMessage({type:'drop',index:k});}}
function windowEnd(i){return Math.min(56,i+Math.min(11,Math.max(3,Math.ceil(indexAt(Math.min(maxA,scaleAt(i)+rateA*1.5)))-i+1)));}
function warm(i){if(fullCache||comparison)return;for(let k=i;k<=windowEnd(i);k++)load(k).catch(()=>{});}
function upload(i){if(gpuCache.has(i))return gpuCache.get(i);const data=cache.get(i);if(!data)return null;
 if(gpuCache.size>=4){const protectedKeys=new Set([loaded,Math.min(loaded+1,56),Math.floor(target),Math.min(Math.floor(target)+1,56)]);let victim=[...gpuCache.keys()].find(k=>!protectedKeys.has(k));if(victim===undefined)return null;gl.deleteBuffer(gpuCache.get(victim));gpuCache.delete(victim);}
 const buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,data,gl.STATIC_DRAW);gpuCache.set(i,buffer);uploads++;return buffer;}
function countVisible(force=false){const now=performance.now();if(loaded<0||(!force&&now-lastCount<200))return;lastCount=now;const threshold=0;countId++;
 if(threshold===0){visible=meta.count;return;}worker.postMessage({type:'count',id:countId,i:loaded,j:Math.min(loaded+1,56),alpha:display-loaded,threshold});}
function updateTime(){const i=Math.floor(display),t=display-i,a=scaleAt(display);$('time').textContent=`z = ${Math.max(0,1/a-1).toFixed(3)} · a = ${a.toFixed(4)}${t>1e-5?' · 插值':''}`;countVisible();}
async function seek(value){target=Math.max(0,Math.min(56,value));$('timeline').value=scaleAt(target);const i=Math.floor(target);
 if(i===loaded){if(fetching){version++;fetching=false;}display=target;return;}
 const serial=++version;fetching=true;if(!cache.has(i)||!cache.has(Math.min(i+1,56)))bufferWaits++;
 try{await Promise.all([load(i,true),load(Math.min(i+1,56),true)]);if(serial!==version)return;
 // Evict only buffers outside the new pair before switching; never re-upload the shared endpoint.
 for(const k of [...gpuCache.keys()])if(gpuCache.size>2&&k!==i&&k!==Math.min(i+1,56)){gl.deleteBuffer(gpuCache.get(k));gpuCache.delete(k);}
 loaded=i;upload(i);upload(Math.min(i+1,56));display=target;fetching=false;prune();countVisible(true);$('error').hidden=true;warm(i);
 }catch(e){if(serial===version){fetching=false;fail(e);}}}
function stop(){playTicket++;playing=false;buffering=false;$('play').textContent='播放';}
$('timeline').oninput=()=>{stop();seek(indexAt(+$('timeline').value));};
$('play').onclick=async()=>{
 if(playing||buffering){stop();return;}
 const ticket=++playTicket;buffering=true;$('play').textContent='取消准备';
 try{if(target>=56)await seek(0);const i=Math.floor(target);await Promise.all(Array.from({length:windowEnd(i)-i+1},(_,k)=>load(i+k,true)));
 if(ticket!==playTicket)return;buffering=false;playing=true;$('play').textContent='暂停';
 }catch(e){if(ticket===playTicket){buffering=false;fail(e);}}
};
$('preload').onclick=async()=>{fullCache=true;$('preload').disabled=true;$('preload').textContent='正在预载完整序列…';
 try{await Promise.all(meta.frames.map((_,i)=>load(i)));$('preload').textContent='完整预载已完成';}
 catch(e){$('preload').disabled=false;$('preload').textContent='重试完整预载';fail(e);}
};

$('reset').onclick=()=>{yaw=-.9;pitch=.42;distance=2.6;center=[0,0,0];};
function basis(){const f=[-Math.cos(yaw)*Math.cos(pitch),-Math.sin(yaw)*Math.cos(pitch),-Math.sin(pitch)],r=[-Math.sin(yaw),Math.cos(yaw),0],u=[-Math.cos(yaw)*Math.sin(pitch),-Math.sin(yaw)*Math.sin(pitch),Math.cos(pitch)];return {f,r,u};}
function pan(dx,dy){const {r,u}=basis();center=center.map((v,k)=>v-dx*.0015*distance*r[k]+dy*.0015*distance*u[k]);}
const pointers=new Map();let previous=null;
canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);previous=null;};
canvas.onpointermove=e=>{if(!pointers.has(e.pointerId))return;const old=pointers.get(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===1){if(e.shiftKey||e.buttons===2)pan(e.clientX-old[0],e.clientY-old[1]);else{yaw-=(e.clientX-old[0])*.006;pitch=Math.max(-1.45,Math.min(1.45,pitch+(e.clientY-old[1])*.006));}}else{const [a,b]=[...pointers.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),mid=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(previous){distance=Math.max(.7,Math.min(10,distance*previous.d/Math.max(1,d)));pan(mid[0]-previous.mid[0],mid[1]-previous.mid[1]);}previous={d,mid};}};
canvas.onpointerup=canvas.onpointercancel=e=>{pointers.delete(e.pointerId);previous=null;};
canvas.addEventListener('wheel',e=>{e.preventDefault();distance=Math.max(.7,Math.min(10,distance*Math.exp(e.deltaY*.001)));},{passive:false});
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail(Error('图形上下文丢失，请刷新页面。'));});
let active=true,renderedFrames=0;const renderIntervals=[];
if(comparison)window.swiftCompare={seek,meta,setActive:v=>{active=v;},camera:()=>({yaw,pitch,distance,center:[...center]}),setCamera:p=>{yaw=p.yaw;pitch=p.pitch;distance=p.distance;center=[...p.center];},metrics:()=>({renderedFrames,intervals:[...renderIntervals],renderer:gl.getParameter(gl.RENDERER),resolution:[canvas.width,canvas.height],dpr:devicePixelRatio})};
if(comparison){for(const event of ['pointermove','wheel'])canvas.addEventListener(event,()=>{parent.postMessage({type:'swift-camera',camera:window.swiftCompare.camera()},location.origin);});}
let last=performance.now();function draw(now){const dt=Math.max(0,(now-last)/1000);last=now;
if(!active){requestAnimationFrame(draw);return;}
if(playing&&!fetching){const next=indexAt(scaleAt(target)+dt*rateA);seek(next);if(next>=56){playing=false;$('play').textContent='播放';}}
const ratio=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.round(canvas.clientWidth*ratio)),h=Math.max(1,Math.round(canvas.clientHeight*ratio));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.viewport(0,0,w,h);gl.clearColor(.015,.024,.039,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
if(loaded>=0){const {f,r,u}=basis();gl.uniform3fv(U.eye,center.map((v,k)=>v-distance*f[k]));gl.uniform3fv(U.right,r);gl.uniform3fv(U.up,u);gl.uniform3fv(U.forward,f);gl.uniform1f(U.aspect,w/h);gl.uniform1f(U.alpha,display-loaded);gl.uniform1f(U.threshold,0);gl.uniform1f(U.pointSize,1.5*ratio);gl.uniform1i(U.colored,1);gl.uniform1i(U.line,0);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
for(let k=0;k<2;k++){gl.bindBuffer(gl.ARRAY_BUFFER,gpuCache.get(Math.min(loaded+k,56)));gl.enableVertexAttribArray(k);gl.vertexAttribPointer(k,4,gl.FLOAT,false,16,0);}gl.drawArrays(gl.POINTS,0,meta.count);
if($('box').checked){gl.uniform1i(U.line,1);gl.bindBuffer(gl.ARRAY_BUFFER,boxBuffer);for(let k=0;k<2;k++)gl.vertexAttribPointer(k,4,gl.FLOAT,false,16,0);gl.drawArrays(gl.LINES,0,24);}}
// Prepare one future GPU buffer per draw instead of uploading both endpoints at the boundary.
if(loaded>=0){for(let k=loaded+2;k<=Math.min(56,loaded+3);k++)if(cache.has(k)&&!gpuCache.has(k)){upload(k);break;}}
frames++;if(now-lastPerf>1000){fps=frames*1000/(now-lastPerf);frames=0;lastPerf=now;glError=gl.getError();}
renderedFrames++;renderIntervals.push(dt*1000);if(renderIntervals.length>120)renderIntervals.shift();
if(now-lastUI>=200){lastUI=now;updateTime();
$('status').textContent=buffering?'正在准备播放…':fetching?'加载中…':fullCache&&cache.size<57?`预载 ${cache.size} / 57` :playing?'播放中':'就绪';}
window.swiftState={loaded,display,scaleFactor:scaleAt(display),timeMode:'linear-a',visible,cacheCount:cache.size,cacheLimit:fullCache?57:16,gpuFrames:gpuCache.size,fetching,buffering,playing,bufferWaits,uploads,activeLoads,fps,yaw,distance,glError};requestAnimationFrame(draw);}
requestAnimationFrame(draw);await seek(56);
}catch(e){fail(e);}
})();
