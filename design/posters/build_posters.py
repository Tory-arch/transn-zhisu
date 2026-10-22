#!/usr/bin/env python3
"""Build the editable Transn / Zhisu poster set without changing website assets by default.

Edit the copy, coordinates, and drawing instructions in build_pdfs().
Requires Python 3.10+; see README.md for fonts, rendering, and explicit site sync.
"""
from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from functools import partial
from io import BytesIO
from urllib.parse import urlsplit

# This file lives at <repository>/design/posters/build_posters.py.
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
DEFAULT_OUTPUT = ROOT / "design" / "posters" / "build"
DEFAULT_SITE_URL = "https://tory-arch.github.io/transn-zhisu/"
VERSION = 6
W, H = 1120, 1584
BLUE='#2468FF'; INK='#132448'; MUTED='#687A96'; LIGHT='#EFF5FF'; LINE='#DCE6F5'; AMBER='#E9A339'; WHITE='#FFFFFF'


class BuildError(Exception):
    """An actionable configuration or build failure."""


def load_dependencies():
    global canvas, pdfmetrics, TTFont, HexColor, qr, Drawing, renderPDF, ImageReader
    global Image, PdfReader, PdfWriter
    try:
        from reportlab.pdfgen import canvas
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import HexColor
        from reportlab.graphics.barcode import qr
        from reportlab.graphics.shapes import Drawing
        from reportlab.graphics import renderPDF
        from reportlab.lib.utils import ImageReader
        from PIL import Image
        from pypdf import PdfReader, PdfWriter
    except ImportError as exc:
        raise BuildError(
            "缺少依赖，请在当前 Python 环境运行："
            "python -m pip install -r design/posters/requirements.txt"
        ) from exc


def repository_relative(path):
    """Serialize paths without leaking checkout- or machine-specific absolute paths."""
    return Path(os.path.relpath(Path(path).resolve(), ROOT)).as_posix()


def resolve_font(path, index, weight):
    if path:
        font_path = Path(path).expanduser()
        if not font_path.is_absolute():
            font_path = ROOT / font_path
        font_index = 0 if index is None else index
    else:
        name = "STHeiti Light.ttc" if weight == "regular" else "STHeiti Medium.ttc"
        font_path = Path("/System/Library/Fonts") / name
        font_index = 1 if index is None else index
        if not font_path.is_file():
            raise BuildError(
                f"未找到中文 {weight} 字体。请用 --font-{weight} 指定支持中文的 TTF 或 "
                f"TrueType TTC 字体；TTC 可用 --font-{weight}-index 指定子字体索引（从 0 开始）。"
            )
    if font_index < 0:
        raise BuildError(f"--font-{weight}-index 必须大于或等于 0。")
    if not font_path.is_file():
        raise BuildError(f"--font-{weight} 指定的字体文件不存在：{font_path.name}")
    return font_path.resolve(), font_index


def register_fonts(regular, bold):
    # Validate all Chinese characters in the editable drawing code before producing files.
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    drawing_node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "build_pdfs")
    required = {ord(ch) for node in ast.walk(drawing_node)
                if isinstance(node, ast.Constant) and isinstance(node.value, str)
                for ch in node.value if "\u4e00" <= ch <= "\u9fff"}
    for name, (path, index) in (("C", regular), ("B", bold), ("E", regular), ("EB", bold)):
        try:
            font = TTFont(name, str(path), subfontIndex=index)
            if name in ("C", "B"):
                missing = sorted(required - set(font.face.charToGlyph))
                if missing:
                    sample = "".join(chr(code) for code in missing[:12])
                    raise BuildError(f"字体 {path.name} 缺少海报需要的中文字形（如：{sample}）。请改用完整中文字体。")
            pdfmetrics.registerFont(font)
        except BuildError:
            raise
        except Exception as exc:
            raise BuildError(
                f"无法加载字体 {path.name}（TTC index={index}）。"
                "请检查索引，并使用 ReportLab 支持的 TrueType 字体；CFF/OTF 字体可能不受支持。"
            ) from exc


