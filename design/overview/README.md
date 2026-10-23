# 一页总览海报导出

`export-overview.cjs` 将仓库根目录的 `overview.html` 作为真实网页渲染，向 `document.documentElement` 添加 `export` class，截取唯一的 `.overview-canvas`。

CSS 海报尺寸必须为 **1280 × 1920**；浏览器以 `deviceScaleFactor=2` 渲染文字与图片，输出 **2560 × 3840 PNG**。脚本不拉伸已有小图，也不裁切为其他比例。最终文件为 `assets/overview/zhisu-overview-4k.png`。

## 运行

页面及资源完成后，从仓库根目录运行：

```sh
node design/overview/export-overview.cjs
```

也可以在任意工作目录使用脚本的绝对路径；仓库位置由 `__dirname` 推导。需要已安装的 Node.js、Playwright 与 Chrome/Chromium；脚本不会安装依赖或下载浏览器。

Playwright 优先查找 Codex bundled runtime 的 `playwright` / `playwright-core`，其次采用 Node.js 常规模块解析。默认先尝试 Playwright 已安装的 Chromium；不可用时回退到本机 Chrome，再尝试常见 Linux Chromium 路径。

需要指定路径时：

```sh
OVERVIEW_PLAYWRIGHT_PATH=/absolute/path/to/node_modules/playwright \
OVERVIEW_BROWSER_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
node design/overview/export-overview.cjs
```

| 环境变量 | 作用 |
| --- | --- |
| `OVERVIEW_PLAYWRIGHT_PATH` | 已安装的 `playwright` 或 `playwright-core` 包目录；显式指定后不会静默换用其他模块。 |
| `OVERVIEW_BROWSER_PATH` | Chrome/Chromium 可执行文件路径；显式指定后只尝试这个浏览器。 |
| `OVERVIEW_TIMEOUT_MS` | 页面加载与主要等待的超时毫秒数，默认 `30000`，最小 `1000`。 |

## 导出前检查

脚本只在本机 `127.0.0.1` 的随机端口提供仓库静态文件，并阻止所有外部资源请求。字体、图片、样式与脚本应来自仓库，不能依赖在线字体或 CDN。导出结束后关闭页面、浏览器和本地服务。

在固定导出布局下，脚本会等待字体加载及图片解码、关闭动画，并验证：

- 恰好存在一个可见的 `.overview-canvas`，边界为 1280 × 1920 CSS px。
- 海报内至少有一张图片，所有 `img` 均加载成功，字体没有加载错误。
- 没有页面异常、控制台错误、失败资源或外部网络请求。
- 可见文字未越出海报边界，常见文字容器没有水平溢出或被 `hidden` / `clip` / 滚动容器真实裁切的纵向内容。
- 最终 PNG 文件头记录的尺寸确实为 2560 × 3840。

所有检查通过后才替换最终图片；失败时保留上次成功版本，清理未完成的临时图片。脚本向终端输出一行 JSON，成功为 `ok: true`，失败为 `ok: false` 并返回非零退出码。

文字溢出检测属于几何检查，不能判断词句是否合适、视觉层级是否清楚或对象之间是否相互遮挡。交付前仍应查看导出的完整 PNG。系统字体可能随操作系统和版本变化；若需要跨机器稳定复现，应在页面中引用可合法分发的仓库本地字体。

当 `overflow-y: visible` 时，字体升部、降部可能使 `scrollHeight` 略高于 `clientHeight`，尤其是大字号、紧凑行高。这类差异记入 JSON 的 `warnings`，不阻止导出；文字超出画布、横向溢出或实际裁切仍判为失败。
