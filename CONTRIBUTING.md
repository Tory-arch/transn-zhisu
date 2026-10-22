# 修改与协作指南

本仓库是静态网站，HTML、CSS、JavaScript 和素材均可在本地编辑。网站访问和 ZIP 下载无需登录；Fork、推送及提交 Pull Request 需要 GitHub 账号。

- [源码仓库](https://github.com/Tory-arch/transn-zhisu)
- [在线网站](https://tory-arch.github.io/transn-zhisu/)
- [匿名下载 ZIP](https://github.com/Tory-arch/transn-zhisu/archive/refs/heads/main.zip)

## 只想下载和修改

下载 ZIP，解压后用编辑器打开文件夹。在包含 `index.html` 的目录启动本地预览即可。ZIP 不包含 Git 历史；若后续希望向原仓库贡献修改，请按下面流程创建 Fork，再把修改放进自己的 Fork。

## Fork → 本地编辑 → 预览 → Pull Request

### 1. 创建自己的 Fork

登录 GitHub，打开[源码仓库](https://github.com/Tory-arch/transn-zhisu)，点击 **Fork**，把仓库复制到自己的账号下。

克隆自己的 Fork，并新建修改分支。将命令中的 `YOUR_GITHUB_USERNAME` 替换成你的 GitHub 用户名；如果 Fork 使用了不同仓库名，也相应替换。

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/transn-zhisu.git
cd transn-zhisu
git switch -c update-site
```

### 2. 编辑对应文件

| 要改什么 | 编辑哪里 |
| --- | --- |
| 首页文案和段落 | `index.html` |
| 四类业务现场的内容、分类与说明 | `business-scenes.js`、`business-scenes.css`，以及 `index.html` 的 `#challenges` 初始内容 |
| “为什么用 AI” | `index.html` 的 `#method`、`ai-value.css` |
| 海报展厅 | `story.html`、`story.css`、`story.js` |
| 海报图片与 PDF | `assets/posters/`；首页单页海报为 `assets/zhisu-poster.pdf` |
| 重新生成海报 | `design/posters/build_posters.py`；安装与生成步骤见[海报制作说明](design/posters/README.md) |
| 查看或使用 PNG 导出图 | `design/posters/exports/01.png`—`07.png`、`overview.png` |
| 调整讲解提示或图稿说明 | [docs/sales-notes.md](docs/sales-notes.md)、[docs/pain-image-prompts.md](docs/pain-image-prompts.md) |

修改场景文案时，请同步 `business-scenes.js` 中的内容与 `index.html` 中的首个场景，避免首次加载显示旧文字。保留 `#scene-identity`、`#scene-recipe`、`#scene-price`、`#scene-stock` 和 `#issue-panel`，让已有分享链接继续有效。

业务图片保持 3:2 完整显示。编号、数量及差额属于演示数据；未确认的差异应继续标为待核对，不能写成已确定的浪费、盘亏或真实客户结果。

### 3. 本地预览

在仓库根目录运行：

```bash
python3 -m http.server 8080
```

打开 `http://localhost:8080/` 查看首页，打开 `http://localhost:8080/story.html` 查看海报展厅。结束预览时，在终端按 `Ctrl+C`。

根据实际修改检查对应部分：场景内容需确认四个分类、图片和说明同步；布局修改需查看桌面与手机宽度；海报更新需确认图片和下载链接能打开。网页素材使用相对路径，避免以 `/assets/` 这样的根路径引用资源，以兼容 GitHub Pages 项目地址。

仅预览网站不需要运行构建命令；只有重新生成海报时，才需按 [design/posters/README.md](design/posters/README.md) 安装依赖。

### 4. 提交到自己的 Fork

先查看修改，再添加本次需要提交的文件。下面以修改首页和业务现场为例，可按实际改动调整文件列表。

```bash
git status
git diff
git add index.html business-scenes.css business-scenes.js
git commit -m "Update business scene presentation"
git push -u origin update-site
```

### 5. 发起 Pull Request

在自己的 Fork 中打开刚推送的分支，创建 Pull Request，目标选择 `Tory-arch/transn-zhisu` 的 `main` 分支。

说明改了什么、原因和预览结果；视觉改动附桌面及手机截图。维护者审核合并后，GitHub Pages 会从 `main` 自动部署。提交 PR 本身不会立即改变在线网站。

## 如果需要直接推送

直接推送到原仓库，需要仓库所有者邀请你的 GitHub 账号成为协作者，并授予相应写入权限。请先与所有者确认协作安排；公开仓库、下载 ZIP 或 Fork 都不代表已获写入权限。本指南不会自动邀请任何人。

## 内容与权利

业务痛点图片为概念示意；网页中的编号、数量、金额为示例数据，不表示真实客户数据或确定的问题成因。服务介绍不构成对审计结论或 IPO 结果的承诺。品牌、文案与图片的权利归各权利人所有。
