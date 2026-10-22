'use strict';

const chapters = [
  {
    "title": "三产品总览",
    "description": "数据对不上，先用体检比对采购、生产、库存与财务记录，交付风险体检报告，确定整改范围。历史成本不清，治理梳理编号、配方与单据，先核数量再逐层算成本，交付三年逐品号明细、调整依据与规则。被问到毛利变化等具体数字，问询数据响应追查来源和计算过程，交付供专业机构使用的证据包。三项服务可单选可衔接。",
    "alt": "01 三产品总览：让数据说得清，让追问有依据。"
  },
  {
    "title": "为什么用AI",
    "description": "配方写 A 料、实际领 B 料，差异原因待核对。AI 找线索、提出候选解释；程序试算，AI 反查修正，再由专业人员确认依据并留痕。已交付案例每年识别 4,000 余条替代用料关系，并用成本结果反向检验。",
    "alt": "02 为什么用AI：找到矛盾背后的原因，用重算验证每个判断。"
  },
  {
    "title": "数据体检",
    "description": "采购已经入库，财务金额却对不上：是缺少单价、单位不一，还是补录重复？程序交叉比对采购、领料、生产、库存与财务记录，AI 梳理可能成因和待确认事项，再定位期间、品号及单据，评估影响与整改工作量。交付风险体检报告，列明风险分级、问题位置、影响范围和治理建议，帮助判断自行整改或专项治理。体检后不必然购买治理，风险分级不预测监管问询概率。",
    "alt": "03 数据体检：先看清问题，再决定怎么处理。"
  },
  {
    "title": "数据治理",
    "description": "原料经过半成品再到成品，数量对上了，成本仍可能因多套编号、替代领料、入库缺价或历史补录接不上。治理先梳理编号与配方、核对进耗存，再由 AI 追查断点、形成候选规则，程序按确认依据逐层重算。交付三年逐品号明细、来源说明、调整台账、残差清单与可重跑规则；每笔调整保留前后值和依据，无法解释的差额单列。三年指数据范围，关键口径由专业人员确认。",
    "alt": "04 数据治理：先把数量对齐，再把成本算清。"
  },
  {
    "title": "问询数据响应",
    "description": "同一产品的毛利率变了，是售价、材料，还是费用分摊变化？AI 将问题拆成可验证的因素，程序定位期间和产品，追查采购、生产与财务单据并取数重算，再把来源、规则和中间结果整理为证据。交付问询数据证据包，包含问题拆解、来源单据、计算过程和数据底稿，供券商、会计师撰写回复。已有治理成果可复用；未治理的数据可评估针对性还原，不替代专业判断或承诺审核结果。",
    "alt": "05 问询数据响应：问到哪笔数据，就追到哪条依据。"
  },
  {
    "title": "客户实践",
    "description": "多层加工企业的三年明细难以还原，编号、配方或入库价的差异会传到后续成本。本匿名治理案例通过归并编号、核对配方、重算工单，先核数量再逐级算成本；AI 追查异常、程序反复校验，关键依据由专业人员确认。实际覆盖三个年度中的 32 个月，单年源数据 144 万至 169 万行，最深 11 层，268,188 条数量调整逐条留痕。交付明细、依据与规则，残差单列；各年度残差金额占入库总额 1.06%–2.38%，不是准确率，也不代表其他项目表现。",
    "alt": "06 客户实践：百万行数据，追到每笔调整的依据。"
  },
  {
    "title": "开始合作",
    "description": "报表有差异，可先查清问题；历史成本说不清，可还原逐品号明细；具体数字需要解释，可准备证据和底稿。首次沟通请准备现有 ERP 或财务报表、涉及年度与业务范围、数据格式、已知问题和已有整改成果，并明确目标节点及业务、财务确认人。共同约定所选服务的交付、周期和费用；三项服务可单选可衔接。本地部署，保留现有 ERP，企业主要提供数据并确认关键事实与口径。",
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
  poster.src = `assets/posters/${number}.webp?v=16`;
  poster.alt = chapter.alt;
  expandedPoster.src = poster.src;
  expandedPoster.alt = chapter.alt;
  document.getElementById('poster-panel').setAttribute('aria-labelledby', tabs[current].id);
  document.getElementById('poster-counter').textContent = number;
  document.getElementById('chapter-category').textContent = chapter.title;
  document.getElementById('chapter-description').textContent = chapter.description;
  document.getElementById('single-download').href = `assets/posters/${number}.pdf?v=16`;
  document.getElementById('single-image-download').href = `assets/posters/${number}.png?v=16`;
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
