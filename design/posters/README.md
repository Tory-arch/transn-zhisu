# 传神智溯海报源码

生成七张 A3 竖版海报、七页合集和一页服务介绍。文案、颜色及坐标保留在 `build_posters.py` 中；绘图使用 1120 × 1584 的设计坐标，PDF 文字可以选取。默认只写 `design/posters/build/`，不会覆盖网站资产，也不会上传或部署。

## 安装与生成

需要 Python 3.10+。以下命令从仓库根目录运行，建议先激活自己的 Python 虚拟环境：

```sh
python -m pip install -r design/posters/requirements.txt
python design/posters/build_posters.py --check
python design/posters/build_posters.py
```

在其他工作目录执行脚本也可以：仓库位置由脚本路径确定，所有相对参数路径均以仓库根目录为准。默认输出包含 7 张单页 PDF、7 页合集、1 张服务总览和 `manifest.json`。终端也输出相同的 JSON 清单，文件路径均相对仓库根目录。

## 中文字体

字体文件不随仓库分发。macOS 会自动尝试系统的 STHeiti Light / Medium（TTC index 1）。其他系统或需要更换字体时，指定已合法安装的中文 TrueType 字体：

```sh
python design/posters/build_posters.py --font-regular fonts/Chinese-Regular.ttf --font-bold fonts/Chinese-Bold.ttf
```

上面的字体名只是占位，请替换为自己的文件。TTC 集合使用 `--font-regular-index 0` 和 `--font-bold-index 0` 选择子字体；也接受带 `-ttc-` 的参数别名。显式指定字体时默认索引为 0。常规及粗体都必须可用；若有意使用同一字重，可为两个参数指定同一文件。英文字母和数字复用对应的中文字体，不依赖 Arial。ReportLab 需要 TrueType 轮廓，部分 CFF/OTF 字体不支持；缺字体、索引错误或缺少中文字形时会在生成前明确报错。

更换字体可能改变字宽，请检查生成预览中的换行和边界。不要把 macOS 系统字体或其他未授权字体提交到仓库。

## 可选：生成 PNG / WebP 预览

先安装 Poppler，让 `pdftoppm` 位于 PATH，或用 `--pdftoppm` 指定可执行文件：

```sh
python design/posters/build_posters.py --render
python design/posters/build_posters.py --render --pdftoppm /path/to/pdftoppm
```

Linux / Windows 同样可以使用这个命令，另加自己的字体参数即可。渲染七张海报和一页服务总览，每张输出 **1120 × 1584** 的 PNG 和 WebP。合集使用相同的七张页面，不额外重复渲染。仅生成 PDF 不需要 Poppler。可用环境变量 `PDFTOPPM` 设置默认可执行文件。

## 修改设计与同步网站

- **文案、字号、坐标与图形**：编辑 `build_pdfs()` 中编号 `01` 至 `07` 以及 `Service overview` 区块。`Poster` 的坐标从画面左上角计算。
- **颜色与画布**：编辑顶部的 `BLUE`、`INK` 等颜色常量；保持 `W=1120`、`H=1584` 可沿用现有网页比例。
- **图片**：使用仓库 `assets/` 中的 Logo、四张业务场景图及蓝色主视觉。保留文件名即可重建。
- **二维码**：使用 `--site-url https://example.com/` 修改第 07 张和服务总览的目标地址。
- **输出目录**：使用 `--output-dir design/posters/build-review`，不允许把输出目录放进 `assets/`。

确认 PDF 内容、字体与预览无误后，再显式同步网站：

```sh
python design/posters/build_posters.py --render --sync-site
```

这会更新 `assets/posters/01.pdf` 至 `07.pdf`、相应七张 PNG/WebP、`assets/posters/zhisu-story.pdf` 和 `assets/zhisu-poster.pdf`。`--sync-site` 不加 `--render` 时只更新 PDF，网页 WebP 保留原样，清单会给出提醒。此脚本不修改 HTML / JS，也不会提交 Git 或发布网站；若改了标题、顺序或说明，请另行同步 `story.html` / `story.js`。`--check` 永远只验证，不生成或同步，即使同时传入其他操作参数。

若需更新仓库供下载的 PNG，请将本次 build 目录的七张 PNG 依次更新到 `design/posters/exports/01.png` 至 `design/posters/exports/07.png`，将服务总览 PNG 更新到 `design/posters/exports/overview.png`；`--sync-site` 不会修改这些导出图。

## 七张海报顺序

1. 三产品总览：数据体检、数据治理、问询数据响应，可单选或组合。
2. 为什么用 AI：A/B 替代料案例，推断 → 规则 → 试算 → 校验 → 修正；人确认关键口径。
3. 数据体检：问题定位、影响范围、治理建议。
4. 数据治理：四类业务矛盾，先数量后金额，五项交付。
5. 问询数据响应：毛利变化问题拆解，追溯来源单据与计算规则，交付证据包。
6. 客户实践：三个年度实际 32 个月，单年源数据 144 万至 169 万行、最深 11 层、268,188 条数量调整留痕，残差单列。
7. 开始合作：按企业阶段选择产品，提供已有数据并确认关键事实。

## 内容边界

品牌统一为传神智溯。三年是数据服务范围，不是实施工期；匿名案例实际覆盖三个年度共 32 个月。268,188 指数量调整条数，每条留有依据；144 万至 169 万行指单年源数据。案例各年度残差金额占入库总额 1.06%–2.38%，不等于准确率，也不能推算未披露的挽损金额。4,000 余条替代关系为该已交付案例的年度数量，不是所有项目的普遍表现。

不宣传待定的体检价格和工期、AI 零错误或 100+ 智能体数量。会计口径和计价依据由企业及相关专业人员确认；问询数据证据包供券商、会计师撰写回复使用，不替代审计、专业判断或问询回复，不承诺 IPO 结果。
