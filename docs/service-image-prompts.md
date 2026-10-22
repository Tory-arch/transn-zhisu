# 传神智溯 · 服务业务插图

生成方式：内置 imagegen。四个业务分别独立生成；工厂图追加一次构图修正，完整纳入右侧输送段。风格参考仅用于材质、摄影与配色，未修改既有认可素材。PNG 保留生成原图；WebP 仅通过 Pillow 格式转换（quality=93，method=6），未裁切或重绘。

参考素材：`assets/material-discrepancy.png`、`assets/pain-recipe.png`。

规格：1536 × 1024，3:2 横图；无文字、数字、品牌或水印，问询图仅有问号符号。

## 验收说明

| 文件 | 业务叙事 | 视觉验收 |
| --- | --- | --- |
| `service-check` | 对应台账定位疑点 | 蓝色放大镜覆盖长短不一的琥珀差异行，旁边单页问题报告保留三处标记；没有全修复暗示。 |
| `service-governance` | 三阶段数据治理与成本追溯 | 原料、半成品、成品分别连到台账，琥珀待核对项另放；没有利润或全部通过符号。 |
| `service-inquiry` | 从问题寻找问询依据 | 提问及变化柱图经三份来源/计算页连到打开的证据文件夹；抽象标签不含数字文字。 |
| `case-factory` | 多层加工项目的复杂度示意 | 阶梯工厂与原料、加工、成品层级清晰，蓝线连到记录页；右侧输送段已完整纳入。属于概念示意，不是客户实际工厂照片。 |

四张保持同一雾白、拉丝铝、钴蓝与柔光摄影语言，主体叙事各自不同。海报应按完整 3:2 比例显示，避免另行裁切重要物体。

## 最终提示词

### service-check · 初始生成

```text
Use case: ads-marketing. Create ONE original high-end 3D business illustration for an enterprise IPO data-service sales poster. The two input images are STYLE REFERENCES ONLY: keep their restrained studio product-photography language, frosted white paper and ceramic, brushed aluminum, saturated cobalt-blue accents, a very small amount of amber reserved for unresolved discrepancies, pale icy-blue background, soft broad daylight, subtle realistic shadows, precise tangible geometry. Do not copy their A/B lettering or their specific objects. Landscape 3:2 canvas, 1536×1024 if available. Fill the image with a few large readable objects and keep an 8% safe margin around them; no large empty headline space. Sophisticated physical objects, not a flat infographic or UI screen. No people, robots, brains, neon, magical glow, brand marks, watermarks, Chinese characters, words, letters or numeric digits. Any document markings must be abstract blue lines and bars only.
PRIMARY STORY: Enterprise data health check: locate a specific discrepancy, without implying that everything is already fixed. Two large corresponding physical purchasing/receiving ledger pages sit side by side on a low brushed aluminum desk, slightly inclined toward the camera so their rows are clearly visible. They have the same small set of cobalt blue horizontal row bars aligned row-for-row. In exactly one corresponding row, show an unmistakable amber mismatch: one amber bar is visibly shorter than its counterpart. A beautifully made cobalt-blue magnifying glass rests over this exact pair of discrepant rows and visibly magnifies the amber difference; the lens must be clear, not opaque. To the side and slightly in front, a single smaller neatly extracted issue-report sheet has two or three small amber square markers among blue abstract row lines. Ledger pair, magnifying glass and amber discrepancy are the three clear large visual subjects. Close three-quarter product camera. No green checkmarks, no all-clear stamps, no automatic repair or profit imagery.
```

### service-governance · 初始生成