def validate_assets():
    required = ["transn-logo.png", "data-sculpture.webp", "pain-identity.png",
                "pain-recipe.png", "pain-price.png", "pain-stock.png"]
    missing = [f"assets/{name}" for name in required if not (ASSETS / name).is_file()]
    if missing:
        raise BuildError("缺少设计图片，请保留仓库 assets 目录：" + ", ".join(missing))


def find_renderer(command):
    renderer = shutil.which(command)
    if not renderer:
        raise BuildError(
            "--render 需要 Poppler 的 pdftoppm。请先安装 Poppler，"
            "或用 --pdftoppm 指定可执行文件；仅生成 PDF 时不需要此工具。"
        )
    return renderer


class Poster:
    def __init__(self,n,topic,filename,*,output_dir,assets_dir):
        self.assets_dir=assets_dir; self.n=n; self.path=output_dir/f'{filename}.pdf'; self.c=canvas.Canvas(str(self.path),pagesize=(841.8898,1190.5512))
        self.c.setTitle(f'传神智溯 · {topic}');self.c.setAuthor('传神 · 智溯')
        self.c.scale(841.8898/W,1190.5512/H)
        self.rect(0,0,W,H,WHITE)
        self.c.drawImage(str(self.assets_dir/'transn-logo.png'),72,H-94,width=181,height=31,mask='auto')
        self.line(278,60,278,95,LINE)
        self.text('智溯',300,62,32,INK,'B')
        self.text(f'{topic}  /  {n:02d}' if n else topic,1048,72,20,MUTED,'C',align='right')
        self.line(72,128,1048,128,LINE)
    def text(self,s,x,y,size=24,color=INK,font='C',align='left'):
        self.c.setFillColor(HexColor(color));self.c.setFont(font,size)
        # y is top of the text em box. Baseline uses font-independent optical alignment.
        if align=='right': self.c.drawRightString(x,H-y-size*.84,s)
        elif align=='center': self.c.drawCentredString(x,H-y-size*.84,s)
        else: self.c.drawString(x,H-y-size*.84,s)
    def lines(self,ss,x,y,size=24,color=INK,font='C',leading=None):
        for i,s in enumerate(ss):self.text(s,x,y+i*(leading or size*1.5),size,color,font)
    def rect(self,x,y,w,h,color,r=0,stroke=None):
        self.c.setFillColor(HexColor(color));self.c.setStrokeColor(HexColor(stroke or color));self.c.setLineWidth(1)
        if r:self.c.roundRect(x,H-y-h,w,h,r,fill=1,stroke=bool(stroke))
        else:self.c.rect(x,H-y-h,w,h,fill=1,stroke=bool(stroke))
    def line(self,x1,y1,x2,y2,color=LINE,width=1,dash=None):
        self.c.saveState();self.c.setStrokeColor(HexColor(color));self.c.setLineWidth(width)
        if dash:self.c.setDash(dash)
        self.c.line(x1,H-y1,x2,H-y2);self.c.restoreState()
    def circle(self,x,y,r,color,stroke=None):
        self.c.setFillColor(HexColor(color));self.c.setStrokeColor(HexColor(stroke or color));self.c.setLineWidth(1)
        self.c.circle(x,H-y,r,fill=1,stroke=bool(stroke))
    def arrow(self,x1,y,x2,color=BLUE,width=2):
        self.line(x1,y,x2,y,color,width);self.line(x2-7,y-6,x2,y,color,width);self.line(x2-7,y+6,x2,y,color,width)
    def title(self,lines,sub=None):
        self.lines(lines,72,189,70,INK,'B',86)
        if sub:self.lines(sub,72,394,25,MUTED,leading=38)
    def footer(self,note='IPO 成本数据还原专项 · 传神智溯'):
        self.line(72,1491,1048,1491,LINE)
        self.text(note,72,1515,17,MUTED)
        self.text(f'{self.n:02d} / 07' if self.n else 'SERVICE OVERVIEW',1048,1516,16,MUTED,'E',align='right')
    def image(self,name,x,y,w,h):
        # Preserve dimensions/content while using efficient JPEG encoding inside PDFs.
        encoded=BytesIO()
        Image.open(self.assets_dir/name).convert('RGB').save(encoded,'JPEG',quality=95,optimize=True)
        encoded.seek(0)
        self.c.drawImage(ImageReader(encoded),x,H-y-h,width=w,height=h)
    def finish(self):
        if self.n:self.footer()
        self.c.showPage();self.c.save();return self.path

