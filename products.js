'use strict';

// Keep product links, tabs, browser history and the enquiry brief in sync.
const productTabs = [...document.querySelectorAll('[data-product]')];
const productKeys = productTabs.map(tab => tab.dataset.product);
const productService = document.getElementById('service');

function selectProduct(key, { focus = false, updateHash = false } = {}) {
  if (!productKeys.includes(key)) return;
  productTabs.forEach(tab => {
    const active = tab.dataset.product === key;
    tab.setAttribute('aria-selected', String(active));
    tab.tabIndex = active ? 0 : -1;
    document.getElementById(tab.getAttribute('aria-controls')).hidden = !active;
    if (active && focus) tab.focus({ preventScroll: true });
  });
  if (updateHash) history.pushState(null, '', `#product-${key}`);
}

function syncProductHash() {
  const key = location.hash.replace('#product-', '');
  if (productKeys.includes(key)) selectProduct(key);
}

productTabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectProduct(tab.dataset.product, { updateHash: true }));
  tab.addEventListener('keydown', event => {
    let next = index;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % productTabs.length;
    else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index + productTabs.length - 1) % productTabs.length;
    else if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = productTabs.length - 1;
    else return;
    event.preventDefault();
    selectProduct(productTabs[next].dataset.product, { focus: true, updateHash: true });
  });
});

document.querySelectorAll('[data-product-link]').forEach(link => {
  link.addEventListener('click', event => {
    if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    selectProduct(link.dataset.productLink, { updateHash: true });
    document.getElementById('delivery').scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    productTabs.find(tab => tab.dataset.product === link.dataset.productLink).focus({ preventScroll: true });
  });
});

document.querySelectorAll('[data-service]').forEach(link => {
  link.addEventListener('click', () => {
    productService.value = link.dataset.service;
  });
});

window.addEventListener('hashchange', syncProductHash);
window.addEventListener('popstate', syncProductHash);
syncProductHash();

// Native hash scrolling happens before scripts reveal an initially hidden panel.
if (productKeys.includes(location.hash.replace('#product-', ''))) {
  requestAnimationFrame(() => document.getElementById('delivery').scrollIntoView({ behavior: 'instant', block: 'start' }));
}
