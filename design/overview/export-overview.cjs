#!/usr/bin/env node
'use strict';

// Render the actual 1280 × 1920 HTML poster at DPR 2. No bitmap upscaling.
const fs = require('node:fs');
const fsp = require('node:fs/promises');
const path = require('node:path');
const os = require('node:os');
const http = require('node:http');

const ROOT = path.resolve(__dirname, '../..');
const OUTPUT = path.join(ROOT, 'assets/overview/zhisu-overview-4k.png');
const SIZE = { width: 1280, height: 1920 };
const SCALE = 2;
const TIMEOUT = Number(process.env.OVERVIEW_TIMEOUT_MS || 30000);
const MIME = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript',
  '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
  '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.woff': 'font/woff',
  '.ttf': 'font/ttf', '.otf': 'font/otf', '.ico': 'image/x-icon', '.json': 'application/json' };

function configuredPath(value) {
  return path.resolve(value.replace(/^~(?=$|[\\/])/, os.homedir()));
}

function loadPlaywright() {
  const explicit = process.env.OVERVIEW_PLAYWRIGHT_PATH;
  const candidates = explicit ? [configuredPath(explicit)] : [
    path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright'),
    path.join(os.homedir(), '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright-core'),
    'playwright', 'playwright-core',
  ];
  for (const candidate of candidates) {
    try {
      const library = require(candidate);
      if (library.chromium) return library;
    } catch (error) {
      if (explicit) throw new Error(`OVERVIEW_PLAYWRIGHT_PATH 无法加载：${error.message}`);
    }
  }
  throw new Error('未找到已安装的 Playwright。请设置 OVERVIEW_PLAYWRIGHT_PATH；本脚本不会下载或安装依赖。');
}

async function launchBrowser(chromium) {
  const explicit = process.env.OVERVIEW_BROWSER_PATH;
  const candidates = explicit ? [configuredPath(explicit)] : [
    chromium.executablePath(),
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    path.join(os.homedir(), 'Applications/Google Chrome.app/Contents/MacOS/Google Chrome'),
    '/usr/bin/google-chrome-stable', '/usr/bin/google-chrome', '/opt/google/chrome/chrome',
    '/usr/bin/chromium', '/usr/bin/chromium-browser',
    ...['LOCALAPPDATA', 'PROGRAMFILES', 'PROGRAMFILES(X86)']
      .filter(key => process.env[key])
      .map(key => path.join(process.env[key], 'Google/Chrome/Application/chrome.exe')),
  ];
  const errors = [];
  for (const executablePath of [...new Set(candidates)].filter(Boolean)) {
    if (!fs.existsSync(executablePath)) continue;
    try {
      const browser = await chromium.launch({ executablePath, headless: true, timeout: TIMEOUT });
      return { browser, name: path.basename(executablePath) };
    } catch (error) {
      errors.push(`${path.basename(executablePath)}: ${error.message.split('\n')[0]}`);
    }
  }
  throw new Error(`没有可启动的本地浏览器。请用 OVERVIEW_BROWSER_PATH 指定 Chrome/Chromium 可执行文件。${errors.length ? ` ${errors.join('; ')}` : ''}`);
}

async function startLocalServer() {
  const server = http.createServer(async (request, response) => {
    try {
      const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
      const filename = path.resolve(ROOT, `.${pathname === '/' ? '/overview.html' : pathname}`);
      if (filename !== ROOT && !filename.startsWith(ROOT + path.sep)) {
        response.writeHead(403).end(); return;
      }
      // Chromium may request this automatically even when the page declares no icon.
      if (pathname === '/favicon.ico' && !fs.existsSync(filename)) {
        response.writeHead(204).end(); return;
      }
      const data = await fsp.readFile(filename);
      response.writeHead(200, { 'Content-Type': MIME[path.extname(filename)] || 'application/octet-stream',
        'Cache-Control': 'no-store' });
      response.end(data);
    } catch (error) {
      response.writeHead(error.code === 'ENOENT' ? 404 : 400).end();
    }
  });
  await new Promise((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '127.0.0.1', resolve);
  });
  return { server, origin: `http://127.0.0.1:${server.address().port}` };
}

