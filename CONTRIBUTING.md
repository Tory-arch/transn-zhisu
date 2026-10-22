# 传神智溯：修改与协作指南

本仓库包含静态网站、三项服务的公开说明、七张故事海报和可编辑生成源码。网站与 ZIP 下载无需登录；Fork、推送及 Pull Request 需要 GitHub 账号。

- [源码仓库](https://github.com/Tory-arch/transn-zhisu)
- [在线网站](https://tory-arch.github.io/transn-zhisu/)
- [v1.2.0 可编辑包](https://github.com/Tory-arch/transn-zhisu/releases/download/v1.2.0/transn-zhisu-editable-v1.2.0.zip)

## 下载后直接修改

下载 ZIP，解压后用编辑器打开文件夹。在包含 `index.html` 的目录启动本地预览即可。ZIP 不包含 Git 历史；希望向原仓库贡献时，请先创建自己的 Fork，再把修改放进 Fork。

## Fork → 本地编辑 → 预览 → Pull Request

### 1. 创建修改分支

登录 GitHub，在[源码仓库](https://github.com/Tory-arch/transn-zhisu)点击 **Fork**。将下面命令的 `YOUR_GITHUB_USERNAME` 替换为自己的用户名；如果 Fork 改过仓库名，也一并替换。

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/transn-zhisu.git
cd transn-zhisu
git switch -c update-site
```

### 2. 找到编辑入口

| 要改什么 | 编辑哪里 |
| --- | --- |
| 品牌、三产品说明、服务范围、客户实践、合作入口 | `index.html` |
| 三产品布局、AI 过程与案例样式 | `products.css` |
| 三产品交付切换、产品分享锚点与合作服务预选 | `products.js` |
| 页面通用布局、交互与沟通清单 | `styles.css`、`app.js` |
| AI 分工与诊断—规则—试算—复核循环 | `index.html` 的 `#method`、`ai-value.css` |
| 四类业务问题的内容与切换 | `business-scenes.js`、`business-scenes.css`，以及 `index.html` 的 `#challenges` 初始内容 |
| 七张海报的章节、说明、下载与直达链接 | `story.html`、`story.css`、`story.js` |
| 海报生成及绘图文案 | `design/posters/build_posters.py`；见[海报制作说明](design/posters/README.md) |
| 网站海报图片与 PDF | `assets/posters/`；首页单页海报为 `assets/zhisu-poster.pdf` |
| PNG 导出图 | `design/posters/exports/01.png`—`07.png`、`overview.png` |
| 销售话术和业务图稿 | [docs/sales-notes.md](docs/sales-notes.md)、[docs/pain-image-prompts.md](docs/pain-image-prompts.md) |

品牌统一使用 **传神智溯**。三产品为 **IPO 数据体检、IPO 数据治理、IPO 问询数据响应**。七张海报顺序固定为 **01 总览 → 02 AI → 03 体检 → 04 治理 → 05 问询 → 06 案例 → 07 合作**。

更新海报后同步生成源码、网页说明、PDF、WebP 和 PNG。保留 `story.html#poster-01` 至 `#poster-07` 的章节含义；批量替换素材时，更新相应资源版本参数，避免访问者看到旧缓存。

修改业务场景文案时，同步 `business-scenes.js` 与 `index.html` 的初始场景。保留 `#scene-identity`、`#scene-recipe`、`#scene-price`、`#scene-stock`、`#issue-panel` 等已有分享入口。业务图保持 3:2 完整显示，未确认的差异不要写成已确定的浪费、盘亏或客户损失。

### 3. 本地预览

在仓库根目录运行：

```bash
python3 -m http.server 8080
```

打开 `http://localhost:8080/` 与 `http://localhost:8080/story.html`，结束时按 `Ctrl+C`。仅预览网站无需安装海报依赖；重新生成海报才需按[海报制作说明](design/posters/README.md)准备 Python 库、字体和可选渲染工具。

按实际改动检查对应部分：三产品的名称、适用阶段和交付是否一致；桌面与手机布局是否可读；七个海报章节、图片、单张及合集下载是否对应；带章节编号的直达链接是否正确。资源引用保留相对路径，避免使用 `/assets/` 这样的站点根路径。

### 4. 提交修改

先查看差异，仅添加本次要提交的文件。以下为修改首页的示例，可按实际文件调整：

```bash
git status
git diff
git add index.html styles.css app.js
git diff --cached
git commit -m "Update IPO data service presentation"
git push -u origin update-site
```

不要将原始销售 DOCX、客户数据、未公开附件、字体文件或本机配置加入提交或 PR 附件。设计构建目录中的临时文件不应代替整理后的正式导出素材。

### 5. 创建 Pull Request

在自己的 Fork 打开修改分支，创建指向 `Tory-arch/transn-zhisu` 的 `main` 分支的 Pull Request。说明改了什么、原因和预览结果；视觉修改附桌面与手机截图。维护者合并后，GitHub Pages 会从 `main` 更新；PR 本身不会直接改变官网。

直接推送原仓库需要所有者邀请并授予写入权限。公开下载或 Fork 不会自动获得原仓库的写入权限。

## 文案与服务边界

- 体检用于定位数据疑点、解释依据与治理工作量，不把风险分级写成对监管问询概率的预测。体检后不必然购买治理。
- 治理交付明细、来源、留痕、残差与可重跑规则；保留无法解释的部分。三年是数据范围，不是工期。
- 问询数据响应提供数据证据和底稿，不替代券商、会计师撰写回复或作出审计判断。未经治理的数据可能需要先做针对性还原。
- AI 推断和规则需要经过校验及专业确认，不使用“零错”“保证全部解决”等承诺。体检周期与费用抵扣未确定前，不写成固定条件。
- 案例数据必须说明适用范围，不能把数据修正金额写成现金收益，把残差比例写成准确率，或把原 ERP 的一年经历写成本服务的实施时长。

服务介绍不构成对审计结论或 IPO 结果的承诺。品牌、文案与图片的权利归各权利人所有。
