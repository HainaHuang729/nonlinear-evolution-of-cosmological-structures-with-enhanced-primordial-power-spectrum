'use strict';
const speeds=new Map();
onmessage=async({data:m})=>{
try{
if(m.type==='load'){
 const r=await fetch(m.url);if(!r.ok)throw Error(`快照加载失败 (${r.status})`);
 const bytes=await r.arrayBuffer();if(bytes.byteLength!==m.count*16)throw Error('缓存长度不一致');
 const values=new Float32Array(bytes),s=new Float32Array(m.count);for(let k=0;k<m.count;k++)s[k]=values[k*4+3];speeds.set(m.index,s);
 postMessage({type:'loaded',id:m.id,index:m.index,bytes},[bytes]);
}else if(m.type==='drop')speeds.delete(m.index);
else if(m.type==='count'){
 const a=speeds.get(m.i),b=speeds.get(m.j);if(!a||!b)return;
 let visible=0;for(let k=0;k<a.length;k++)if(a[k]*(1-m.alpha)+b[k]*m.alpha>=m.threshold)visible++;
 postMessage({type:'counted',id:m.id,visible});
}
}catch(e){postMessage({type:'error',id:m.id,message:e.message});}
};
