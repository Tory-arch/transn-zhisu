# 传神 · 智溯

IPO 成本数据还原服务展示网站。完整静态源码与展示素材，可直接部署，无需数据库或构建工具。

- **在线浏览**：[GitHub Pages](https://tory-arch.github.io/transn-zhisu/)
- **四类业务痛点**：[图片与说明](https://tory-arch.github.io/transn-zhisu/#challenges)
- **故事海报**：[六张海报](https://tory-arch.github.io/transn-zhisu/story.html)
- **原官网地址**：[Sites](https://zhisu-data-clarity.zz8jc7tsh8.chatgpt.site/)

## 内容

- 服务首页：价值说明、处理方法、五项交付、客户实践、合作方式及常见问题。
- 四张独立生成的业务痛点图：多套编号、领料偏离配方、入库缺价、库存不符。
- AI 价值说明：跨单据梳理、100+ 专项智能体分工、规则变化后三年统一重算。
- 左侧分类切换右侧图片与说明，支持键盘导航和独立链接；手机上分类排为 2×2。
- 六张故事海报，包含网页图片、单张 PDF 和合订 PDF。
- 销售演示及本地生成的沟通清单。

## 主要文件

| 文件 | 用途 |
| --- | --- |
| `index.html` | 官网首页与业务现场入口 |
| `styles.css`、`app.js` | 官网样式及交互 |
| `business-scenes.css`、`business-scenes.js` | 四类业务痛点图片切换 |
| `assets/pain-*.png` | 四张蓝白业务场景概念图 |
| `ai-value.css` | 为什么采用专项 AI 与规则执行 |
| `story.html`、`story.css`、`story.js` | 故事海报展厅 |
| `assets/` | 品牌标识、展示图片及 PDF |

## 本地预览

在仓库目录运行：

```bash
python3 -m http.server 8080
```

然后访问 `http://localhost:8080/`。所有资源使用相对路径，也兼容 GitHub Pages 项目路径。

## 发布

GitHub Pages 从 `main` 分支的根目录发布。`.nojekyll` 保留原始静态文件；推送更新后会自动重新部署。

页面不要求访问者登录。沟通清单仅在当前浏览器生成，不上传或自动发送企业信息。

## 内容说明

业务痛点图片为概念示意；网页中的编号、数量、金额为示例数据，不表示真实客户数据或确定的问题成因。服务介绍不构成对审计结论或 IPO 结果的承诺。品牌、文案与图片的权利归各权利人所有。
