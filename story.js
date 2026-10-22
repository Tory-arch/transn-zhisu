'use strict';

const chapters = [
  {
    "title": "业务难题",
    "description": "同物多码、领料偏离配方、入库缺价、手工补录与库存不符。当这些问题穿过多层加工，三年逐品号成本明细就难以形成。",
    "alt": "01 业务难题：数据都在，成本为何对不上？"
  },
  {
    "title": "为什么用AI",
    "description": "核清一笔，需要对照采购、领料、工单、半成品、委外与入库。这样的追查，要沿着不同品号和加工层级贯穿三年。难的不只是算数，还有反复找数、对数、查依据。",
    "alt": "02 为什么用AI：一笔成本，要追多远？"
  },
  {
    "title": "专项智能体",
    "description": "完整清洗服务调用 100+ 专项智能体，具体按企业数据问题配置。编号、配方、工单、缺价分别识别，形成可核对的线索与待确认事项，让专业人员聚焦关键事实与口径。",
    "alt": "03 专项智能体：一个难题，一个专项智能体。"
  },
  {
    "title": "规则重算",
    "description": "确认后的规则由程序执行，沿加工层级还原进耗存与成本。规则调整后，三年数据统一重算，保留调整前后及所用依据，减少逐表修改和重复核对。",
    "alt": "04 规则重算：规则变了，三年统一重算。"
  },
  {
    "title": "可复核交付",
    "description": "三年逐品号明细、来源说明、调整留痕台账、残差清单、可重跑规则。结果能复核，调整有记录；无法解释的差额如实列明，交企业确认。",
    "alt": "05 可复核交付：交付数字，也交付依据。"
  },
  {
    "title": "客户实践",
    "description": "一家经券商推荐的多层加工拟 IPO 企业，在 ERP 方案尝试一年未完成后，通过智溯完成数据还原交付并获客户认可。匿名案例，依据现有服务材料整理，不代表审计或 IPO 结果。",
    "alt": "06 客户实践：走出数据困境，完成项目交付。"
  },
  {
    "title": "开始合作",
    "description": "从系统与数据范围、品号与加工层级、已知问题与整改历史、交付节点与关键确认人开始沟通。先了解现状，再联合评估、约定范围。企业主要提供已有数据并确认关键问题。",
    "alt": "07 开始合作：从现有数据，开始下一步。"
  }
];

const tabs = [...document.querySelectorAll('[data-chapter]')];
const poster = document.getElementById('poster-image');
const dialog = document.getElementById('poster-dialog');
const expandedPoster = document.getElementById('expanded-image');
let current = 0;

function chapterFromHash() {
  const match = /^#poster-(\d{2})$/.exec(location.hash);
  const index = match ? Number(match[1]) - 1 : 0;
  return index >= 0 && index < chapters.length ? index : 0;
}

function selectChapter(index, { focus = false, updateHash = false } = {}) {
  current = Math.max(0, Math.min(chapters.length - 1, index));
  const chapter = chapters[current];
  const number = String(current + 1).padStart(2, '0');

  tabs.forEach((tab, i) => {
    const active = i === current;
    tab.classList.toggle('active', active);
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
  });
  poster.src = `assets/posters/${number}.webp?v=6`;
  poster.alt = chapter.alt;
  expandedPoster.src = poster.src;
  expandedPoster.alt = chapter.alt;
  document.getElementById('poster-panel').setAttribute('aria-labelledby', tabs[current].id);
  document.getElementById('poster-counter').textContent = number;
  document.getElementById('chapter-category').textContent = chapter.title;
  document.getElementById('chapter-description').textContent = chapter.description;
  document.getElementById('single-download').href = `assets/posters/${number}.pdf?v=6`;
  document.getElementById('poster-prev').disabled = current === 0;
  document.getElementById('poster-next').disabled = current === chapters.length - 1;

  const hash = `#poster-${number}`;
  if (updateHash && location.hash !== hash) {
    // Keep scroll position while giving each selected chapter a shareable URL.
    history.pushState(null, '', hash);
  }
  if (focus) tabs[current].focus({ preventScroll: true });
}

tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectChapter(index, { updateHash: true }));
  tab.addEventListener('keydown', event => {
    let next = index;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    else if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    else return;
    event.preventDefault();
    selectChapter(next, { focus: true, updateHash: true });
  });
});

document.getElementById('poster-prev').addEventListener('click', () => selectChapter(current - 1, { updateHash: true }));
document.getElementById('poster-next').addEventListener('click', () => selectChapter(current + 1, { updateHash: true }));
document.getElementById('expand-poster').addEventListener('click', () => dialog.showModal());
document.getElementById('close-poster').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const bounds = dialog.getBoundingClientRect();
  if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
});

document.addEventListener('keydown', event => {
  if (dialog.open || document.activeElement?.getAttribute('role') === 'tab') return;
  if (event.key === 'ArrowRight') {
    event.preventDefault();
    selectChapter(current + 1, { updateHash: true });
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault();
    selectChapter(current - 1, { updateHash: true });
  }
});

window.addEventListener('popstate', () => selectChapter(chapterFromHash()));
window.addEventListener('hashchange', () => selectChapter(chapterFromHash()));
selectChapter(chapterFromHash());

const mobileChapters = matchMedia('(max-width:700px)');
function syncChapterOrientation() {
  document.querySelector('.chapter-tabs').setAttribute('aria-orientation', mobileChapters.matches ? 'horizontal' : 'vertical');
}
mobileChapters.addEventListener('change', syncChapterOrientation);
syncChapterOrientation();
