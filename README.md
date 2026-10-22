# 传神 · 智溯

IPO 成本数据还原服务展示网站。提供完整静态网站、展示素材及海报生成源码，可下载后修改；网站无需数据库或构建工具。

- **源码仓库**：[Tory-arch/transn-zhisu](https://github.com/Tory-arch/transn-zhisu)
- **下载全部文件**：[Download ZIP](https://github.com/Tory-arch/transn-zhisu/archive/refs/heads/main.zip)（无需登录，解压后即可编辑）
- **在线浏览**：[GitHub Pages](https://tory-arch.github.io/transn-zhisu/)（无需登录）
- **四类业务痛点**：[图片与说明](https://tory-arch.github.io/transn-zhisu/#challenges)
- **故事海报**：[七张海报](https://tory-arch.github.io/transn-zhisu/story.html)
- **参与修改**：[协作指南](CONTRIBUTING.md)（Fork → 本地编辑 → 预览 → Pull Request）
- **原官网地址**：[Sites](https://zhisu-data-clarity.zz8jc7tsh8.chatgpt.site/)

任何人都可以浏览和下载公开文件。希望把修改合入本仓库时，可登录 GitHub 后 Fork 并提交 Pull Request；直接向本仓库推送，需要仓库所有者先邀请为协作者并授予相应权限。下载或 Fork 不会自动获得原仓库的写入权限。

## 内容

- 服务首页：价值说明、处理方法、五项交付、客户实践、合作方式及常见问题。
- 四张独立生成的业务痛点图：多套编号、领料偏离配方、入库缺价、库存不符。
- AI 价值说明：跨单据梳理、100+ 专项智能体分工、规则变化后三年统一重算。
- 左侧四分类切换右侧图片与说明，支持键盘导航和独立链接；分类下方随场景显示“问题出在哪 / 为什么难查 / 会影响什么”，用细分隔线补充业务解释。
- 手机上分类排为 2×2，补充说明移到图片和图下文字之后；四张图片保持完整比例，不裁切。
- 七张故事海报，主线依次为：业务难题 → 为什么用 AI → 专项智能体 → 规则重算 → 交付 → 案例 → 合作；包含网页图片、单张 PDF 和合订 PDF。
- 海报可编辑生成源码，以及 `01.png`—`07.png` 和 `overview.png` 导出图。
- 销售演示、本地生成的沟通清单、讲解提示与业务场景图稿说明。

## 修改什么，去哪里

| 修改内容 | 对应文件 |
| --- | --- |
| 首页文案、段落结构 | [index.html](index.html) |
| 官网通用样式与交互 | [styles.css](styles.css)、[app.js](app.js) |
| 四类业务问题的分类、说明与切换 | [business-scenes.js](business-scenes.js)、[business-scenes.css](business-scenes.css)；初始内容在 `index.html` 的 `#challenges` 段 |
| 四张业务场景图 | `assets/pain-identity.png`、`assets/pain-recipe.png`、`assets/pain-price.png`、`assets/pain-stock.png` |
| 为什么用 AI | `index.html` 的 `#method` 段、[ai-value.css](ai-value.css) |
| 海报展厅与下载入口 | [story.html](story.html)、[story.css](story.css)、[story.js](story.js)、`assets/posters/`；首页服务海报为 `assets/zhisu-poster.pdf` |
| 海报可编辑生成源码 | [design/posters/build_posters.py](design/posters/build_posters.py) |
| 海报 PNG 导出图 | [design/posters/exports/](design/posters/exports/)：`01.png`—`07.png`、`overview.png` |
| 销售讲解提示 | [docs/sales-notes.md](docs/sales-notes.md) |
| 业务场景图稿说明 | [docs/pain-image-prompts.md](docs/pain-image-prompts.md) |

海报依赖安装、生成命令和产物说明见 [海报制作说明](design/posters/README.md)。仅修改网站不需要安装海报生成依赖。

## 本地预览

下载 ZIP 并解压，或克隆仓库后，在包含 `index.html` 的仓库目录运行：

```bash
python3 -m http.server 8080
```

然后访问 `http://localhost:8080/`。所有资源使用相对路径，也兼容 GitHub Pages 项目路径。完整协作步骤见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 发布

GitHub Pages 从 `main` 分支的根目录发布。`.nojekyll` 保留原始静态文件；修改合入 `main` 后会自动重新部署。

本地修改和 Fork 不会改变本仓库的在线网站。直接推送由仓库所有者授权；普通贡献者通过 Pull Request 交由维护者审核合并。GitHub Pages 的更新不会自动同步到原 Sites 地址。

页面不要求访问者登录。沟通清单仅在当前浏览器生成，不上传或自动发送企业信息。

## 内容说明

业务痛点图片为概念示意；网页中的编号、数量、金额为示例数据，不表示真实客户数据或确定的问题成因。服务介绍不构成对审计结论或 IPO 结果的承诺。品牌、文案与图片的权利归各权利人所有。