```text
Use case: ads-marketing. Create ONE original high-end 3D business illustration for an enterprise IPO data-service sales poster. The two input images are STYLE REFERENCES ONLY: keep their restrained studio product-photography language, frosted white paper and ceramic, brushed aluminum, saturated cobalt-blue accents, a very small amount of amber reserved for unresolved discrepancies, pale icy-blue background, soft broad daylight, subtle realistic shadows, precise tangible geometry. Do not copy their A/B lettering or their specific objects. Landscape 3:2 canvas, 1536×1024 if available. Fill the image with a few large readable objects and keep an 8% safe margin around them; no large empty headline space. Sophisticated physical objects, not a flat infographic or UI screen. No people, robots, brains, neon, magical glow, brand marks, watermarks, Chinese characters, words, letters or numeric digits. Any document markings must be abstract blue lines and bars only.
PRIMARY STORY: Historical data governance as traceable reconstruction of production cost. One continuous minimal industrial tabletop has exactly three substantial machining stages from LEFT to RIGHT: a raw brushed-metal billet, a partially machined component, and a finished precise metal part with cobalt-blue detail. Place each on its own small white ceramic tray or short clean brushed aluminum roller bed. Make the physical progression obvious, using a consistent recognizable component family. In the FOREGROUND a large orderly white cost-ledger sheet contains abstract blue rows. Three thin crisp cobalt-blue non-glowing lines physically connect each material stage to a different clear row on this ledger, making each cost record's source visible. The lines form a coherent continuous evidence path; no arbitrary tangled cables. A separate small white note with ONE amber square sits at the far edge, visibly set aside as an unresolved item. Three production objects plus the ledger are the dominant subjects. Calm three-quarter product photography, no large machine complex. No cash, rising profit charts, checkmarks or all-pass symbols. The central story is provenance, not miraculous success.
```

### service-inquiry · 初始生成

```text
Use case: ads-marketing. Create ONE original high-end 3D business illustration for an enterprise IPO data-service sales poster. The two input images are STYLE REFERENCES ONLY: keep their restrained studio product-photography language, frosted white paper and ceramic, brushed aluminum, saturated cobalt-blue accents, a very small amount of amber reserved for unresolved discrepancies, pale icy-blue background, soft broad daylight, subtle realistic shadows, precise tangible geometry. Do not copy their A/B lettering or their specific objects. Landscape 3:2 canvas, 1536×1024 if available. Fill the image with a few large readable objects and keep an 8% safe margin around them; no large empty headline space. Sophisticated physical objects, not a flat infographic or UI screen. No people, robots, brains, neon, magical glow, brand marks, watermarks, Chinese characters, words, letters or numeric digits. Any document markings must be abstract blue lines and bars only.
PRIMARY STORY: Responding to a data question by tracing its evidence. Compose a simple clear left-to-right physical evidence chain with only a few large readable groups. LEFT: one upright white question sheet with a single large cobalt-blue QUESTION MARK symbol (the only permitted character), beside a small simple three-bar blue gross-margin-change chart with visibly differing heights but NO axes labels, numbers or values. CENTER: exactly three white source/calculation pages, slightly fanned, each with different clean abstract blue ledger rows and one small solid blue index tab without letters or digits. Thin cobalt-blue non-glowing lines visibly lead from the question through these source pages. RIGHT: a large neatly OPEN white evidence folder with a cobalt-blue inner edge, containing several orderly source pages with solid blue index tabs, again no writing or numbers. The connecting lines terminate inside the folder. Keep each group distinct with natural breathing room, readable at a glance. Gentle three-quarter front view, matching the reference material and light. This is a question traced to supporting records, not an AI writing a final answer. No giant paragraph, no chat bubbles, no robotic assistant, no tickmarks or verdict stamps.
```

### case-factory · 初始生成

```text
Use case: ads-marketing. Create ONE original high-end 3D business illustration for an enterprise IPO data-service sales poster. The two input images are STYLE REFERENCES ONLY: keep their restrained studio product-photography language, frosted white paper and ceramic, brushed aluminum, saturated cobalt-blue accents, a very small amount of amber reserved for unresolved discrepancies, pale icy-blue background, soft broad daylight, subtle realistic shadows, precise tangible geometry. Do not copy their A/B lettering or their specific objects. Landscape 3:2 canvas, 1536×1024 if available. Fill the image with a few large readable objects and keep an 8% safe margin around them; no large empty headline space. Sophisticated physical objects, not a flat infographic or UI screen. No people, robots, brains, neon, magical glow, brand marks, watermarks, Chinese characters, words, letters or numeric digits. Any document markings must be abstract blue lines and bars only.
PRIMARY STORY: Illustrative complexity of a delivered multilayer manufacturing data-governance project, not a photograph of a real customer factory. A refined isometric miniature production workshop on a white CERAMIC STEPPED platform, viewed from a wider slightly top-down three-quarter angle. Three clear terraces hold a few substantial workstations: raw brushed-metal stock on the first, an intermediate machined part on the second, a finished precise component with cobalt-blue detail on the third. Use a small number of readable short conveyors/transfer paths linking the terraces; show clear spatial processing depth without filling the image with tiny meaningless machines. Below and in front of the stepped platform sits one orderly stack of large white record pages, with the top few abstract blue ledger rows clearly visible. Thin non-glowing cobalt-blue lines connect each workstation to distinct record rows, expressing that every adjustment has a traceable origin. Keep a few dominant objects, strong hierarchy, clean silhouette, saturated blue restrained to rails/components and records. Wide isometric architecture-like product photography rather than the flatter single-table composition of a production line. No actual customer logos, no case statistics, no numbers or text, no smoke, no people, no dashboards, no generic cityscape.
```

