/*
 * Project Moon Life — independent Thai accessibility/localization overlay.
 * Preserves native app logic: only displays translated text nodes and labels.
 * Local dictionary handles common UI; optional local-server proxy translates
 * new narrative events online, storing results in the user's translation cache.
 */
(() => {
  'use strict';
  if (window.__moonlifeThaiOverlayLoaded) return;
  window.__moonlifeThaiOverlayLoaded = true;

  const NS = 'moonlife-8129';
  const $id = (suffix) => `${NS}-${suffix}`;
  function safeGet(k) { try { return window.localStorage.getItem(k); } catch (_) { return null; } }
  function safeSet(k,v) { try { window.localStorage.setItem(k,v); } catch (_) {} }
  const PREFERRED_LANG = 'moonlife.lang';
  const NETWORK_ENABLED = 'moonlife.online.translation';
  const endpoint = '/__moonlife__/translate';
  let language = safeGet(PREFERRED_LANG) || 'th';
  let online = safeGet(NETWORK_ENABLED) !== 'false';
  const dictionary = new Map();
  const remoteCache = new Map();
  let nodes = new WeakMap();
  let attrs = new WeakMap();
  const pending = new Set();
  const retryAfter = new Map();
  let scheduled = false;
  let fetching = false;
  let mutationTimeout = null;
  let statusTimer = null;
  let offlineNoticeShown = false;
  const metrics = { translated: 0, untranslated: 0 };
  const SKIP = new Set(['SCRIPT','STYLE','NOSCRIPT','TEXTAREA','CODE','PRE','CANVAS']);
  const ATTRIBUTE_LIST = ['placeholder', 'aria-label', 'title', 'alt'];

  function squash(str) { return str.replace(/\s+/g, ' ').trim(); }
  function isCandidate(str) {
    const value = squash(str);
    if (!value || value.length < 2 || value.length > 2200) return false;
    if (/^(?:[\d\s.,/%+\-=:()\[\]×x]+)$/i.test(value)) return false;
    if (/^(?:https?:\/\/|www\.|#[0-9a-f]{3,8}$)/i.test(value)) return false;
    if (/^[A-Z]?(?:\d{1,4}|[A-Z])\s*(?:Corp\.)?$/i.test(value)) return false;
    if (/^[\d.]+\s*(?:%|x|×|ms|km|HP|MB|KB)$/i.test(value)) return false;
    if (/^[\w.\-]+@[\w.\-]+\.[\w.]+$/.test(value)) return false;
    return /[A-Za-z\u3130-\u318f\uac00-\ud7af\u3040-\u30ff\u4e00-\u9fff]/.test(value);
  }
  function localTranslation(original) {
    const key = squash(original);
    if (dictionary.has(key)) return dictionary.get(key);
    let match = key.match(/^Continue\s*[·|:]\s*(.+?)\s*[·|:]\s*Age\s*(\d+)\s*[·|:]\s*(.+)$/i);
    if (match) return `เล่นต่อ · ${match[1]} · อายุ ${match[2]} · ${match[3]}`;
    match = key.match(/^Age\s*(\d+)(?:\s*(?:years?|yrs?))?$/i);
    if (match) return `อายุ ${match[1]} ปี`;
    match = key.match(/^(\d+)\s*(?:years? old|yrs? old)$/i);
    if (match) return `อายุ ${match[1]} ปี`;
    match = key.match(/^Year\s*(\d+)$/i);
    if (match) return `ปีที่ ${match[1]}`;
    match = key.match(/^([A-Y])\s*Corp\.$/i);
    if (match) return `บริษัท ${match[1].toUpperCase()}`;
    // Names and unique identifiers should not be sent to the online translator.
    if (/^[A-Z][a-zA-Z'-]{1,35}$/.test(key)) return null;
    if (/^[A-Z][a-zA-Z'-]{1,35}\s+[A-Z][a-zA-Z'-]{1,35}$/.test(key)) return null;
    return remoteCache.get(key) || null;
  }

  function isExcluded(node) {
    const parent = node.parentElement;
    if (!parent) return true;
    if (SKIP.has(parent.tagName) || parent.closest(`[data-${NS}-skip],#${$id('toolbar')}`)) return true;
    if (parent.closest('input, textarea, select, [contenteditable], [translate="no"]')) return true;
    return false;
  }
  function formatTranslation(original, translated) {
    const prefix = (original.match(/^\s*/) || [''])[0];
    const suffix = (original.match(/\s*$/) || [''])[0];
    return prefix + translated + suffix;
  }
  function setNode(node, original, translated) {
    if (!node.isConnected || !translated || language !== 'th' || isExcluded(node)) return;
    const current = nodes.get(node);
    if (current && current.original !== original && node.nodeValue !== current.rendered) return;
    const value = formatTranslation(original, translated);
    if (node.nodeValue !== value) node.nodeValue = value;
    nodes.set(node, { original, rendered: value });
    metrics.translated++;
  }
  function translateNode(node) {
    if (!node.isConnected || isExcluded(node)) return;
    const value = node.nodeValue;
    const previous = nodes.get(node);
    if (previous && value === previous.rendered) return;
    if (language === 'en') return;
    if (!isCandidate(value)) return;
    const key = squash(value);
    const translated = localTranslation(value);
    if (translated) setNode(node, value, translated);
    else enqueue(key);
  }
  function processAttributes(el) {
    if (!el || !el.isConnected || el.closest(`#${$id('toolbar')}`) || SKIP.has(el.tagName)) return;
    if (el.hasAttribute('data-' + NS + '-skip')) return;
    let saved = attrs.get(el);
    if (!saved) { saved = {}; attrs.set(el, saved); }
    for (const attr of ATTRIBUTE_LIST) {
      const raw = el.getAttribute(attr);
      if (!raw) continue;
      if (saved[attr] && saved[attr].rendered === raw) continue;
      if (language !== 'th' || !isCandidate(raw)) continue;
      const translated = localTranslation(raw);
      if (translated) {
        const result = translated;
        saved[attr] = { original: raw, rendered: result };
        if (raw !== result) el.setAttribute(attr, result);
      } else enqueue(squash(raw));
    }
  }
  function scan(root) {
    if (!root) return;
    if (root.nodeType === Node.TEXT_NODE) { translateNode(root); return; }
    if (root.nodeType !== Node.ELEMENT_NODE && root.nodeType !== Node.DOCUMENT_NODE) return;
    if (root.nodeType === Node.ELEMENT_NODE) {
      if (root.id === $id('toolbar') || root.closest(`#${$id('toolbar')}`)) return;
      processAttributes(root);
      if (SKIP.has(root.tagName)) return;
    }
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.nodeType === Node.TEXT_NODE) translateNode(node);
      else if (node.nodeType === Node.ELEMENT_NODE) processAttributes(node);
    }
  }
  function restoreOriginal() {
    // WeakMaps cannot be iterated. Walk existing text nodes and attributes.
    const walker = document.createTreeWalker(document.documentElement, NodeFilter.SHOW_TEXT | NodeFilter.SHOW_ELEMENT);
    while (walker.nextNode()) {
      const el = walker.currentNode;
      if (el.nodeType === Node.TEXT_NODE) {
        const state = nodes.get(el);
        if (state && el.nodeValue === state.rendered) el.nodeValue = state.original;
        nodes.delete(el);
      } else if (el.nodeType === Node.ELEMENT_NODE) {
        const state = attrs.get(el);
        if (!state) continue;
        for (const [key, previous] of Object.entries(state)) {
          if (el.getAttribute(key) === previous.rendered) el.setAttribute(key, previous.original);
        }
        attrs.delete(el);
      }
    }
    nodes = new WeakMap();
    attrs = new WeakMap();
  }
  function enqueue(value) {
    if (!isCandidate(value) || dictionary.has(value) || remoteCache.has(value) || !online || language !== 'th') return;
    if ((retryAfter.get(value) || 0) > Date.now()) return;
    pending.add(value);
    if (!scheduled) {
      scheduled = true;
      setTimeout(flush, 250);
    }
  }
  async function flush() {
    scheduled = false;
    if (fetching || !online || language !== 'th' || !pending.size) return;
    const batch = [];
    let size = 0;
    for (const item of pending) {
      if (batch.length >= 12 || size + item.length > 14000) break;
      pending.delete(item);
      batch.push(item);
      size += item.length;
    }
    if (!batch.length) return;
    fetching = true;
    showStatus('กำลังแปลข้อความใหม่…');
    try {
      const resp = await fetch(endpoint, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ texts: batch, online: true }), cache: 'no-store'
      });
      if (!resp.ok) throw new Error('Translation HTTP ' + resp.status);
      const data = await resp.json();
      batch.forEach((original, i) => {
        const translated = data.results && data.results[i];
        if (typeof translated === 'string' && translated.trim()) remoteCache.set(original, translated);
        else { metrics.untranslated++; retryAfter.set(original, Date.now() + 120000); }
      });
      if (language === 'th') scan(document.body);
      showStatus('ภาษาไทยพร้อมใช้งาน');
    } catch (error) {
      metrics.untranslated += batch.length;
      batch.forEach(item => retryAfter.set(item, Date.now() + 120000));
      if (!offlineNoticeShown) {
        offlineNoticeShown = true;
        showStatus('บริการแปลออนไลน์ไม่พร้อม · คำแปลพื้นฐานยังใช้งานได้', 6000);
      }
      console.warn('[MoonLife Thai] New text could not be translated:', error.message);
    } finally {
      fetching = false;
      if (pending.size) { scheduled = true; setTimeout(flush, 750); }
    }
  }
  function showStatus(message, delay = 2200) {
    const target = document.getElementById($id('status'));
    if (!target) return;
    target.textContent = message;
    if (statusTimer) clearTimeout(statusTimer);
    statusTimer = setTimeout(() => target.textContent = '', delay);
  }
  function updateToolbar() {
    const th = document.getElementById($id('th'));
    const en = document.getElementById($id('en'));
    const on = document.getElementById($id('online'));
    if (th) { th.classList.toggle('selected', language === 'th'); th.setAttribute('aria-pressed', String(language === 'th')); }
    if (en) { en.classList.toggle('selected', language === 'en'); en.setAttribute('aria-pressed', String(language === 'en')); }
    if (on) on.checked = online;
    document.documentElement.lang = language;
    document.title = language === 'th' ? 'เกิดมาเป็นคนคนหนึ่งในนคร — Project Moon Life' : nativeTitle;
  }
  function switchLanguage(next) {
    if (next === language) return;
    language = next;
    safeSet(PREFERRED_LANG, language);
    if (next === 'en') { pending.clear(); restoreOriginal(); }
    updateToolbar();
    if (next === 'th') scan(document.body);
  }
  function installToolbar() {
    if (document.getElementById($id('toolbar'))) return;
    const box = document.createElement('section');
    box.id = $id('toolbar');
    box.setAttribute('data-' + NS + '-skip', '');
    box.setAttribute('aria-label', 'Thai translation controls');
    box.innerHTML = `<div class="moon-head"><strong>ภาษา / Language</strong><span>8129 · Local</span><button id="${$id('min')}" type="button" class="moon-min" title="ย่อ / ขยายแถบภาษา">−</button></div>
      <div class="moon-actions"><button id="${$id('th')}" type="button" title="แสดงภาษาไทย">TH · ไทย</button>
        <button id="${$id('en')}" type="button" title="Show original language">EN · Original</button></div>
      <label class="moon-opt"><input id="${$id('online')}" type="checkbox" checked>
        <span>แปลเหตุการณ์ออนไลน์</span></label>
      <small class="moon-note">เปิดใช้แล้ว ข้อความใหม่อาจส่งไป Google Translate<br>ยกเลิกเครื่องหมายถูกเพื่อใช้เฉพาะคำแปลในเครื่อง</small>
      <div id="${$id('status')}" class="moon-status" role="status" aria-live="polite"></div>`;
    (document.body || document.documentElement).appendChild(box);
    document.getElementById($id('min')).addEventListener('click', () => {
      const collapsed = box.classList.toggle('moon-collapsed');
      document.getElementById($id('min')).textContent = collapsed ? '+' : '−';
    });
    document.getElementById($id('th')).addEventListener('click', () => switchLanguage('th'));
    document.getElementById($id('en')).addEventListener('click', () => switchLanguage('en'));
    document.getElementById($id('online')).addEventListener('change', (event) => {
      online = Boolean(event.target.checked);
      safeSet(NETWORK_ENABLED, String(online));
      offlineNoticeShown = false;
      if (online && language === 'th') scan(document.body);
      showStatus(online ? 'เปิดการแปลข้อความใหม่ผ่านอินเทอร์เน็ตแล้ว' : 'ใช้เฉพาะคำแปลในเครื่องแล้ว');
    });
    updateToolbar();
  }
  const nativeTitle = document.title;
  async function initialize() {
    try {
      const response = await fetch('/__moonlife__/thai_dictionary.json', {cache:'no-store'});
      if (!response.ok) throw new Error('Could not load local dictionary');
      const mapping = await response.json();
      Object.entries(mapping).forEach(([key, translated]) => dictionary.set(squash(key), translated));
    } catch (error) {
      console.warn('[MoonLife Thai] Local dictionary not loaded:', error);
    }
    installToolbar();
    if (language === 'th') scan(document.body);
    const observer = new MutationObserver((changes) => {
      if (language !== 'th') return;
      const targets = new Set();
      for (const change of changes) {
        if (change.type === 'characterData') targets.add(change.target);
        else if (change.type === 'attributes') targets.add(change.target);
        else for (const node of change.addedNodes) targets.add(node);
      }
      for (const node of targets) scan(node);
    });
    observer.observe(document.documentElement, {
      subtree:true, childList:true, characterData:true,
      attributes:true, attributeFilter: ATTRIBUTE_LIST
    });
    window.addEventListener('pageshow', () => { if (language === 'th') scan(document.body); });
    // Some SPA engines replace a large subtree without a MutationObserver-visible
    // text change. Rare, low-frequency rescans recover those nodes.
    setInterval(() => { if (language === 'th' && document.body) scan(document.body); }, 3500);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initialize, {once:true});
  else initialize();
})();
