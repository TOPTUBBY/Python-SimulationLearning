/*
 * SimulationLearning Thai UI overlay — PREVIEW, not upstream website code.
 * Translates user-visible DOM text/labels without replacing interactive nodes.
 * Intentionally skips code, editable input, numeric data and canvas/WebGL pixels.
 * Online translation is opt-in; only displayed text sent to local /__thai__/translate.
 */
(() => {
  'use strict';
  if (window.__simthaiOverlayActive) return;
  window.__simthaiOverlayActive = true;
  const script = document.currentScript;
  const site = script?.dataset?.site || 'local-clone';
  const defaultLang = script?.dataset?.default === 'th' ? 'th' : 'original';
  const defaultOnline = script?.dataset?.online === 'true';
  const prefix = `simulationlearning.th.${site}.`;
  function read(k) { try { return localStorage.getItem(prefix+k); } catch (_) { return null; } }
  function save(k,v) { try { localStorage.setItem(prefix+k, String(v)); } catch (_) {} }
  let lang = read('lang') || defaultLang;
  let online = read('online') === null ? defaultOnline : read('online') === 'true';
  let folded = read('folded') === 'true';
  let textNodes = new WeakMap();
  let elementAttrs = new WeakMap();
  const known = new Map();
  const translatedOnline = new Map();
  const waiting = new Set();
  const rejectedUntil = new Map();
  const skipTags = new Set(['SCRIPT','STYLE','NOSCRIPT','TEMPLATE','CANVAS','CODE','PRE','KBD','SAMP','TEXTAREA','OPTION']);
  const attributes = ['title','placeholder','aria-label','alt'];
  let sending=false, dispatchTimer=0, scanTimer=0, scanning=false;
  const UI = 'simthai-language-ui';
  const nativeTitle = document.title;
  const stats = {local:0, online:0};
  const compact = s => s.replace(/\s+/g,' ').trim();
  function translatable(raw) {
    const s=compact(raw);
    if (s.length < 2 || s.length > 2200) return false;
    if (!/[A-Za-z\u3130-\u318f\uac00-\ud7af\u3040-\u30ff\u4e00-\u9fff]/.test(s)) return false;
    if (/^[\d\s.,/%+\-=:()\[\]×x]+$/.test(s) || /^[A-Z]{1,5}\d{0,5}$/.test(s) || /^(?:https?:\/\/\S+|www\.\S+|#[0-9a-f]{3,8})$/i.test(s)) return false;
    if (/^\S+@\S+\.\S+$/.test(s) || /^\S+\.(?:js|ts|css|py|json|html|cpp|h|ino)$/i.test(s)) return false;
    if (/^(?:0x[\da-f]+|GPIO\d+|D\d+|A\d+|ADC\d*|I2C|I²C|SPI|UART|LED|PWM|USB|GND|VCC)$/i.test(s)) return false;
    return true;
  }
  function protectedElement(el, allowInput=false) {
    if (!el || !el.closest) return true;
    if (el.closest(`#${UI},[contenteditable=""],[contenteditable="true"],[translate="no"],[data-simthai-skip]`)) return true;
    if (!allowInput && el.closest('input,textarea,select')) return true;
    if (allowInput && el.closest('textarea,select')) return true;
    for (let p=el;p;p=p.parentElement) if(skipTags.has(p.tagName)) return true;
    return false;
  }
  function translateTemplate(str) {
    const s=compact(str);
    if(known.has(s)) return known.get(s);
    let m=s.match(/^(Step|Lesson)\s+(\d+)\s+(?:of|\/)\s+(\d+)$/i);
    if(m) return `${m[1].toLowerCase()==='step'?'ขั้นตอน':'บทเรียน'} ${m[2]} จาก ${m[3]}`;
    m=s.match(/^(\d+)\s+(lessons?|steps?|questions?|parts?|items?|pins?|boards?)$/i);
    if(m) return `${m[1]} ${({lesson:'บทเรียน',step:'ขั้นตอน',question:'คำถาม',part:'ชิ้นส่วน',item:'รายการ',pin:'ขา',board:'บอร์ด'})[m[2].toLowerCase().replace(/s$/,'')]||m[2]}`;
    m=s.match(/^(\d+)(?:\s*\/\s*)(\d+)\s*(lessons?|steps?)?$/i);
    if(m&&m[3])return `${m[1]} / ${m[2]} ${m[3].toLowerCase().startsWith('lesson')?'บทเรียน':'ขั้นตอน'}`;
    m=s.match(/^(\d{1,2})\.\s+(.+)$/);
    if(m&&known.has(m[2]))return `${m[1]}. ${known.get(m[2])}`;
    m=s.match(/^(Next|Back|Previous|Go to|Jump to):\s+(.+)$/i);
    if(m){const start=known.get(m[1])||({Next:'ถัดไป',Back:'ย้อนกลับ',Previous:'ก่อนหน้า','Go to':'ไปที่','Jump to':'ข้ามไปที่'})[m[1]]||m[1];const suffix=known.get(m[2])||translatedOnline.get(m[2]);return suffix?`${start}: ${suffix}`:null;}
    return translatedOnline.get(s)||null;
  }
  function preserveWhitespace(original,output){return (original.match(/^\s*/)||[''])[0]+output+(original.match(/\s*$/)||[''])[0];}
  function maybeQueue(s) {
    if (!online || lang!=='th' || !translatable(s) || known.has(s) || translatedOnline.has(s)) return;
    if(Date.now() < (rejectedUntil.get(s)||0))return;
    waiting.add(s);
    if(!dispatchTimer)dispatchTimer=setTimeout(sendTranslations,400);
  }
  function applyText(node) {
    if(!node.isConnected||protectedElement(node.parentElement)||lang!=='th')return;
    const current=node.nodeValue;
    const state=textNodes.get(node);
    if(state && current===state.translated)return;
    if(!translatable(current))return;
    const key=compact(current);
    const found=translateTemplate(key);
    if(found&&found!==key){const value=preserveWhitespace(current,found);textNodes.set(node,{original:current,translated:value});node.nodeValue=value;if(known.has(key))stats.local++;else stats.online++;}
    else maybeQueue(key);
  }
  function applyAttributes(el) {
    if(!el.isConnected||protectedElement(el,true)||lang!=='th')return;
    let prior=elementAttrs.get(el);
    if(!prior){prior={};elementAttrs.set(el,prior);}
    const names=attributes.slice();
    if(el.tagName==='INPUT'&&/^(button|submit|reset)$/i.test(el.type))names.push('value');
    for(const attr of names){
      const raw=el.getAttribute(attr);
      if(!raw||!translatable(raw)||prior[attr]?.translated===raw)continue;
      const found=translateTemplate(raw);
      if(found&&found!==raw){prior[attr]={original:raw,translated:found};el.setAttribute(attr,found);}
      else maybeQueue(compact(raw));
    }
  }
  function inspect(root) {
    if(!root||lang!=='th'||scanning)return;
    scanning=true;
    try {
      if(root.nodeType===Node.TEXT_NODE){applyText(root);return;}
      if(root.nodeType!==Node.ELEMENT_NODE&&root.nodeType!==Node.DOCUMENT_NODE)return;
      if(root.nodeType===Node.ELEMENT_NODE){if(root.id===UI||root.closest(`#${UI}`))return;applyAttributes(root);if(skipTags.has(root.tagName))return;}
      const walker=document.createTreeWalker(root,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
      while(walker.nextNode()){
        const node=walker.currentNode;
        if(node.nodeType===Node.TEXT_NODE)applyText(node);
        else if(node.nodeType===Node.ELEMENT_NODE)applyAttributes(node);
      }
      if(document.title===nativeTitle){const t=translateTemplate(nativeTitle);if(t)document.title=t;}
    } finally{scanning=false;}
  }
  function restore() {
    if(!document.documentElement)return;
    const walker=document.createTreeWalker(document.documentElement,NodeFilter.SHOW_ELEMENT|NodeFilter.SHOW_TEXT);
    while(walker.nextNode()){
      const n=walker.currentNode;
      if(n.nodeType===Node.TEXT_NODE){const state=textNodes.get(n);if(state&&n.nodeValue===state.translated)n.nodeValue=state.original;}
      else if(n.nodeType===Node.ELEMENT_NODE){const state=elementAttrs.get(n);if(!state)continue;for(const [key,v] of Object.entries(state))if(n.getAttribute(key)===v.translated)n.setAttribute(key,v.original);}
    }
    textNodes=new WeakMap();elementAttrs=new WeakMap();
    if(document.title!==nativeTitle) document.title=nativeTitle;
  }
  function queueScan() {if(!scanTimer)scanTimer=setTimeout(()=>{scanTimer=0;if(lang==='th')inspect(document.body);},90);}
  async function sendTranslations() {
    dispatchTimer=0;
    if(sending||!online||lang!=='th'||!waiting.size)return;
    const batch=[];let length=0;
    for(const phrase of waiting){if(batch.length>=12||length+phrase.length>13000)break;batch.push(phrase);length+=phrase.length;waiting.delete(phrase);}
    if(!batch.length)return;
    sending=true;
    try {
      const res=await fetch('/__thai__/translate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({texts:batch,online:true})});
      if(!res.ok)throw new Error(`HTTP ${res.status}`);
      const data=await res.json();
      for(let i=0;i<batch.length;i++){
        const translated=data.results?.[i];
        if(typeof translated==='string'&&translated.trim()&&translated!==batch[i])translatedOnline.set(batch[i],translated);
        else rejectedUntil.set(batch[i],Date.now()+180000);
      }
      queueScan();
    } catch(error){console.warn('[SimulationLearning TH] Translation service unavailable:',error);for(const s of batch)rejectedUntil.set(s,Date.now()+180000);setStatus('การแปลออนไลน์ไม่พร้อมใช้งาน (ยังใช้คำแปลในเครื่องได้)');}
    finally{sending=false;if(waiting.size&&online&&lang==='th')dispatchTimer=setTimeout(sendTranslations,450);}
  }
  function setStatus(message){const el=document.querySelector(`#${UI} .simthai-status`);if(el)el.textContent=message||'';}
  function updateUI(){
    const root=document.getElementById(UI);if(!root)return;
    root.querySelector('[data-lang="th"]').setAttribute('aria-pressed',lang==='th');
    root.querySelector('[data-lang="original"]').setAttribute('aria-pressed',lang!=='th');
    root.querySelector('input').checked=online;
    root.classList.toggle('simthai-compact',folded);
    root.querySelector('[data-fold]').textContent=folded?'+':'−';
    root.querySelector('[data-fold]').setAttribute('aria-label',folded?'ขยายตัวเลือกภาษา':'ย่อตัวเลือกภาษา');
  }
  function chooseLanguage(next){
    if(lang===next)return;
    lang=next;save('lang',next);
    if(next==='original'){waiting.clear();restore();setStatus('แสดงภาษาต้นฉบับแล้ว');}
    else{setStatus('เปิดภาษาไทยแล้ว');queueScan();}
    updateUI();
  }
  function setupToolbar(){
    if(document.getElementById(UI))return;
    const root=document.createElement('aside');
    root.id=UI;
    root.setAttribute('aria-label','SimulationLearning language options');
    root.setAttribute('data-simthai-skip','true');
    root.innerHTML=`<div class="simthai-head"><strong>ภาษา / Language</strong><button type="button" data-fold aria-label="ย่อตัวเลือกภาษา" title="ย่อหรือขยาย">−</button></div>
      <div class="simthai-choices"><button type="button" data-lang="th" aria-pressed="false">TH · ไทย</button><button type="button" data-lang="original" aria-pressed="true">Original</button></div>
      <div class="simthai-options"><label><input type="checkbox" id="simthai-online-check">แปลข้อความใหม่ผ่านออนไลน์</label></div>
      <small class="simthai-notes">เมื่อเปิดออนไลน์ ข้อความที่แสดงบนเว็บอาจส่งไป Google Translate • ไม่แก้ไขเกมหรือบทเรียนต้นฉบับ</small>
      <div class="simthai-status" role="status" aria-live="polite"></div>`;
    (document.body||document.documentElement).appendChild(root);
    root.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>chooseLanguage(b.dataset.lang)));
    root.querySelector('[data-fold]').addEventListener('click',()=>{folded=!folded;save('folded',folded);updateUI();});
    root.querySelector('input').addEventListener('change',e=>{online=Boolean(e.target.checked);save('online',online);if(!online)waiting.clear();else if(lang==='th')queueScan();setStatus(online?'เปิดแปลออนไลน์แล้ว':'ใช้เฉพาะคำแปลที่บันทึกไว้');});
    updateUI();
  }
  async function start(){
    setupToolbar();
    try {
      const res=await fetch('/__thai__/dictionary.json',{cache:'no-store'});
      if(!res.ok)throw new Error(`HTTP ${res.status}`);
      const dict=await res.json();
      for(const [key,value] of Object.entries(dict))if(typeof value==='string'&&value.trim())known.set(compact(key),value);
    } catch(error){setStatus('ไม่สามารถโหลดพจนานุกรมภาษาไทยได้');console.warn('[SimulationLearning TH]',error);}
    if(lang==='th')inspect(document.body);
    const observer=new MutationObserver(changes=>{
      if(lang!=='th')return;
      let changed=false;
      for(const c of changes){
        if(c.target?.nodeType===Node.ELEMENT_NODE&&c.target.closest(`#${UI}`))continue;
        if(c.target?.nodeType===Node.TEXT_NODE&&c.target.parentElement?.closest(`#${UI}`))continue;
        if(c.type==='characterData'){
          const s=textNodes.get(c.target);if(!s||c.target.nodeValue!==s.translated){changed=true;break;}
        }else if(c.type==='attributes'){
          const prior=elementAttrs.get(c.target)?.[c.attributeName];
          if(!prior||c.target.getAttribute(c.attributeName)!==prior.translated){changed=true;break;}
        }else if(c.addedNodes.length){changed=true;break;}
      }
      if(changed)queueScan();
    });
    observer.observe(document.documentElement,{subtree:true,characterData:true,childList:true,attributes:true,attributeFilter:attributes});
    window.addEventListener('hashchange',queueScan);
    window.addEventListener('pageshow',queueScan);
    // SPA frameworks may replace sections; periodic scan is throttled and avoids changed nodes.
    setInterval(()=>{if(lang==='th'&&document.body)queueScan();},4000);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});
  else start();
})();
