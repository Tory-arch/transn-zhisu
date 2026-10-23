# 传神智溯

面向拟上市制造企业及券商项目组的 IPO 数据服务网站：**数据体检、数据治理、问询数据响应**。本仓库提供可编辑的静态网站、七张故事海报、导出素材和海报生成源码。

- **在线浏览**：[传神智溯官网](https://tory-arch.github.io/transn-zhisu/)（公开访问，无需登录）
- **下载可编辑包**：[v1.3.1 完整 ZIP](https://github.com/Tory-arch/transn-zhisu/releases/download/v1.3.1/transn-zhisu-editable-v1.3.1.zip)（无需登录，解压后可修改）
- **源码仓库**：[Tory-arch/transn-zhisu](https://github.com/Tory-arch/transn-zhisu)
- **故事海报**：[七张海报](https://tory-arch.github.io/transn-zhisu/story.html)
- **一页总览**：[HTML 版总览](https://tory-arch.github.io/transn-zhisu/overview.html) · [4K PNG](https://tory-arch.github.io/transn-zhisu/assets/overview/zhisu-overview-4k.png)
- **参与修改**：[协作指南](CONTRIBUTING.md)（Fork → 本地编辑 → 预览 → Pull Request）

公开浏览和下载不需要 GitHub 账号。希望合入修改时，可登录 GitHub 后 Fork 并提交 Pull Request；直接推送原仓库需要所有者授予写入权限。

## 三项服务

| 产品 | 适用需求 | 主要交付与边界 |
| --- | --- | --- |
| **IPO 数据体检** | 先了解跨系统数据能否勾稽，定位问题与缺失依据，判断处理范围 | 风险体检报告：问题定位、影响范围与治理建议；体检后不必然进入治理 |
| **IPO 数据治理** | 历史数据互相矛盾，需要形成可复核的逐品号进耗存与成本明细 | 三年逐品号明细、来源说明、调整留痕台账、残差清单、可重跑规则集 |
| **IPO 问询数据响应** | 围绕具体问询，查找来源单据、核对计算过程并整理底稿 | 问询数据证据包；供券商、会计师编写回复，不替代专业机构撰写回复或作出审计判断 |

三项服务可按需选择，也可衔接使用。未做过治理的客户可先评估问询涉及的数据范围，必要时进行针对性还原。周期、费用与配合事项按具体范围评估，不把一种产品的报价或周期套用到其他产品。

AI 的价值在于读取诊断、梳理线索、推断矛盾成因并提出规则；程序按确认后的规则试算、校验与重算；企业及专业人员确认关键事实、计价依据和会计口径。结果仍需复核，无法解释的差额继续列明。

## 七张海报

| 编号 | 主题 | 讲述重点 |
| --- | --- | --- |
| 01 | 服务总览 | 让数据说得清，让追问有依据。分别说明什么情况下需要、具体怎么做与最终交付，可单选可衔接 |
| 02 | 为什么用 AI | 以 A/B 用料差异为起点，AI 提出候选解释、程序试算、AI 反查修正，专业确认并留痕 |
| 03 | 数据体检 | 先看清问题，再决定怎么处理。从入库与财务金额对不上的例子，说明批量比对、辅助归因、范围评估与报告交付 |
| 04 | 数据治理 | 先把数量对齐，再把成本算清。解释加工链断点、先核数量再算成本，以及明细、来源、留痕、残差与规则五项交付 |
| 05 | 问询数据响应 | 问到哪笔数据，就追到哪条依据。以毛利变化说明问题拆解、取数重算和证据整理，交付问询数据证据包 |
| 06 | 客户实践 | 百万行数据，追到每笔调整的依据。说明原先难题、还原路径与交付，保留案例规模、调整留痕与残差口径 |
| 07 | 开始合作 | 从当前难题，找到合作起点。准备现有数据、已知问题、目标与确认人，共同约定服务范围 |

海报以统一的蓝白业务插图配合具体例子，说明适用情况、处理步骤和客户能拿到的成果。数据体检从入库与财务金额不符讲起，数据治理解释加工链上的数量与计价断点，问询数据响应以毛利变化串联来源和计算过程。第 02 张通过 A/B 用料差异说明 AI、程序与专业人员的分工。七张海报包含网页 WebP、单张 PDF、合订 PDF 和 PNG 导出图。网页可用 `story.html#poster-01` 至 `#poster-07` 直达指定章节；例如 [为什么用 AI](https://tory-arch.github.io/transn-zhisu/story.html#poster-02)。服务总览单页 PDF 位于 `assets/zhisu-poster.pdf`，可独立发送给客户，包含三项服务的适用问题、工作内容、交付及 AI / 程序 / 人的分工。

网站还保留四类业务问题示意：多套编号、领料偏离配方、入库缺价、库存不符。场景图是解释业务问题的辅助素材，其编号独立于海报章节。销售演示与沟通清单在浏览器本地运行，不自动上传或发送企业信息。

## 修改什么，去哪里

| 修改内容 | 对应文件 |
| --- | --- |
| 一页总览网页（真实文字、业务图、手机自适应） | [overview.html](overview.html)、[overview.css](overview.css)、[overview.js](overview.js) |
| 一页总览 4K 导出 | [导出脚本与使用说明](design/overview/README.md)；浏览器以 1280×1920 CSS 像素、2 倍像素密度直接渲染为 2560×3840 PNG |
| 三产品定位、服务范围、首页文案与结构 | [index.html](index.html) |
| 三产品布局、AI 过程与案例样式 | [products.css](products.css) |
| 三产品交付切换、产品分享锚点与合作服务预选 | [products.js](products.js) |
| 通用样式、页面交互和沟通清单 | [styles.css](styles.css)、[app.js](app.js) |
| AI 分工与工作循环 | `index.html` 的 `#method` 段、[ai-value.css](ai-value.css) |
| 四类业务问题的分类、说明与切换 | [business-scenes.js](business-scenes.js)、[business-scenes.css](business-scenes.css)，以及 `index.html` 的 `#challenges` 初始内容 |
| AI 用料差异插图 | `assets/material-discrepancy.webp`（网页）、`assets/material-discrepancy.png`（第 02 张海报共用原图）；[生成说明](docs/material-discrepancy-prompt.md) |
| 三项服务与案例插图 | `assets/service-check.png`、`assets/service-governance.png`、`assets/service-inquiry.png`、`assets/case-factory.png`；[生成说明](docs/service-image-prompts.md) |
| 四张业务图片 | `assets/pain-identity.png`、`pain-recipe.png`、`pain-price.png`、`pain-stock.png` |
| 海报展厅的章节、说明与交互 | [story.html](story.html)、[story.css](story.css)、[story.js](story.js) |
| 海报网页图与 PDF | `assets/posters/01.webp`—`07.webp`、`01.pdf`—`07.pdf`、`zhisu-story.pdf`；首页单页为 `assets/zhisu-poster.pdf` |
| 海报生成源码 | [design/posters/build_posters.py](design/posters/build_posters.py)；步骤见[海报制作说明](design/posters/README.md) |
| 海报 PNG 导出图 | [design/posters/exports/](design/posters/exports/) 中的 `01.png`—`07.png`、`overview.png` |
| 销售讲解提示 | [docs/sales-notes.md](docs/sales-notes.md) |
| 业务场景图稿说明 | [docs/pain-image-prompts.md](docs/pain-image-prompts.md) |

修改海报标题、顺序或内容后，需要同时更新生成源码、展厅说明与导出素材。仅修改网站不需要安装海报生成依赖。

## 本地预览

下载 ZIP 并解压，或克隆仓库。在包含 `index.html` 的仓库目录运行：

```bash
python3 -m http.server 8080
```

访问 `http://localhost:8080/` 查看首页，访问 `http://localhost:8080/story.html` 查看海报，访问 `http://localhost:8080/overview.html` 查看一页总览。结束时按 `Ctrl+C`。网站无需数据库或构建工具；资源使用相对路径，兼容 GitHub Pages 的项目地址。

一页总览的文字、数字、图标与流程线由 HTML/CSS/SVG 排版，业务插图复用现有原图的 WebP 版本。电脑端保持整页海报比例，手机端纵向展开。页面可下载 4K PNG，并通过浏览器打印保存 PDF；底部以用户确认的“智解数据，溯源有据。”品牌标语收尾，不放网址、箭头或咨询入口。它是独立页面，不覆盖官网首页和七张海报。标题字号按主标题、板块标题、产品名称及内容小标题统一管理，长交付物名称采用同字号换行。

## 发布与版本

GitHub Pages 从 `main` 分支的根目录发布，保留 `.nojekyll`。修改合入 `main` 后会触发站点更新；本地修改、Fork 或提交 PR 本身不会改变官网。可编辑发布包使用版本号固定内容，v1.3.1 的下载地址见本页顶部。

## 公开内容边界

品牌统一为 **传神智溯**。公开仓库保存获准公开的网站内容与素材；不加入原始销售 DOCX、客户原始单据、企业数据、未公开附件或本机配置。新增原始资料应先整理成可公开的文案再提交。

业务场景图片和示例数值不代表真实客户数据或已确定的损失；差额原因未明确时保留待核对状态。案例中的三年是数据范围，原 ERP 尝试一年不是本服务的交付时长。服务不承诺 AI 零错、固定体检周期、未确认的费用抵扣、审计结论或 IPO 结果。品牌、文案与图片的权利归各权利人所有。
