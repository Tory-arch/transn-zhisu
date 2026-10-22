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
VERSION = 8
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
                "pain-recipe.png", "pain-price.png", "pain-stock.png", "material-discrepancy.png"]
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
        self.c.setTitle(f'传神智溯 · {topic}');self.c.setAuthor('传神智溯')
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
    def footer(self,note='IPO 数据服务 · 传神智溯'):
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

    # 01 — Three products, one continuous evidence chain.
    p=make_poster(1,'三产品总览','01-三产品总览')
    p.title(['让数据说得清，','让问询有依据。'],['从辅导期到审核问询，三项服务按需组合。'])
    products=[('01','辅导期早期','数据体检','找到风险，定位问题。','交付 IPO 数据风险体检报告'),
              ('02','申报前','数据治理','还原成本，保留来路。','交付三年逐品号明细、留痕与规则'),
              ('03','审核问询','问询数据响应','逐问拆解，逐层追溯。','交付问询数据证据包')]
    p.line(99,536,99,1150,'#BED0F4',2)
    for i,(num,stage,name,value,delivery) in enumerate(products):
        y=504+i*243
        p.circle(99,y+27,27,BLUE);p.text(num,99,y+15,23,WHITE,'EB','center')
        p.text(stage,151,y+5,20,BLUE,'B')
        p.text(name,151,y+47,43,INK,'B')
        p.text(value,151,y+116,28,INK)
        p.text(delivery,151,y+163,23,MUTED)
        if i<2:p.line(151,y+220,1048,y+220,LINE)
    p.rect(72,1252,976,172,BLUE,18)
    p.text('可单独选择，也可组合推进。',108,1291,36,WHITE,'B')
    p.text('先体检 → 再治理 → 问询响应，按企业当前需要开始。',108,1362,23,'#E0EAFF')
    paths=[p.finish()]

    # 02 — A concrete, falsifiable AI inference loop.
    p=make_poster(2,'为什么用 AI','02-为什么用AI')
    p.text('找到矛盾背后的原因，',72,189,70,INK,'B')
    p.text('用重算验证每个判断。',72,275,70,BLUE,'B')
    p.text('百万行记录，跨年度、多层加工。让追查与验证持续推进。',72,394,25,MUTED)
    p.rect(72,456,976,450,LIGHT,18)
    p.text('从一处用料差异开始',104,492,19,BLUE,'B')
    p.lines(['配方写 A，','车间却领了 B。'],104,548,40,INK,'B',58)
    p.lines(['是录错了、临时替代，','还是编号不同的','同一种物料？'],104,696,23,MUTED,leading=36)
    # Use the approved website image at its original 4:3 aspect ratio.
    p.image('material-discrepancy.png',486,468,546,409.5)
    p.text('配方要求 A',622,878,18,MUTED,'C','center')
    p.text('实际领用 B',895,878,18,MUTED,'C','center')
    p.text('业务示意 · A/B 为示意物料，差异原因待核对',72,925,17,MUTED)
    stages=[('AI 追查','从差异中找线索',['对照工单与配方，','找到 A 缺失、B 多出。']),
            ('AI 推断','提出候选解释',['推断差异成因，','写成有条件的规则。']),
            ('程序校验','让规则接受试算',['重算数量与成本，','检查守恒与约束。']),
            ('AI 修正','用结果反查判断',['反查异常价差，','修正规则再验证。']),
            ('专业确认','确认依据再重算',['人确认关键口径，','程序执行并留痕。'])]
    for i,(role,title,desc) in enumerate(stages):
        x=72+i*199
        p.text(f'0{i+1}',x,986,24,BLUE,'EB')
        p.text(role,x+43,990,18,MUTED)
        if i<4:p.arrow(x+142,1000,x+178,'#AFC7F5',1.5)
        p.text(title,x,1037,23,INK,'B')
        p.lines(desc,x,1083,18,MUTED,leading=31)
    p.rect(72,1191,976,192,LIGHT,18)
    p.text('已交付案例',104,1219,18,BLUE,'B')
    p.text('4,000',104,1258,66,BLUE,'EB')
    p.text('余条 / 年',104+pdfmetrics.stringWidth('4,000','EB',66)+22,1291,20,BLUE)
    p.text('识别的替代用料关系',104,1342,21,INK,'B')
    p.lines(['用成本结果反向检验，','排除不成立的判断，','再修正规则、重新试算。'],596,1229,25,INK,leading=43)
    p.text('AI 推断成因 · 程序验证计算 · 人确认关键依据',72,1412,26,BLUE,'B')
    p.text('数据来自单个已交付治理案例；关键事实与计价依据仍需专业确认。',72,1455,17,MUTED)
    paths.append(p.finish())

    # 03 — Diagnose relationships before choosing remediation.
    p=make_poster(3,'IPO 数据体检','03-数据体检')
    p.title(['先看清风险，','再决定怎么治理。'],['跨系统查勾稽，定位未来可能解释不清的数据。'])
    checks=[('采购 · 入库 · 应付','数量与金额是否一致'),('领料 · BOM · 产量','实际耗用是否匹配配方'),('生产 · 库存','工单与成品入库是否接续'),('库存 · 财务','进耗存是否与总账一致'),('成本 · 收入','毛利波动能否解释'),('主数据','编号与版本是否统一')]
    for i,(title,desc) in enumerate(checks):
        x=72+i%2*512;y=506+i//2*138
        p.line(x,y,x+464,y,LINE,2)
        p.text(f'0{i+1}',x,y+25,18,BLUE,'EB')
        p.text(title,x+43,y+20,27,INK,'B')
        p.text(desc,x+43,y+71,22,MUTED)
    p.text('程序批量检查，AI 逐类归因，区分规则修复与待确认事项。',72,959,24,BLUE,'B')
    p.rect(72,1042,976,386,LIGHT,18)
    p.text('交付 · IPO 数据风险体检报告',108,1081,31,INK,'B')
    results=[('问题定位','系统、年度、品号或单据类型'),('影响范围','风险分级与数据影响规模'),('治理建议','处理建议与工作量评估')]
    for i,(title,desc) in enumerate(results):
        y=1156+i*79
        p.circle(120,y+13,5,BLUE);p.text(title,146,y,26,INK,'B');p.text(desc,355,y+1,23,MUTED)
    paths.append(p.finish())

    # 04 — Quantity conservation before cost allocation, with five deliverables.
    p=make_poster(4,'IPO 数据治理','04-数据治理')
    p.title(['先把数量对齐，','再把金额算清。'],['把互相矛盾的记录，还原成可追溯的三年逐品号明细。'])
    pains=[('identity','同物多码'),('recipe','领料偏离配方'),('price','入库缺价'),('stock','补录与库存不符')]
    for i,(key,title) in enumerate(pains):
        x=72+i*250
        p.image(f'pain-{key}.png',x,500,226,150.67)
        p.text(title,x,674,24,INK,'B')
    for i,(num,title,desc) in enumerate([('01','数量重算','先核对进、耗、存，达到守恒'),('02','金额滚算','锁定数量，再沿加工层级计算成本')]):
        x=72+i*512
        p.rect(x,758,464,164,BLUE if i==0 else LIGHT,16)
        fg=WHITE if i==0 else INK
        p.text(num,x+27,785,19,'#DCE7FF' if i==0 else BLUE,'EB')
        p.text(title,x+79,778,35,fg,'B')
        p.text(desc,x+27,862,22,'#E0EAFF' if i==0 else MUTED)
    p.text('五项交付，保留每一笔数字的来路。',72,984,30,INK,'B')
    deliveries=[('三年逐品号明细','进、耗、存与成本'),('来源说明','直接取数 / 按规则还原 / 待确认残差'),('调整留痕台账','调整前后数值、依据规则与智能体'),('残差清单','无法解释的差额单列，并附待确认事项'),('可重跑规则集','逐条复核，规则变更后三年统一重算')]
    for i,(title,desc) in enumerate(deliveries):
        y=1054+i*72
        p.line(72,y,1048,y,LINE)
        p.text(f'0{i+1}',72,y+22,18,BLUE,'EB');p.text(title,118,y+17,25,INK,'B');p.text(desc,408,y+20,22,MUTED)
    p.text('业务场景图片为示意。无法还原的部分如实单列，不作隐性摊销。',72,1441,17,MUTED)
    paths.append(p.finish())

    # 05 — Natural-language question to a source-backed data package.
    p=make_poster(5,'IPO 问询数据响应','05-问询数据响应')
    p.title(['问到哪笔数据，','就追到哪条依据。'],['AI 拆解问题，规则程序取数与重算，形成问询数据证据包。'])
    p.rect(72,500,976,166,BLUE,18)
    p.text('一个典型问询',108,530,20,'#DCE7FF')
    p.text('某产品毛利率，为什么变了？',108,580,42,WHITE,'B')
    p.text('01  拆成可验证的子问题',72,722,25,BLUE,'B')
    for i,label in enumerate(['销售单价','材料成本','人工成本','制造费用']):
        x=72+i*250
        p.rect(x,776,226,91,LIGHT,12);p.text(label,x+113,806,28,INK,'B','center')
    p.text('定位到具体期间、品号与单据，计算各因素的影响。',72,899,23,MUTED)
    p.text('02  沿业务链追到来源与计算规则',72,978,25,BLUE,'B')
    for i,label in enumerate(['ERP','BOM','采购','生产','财务']):
        x=72+i*199
        p.circle(x+35,1075,35,LIGHT);p.text(label,x+35,1061,25,INK,'B','center')
        if i<4:p.arrow(x+89,1075,x+171,'#B6CDF4',2)
    p.rect(72,1166,976,263,LIGHT,18)
    p.text('03  交付问询数据证据包',108,1199,30,INK,'B')
    for i,(title,desc) in enumerate([('问题拆解','子问题与验证路径'),('证据链','单据、规则与中间结果'),('回复底稿','数据表与说明')]):
        x=108+i*313
        if i:p.line(x-20,1261,x-20,1357,'#CBDCF7')
        p.text(title,x,1265,28,INK,'B');p.text(desc,x,1317,21,MUTED)
    p.text('供券商、会计师撰写问询回复使用；专业判断与回复由专业机构负责。',72,1445,17,MUTED)
    paths.append(p.finish())

    # 06 — Case scope is explicit; residuals are disclosed, never inverted to accuracy.
    p=make_poster(6,'客户实践','06-客户实践')
    p.title(['百万行数据，','追到每笔调整的依据。'],['匿名数据治理案例 · 经券商推荐的多层加工制造业拟 IPO 企业'])
    metrics=[('32','个月','覆盖三个年度，实际 32 个月'),('144–169','万行','单年源数据规模'),('11','层','最深加工层级'),('268,188','条','数量调整，每条都留有依据')]
    for i,(value,unit,desc) in enumerate(metrics):
        x=72+i%2*512;y=521+i//2*244
        p.line(x,y,x+464,y,LINE,2)
        p.text(value,x,y+31,76 if len(value)<5 else 64,BLUE,'EB')
        p.text(unit,x+441,y+73,25,BLUE,'B','right')
        p.text(desc,x,y+143,24,INK,'B')
    p.rect(72,1071,976,231,LIGHT,18)
    p.text('残差金额 / 入库总额',108,1105,23,INK,'B')
    p.text('1.06%–2.38%',108,1153,68,BLUE,'EB')
    p.lines(['各年度残差全部单独列示，','供企业确认。'],657,1158,25,INK,leading=42)
    p.text('三个年度均达到项目交付标准，数量与金额校验通过。',72,1346,26,INK,'B')
    p.text('上述为本案例数据；残差比例不等于准确率，也不代表其他项目表现。',72,1412,19,MUTED)
    paths.append(p.finish())

    # 07 — Select an entry point, then establish scope and factual confirmations.
    p=make_poster(7,'开始合作','07-开始合作')
    p.title(['从您的阶段，','选择需要的服务。'],['三个产品可单独签约，也可组合推进。'])
    entries=[('辅导期早期','数据体检','先看清风险'),('申报前','数据治理','还原历史成本'),('审核问询','问询数据响应','逐问准备依据')]
    for i,(stage,name,why) in enumerate(entries):
        x=72+i*333
        p.rect(x,501,310,219,LIGHT,16)
        p.text(stage,x+25,531,20,BLUE,'B');p.text(name,x+25,586,31 if i<2 else 29,INK,'B');p.text(why,x+25,659,23,MUTED)
    p.text('先从四项信息，明确合作范围。',72,794,32,INK,'B')
    for i,(title,desc) in enumerate([('系统与数据','ERP 等现有系统，涉及年度与数据范围'),('品号与层级','物料、工艺、半成品及委外的复杂程度'),('问题与历史','已知差异，以及此前做过的整改'),('节点与确认人','目标节点，关键事实与口径由谁确认')]):
        y=866+i*72
        p.text(f'0{i+1}',72,y+3,19,BLUE,'EB');p.text(title,119,y,25,INK,'B');p.text(desc,330,y+2,22,MUTED)
    p.rect(72,1200,976,229,BLUE,18)
    p.lines(['提供现有数据，','确认关键事实。'],108,1234,39,WHITE,'B',53)
    p.text('本地部署 · 数据不出企业内网 · 无需替换 ERP',108,1370,21,'#E0EAFF')
    p.rect(859,1231,153,153,WHITE,8);make_qr(p,870,1242,131,site_url)
    p.text('了解服务',935,1394,17,WHITE,'C','center')
    p.text('服务不替代审计及专业判断，不承诺 IPO 结果。具体范围以合同约定为准。',72,1451,16,MUTED)
    paths.append(p.finish())

    combined=output_dir/'传神智溯-七张销售海报.pdf'
    writer=PdfWriter()
    for path in paths:
        reader=PdfReader(path)
        if len(reader.pages)!=1:raise BuildError(f'单张海报应为一页：{path.name}')
        writer.add_page(reader.pages[0])
    with combined.open('wb') as stream:writer.write(stream)

    # Service overview — one-page handout, using the same product language.
    p=make_poster(0,'IPO 数据服务','传神智溯-服务总览')
    p.title(['把说不清的数据，','变成经得起问的依据。'],['数据体检 · 数据治理 · 问询数据响应'])
    p.image('data-sculpture.webp',72,475,976,460)
    for i,(name,desc) in enumerate([('数据体检',['问题定位','影响范围与治理建议']),('数据治理',['三年逐品号明细','留痕、残差与可重跑规则']),('问询数据响应',['每个问题一条证据链','数据表与说明'])]):
        x=72+i*333
        p.line(x,983,x+310,983,LINE,2);p.text(name,x,1010,29,INK,'B');p.lines(desc,x,1065,22,MUTED,leading=36)
    p.rect(72,1191,976,229,LIGHT,18)
    p.lines(['AI 推断成因，程序按规则计算。','关键口径，由人确认。'],108,1230,31,INK,'B',48)
    p.text('可单选 · 可组合 · 本地部署 · 无需替换 ERP',108,1358,22,BLUE,'B')
    make_qr(p,881,1231,130,site_url)
    p.footer('服务不替代审计及专业判断，不承诺 IPO 结果。')
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
        pairs += [(path.with_suffix(extension), ASSETS / "posters" / f"{i:02d}{extension}")
                  for i, path in enumerate(paths, 1) for extension in (".png", ".webp")]
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
    parser.add_argument("--sync-site", action="store_true", help="显式覆盖网站 PDF；与 --render 同用时也更新七张 PNG/WebP。")
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
                    "content_source": "用户提供的三产品销售资料；品牌按用户要求统一为传神智溯",
                    "claims": "Three products may be purchased individually or combined. The anonymous case covers "
                              "32 months across three reporting years, with 1.44–1.69 million source rows per year, "
                              "11 processing levels, and 268188 quantity adjustments with retained evidence. "
                              "Annual residual amount / receipt value is 1.06%–2.38%; this is not accuracy. "
                              "No pending price or duration, AI zero-error promise, or IPO outcome guarantee is advertised.",
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
