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
VERSION = 10
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
                "pain-recipe.png", "pain-price.png", "pain-stock.png", "material-discrepancy.png",
                "service-check.png", "service-governance.png", "service-inquiry.png", "case-factory.png"]
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

    def visual_title(p, first, second, subtitle):
        p.text(first,72,189,70,INK,'B')
        p.text(second,72,275,70,BLUE,'B')
        p.text(subtitle,72,394,25,MUTED)

    def product_rows(p, qr_url=None):
        # Each choice explains the situation, work and tangible deliverable.
        products=[
            ('IPO 数据体检','数据对不上，先查清问题。',
             ['比对采购、生产、库存与财务记录，定位差异。',
              '区分可能成因、评估影响，给出整改建议与工作量。'],
             '交付：风险体检报告，用于确定整改范围。','service-check.png'),
            ('IPO 数据治理','历史成本不清，逐笔还原。',
             ['梳理编号、配方与单据，先核数量，再逐层算成本。',
              '每笔调整保留前后数值与依据，未解释差额单列。'],
             '交付：三年逐品号明细、调整台账与可重跑规则。','service-governance.png'),
            ('IPO 问询数据响应','被问到一个数字，拿出依据。',
             ['把毛利变化等问题拆开，追查来源单据和计算过程。',
              '将数据表、规则与中间结果整理为可复核的证据。'],
             '交付：问询数据证据包，供专业机构撰写回复。','service-inquiry.png')]
        for i,(name,value,details,delivery,asset) in enumerate(products):
            y=458+i*290
            p.image(asset,72,y+8,310,310*2/3)
            p.text(f'0{i+1} / {name}',420,y+2,23,BLUE,'B')
            p.text(value,420,y+47,33,INK,'B')
            p.lines(details,420,y+106,23,INK,leading=37)
            p.text(delivery,420,y+203,23,BLUE,'B')
            if i<2:p.line(72,y+263,1048,y+263,LINE)
        p.rect(72,1348,976,112,BLUE,16)
        p.text('按需要单独选择，也可衔接使用。',104,1372,30,WHITE,'B')
        p.text('AI 追查成因 · 程序计算验证 · 人确认关键依据',104,1420,21,'#E0EAFF')
        if qr_url:
            p.rect(925,1358,96,96,WHITE,4)
            make_qr(p,933,1366,80,qr_url)

    def business_example(p, asset, heading, explanation, supporting):
        # Preserve the full approved image; use the adjacent space to explain its business meaning.
        p.image(asset,72,456,624,416)
        p.text('一个常见现场',736,465,20,BLUE,'B')
        p.lines(heading,736,511,32,INK,'B',46)
        p.lines(explanation,736,636,23,INK,leading=35)
        p.lines(supporting,736,773,21,MUTED,leading=33)
        p.text('业务示意 · 具体原因以单据、规则校验与专业确认为准',72,891,17,MUTED)

    def work_steps(p, heading, steps):
        p.text(heading,72,948,27,INK,'B')
        for i,(title,desc) in enumerate(steps):
            x=72+i*333
            p.text(f'0{i+1}',x,1007,22,BLUE,'EB')
            p.text(title,x+44,1002,28,INK,'B')
            p.lines(desc,x,1055,23,INK,leading=35)
        p.text('AI 负责追查与推断，程序负责计算校验，关键依据由人确认。',72,1150,21,MUTED)

    def delivery_band(p, title, contents, use):
        p.rect(72,1210,976,218,BLUE,18)
        p.text('客户拿到什么',108,1235,19,'#C8DBFF','B')
        p.text(title,108,1275,35,WHITE,'B')
        p.text(contents,108,1337,24,WHITE)
        p.text(use,108,1383,23,'#E0EAFF')

    # 01 — Three products, one continuous evidence chain.
    p=make_poster(1,'三产品总览','01-三产品总览')
    visual_title(p,'让数据说得清，','让追问有依据。','面向拟上市制造企业及券商项目组：查问题、理成本、备证据。')
    product_rows(p)
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

    # 03 — Explain what is checked and how it changes the client's next decision.
    p=make_poster(3,'IPO 数据体检','03-数据体检')
    visual_title(p,'先看清问题，','再决定怎么处理。','适合企业和券商先摸清数据问题，再安排整改。')
    business_example(p,'service-check.png',
                     ['采购已经入库，','财务金额却对不上。'],
                     ['是缺少单价、单位不一，','还是补录造成重复？','先定位差异，再核对原因。'],
                     ['同样检查：领料与配方、','生产与库存、成本与收入。'])
    work_steps(p,'从一处差异，查清问题和影响范围',[
        ('程序批量比对',['交叉比对采购、领料、','生产、库存和财务记录。']),
        ('AI 辅助归因',['区分缺价、同物多码等','成因，列出待确认事项。']),
        ('明确整改范围',['定位期间、品号与单据，','评估影响与整改工作量。'])])
    delivery_band(p,'《IPO 数据风险体检报告》',
                  '风险分级 · 问题位置 · 影响范围 · 治理建议及工作量评估',
                  '据此判断：哪些可自行整改，哪些需要专项治理。')
    p.text('体检用于发现与评估问题，不要求继续购买数据治理。',72,1454,19,MUTED)
    paths.append(p.finish())

    # 04 — Explain why quantities and costs must be reconstructed in order.
    p=make_poster(4,'IPO 数据治理','04-数据治理')
    visual_title(p,'先把数量对齐，','再把成本算清。','适合历史记录互相矛盾、无法形成可靠成本明细的企业。')
    business_example(p,'service-governance.png',
                     ['数量对上了，','成本却接不上。'],
                     ['多套编号、替代领料、','入库缺价、历史补录，','都可能让加工链断开。'],
                     ['从原料到半成品、成品，','每一级都要核清数量与计价。'])
    work_steps(p,'沿加工链，把每一级的数量与成本接起来',[
        ('先核数量',['归并编号、梳理配方，','核对进货、耗用与结存。']),
        ('再算成本',['AI 追查断点、形成规则，','程序按确认依据逐层重算。']),
        ('逐笔留痕',['记录调整前后值与依据，','无法解释的差额单列。'])])
    delivery_band(p,'三年逐品号进耗存与成本明细',
                  '配套：来源说明、调整台账、残差清单与可重跑规则。',
                  '每个物料编号都能查数量、成本与依据，规则变化后可统一重算。')
    p.text('三年指数据范围；会计口径与计价依据由企业及相关专业人员确认。',72,1454,19,MUTED)
    paths.append(p.finish())

    # 05 — Turn a familiar business question into verifiable evidence.
    p=make_poster(5,'IPO 问询数据响应','05-问询数据响应')
    visual_title(p,'问到哪笔数据，','就追到哪条依据。','适合需要在回复时限内，说明数据来源与计算过程的项目。')
    business_example(p,'service-inquiry.png',
                     ['同一产品，','毛利率为什么变了？'],
                     ['售价变了、材料涨了，','还是费用分摊变化？','每项解释都要有依据。'],
                     ['回答需要跨部门、跨系统，','把同一口径的数据找齐。'])
    work_steps(p,'把一个问题，变成一条能复核的证据链',[
        ('AI 拆解问题',['将毛利变化拆成售价、','材料、人工与费用等因素。']),
        ('程序取数重算',['定位期间与产品，追查','采购、生产和财务单据。']),
        ('整理证据链',['将来源、规则和中间结果','整理成可逐项复核的数据表。'])])
    delivery_band(p,'问询数据证据包',
                  '问题拆解 + 来源单据 + 计算过程 + 回复所需数据底稿',
                  '供券商、会计师撰写回复，核对每个数字从哪里来。')
    p.text('已有治理成果可复用；未治理的相关数据可先做针对性还原。',72,1454,19,MUTED)
    paths.append(p.finish())

    # 06 — Add the starting problem and the reconstruction path around verified case facts.
    p=make_poster(6,'客户实践','06-客户实践')
    visual_title(p,'百万行数据，','追到每笔调整的依据。','已交付治理案例 · 多层加工制造业 · 拟 IPO')
    p.image('case-factory.png',72,456,624,416)
    p.text('原先卡在哪里',736,465,20,BLUE,'B')
    p.lines(['三年明细拿不全，','不同环节对不上。'],736,511,32,INK,'B',46)
    p.lines(['材料经过多级加工，','编号、配方或入库价出错，','差异会传到后续的成本。'],736,636,23,INK,leading=35)
    p.lines(['需要把单据重新串起来，','才能解释每一级怎么算。'],736,773,21,MUTED,leading=33)
    p.text('业务复杂度示意 · 非客户现场照片',72,891,17,MUTED)
    metrics=[('32','个月 · 跨三个年度'),('144–169','万行 / 年 · 源数据'),
             ('11','层 · 最深加工层级'),('268,188','条数量调整 · 逐条留痕')]
    for i,(value,meaning) in enumerate(metrics):
        x=72+i*250
        p.line(x,945,x+226,945,LINE,2)
        p.text(value,x,969,48 if len(value)>5 else 56,BLUE,'EB')
        p.text(meaning,x,1040,20,INK)
    p.text('怎样还原',72,1114,27,INK,'B')
    p.lines(['归并编号、核对配方、重算工单；先核清数量，再逐级计算成本。',
             'AI 追查异常并修正规则，程序反复校验，关键依据由企业和专业人员确认。'],
            72,1162,25,INK,leading=40)
    p.rect(72,1270,976,158,BLUE,18)
    p.text('交付：可复核的明细、调整依据与规则',108,1300,32,WHITE,'B')
    p.text('无法还原的差额单独列明，不把未解释的问题藏进其他科目。',108,1364,24,WHITE)
    p.text('单个已交付案例；各年度残差金额占入库总额 1.06%–2.38%，不代表其他项目效果。',72,1454,17,MUTED)
    paths.append(p.finish())

    # 07 — Make the first conversation concrete for a client with existing systems.
    p=make_poster(7,'开始合作','07-开始合作')
    visual_title(p,'从当前难题，','找到合作起点。','先选需要解决的问题，再一起明确服务范围。')
    entries=[('service-check.png','数据体检',['报表有差异，先查清','问题位置与影响范围。']),
             ('service-governance.png','数据治理',['历史成本说不清，形成','逐品号明细与调整依据。']),
             ('service-inquiry.png','问询数据响应',['需要解释具体数字，','准备来源、计算与底稿。'])]
    for i,(asset,name,desc) in enumerate(entries):
        x=72+i*333
        p.image(asset,x,456,310,310*2/3)
        p.text(name,x,697,30,INK,'B')
        p.lines(desc,x,750,23,INK,leading=35)
    p.text('第一次沟通，先准备这些信息',72,872,28,INK,'B')
    steps=[('现有数据',['现有 ERP 或财务报表，','涉及年度与业务范围，','以及系统和数据格式。']),
           ('已知问题',['最难解释的数据差异、','已有整改或治理成果，','当前需要回答的问题。']),
           ('目标与配合',['计划完成的时间节点、','业务与财务确认人；','共同约定交付、周期与费用。'])]
    for i,(title,desc) in enumerate(steps):
        x=72+i*333
        p.text(f'0{i+1}',x,935,22,BLUE,'EB')
        p.text(title,x+44,930,28,INK,'B')
        p.lines(desc,x,982,23,INK,leading=35)
    p.rect(72,1178,976,250,BLUE,18)
    p.text('从一份现有数据开始。',108,1213,42,WHITE,'B')
    p.lines(['本地部署，数据不出企业内网。','保留现有 ERP，按所选服务交付。','企业主要提供数据，并确认关键事实与口径。'],
            108,1290,24,WHITE,leading=39)
    p.rect(859,1211,153,153,WHITE,8)
    make_qr(p,870,1222,131,site_url.split('#')[0]+'#start')
    p.text('扫码了解合作',935,1384,18,WHITE,'C','center')
    p.text('三款产品可单独选择或衔接使用；范围、周期与费用按具体项目约定。',72,1454,19,MUTED)
    paths.append(p.finish())

    combined=output_dir/'传神智溯-七张销售海报.pdf'
    writer=PdfWriter()
    for path in paths:
        reader=PdfReader(path)
        if len(reader.pages)!=1:raise BuildError(f'单张海报应为一页：{path.name}')
        writer.add_page(reader.pages[0])
    with combined.open('wb') as stream:writer.write(stream)

    # Service overview — a visual one-page handout, sharing the product choices.
    p=make_poster(0,'IPO 数据服务','传神智溯-服务总览')
    visual_title(p,'让数据说得清，','让追问有依据。','面向拟上市制造企业及券商项目组：查问题、理成本、备证据。')
    product_rows(p,site_url)
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
