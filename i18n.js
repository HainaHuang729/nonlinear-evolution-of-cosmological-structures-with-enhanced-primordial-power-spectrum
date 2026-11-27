/* Translate presentation nodes in place; controls, media and scientific state stay intact. */
(() => {
  'use strict';
  const catalog=window.ARTICLE_EN||{};
  const phrases=Object.keys(catalog).sort((a,b)=>b.length-a.length);
  const patterns=window.ARTICLE_EN_PATTERNS||[];
  const originals=new WeakMap(),cache=new Map();
  const han=/[\u3400-\u9fff]/;
  const attributes=['aria-label','aria-valuetext','title','alt','placeholder','data-series'];
  let language='zh';
  try{const saved=localStorage.getItem('article-language');if(saved==='en')language='en';}catch{}
  const requested=new URL(location.href).searchParams.get('lang');
  if(requested==='en'||requested==='zh')language=requested;
  let observer;
  function english(value){
    if(!value)return value;
    if(cache.has(value))return cache.get(value);
    const source=value.trim();
    let result=catalog[source];
    if(result===undefined){
      for(const [pattern,replace] of patterns){if(pattern.test(source)){result=source.replace(pattern,replace);break;}}
    }
    if(result===undefined){
      result=source;
      if(han.test(result))for(const phrase of phrases)if(result.includes(phrase))result=result.split(phrase).join(catalog[phrase]);
      result=result.replaceAll('，',', ').replaceAll('；','; ').replaceAll('：',': ').replaceAll('。','.').replaceAll('？','?').replaceAll('、',', ').replaceAll('「','“').replaceAll('」','”');
    }
    const translated=source?value.replace(source,result):value;
    cache.set(value,translated);return translated;
  }
  function ignored(node){
    const element=node.nodeType===Node.ELEMENT_NODE?node:node.parentElement;
    return !element||!!element.closest('script,style,template,noscript,[data-no-i18n]');
  }
  function update(node,key,current,write){
    let record=originals.get(node);if(!record){record=new Map();originals.set(node,record);}
    let entry=record.get(key);
    if(!entry||current!==entry.rendered)entry={source:current,rendered:current};
    const output=language==='en'?english(entry.source):entry.source;
    entry.rendered=output;record.set(key,entry);
    if(output!==current)write(output);
  }
  function translateNode(node){
    if(ignored(node))return;
    if(node.nodeType===Node.TEXT_NODE){update(node,'text',node.data,value=>{node.data=value;});return;}
    if(node.nodeType!==Node.ELEMENT_NODE)return;
    for(const key of attributes)if(node.hasAttribute(key))update(node,key,node.getAttribute(key),value=>node.setAttribute(key,value));
    if(node.matches('meta[name=description]'))update(node,'content',node.content,value=>{node.content=value;});
  }
  function translateTree(root){
    translateNode(root);
    const walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT,{acceptNode:node=>ignored(node)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
    while(walker.nextNode())translateNode(walker.currentNode);
  }
  function observe(){observer?.observe(document.documentElement,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:[...attributes,'content']});}
  function updateButton(){
    const button=document.getElementById('language-toggle');if(!button)return;
    button.textContent=language==='zh'?'EN':'中文';
    button.lang=language==='zh'?'en':'zh-CN';
    button.setAttribute('aria-label',language==='zh'?'Switch to English':'切换为中文');
    button.title=language==='zh'?'Switch to English':'切换为中文';
  }
  function setLanguage(next,persist=true){
    if(!['zh','en'].includes(next))return;
    observer?.disconnect();language=next;
    document.documentElement.lang=next==='en'?'en':'zh-CN';
    translateTree(document.documentElement);updateButton();observe();
    if(persist)try{localStorage.setItem('article-language',next);}catch{}
    window.dispatchEvent(new CustomEvent('languagechange',{detail:{language:next}}));
  }
  window.ArticleI18n=Object.freeze({english,setLanguage,get language(){return language;},sourceAttribute:(node,key)=>originals.get(node)?.get(key)?.source??node.getAttribute(key)});
  document.addEventListener('DOMContentLoaded',()=>{
    observer=new MutationObserver(records=>{
      const roots=new Set();
      for(const record of records){
        if(record.type==='childList')record.addedNodes.forEach(node=>roots.add(node));
        else roots.add(record.target);
      }
      observer.disconnect();
      roots.forEach(node=>{if(node.isConnected)translateTree(node);});observe();
    });
    setLanguage(language,false);
    document.getElementById('language-toggle')?.addEventListener('click',()=>setLanguage(language==='zh'?'en':'zh'));
  });
})();