async function main() {
  if (!Number.isFinite(TIMEOUT) || TIMEOUT < 1000) throw new Error('OVERVIEW_TIMEOUT_MS 必须是至少 1000 的毫秒数。');
  if (!fs.existsSync(path.join(ROOT, 'overview.html'))) throw new Error('仓库根目录缺少 overview.html；请先完成页面。');
  const { chromium } = loadPlaywright();
  const pageErrors = [], resourceErrors = [], consoleErrors = [];
  let browser, server, temporary;
  try {
    const launched = await launchBrowser(chromium); browser = launched.browser;
    const local = await startLocalServer(); server = local.server;
    const context = await browser.newContext({ viewport: SIZE, deviceScaleFactor: SCALE,
      reducedMotion: 'reduce', colorScheme: 'light', locale: 'zh-CN', serviceWorkers: 'block' });
    // The exporter serves only this repository and never loads internet resources.
    await context.route('**/*', route => {
      const url = route.request().url();
      if (url.startsWith(local.origin + '/') || /^(data|blob):/.test(url)) return route.continue();
      resourceErrors.push(`外部资源已阻止：${url}`); return route.abort('blockedbyclient');
    });
    const page = await context.newPage();
    page.setDefaultTimeout(TIMEOUT);
    page.on('pageerror', error => pageErrors.push(error.message));
    page.on('console', message => { if (message.type() === 'error') consoleErrors.push(message.text()); });
    page.on('requestfailed', request => resourceErrors.push(`${request.url()}: ${request.failure()?.errorText}`));
    page.on('response', response => {
      if (response.status() >= 400) resourceErrors.push(`${response.status()} ${response.url()}`);
    });
    await page.goto(`${local.origin}/overview.html`, { waitUntil: 'load', timeout: TIMEOUT });
    await page.evaluate(() => document.documentElement.classList.add('export'));
    await page.addStyleTag({ content: 'html.export *, html.export *::before, html.export *::after { animation: none !important; transition: none !important; caret-color: transparent !important; } html.export { scroll-behavior: auto !important; }' });
    const canvas = page.locator('.overview-canvas');
    if (await canvas.count() !== 1) throw new Error('页面必须恰好包含一个 .overview-canvas。');
    await canvas.waitFor({ state: 'visible' });
    await page.waitForFunction(() => document.fonts.status === 'loaded'
      && [...document.querySelectorAll('.overview-canvas img')].every(img => img.complete), null, { timeout: TIMEOUT });
    const checks = await canvas.evaluate(async element => {
      await document.fonts.ready;
      const images = [...element.querySelectorAll('img')];
      await Promise.all(images.map(image => image.decode().catch(() => {})));
      await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
      const bounds = element.getBoundingClientRect();
      const brokenImages = images.filter(image => !image.complete || !image.naturalWidth || !image.naturalHeight)
        .map(image => image.getAttribute('src'));
      const failedFonts = [...document.fonts].filter(font => font.status === 'error').map(font => font.family);
      const overflow = [], warnings = [];
      const label = node => node.id ? `#${node.id}` : `${node.tagName.toLowerCase()}${[...node.classList].map(name => `.${name}`).join('')}`;
      const visible = node => {
        const style = getComputedStyle(node);
        return node.getClientRects().length && style.visibility !== 'hidden' && style.opacity !== '0';
      };
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
      let node, textRuns = 0;
      while ((node = walker.nextNode())) {
        if (!node.textContent.trim() || !visible(node.parentElement)) continue;
        const range = document.createRange(); range.selectNodeContents(node); textRuns++;
        for (const rect of range.getClientRects()) {
          if (rect.width && rect.height && (rect.left < bounds.left - 1.5 || rect.right > bounds.right + 1.5
            || rect.top < bounds.top - 1.5 || rect.bottom > bounds.bottom + 1.5)) {
            overflow.push({ type: 'outside-canvas', element: label(node.parentElement), text: node.textContent.trim().slice(0, 48) }); break;
          }
        }
      }
      for (const node of element.querySelectorAll('h1,h2,h3,h4,h5,h6,p,li,dt,dd,button,a,span,strong,em,small,label')) {
        if (!visible(node) || !node.textContent.trim()) continue;
        const horizontal = node.clientWidth && node.scrollWidth > node.clientWidth + 2;
        const vertical = node.clientHeight && node.scrollHeight > node.clientHeight + 2;
        if (horizontal || vertical) {
          const style = getComputedStyle(node);
          const measurement = { type: 'text-box-overflow', element: label(node), text: node.textContent.trim().slice(0, 48),
            client: [node.clientWidth, node.clientHeight], scroll: [node.scrollWidth, node.scrollHeight],
            overflowX: style.overflowX, overflowY: style.overflowY, lineHeight: style.lineHeight };
          // Ascenders/descenders may extend beyond a compact line box without being clipped.
          // Horizontal overflow and actual vertical clipping remain hard failures.
          if (horizontal || (vertical && style.overflowY !== 'visible')) overflow.push(measurement);
          else warnings.push({ ...measurement, type: 'visible-font-linebox' });
        }
      }
      return { width: bounds.width, height: bounds.height, imageCount: images.length, brokenImages,
        loadedFontFaces: [...document.fonts].filter(font => font.status === 'loaded').length,
        failedFonts, textRuns, overflow: overflow.slice(0, 12),
        warningCount: warnings.length, warnings: warnings.slice(0, 12) };
    });
    if (Math.abs(checks.width - SIZE.width) > 0.01 || Math.abs(checks.height - SIZE.height) > 0.01)
      throw new Error(`导出布局尺寸错误：${checks.width}×${checks.height}，要求 1280×1920 CSS px。`);
    if (!checks.imageCount) throw new Error('海报未包含 img 图片，请检查页面是否已完成。');
    if (checks.brokenImages.length) throw new Error(`图片加载失败：${JSON.stringify(checks.brokenImages)}`);
    if (checks.failedFonts.length) throw new Error(`字体加载失败：${JSON.stringify(checks.failedFonts)}`);
    if (checks.overflow.length) throw new Error(`发现文字溢出：${JSON.stringify(checks.overflow)}`);
    const errors = () => [...pageErrors, ...consoleErrors, ...resourceErrors];
    if (errors().length) throw new Error(`页面/资源错误：${JSON.stringify(errors().slice(0, 8))}`);
    await fsp.mkdir(path.dirname(OUTPUT), { recursive: true });
    temporary = `${OUTPUT}.${process.pid}.tmp.png`;
    await canvas.screenshot({ path: temporary, type: 'png', scale: 'device', animations: 'disabled', timeout: TIMEOUT });
    const png = await fsp.readFile(temporary);
    if (!png.subarray(0, 8).equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))) throw new Error('导出文件不是 PNG。');
    const pixels = { width: png.readUInt32BE(16), height: png.readUInt32BE(20) };
    if (pixels.width !== 2560 || pixels.height !== 3840) throw new Error(`PNG 像素错误：${pixels.width}×${pixels.height}。`);
    if (errors().length) throw new Error(`渲染时出现页面/资源错误：${JSON.stringify(errors().slice(0, 8))}`);
    await fsp.rename(temporary, OUTPUT); temporary = null;
    console.log(JSON.stringify({ ok: true, output: path.relative(ROOT, OUTPUT).split(path.sep).join('/'),
      css: SIZE, pixels, deviceScaleFactor: SCALE, images: checks.imageCount,
      loadedFontFaces: checks.loadedFontFaces, textRuns: checks.textRuns,
      textOverflow: 0, pageErrors: 0, browser: launched.name,
      warningCount: checks.warningCount, warnings: checks.warnings.map(item => ({
        type: item.type, element: item.element, clientHeight: item.client[1], scrollHeight: item.scroll[1],
      })) }));
  } finally {
    if (temporary) await fsp.rm(temporary, { force: true }).catch(() => {});
    if (browser) await browser.close().catch(() => {});
    if (server) await new Promise(resolve => server.close(resolve));
  }
}

main().catch(error => {
  console.error(JSON.stringify({ ok: false, error: error.message }));
  process.exitCode = 1;
});
