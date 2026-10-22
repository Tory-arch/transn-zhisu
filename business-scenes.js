(() => {
  'use strict';
  const root = document.getElementById('business-scenes');
  if (!root) return;

  const scenes = {
    identity: {
      label: '01 / 多套编号',
      title: '同一种物料，跨部门却接不上。',
      description: '采购、生产、财务各用一套编号，同一物料的记录难以串联核对。',
      facts: '采购 <span>MAT-028</span><i>·</i>生产 <span>YL-028A</span><i>·</i>财务 <span>000028</span>',
      image: 'assets/pain-identity.png',
      alt: '同一物料在采购、生产与财务中采用不同标识的业务场景示意'
    },
    recipe: {
      label: '02 / 领料偏配方',
      title: '多出的 7 kg，究竟差在哪里？',
      description: '配方投入 100 kg，净领料 107 kg。差额 7 kg，仍需核对业务原因。',
      facts: '<span>112 kg</span> 领料 − <span>5 kg</span> 退料 = <span>107 kg</span> 净领料',
      image: 'assets/pain-recipe.png',
      alt: '标准配方与实际领料出现差异、需要进一步核对的业务场景示意'
    },
    price: {
      label: '03 / 入库缺价',
      title: '入库有数量，成本却缺了起点。',
      description: '200 kg 已入库，单价仍缺失。价格依据未明确，后续加工成本待接续。',
      facts: '<span>200 kg</span> 入库 × 待确认单价 → 成本待接续',
      image: 'assets/pain-price.png',
      alt: '物料已经入库但缺少价格依据，后续成本链无法接续的业务场景示意'
    },
    stock: {
      label: '04 / 库存不符',
      title: '账上 65 件，库存为何只有 62 件？',
      description: '台账与库存相差 3 件，需核对进耗存及补录依据，原因仍待确认。',
      facts: '<span>65 件</span> 台账 − <span>62 件</span> 库存 = <span>3 件</span> 待核对差额',
      image: 'assets/pain-stock.png',
      alt: '台账结存与库存记录不一致，差额尚待确认的业务场景示意'
    }
  };
  const tabs = [...root.querySelectorAll('[data-pain]')];
  const tablist = root.querySelector('[role="tablist"]');
  const panel = document.getElementById('pain-panel');
  const image = document.getElementById('pain-image');
  const imageFrame = root.querySelector('.pain-image-frame');
  const imageStatus = root.querySelector('.pain-image-status');
  const announcement = document.getElementById('pain-announcement');
  const compact = matchMedia('(max-width: 850px)');
  const prefetched = new Set();
  let selected = null;

  function setImageState(state) {
    imageFrame.dataset.imageState = state;
    imageFrame.setAttribute('aria-busy', String(state === 'loading'));
    imageStatus.textContent = state === 'error' ? '场景图片暂时不可用，请参阅下方说明。' : '场景图片加载中…';
  }
  image.addEventListener('load', () => setImageState('ready'));
  image.addEventListener('error', () => setImageState('error'));

  function keyFromHash() {
    const key = location.hash.startsWith('#scene-') ? location.hash.slice(7) : null;
    return key && Object.hasOwn(scenes, key) ? key : null;
  }
  function selectScene(key, {push = false, focus = false, announce = false} = {}) {
    const scene = scenes[key];
    if (!scene) return;
    const changed = selected !== key;
    selected = key;
    tabs.forEach(tab => {
      const active = tab.dataset.pain === key;
      tab.setAttribute('aria-selected', String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    panel.setAttribute('aria-labelledby', `pain-tab-${key}`);
    if (changed) {
      document.getElementById('pain-scene-label').textContent = scene.label;
      document.getElementById('pain-title').textContent = scene.title;
      document.getElementById('pain-description').textContent = scene.description;
      document.getElementById('pain-facts').innerHTML = scene.facts;
      image.alt = scene.alt;
      if (image.getAttribute('src') !== scene.image) {
        setImageState('loading');
        image.src = scene.image;
      } else if (image.complete) setImageState(image.naturalWidth > 0 ? 'ready' : 'error');
      if (announce) announcement.textContent = `已选择：${scene.title}`;
    }
    if (push && location.hash !== `#scene-${key}`) {
      // A history update changes the shareable URL without native anchor scrolling.
      history.pushState(null, '', `#scene-${key}`);
    }
    if (focus) document.getElementById(`pain-tab-${key}`).focus({preventScroll:true});
  }
  function preloadScene(key) {
    const src = scenes[key].image;
    if (prefetched.has(src)) return;
    prefetched.add(src);
    const preload = new Image();
    preload.src = src;
  }
  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => selectScene(tab.dataset.pain, {push:true, announce:true}));
    tab.addEventListener('pointerenter', () => preloadScene(tab.dataset.pain), {once:true});
    tab.addEventListener('focus', () => preloadScene(tab.dataset.pain), {once:true});
    tab.addEventListener('keydown', event => {
      let next;
      if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = (index + 1) % tabs.length;
      else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
      else if (event.key === 'Home') next = 0;
      else if (event.key === 'End') next = tabs.length - 1;
      else return;
      event.preventDefault();
      event.stopPropagation();
      selectScene(tabs[next].dataset.pain, {push:true, focus:true, announce:true});
    });
  });
  function syncLocation() {
    const key = keyFromHash();
    if (key) selectScene(key);
    else if (['', '#top', '#challenges', '#issue-panel'].includes(location.hash)) selectScene('identity');
  }
  // Back/forward may emit both events; selecting an unchanged scene is idempotent.
  window.addEventListener('popstate', syncLocation);
  window.addEventListener('hashchange', syncLocation);
  function syncTabOrientation() { tablist.setAttribute('aria-orientation', compact.matches ? 'horizontal' : 'vertical'); }
  compact.addEventListener('change', syncTabOrientation);
  syncTabOrientation();
  selectScene(keyFromHash() || 'identity');
})();
