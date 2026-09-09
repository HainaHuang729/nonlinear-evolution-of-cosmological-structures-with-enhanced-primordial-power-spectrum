/* Content-independent presentation components. No data fetching or app state. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const NS='http://www.w3.org/2000/svg';
  const indices=new WeakMap();
  const svgNode=(tag,attrs)=>{
    const node=document.createElementNS(NS,tag);
    Object.entries(attrs).forEach(([name,value])=>node.setAttribute(name,value));
    return node;
  };
  function frameIndex(root,{items,index,onSelect,label='FRAME',selectLabel='选择条目'}) {
    if(!root||!items.length)return;
    const key=JSON.stringify([items,label,selectLabel]);
    let state=indices.get(root);
    if(!state||state.key!==key){
      const diagram=svgNode('svg',{viewBox:'0 0 300 300','aria-hidden':'true'});
      diagram.append(svgNode('circle',{cx:150,cy:150,r:124}),svgNode('circle',{cx:150,cy:150,r:92,class:'index-ring-inner'}));
      const needle=svgNode('line',{x1:150,y1:150,x2:150,y2:58,class:'index-needle'});
      diagram.append(needle,svgNode('circle',{cx:150,cy:150,r:3,class:'index-origin'}));
      const reading=document.createElement('div');reading.className='index-reading';
      const count=document.createElement('span'),value=document.createElement('strong');reading.append(count,value);
      root.replaceChildren(diagram,reading);
      state={key,needle,count,value,onSelect,buttons:[]};indices.set(root,state);
      items.forEach((item,i)=>{
        const angle=i/items.length*Math.PI*2-Math.PI/2;
        const button=document.createElement('button');button.type='button';
        button.textContent=String(i+1).padStart(2,'0');
        button.setAttribute('aria-label',selectLabel+' '+(i+1)+'：'+item.label);
        button.style.setProperty('--x',(50+Math.cos(angle)*41.333)+'%');
        button.style.setProperty('--y',(50+Math.sin(angle)*41.333)+'%');
        button.addEventListener('click',()=>indices.get(root).onSelect(i));
        button.addEventListener('keydown',event=>{
          const keys={ArrowRight:(i+1)%items.length,ArrowDown:(i+1)%items.length,ArrowLeft:(i+items.length-1)%items.length,ArrowUp:(i+items.length-1)%items.length,Home:0,End:items.length-1};
          if(!(event.key in keys))return;
          event.preventDefault();const next=keys[event.key];
          indices.get(root).onSelect(next);indices.get(root).buttons[next].focus({preventScroll:true});
        });
        state.buttons.push(button);root.append(button);
      });
    }
    state.onSelect=onSelect;
    state.buttons.forEach((button,i)=>button.setAttribute('aria-pressed',String(i===index)));
    state.count.textContent=label+' / '+String(index+1).padStart(2,'0')+' OF '+String(items.length).padStart(2,'0');
    state.value.textContent=items[index].label;
    const angle=index/items.length*Math.PI*2-Math.PI/2;
    state.needle.setAttribute('x2',150+Math.cos(angle)*110);
    state.needle.setAttribute('y2',150+Math.sin(angle)*110);
  }
  window.ScientificModernism=Object.freeze({frameIndex});

  document.addEventListener('DOMContentLoaded',()=>{
    const toggle=document.querySelector('.navigation-toggle');
    const navigation=document.getElementById(toggle?.getAttribute('aria-controls'));
    const mobile=matchMedia('(max-width:720px)');
    const header=document.querySelector('.topbar');
    if(header&&'ResizeObserver' in window)new ResizeObserver(()=>{
      document.documentElement.style.setProperty('--header-height',header.getBoundingClientRect().height+'px');
    }).observe(header);
    // Optional placement adapter: move an existing control without rebuilding it.
    const placements=[...document.querySelectorAll('[data-mobile-before]')].map(element=>{
      const anchor=document.createComment('desktop placement');element.before(anchor);
      return {element,anchor,target:document.querySelector(element.dataset.mobileBefore)};
    });
    const recompose=()=>placements.forEach(({element,anchor,target})=>{
      if(!target)return;
      const focused=element.contains(document.activeElement)?document.activeElement:null;
      if(mobile.matches)target.before(element);else anchor.after(element);
      focused?.focus({preventScroll:true});
    });
    mobile.addEventListener('change',recompose);recompose();
    const setMenu=open=>{
      if(!toggle||!navigation)return;
      toggle.setAttribute('aria-expanded',String(open));navigation.classList.toggle('is-open',open);
      toggle.querySelector('span').textContent=open?'×':'＋';
    };
    toggle?.addEventListener('click',()=>setMenu(toggle.getAttribute('aria-expanded')!=='true'));
    navigation?.addEventListener('click',event=>{if(event.target.closest('a'))setMenu(false);});
    document.addEventListener('keydown',event=>{
      if(event.key==='Escape'&&toggle?.getAttribute('aria-expanded')==='true'){setMenu(false);toggle.focus();}
    });
    mobile.addEventListener('change',()=>setMenu(false));

    const groups=['#site-navigation','.topic-nav'].map(selector=>[...document.querySelectorAll(selector+' a[href^="#"]')].map(link=>({link,target:document.getElementById(link.hash.slice(1))})).filter(item=>item.target));
    let pending=false;
    function updateNavigation(){
      pending=false;
      const threshold=(document.querySelector('.topbar')?.getBoundingClientRect().height||0)+72;
      groups.forEach(group=>{
        const current=group.filter(({target})=>{const r=target.getBoundingClientRect();return r.top<=threshold&&r.bottom>threshold;}).at(-1);
        group.forEach(item=>{if(item===current)item.link.setAttribute('aria-current','location');else item.link.removeAttribute('aria-current');});
      });
    }
    const schedule=()=>{if(!pending){pending=true;requestAnimationFrame(updateNavigation);}};
    window.addEventListener('scroll',schedule,{passive:true});window.addEventListener('resize',schedule,{passive:true});updateNavigation();

    // Observe short headings only: charts, figures, controls and long sections
    // remain visible, including when loaded at an anchor or through keyboard focus.
    const motion=matchMedia('(prefers-reduced-motion:reduce)');
    let observer;
    const revealAll=()=>{
      observer?.disconnect();
      document.querySelectorAll('.reveal-pending').forEach(el=>el.classList.remove('reveal-pending'));
    };
    if(!motion.matches&&'IntersectionObserver' in window){
      observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
        if(entry.isIntersecting){entry.target.classList.remove('reveal-pending');entry.target.classList.add('reveal-visible');observer.unobserve(entry.target);}
      }),{rootMargin:'0px 0px 60px 0px',threshold:0});
      document.querySelectorAll('.section-heading,.closing-statement').forEach(el=>{
        if(el.getBoundingClientRect().top>innerHeight){el.classList.add('reveal-pending');observer.observe(el);}
      });
    }
    motion.addEventListener('change',event=>{if(event.matches)revealAll();});
    document.addEventListener('focusin',event=>event.target.closest('.reveal-pending')?.classList.remove('reveal-pending'));
    window.addEventListener('beforeprint',revealAll);
  });
})();