def make_qr(p,x,y,size,url):
    widget=qr.QrCodeWidget(url,barFillColor=HexColor(INK),barBorder=0)
    bx,by,bw,bh=widget.getBounds();d=Drawing(size,size,transform=[size/(bw-bx),0,0,size/(bh-by),0,0]);d.add(widget)
    renderPDF.draw(d,p.c,x,H-y-size)

def build_pdfs(output_dir, site_url):
    """Editable copy and 1120 × 1584 layout; exported PDF pages remain A3 portrait."""
    output_dir.mkdir(parents=True, exist_ok=True)
    make_poster = partial(Poster, output_dir=output_dir, assets_dir=ASSETS)
    # 01 — Four recognizable contradictions.
    p=make_poster(1,'业务难题','01-业务难题')
    p.title(['数据都在，','成本为何对不上？'],['问题藏在记录之间。经过多层加工，差异会一路传递。'])
    items=[('identity','同一物料，多套编号','采购、生产、财务，记录接不上。'),('recipe','领料记录，偏离配方','配方用量与净领料，存在待核对差异。'),('price','入库缺价，成本断层','上游缺少单价，后续成本难接续。'),('stock','手工补录，库存不符','历史单据与库存，需要重新梳理。')]
    for i,(key,title,desc) in enumerate(items):
        x=72+(i%2)*512;y=481+(i//2)*430
        p.image(f'pain-{key}.png',x,y,464,309.33)
        p.text(f'0{i+1}',x,y+326,18,BLUE,'EB');p.text(title,x+42,y+321,26,INK,'B')
        p.text(desc,x,y+367,21,MUTED)
    p.line(72,1340,1048,1340,LINE)
    p.text('需要还原的，是三年逐品号的进、耗、存与成本。',72,1371,28,BLUE,'B')
    p.text('图片为业务场景示意，非真实客户数据。',72,1430,18,MUTED)
    paths=[p.finish()]

    # 02 — Why AI: one chain multiplied by scope and time.
    p=make_poster(2,'为什么用 AI','02-为什么用AI')
    p.title(['一笔成本，','要追多远？'],['核清一笔，要跨多张单据；还原全局，要贯穿三年。'])
    p.text('一条成本链，要核对这些环节',72,503,24,BLUE,'B')
    nodes=['采购','领退料','工单','半成品','委外','入库']
    for i,label in enumerate(nodes):
        x=72+i*167
        p.rect(x,563,141,155,LIGHT,12)
        p.text(f'0{i+1}',x+20,586,17,BLUE,'EB')
        p.text(label,x+20,632,26,INK,'B')
        if i<5:p.arrow(x+146,640,x+163)
    p.text('同样的追查，在不同品号、不同加工层级重复发生。',72,754,25,MUTED)
    for row in range(3):
        y=835+row*92
        p.text(f'第 {row+1} 年',72,y+14,24,INK,'B')
        p.line(222,y+28,1048,y+28,LINE,2)
        for col in range(13):
            x=233+col*66
            p.circle(x,y+28,10,BLUE if col in [2+row,6+row,11-row] else '#C7D8F6')
            if col in [2+row,6+row,11-row]:p.circle(x,y+28,4,WHITE)
    p.text('示意：三年、多品号、多层级的关联追查',72,1120,18,MUTED)
    p.rect(72,1200,976,230,BLUE,18)
    p.lines(['让 AI 承接海量追查，','让专家聚焦关键判断。'],108,1234,42,WHITE,'B',57)
    p.text('AI 梳理线索与待确认事项，专业人员确认关键事实与口径。',108,1373,22,'#DCE7FF')
    paths.append(p.finish())

    # 03 — One job per specialized agent, not a mysterious black box.
    p=make_poster(3,'专项智能体','03-专项智能体')
    p.title(['一个难题，','一个专项智能体。'])
    p.text('100',72,401,184,BLUE,'EB');p.text('+',383,425,105,BLUE,'E')
    p.text('专项智能体',540,455,42,INK,'B')
    p.lines(['完整清洗服务调用，','按企业数据问题配置。'],542,520,24,MUTED,leading=36)
    jobs=[('01','编号关联','梳理跨系统编号对应线索','名称 / 规格 / 单位'),('02','配方核对','识别投入与领退料的矛盾','配方 / 领料 / 退料'),('03','工单识别','查找加工环节中的记录断点','工单 / 半成品 / 委外'),('04','缺价定位','追查缺失单价的来源依据','入库 / 采购 / 计价')]
    for i,(n,title,body,meta) in enumerate(jobs):
        x=72+i%2*512;y=687+i//2*232
        p.line(x,y,x+464,y,LINE,2);p.text(n,x,y+24,18,BLUE,'EB')
        p.text(title,x+46,y+18,34,INK,'B');p.text(body,x,y+86,25,MUTED);p.text(meta,x,y+137,20,BLUE)
    p.rect(72,1198,976,230,LIGHT,18)
    for i,(title,desc) in enumerate([('AI 找线索',['识别问题','形成待确认项']),('规则做计算',['依据确认后','由程序执行']),('专家作判断',['确认事实','明确口径与边界'])]):
        x=107+i*313
        if i:p.line(x-20,1241,x-20,1383,'#CFDDF4')
        p.text(title,x,1245,29,INK,'B');p.lines(desc,x,1304,23,MUTED,leading=35)
    paths.append(p.finish())

    # 04 — Clearly separate human confirmation, execution, and rerun.
    p=make_poster(4,'规则重算','04-规则重算')
    p.title(['规则变了，','三年统一重算。'],['把确认后的处理口径写成规则，沿加工层级执行。'])
    p.rect(72,506,976,173,LIGHT,16)
    p.text('01',102,544,20,BLUE,'EB');p.text('确认关键依据与处理规则',164,534,34,INK,'B')
    p.text('由企业及相关专业人员确认事实与口径。',164,594,24,MUTED)
    p.line(560,680,560,738,BLUE,2)
    p.circle(560,745,7,BLUE)
    p.text('02  程序统一执行',72,747,26,BLUE,'B')
    for i in range(3):
        x=72+i*335
        p.rect(x,817,306,238,BLUE,16)
        p.text(f'第 {i+1} 年',x+28,849,35,WHITE,'B')
        p.line(x+28,914,x+278,914,'#75A0FF')
        p.text('进 · 耗 · 存',x+28,939,27,WHITE,'B')
        p.text('逐品号成本明细',x+28,994,22,'#DDE8FF')
    p.line(225,1094,895,1094,BLUE,2);p.line(225,1057,225,1094,BLUE,2);p.line(895,1057,895,1094,BLUE,2);p.line(560,1057,560,1127,BLUE,2)
    p.text('规则调整后，可重新执行完整三年数据。',560,1155,29,BLUE,'B',align='center')
    p.line(72,1240,1048,1240,LINE)
    p.text('03',72,1280,20,BLUE,'EB');p.text('每次调整，都留下依据。',126,1269,34,INK,'B')
    p.lines(['保留调整前后值、执行规则与相关智能体记录。','减少逐表修改和重复核对，让重算过程可追溯。'],126,1330,25,MUTED,leading=39)
    paths.append(p.finish())

    # 05 — Five concrete deliverables as an evidence ledger.
    p=make_poster(5,'可复核交付','05-可复核交付')
    p.title(['交付数字，','也交付依据。'],['让项目组能对照、能追问，也能复核。'])
    deliver=[('三年逐品号明细','进、耗、存与成本，沿加工层级还原。'),('数据来源说明','区分直接取数、规则还原与无法解释的残差。'),('调整留痕台账','调整前后值、规则与相关智能体记录。'),('残差清单','未能解释的差额如实列示，附待确认事项。'),('可重跑规则集','规则变化后，支持完整三年数据重新执行。')]
    for i,(title,desc) in enumerate(deliver):
        y=515+i*153
        p.line(72,y,1048,y,LINE)
        p.text(f'0{i+1}',72,y+30,38,BLUE,'EB');p.text(title,171,y+26,35,INK,'B');p.text(desc,171,y+87,24,MUTED)
    p.rect(72,1323,976,106,LIGHT,12)
    p.text('每一项结果，都有对应的核对入口。',560,1357,32,BLUE,'B',align='center')
    paths.append(p.finish())

    # 06 — Accurate anonymous case, no invented implementation timeline.
    p=make_poster(6,'客户实践','06-客户实践')
    p.title(['走出数据困境，','完成项目交付。'],['一家经券商推荐的多层加工拟 IPO 制造企业。'])
    p.text('原有困境',72,511,22,MUTED,'B')
    p.text('1',72,558,148,INK,'EB');p.text('年',171,643,35,INK,'B')
    p.text('ERP 方案尝试后，仍未完成',320,584,34,INK,'B')
    p.lines(['多层加工环节交织，','成本数据还原持续受阻。'],320,648,25,MUTED,leading=39)
    p.line(72,763,1048,763,LINE)
    p.text('智溯介入',72,805,22,BLUE,'B')
    steps=[('本地部署','在企业内网处理已有数据'),('专项识别','核对配方、工单与编号关联'),('规则还原','依据确认后补价，接续多级成本')]
    for i,(title,desc) in enumerate(steps):
        y=868+i*108
        p.circle(91,y+19,18,LIGHT);p.text(str(i+1),91,y+8,21,BLUE,'EB',align='center')
        if i<2:p.line(91,y+39,91,y+88,LINE,2)
        p.text(title,140,y,30,INK,'B');p.text(desc,372,y+5,25,MUTED)
    p.rect(72,1236,976,191,BLUE,16)
    p.text('完成数据还原交付',108,1272,43,WHITE,'B')
    p.text('并获得客户认可。',108,1345,27,'#DDE8FF')
    p.text('匿名案例依据现有服务材料整理，不代表审计或 IPO 结果。',72,1454,17,MUTED)
    paths.append(p.finish())

    # 07 — Useful preparation, real public destination.
    p=make_poster(7,'开始合作','07-开始合作')
    p.title(['从现有数据，','开始下一步。'],['先梳理现状，再评估范围与实施安排。'])
    prep=[('系统与数据范围','现有 ERP、数据年份、可提供的单据'),('品号与加工层级','原料、半成品、委外与产成品关系'),('已知问题与整改历史','编号、配方、缺价、库存及已有成果'),('交付节点与确认人','项目时间要求、业务与财务对接人')]
    for i,(title,desc) in enumerate(prep):
        y=515+i*147
        p.line(72,y,1048,y,LINE)
        p.rect(72,y+35,30,30,WHITE,5,LINE)
        p.text(title,136,y+24,34,INK,'B');p.text(desc,136,y+82,24,MUTED)
    p.rect(72,1156,976,272,LIGHT,16)
    p.text('了解现状  →  联合评估  →  约定范围',104,1190,28,BLUE,'B')
    p.lines(['企业主要提供已有数据，','配合确认关键问题。'],104,1254,28,INK,'B',43)
    p.text('数据与模型在企业内网运行。',104,1368,22,MUTED)
    make_qr(p,856,1211,150,site_url)
    p.text('扫码查看官网',931,1377,19,MUTED,align='center')
    paths.append(p.finish())

    combined=output_dir/'传神智溯-七张故事海报-AI价值版.pdf'
    writer=PdfWriter()
    for path in paths: writer.append(PdfReader(path))
    with combined.open('wb') as f: writer.write(f)

    # Service overview: refresh homepage download to carry the same AI narrative.
    p=make_poster(0,'服务总览','传神智溯-一页服务介绍-AI价值版')
    p.title(['把历史数据，','还原成可复核的成本。'],['智溯 · AI 数据治理服务 / IPO 成本数据还原专项'])
    p.image('data-sculpture.webp',580,500,468,351)
    p.text('为什么用 AI',72,516,22,BLUE,'B')
    p.lines(['跨单据找线索，','跨层级追成本。'],72,569,42,INK,'B',57)
    p.lines(['专项智能体识别问题，','确认后的规则由程序执行，','让专家聚焦关键事实与口径。'],72,716,25,MUTED,leading=39)
    p.line(72,886,1048,886,LINE)
    for i,(v,label,small) in enumerate([('100+','专项智能体','按企业数据问题配置'),('3年','统一还原与重算','逐品号进耗存与成本'),('本地','部署与运行','数据与模型在企业内网')]):
        x=72+i*335
        p.text(v,x,932,65,BLUE,'EB' if i==0 else 'B');p.text(label,x,1022,27,INK,'B');p.text(small,x,1070,20,MUTED)
    p.line(72,1132,1048,1132,LINE)
    p.text('交付数字，也交付依据。',72,1174,34,INK,'B')
    p.lines(['三年逐品号明细 · 数据来源说明 · 调整留痕台账','残差清单 · 可重跑规则集'],72,1236,25,MUTED,leading=40)
    p.rect(72,1359,976,73,LIGHT,10)
    p.text('面向拟 IPO 制造业企业及券商项目组',98,1382,26,BLUE,'B')
    make_qr(p,888,1183,133,site_url)
    p.text('扫码了解服务',954,1330,18,MUTED,align='center')
    p.footer('服务范围与实施安排以项目方案为准。')
    overview=p.finish()

    return paths, combined, overview


def render_preview(pdf_path, renderer):
    prefix = pdf_path.with_suffix("")
    command = [renderer, "-f", "1", "-singlefile", "-scale-to-x", str(W),
               "-scale-to-y", str(H), "-png", str(pdf_path), str(prefix)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise BuildError(f"pdftoppm 渲染失败：{pdf_path.name}。请检查 Poppler 安装及输入 PDF。") from exc
    png = prefix.with_suffix(".png")
    webp = prefix.with_suffix(".webp")
    with Image.open(png) as image:
        if image.size != (W, H):
            raise BuildError(f"预览尺寸不正确：{png.name}，预期 {W}×{H}。")
        image.convert("RGB").save(webp, "WEBP", quality=92, method=6)
    return {"png": repository_relative(png), "webp": repository_relative(webp)}


def sync_site(paths, combined, overview, previews):
    """The only function allowed to write into assets; called solely by --sync-site."""
    destinations = []
    pairs = [(path, ASSETS / "posters" / f"{i:02d}.pdf") for i, path in enumerate(paths, 1)]
    pairs += [(combined, ASSETS / "posters" / "zhisu-story.pdf"),
              (overview, ASSETS / "zhisu-poster.pdf")]
    if previews:
        pairs += [(path.with_suffix(".webp"), ASSETS / "posters" / f"{i:02d}.webp")
                  for i, path in enumerate(paths, 1)]
    for source, destination in pairs:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        destinations.append(repository_relative(destination))
    return destinations


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="生成传神智溯七张海报、合集及一页服务介绍。默认不修改网站资产。")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT.relative_to(ROOT)),
                        help="生成目录，默认 design/posters/build；相对路径以仓库根目录为准。")
    parser.add_argument("--font-regular", help="常规中文 TTF/TTC 字体路径；未指定时尝试 macOS STHeiti Light。")
    parser.add_argument("--font-bold", help="粗体中文 TTF/TTC 字体路径；未指定时尝试 macOS STHeiti Medium。")
    parser.add_argument("--font-regular-index", "--font-regular-ttc-index", dest="font_regular_index", type=int,
                        help="常规 TTC 子字体索引，从 0 开始；显式字体默认 0，自动发现的 STHeiti 默认 1。")
    parser.add_argument("--font-bold-index", "--font-bold-ttc-index", dest="font_bold_index", type=int,
                        help="粗体 TTC 子字体索引，从 0 开始；显式字体默认 0，自动发现的 STHeiti 默认 1。")
    parser.add_argument("--site-url", default=DEFAULT_SITE_URL, help="第 07 张及服务总览二维码的目标网址。")
    parser.add_argument("--render", action="store_true", help="用 pdftoppm 渲染单张 PDF，生成 1120×1584 PNG/WebP。")
    parser.add_argument("--pdftoppm", default=os.environ.get("PDFTOPPM", "pdftoppm"),
                        help="pdftoppm 的名称或路径，也可设置 PDFTOPPM 环境变量。")
    parser.add_argument("--sync-site", action="store_true", help="显式覆盖网站 PDF；与 --render 同用时也更新七张 WebP。")
    parser.add_argument("--check", action="store_true", help="只检查依赖、图片和字体；不生成、渲染或同步文件。")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        load_dependencies()
        validate_assets()
        regular = resolve_font(args.font_regular, args.font_regular_index, "regular")
        bold = resolve_font(args.font_bold, args.font_bold_index, "bold")
        register_fonts(regular, bold)
        renderer = find_renderer(args.pdftoppm) if args.render else None
        url = urlsplit(args.site_url)
        if url.scheme not in ("http", "https") or not url.netloc:
            raise BuildError("--site-url 必须是完整的 http 或 https 网址。")
        output_dir = Path(args.output_dir).expanduser()
        if not output_dir.is_absolute():
            output_dir = ROOT / output_dir
        output_dir = output_dir.resolve()
        # A custom output directory must not bypass the explicit site-sync boundary.
        if output_dir == ASSETS.resolve() or ASSETS.resolve() in output_dir.parents:
            raise BuildError("--output-dir 不能放在 assets 中；请用 --sync-site 显式同步。")
        fonts = {"regular": {"file": regular[0].name, "ttc_index": regular[1]},
                 "bold": {"file": bold[0].name, "ttc_index": bold[1]}}
        if args.check:
            print(json.dumps({"check": "ok", "output_directory": repository_relative(output_dir),
                              "fonts": fonts, "renderer_checked": bool(renderer)}, ensure_ascii=False, indent=2))
            return 0
        paths, combined, overview = build_pdfs(output_dir, args.site_url)
        previews = {path: render_preview(path, renderer) for path in [*paths, overview]} if renderer else {}
        manifest = {"version": VERSION, "size": "A3 portrait", "preview_size": [W, H],
                    "poster_count": len(paths), "public_url": args.site_url, "fonts": fonts,
                    "posters": [{"number": i, "pdf": repository_relative(path), **previews.get(path, {})}
                                for i, path in enumerate(paths, 1)],
                    "combined": repository_relative(combined),
                    "overview": {"pdf": repository_relative(overview), **previews.get(overview, {})},
                    "content_source": "智溯_IPO数据治理服务_销售一指禅(1).docx",
                    "claims": "100+ refers to a complete cleaning service, configured by data issues. "
                              "Three years is the data scope, not a delivery duration. The anonymous case's "
                              "earlier ERP attempt lasted one year without completion; no AI case duration is claimed.",
                    "site_synced": bool(args.sync_site), "site_files": []}
        if args.sync_site:
            manifest["site_files"] = sync_site(paths, combined, overview, previews)
            if not renderer:
                manifest["warnings"] = ["仅更新了网站 PDF；要同时更新网页 WebP 预览，请加 --render。"]
        manifest_path = output_dir / "manifest.json"
        manifest["manifest"] = repository_relative(manifest_path)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
        return 0
    except BuildError as exc:
        print(f"海报构建失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
