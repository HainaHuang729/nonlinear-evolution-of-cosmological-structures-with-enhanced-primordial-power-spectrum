(async()=>{'use strict';
const $=id=>document.getElementById(id),canvas=$('view'),gl=canvas.getContext('webgl2',{antialias:true,alpha:false});
function fail(e){$('error').hidden=false;$('error').textContent=e.message||String(e);playing=false;$('play').textContent='播放';}
let playing=false;
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
const buffers=[gl.createBuffer(),gl.createBuffer()],boxBuffer=gl.createBuffer(),edges=[];
for(let axis=0;axis<3;axis++)for(let b=0;b<2;b++)for(let c=0;c<2;c++)for(let end=0;end<2;end++){let p=[];p[axis]=end-.5;p[(axis+1)%3]=b-.5;p[(axis+2)%3]=c-.5;edges.push(...p,0);}
gl.bindBuffer(gl.ARRAY_BUFFER,boxBuffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(edges),gl.STATIC_DRAW);
const res=await fetch('metadata.json');if(!res.ok)throw Error('metadata 加载失败');const meta=await res.json();
let target=56,display=56,loaded=-1,version=0,controller=null,fetching=false,yaw=-.9,pitch=.42,distance=2.6,center=[0,0,0],frames=0,lastPerf=performance.now(),fps=0;
const cache=new Map();let visible=0;
async function load(i,signal){if(cache.has(i))return cache.get(i);const r=await fetch(meta.frames[i].file,{signal});if(!r.ok)throw Error(`快照 ${i} 加载失败 (${r.status})`);const bytes=await r.arrayBuffer();if(bytes.byteLength!==meta.count*16)throw Error('缓存长度不一致');const data=new Float32Array(bytes);if(signal.aborted)throw new DOMException('Aborted','AbortError');cache.set(i,data);prune();return data;}
function prune(){const i=Math.floor(target);for(const k of [...cache.keys()])if(cache.size>3 && k!==i&&k!==Math.min(i+1,56))cache.delete(k);}
function countVisible(){if(loaded<0)return;const a=cache.get(loaded),b=cache.get(Math.min(loaded+1,56));if(!a||!b)return;const t=display-loaded,min=+$('threshold').value;visible=0;for(let k=3;k<a.length;k+=4)if(a[k]*(1-t)+b[k]*t>=min)visible++;}
function updateTime(){const i=Math.floor(display),t=display-i,a=meta.frames[i].a*(1-t)+meta.frames[Math.min(i+1,56)].a*t;$('time').textContent=`z = ${Math.max(0,1/a-1).toFixed(3)} · a = ${a.toFixed(4)}${t>1e-5?' · 插值':''}`;countVisible();}
async function seek(value){target=Math.max(0,Math.min(56,value));$('timeline').value=target;const i=Math.floor(target);
if(i===loaded){if(fetching){version++;controller?.abort();fetching=false;}display=target;updateTime();return;}
const serial=++version;controller?.abort();controller=new AbortController();const signal=controller.signal;fetching=true;
try{const [a,b]=await Promise.all([load(i,signal),load(Math.min(i+1,56),signal)]);if(serial!==version)return;
for(let k=0;k<2;k++){gl.bindBuffer(gl.ARRAY_BUFFER,buffers[k]);gl.bufferData(gl.ARRAY_BUFFER,k?b:a,gl.STATIC_DRAW);}loaded=i;display=target;fetching=false;prune();updateTime();$('error').hidden=true;
if(i+2<57&&!cache.has(i+2))load(i+2,signal).catch(e=>{if(e.name!=='AbortError')console.warn('Prefetch deferred');});
}catch(e){if(serial===version){fetching=false;if(e.name!=='AbortError')fail(e);}}}
$('timeline').oninput=()=>{playing=false;$('play').textContent='播放';seek(+$('timeline').value);};
$('play').onclick=()=>{playing=!playing;$('play').textContent=playing?'暂停':'播放';if(playing&&target>=56)seek(0);};
$('threshold').oninput=()=>{$('threshold-value').textContent=$('threshold').value;countVisible();};
$('reset').onclick=()=>{yaw=-.9;pitch=.42;distance=2.6;center=[0,0,0];};
function basis(){const f=[-Math.cos(yaw)*Math.cos(pitch),-Math.sin(yaw)*Math.cos(pitch),-Math.sin(pitch)],r=[-Math.sin(yaw),Math.cos(yaw),0],u=[-Math.cos(yaw)*Math.sin(pitch),-Math.sin(yaw)*Math.sin(pitch),Math.cos(pitch)];return {f,r,u};}
function pan(dx,dy){const {r,u}=basis();center=center.map((v,k)=>v-dx*.0015*distance*r[k]+dy*.0015*distance*u[k]);}
const pointers=new Map();let previous=null;
canvas.oncontextmenu=e=>e.preventDefault();canvas.onpointerdown=e=>{canvas.setPointerCapture(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);previous=null;};
canvas.onpointermove=e=>{if(!pointers.has(e.pointerId))return;const old=pointers.get(e.pointerId);pointers.set(e.pointerId,[e.clientX,e.clientY]);if(pointers.size===1){if(e.shiftKey||e.buttons===2)pan(e.clientX-old[0],e.clientY-old[1]);else{yaw-=(e.clientX-old[0])*.006;pitch=Math.max(-1.45,Math.min(1.45,pitch+(e.clientY-old[1])*.006));}}else{const [a,b]=[...pointers.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),mid=[(a[0]+b[0])/2,(a[1]+b[1])/2];if(previous){distance=Math.max(.7,Math.min(10,distance*previous.d/Math.max(1,d)));pan(mid[0]-previous.mid[0],mid[1]-previous.mid[1]);}previous={d,mid};}};
canvas.onpointerup=canvas.onpointercancel=e=>{pointers.delete(e.pointerId);previous=null;};
canvas.addEventListener('wheel',e=>{e.preventDefault();distance=Math.max(.7,Math.min(10,distance*Math.exp(e.deltaY*.001)));},{passive:false});
document.addEventListener('visibilitychange',()=>{if(document.hidden){playing=false;$('play').textContent='播放';}});
canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();fail(Error('图形上下文丢失，请刷新页面。'));});
let last=performance.now();function draw(now){const dt=Math.min(.1,(now-last)/1000);last=now;
if(playing&&!fetching){const next=Math.min(56,target+dt*4);seek(next);if(next>=56){playing=false;$('play').textContent='播放';}}
const ratio=Math.min(devicePixelRatio||1,2),w=Math.max(1,Math.round(canvas.clientWidth*ratio)),h=Math.max(1,Math.round(canvas.clientHeight*ratio));if(canvas.width!==w||canvas.height!==h){canvas.width=w;canvas.height=h;}gl.viewport(0,0,w,h);gl.clearColor(.015,.024,.039,1);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);
if(loaded>=0){const {f,r,u}=basis();gl.uniform3fv(U.eye,center.map((v,k)=>v-distance*f[k]));gl.uniform3fv(U.right,r);gl.uniform3fv(U.up,u);gl.uniform3fv(U.forward,f);gl.uniform1f(U.aspect,w/h);gl.uniform1f(U.alpha,display-loaded);gl.uniform1f(U.threshold,+$('threshold').value);gl.uniform1f(U.pointSize,+$('size').value*ratio);gl.uniform1i(U.colored,+$('color').value);gl.uniform1i(U.line,0);gl.enable(gl.DEPTH_TEST);gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);
for(let k=0;k<2;k++){gl.bindBuffer(gl.ARRAY_BUFFER,buffers[k]);gl.enableVertexAttribArray(k);gl.vertexAttribPointer(k,4,gl.FLOAT,false,16,0);}gl.drawArrays(gl.POINTS,0,meta.count);
if($('box').checked){gl.uniform1i(U.line,1);gl.bindBuffer(gl.ARRAY_BUFFER,boxBuffer);for(let k=0;k<2;k++)gl.vertexAttribPointer(k,4,gl.FLOAT,false,16,0);gl.drawArrays(gl.LINES,0,24);}}
frames++;if(now-lastPerf>1000){fps=frames*1000/(now-lastPerf);frames=0;lastPerf=now;}$('status').textContent=`${fetching?'加载目标快照；暂保留上一帧':'已加载'} · 显示 ${visible.toLocaleString()} / 100,000 · ${fps.toFixed(1)} FPS · CPU 帧缓存 ${cache.size}/3`;
window.swiftState={loaded,display,visible,cacheCount:cache.size,fetching,fps,yaw,distance,glError:gl.getError()};requestAnimationFrame(draw);}
requestAnimationFrame(draw);await seek(56);
}catch(e){fail(e);}
})();