### case-factory · 最终构图修正

输入为该图初次生成版本；只调整取景，不改业务内容。

```text
Edit this image only to correct framing. Preserve the exact same stepped miniature factory, machinery, materials, blue routes to the paper ledger, lighting, camera direction, and business story. Pull the camera back enough so the FULL rightmost conveyor including its end and ALL outer edges of the factory platform and foreground paper stack are visible inside the frame, with a minimum 8 percent pale icy-blue background margin at every edge. The current rightmost conveyor is clipped by the frame; fully include it. Keep the finished image LANDSCAPE 3:2, 1536x1024. Do not add or remove any workstation, do not change the three production stages, do not introduce text, numbers, logos, watermarks or new objects. Do not shift into a distant shot; only add the safe breathing margin needed to fit the full existing scene.
```

## Manifest

```json
{
  "generator": "built-in imagegen",
  "webp_conversion": "Pillow, RGB, quality=93, method=6",
  "review": "visual inspection completed",
  "files": [
    {
      "name": "service-check",
      "width": 1536,
      "height": 1024,
      "aspect_ratio": "3:2",
      "assets": [
        {
          "path": "assets/service-check.png",
          "bytes": 2219888,
          "sha256": "9a5b0f8f27ec9787600f87916bee86cb47e738068981f87f0d58e736b4ffec97"
        },
        {
          "path": "assets/service-check.webp",
          "bytes": 253324,
          "sha256": "d499df12c20e3f70a988c3389e1e22f9c01f2f0299cfaaff18f9490c8af7587f"
        }
      ],
      "generation_file": "exec-de92000f-4a78-4dfd-9a6e-51397194ee2a.png",
      "initial_generation_calls": 1,
      "targeted_revision_calls": 0
    },
    {
      "name": "service-governance",
      "width": 1536,
      "height": 1024,
      "aspect_ratio": "3:2",
      "assets": [
        {
          "path": "assets/service-governance.png",
          "bytes": 2247802,
          "sha256": "9017e737f1e85a00cfe8f5e532553745b9ceabfc30067a61261898180ba01eb6"
        },
        {
          "path": "assets/service-governance.webp",
          "bytes": 239512,
          "sha256": "f886b64b802c839bda553823ec1c8f8b3887604f6e5d586a89610c6a2c199a3e"
        }
      ],
      "generation_file": "exec-029f3331-2ec0-4a06-a042-904c28286b38.png",
      "initial_generation_calls": 1,
      "targeted_revision_calls": 0
    },
    {
      "name": "service-inquiry",
      "width": 1536,
      "height": 1024,
      "aspect_ratio": "3:2",
      "assets": [
        {
          "path": "assets/service-inquiry.png",
          "bytes": 1804864,
          "sha256": "8e77b2c27b966f9ab9ae9deeee9843679f1b0a278510b36841ec4c255e888066"
        },
        {
          "path": "assets/service-inquiry.webp",
          "bytes": 131576,
          "sha256": "e12a638bcb5b205e752fec5f4c89703a28fa5696bd2572e56cfa365d4514bf82"
        }
      ],
      "generation_file": "exec-014ea9b5-828b-45ae-b5e0-f91a40a15d0b.png",
      "initial_generation_calls": 1,
      "targeted_revision_calls": 0
    },
    {
      "name": "case-factory",
      "width": 1536,
      "height": 1024,
      "aspect_ratio": "3:2",
      "assets": [
        {
          "path": "assets/case-factory.png",
          "bytes": 2021105,
          "sha256": "6288394a0887ed3d1c77710a0fce196eff4304930e869fd8cd8676529fd83131"
        },
        {
          "path": "assets/case-factory.webp",
          "bytes": 189438,
          "sha256": "32add53c343427af482457787a716dc4d9b93878ae800565df62d9851bab7487"
        }
      ],
      "generation_file": "exec-5c5e6c8c-67cf-4ba4-8195-a84a5d3f320f.png",
      "initial_generation_calls": 1,
      "targeted_revision_calls": 1
    }
  ]
}
```
