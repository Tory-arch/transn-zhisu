'use strict';

const chapters = [
  {
    "title": "三产品总览",
    "description": "数据体检先找到问题，交付风险体检报告；数据治理还原历史成本，交付逐品号明细与依据；问询数据响应解释具体数字，交付问询数据证据包。三项服务可单独选择，也可按实际需要衔接。",
    "alt": "01 三产品总览：让数据说得清，让追问有依据。"
  },
  {
    "title": "为什么用AI",
    "description": "配方写 A 料、实际领 B 料，差异原因待核对。AI 找线索、提出候选解释；程序试算，AI 反查修正，再由专业人员确认依据并留痕。已交付案例每年识别 4,000 余条替代用料关系，并用成本结果反向检验。",
    "alt": "02 为什么用AI：找到矛盾背后的原因，用重算验证每个判断。"
  },
  {
    "title": "数据体检",
    "description": "从采购、领料、生产、库存、成本及主数据之间的勾稽关系入手，先定位数据疑点。交付风险体检报告，列明问题位置、影响范围和治理建议，帮助企业与券商判断处理范围；体检后不必然购买治理。",
    "alt": "03 数据体检：先看清问题，再决定怎么处理。"
  },
  {
    "title": "数据治理",
    "description": "沿生产与加工链梳理记录，先核对数量，再按确认后的口径计算成本。交付三年逐品号明细、来源说明、调整留痕台账、残差清单和可重跑规则；无法解释的差额单独列明，关键依据与会计口径由专业人员确认。",
    "alt": "04 数据治理：先把数量对齐，再把成本算清。"
  },
  {
    "title": "问询数据响应",
    "description": "围绕具体数字，把问题连接到来源单据、计算过程和数据底稿，交付问询数据证据包。已有治理成果可复用，缺少依据时按涉及范围做针对性还原；供券商、会计师撰写回复，不替代专业判断，也不承诺审核结果。",
    "alt": "05 问询数据响应：问到哪笔数据，就追到哪条依据。"
  },
  {
    "title": "客户实践",
    "description": "匿名数据治理案例覆盖三个年度实际 32 个月，单年源数据 144 万至 169 万行，加工最深 11 层，共 268,188 条数量调整并逐条留痕。各年度残差金额占入库总额 1.06%–2.38%，全部单列；该比例不等于准确率，也不代表其他项目表现。",
    "alt": "06 客户实践：百万行数据，追到每笔调整的依据。"
  },
  {
    "title": "开始合作",
    "description": "从当前最需要解释的问题出发，选择数据体检、数据治理或问询数据响应。提供已有数据，共同确认问题，再约定服务范围；三项服务可单选或衔接。本地部署，不更换原 ERP，企业主要提供数据并确认关键事实与口径。",
    "alt": "07 开始合作：从当前难题，找到合作起点。"
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
  poster.src = `assets/posters/${number}.webp?v=15`;
  poster.alt = chapter.alt;
  expandedPoster.src = poster.src;
  expandedPoster.alt = chapter.alt;
  document.getElementById('poster-panel').setAttribute('aria-labelledby', tabs[current].id);
  document.getElementById('poster-counter').textContent = number;
  document.getElementById('chapter-category').textContent = chapter.title;
  document.getElementById('chapter-description').textContent = chapter.description;
  document.getElementById('single-download').href = `assets/posters/${number}.pdf?v=15`;
  document.getElementById('single-image-download').href = `assets/posters/${number}.png?v=15`;
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
