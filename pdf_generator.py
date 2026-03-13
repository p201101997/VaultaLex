"""
VaultaLex — PDF Report Generator
VaultaLex · Digital Estate Planning & Legal Documentation · Analytics Command Center
Uses ReportLab native drawing — no kaleido / screenshot dependency.
"""
import io, math
from datetime import datetime
import pandas as pd
import numpy as np

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.graphics.shapes import (
    Drawing, Rect, String, Line, Circle, Wedge, Polygon,
)

W, H = A4  # 595 × 842 pt

# ── PALETTE ───────────────────────────────────────────────────────────────────
BG     = colors.HexColor('#0a0e1a')
CARD   = colors.HexColor('#111827')
CARD2  = colors.HexColor('#1a2235')
MGRAY  = colors.HexColor('#1e2d4a')
GOLD   = colors.HexColor('#f5c518')
CYAN   = colors.HexColor('#00d4a0')
BLUE   = colors.HexColor('#4da6ff')
ORANGE = colors.HexColor('#ff6b35')
PURPLE = colors.HexColor('#b47cff')
RED    = colors.HexColor('#ff4757')
T_MAIN = colors.HexColor('#e8eaf0')
T_MID  = colors.HexColor('#8899b8')
T_DIM  = colors.HexColor('#6b7fa3')
T_DARK = colors.HexColor('#4a6080')

TIER_C = {'Free': BLUE, 'Basic': CYAN, 'Premium': GOLD, 'Family': ORANGE}
PALETTE = [GOLD, CYAN, BLUE, ORANGE, PURPLE, RED,
           colors.HexColor('#00c8d4'), colors.HexColor('#ffa726')]

# ── STYLES ────────────────────────────────────────────────────────────────────
def S():
    return {
        'h1':   ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=28, textColor=GOLD,
                               leading=34, spaceBefore=0, spaceAfter=10),
        'h2':   ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=15, textColor=T_MAIN,
                               leading=19, spaceBefore=16, spaceAfter=8,
                               borderPad=0, borderColor=None),
        'h3':   ParagraphStyle('h3', fontName='Helvetica-Bold', fontSize=11, textColor=GOLD,
                               leading=15, spaceBefore=10, spaceAfter=5),
        'body': ParagraphStyle('body', fontName='Helvetica', fontSize=9, textColor=T_MID,
                               leading=14, spaceAfter=5),
        'mono': ParagraphStyle('mono', fontName='Courier', fontSize=8, textColor=T_DIM, leading=12),
        'tag':  ParagraphStyle('tag', fontName='Helvetica', fontSize=8, textColor=T_DARK,
                               leading=11, spaceAfter=2),
        'kv':   ParagraphStyle('kv', fontName='Helvetica-Bold', fontSize=20, textColor=GOLD,
                               leading=24, alignment=TA_CENTER),
        'kl':   ParagraphStyle('kl', fontName='Helvetica', fontSize=7, textColor=T_DIM,
                               leading=10, alignment=TA_CENTER),
        'kd':   ParagraphStyle('kd', fontName='Helvetica', fontSize=8, textColor=CYAN,
                               leading=11, alignment=TA_CENTER),
        'th':   ParagraphStyle('th', fontName='Helvetica-Bold', fontSize=8, textColor=GOLD,
                               alignment=TA_CENTER),
        'tc':   ParagraphStyle('tc', fontName='Helvetica', fontSize=8, textColor=T_MID,
                               alignment=TA_LEFT),
        'tcr':  ParagraphStyle('tcr', fontName='Helvetica', fontSize=8, textColor=T_MID,
                               alignment=TA_RIGHT),
        'ins':  ParagraphStyle('ins', fontName='Helvetica', fontSize=9,
                               textColor=colors.HexColor('#b8c8e0'), leading=15, spaceAfter=3),
        'ft':   ParagraphStyle('ft', fontName='Helvetica', fontSize=7, textColor=T_DIM,
                               alignment=TA_CENTER),
        'cov_sub': ParagraphStyle('cs', fontName='Helvetica', fontSize=11, textColor=T_DIM,
                                  leading=15, spaceAfter=4),
        'meta_k':  ParagraphStyle('mk', fontName='Helvetica', fontSize=9, textColor=T_DIM),
        'meta_v':  ParagraphStyle('mv', fontName='Helvetica-Bold', fontSize=9, textColor=T_MAIN),
    }

ST = S()

# ── PAGE CALLBACK ─────────────────────────────────────────────────────────────
def _page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BG)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    # gold top bar
    canvas.setFillColor(GOLD)
    canvas.rect(0, H - 5, W, 5, fill=1, stroke=0)
    # header
    canvas.setStrokeColor(MGRAY); canvas.setLineWidth(0.5)
    canvas.line(28, H - 24, W - 28, H - 24)
    canvas.setFont('Helvetica-Bold', 9); canvas.setFillColor(GOLD)
    canvas.drawString(28, H - 19, 'VaultaLex  ·  Digital Estate Planning & Legal Documentation')
    canvas.setFont('Helvetica', 8); canvas.setFillColor(T_DIM)
    lbl = getattr(doc, 'layer_label', '')
    canvas.drawRightString(W - 28, H - 19, lbl)
    # footer
    canvas.line(28, 22, W - 28, 22)
    canvas.setFont('Helvetica', 7); canvas.setFillColor(T_DIM)
    canvas.drawString(28, 12, f'Generated {datetime.now().strftime("%d %b %Y %H:%M")}  ·  Confidential')
    canvas.drawRightString(W - 28, 12, f'Page {doc.page}')
    canvas.restoreState()

# ── DRAWING PRIMITIVES ────────────────────────────────────────────────────────
def _bg(d, w, h, accent=GOLD):
    d.add(Rect(0, 0, w, h, fillColor=CARD, strokeColor=MGRAY, strokeWidth=0.5, rx=3, ry=3))
    d.add(Rect(0, h - 3, w, 3, fillColor=accent, strokeColor=None))

def _bar(d, x, y_base, bar_w, bar_h, color, val_str='', max_h=100):
    d.add(Rect(x, y_base, bar_w, max(2, bar_h), fillColor=color, strokeColor=None))
    if val_str:
        d.add(String(x + bar_w / 2, y_base + max(2, bar_h) + 3, val_str,
                     fontName='Helvetica', fontSize=6, fillColor=T_MID, textAnchor='middle'))

def _grid(d, ml, mb, cw, ch, n_lines=5, max_v=100, prefix='', suffix=''):
    for i in range(n_lines + 1):
        y = mb + ch * i / n_lines
        d.add(Line(ml, y, ml + cw, y, strokeColor=MGRAY, strokeWidth=0.3))
        val = max_v * i / n_lines
        lbl = f"{prefix}{val:,.0f}{suffix}"
        d.add(String(ml - 3, y - 3, lbl, fontName='Helvetica', fontSize=5.5,
                     fillColor=T_DIM, textAnchor='end'))

def _x_label(d, x, mb, lbl, font_size=6):
    d.add(String(x, mb - 14, lbl[:13], fontName='Helvetica', fontSize=font_size,
                 fillColor=T_DIM, textAnchor='middle'))

def _title_str(d, w, h, title):
    d.add(String(10, h - 14, title, fontName='Helvetica-Bold', fontSize=9, fillColor=T_MAIN))

# ── CHART BUILDERS ────────────────────────────────────────────────────────────
def chart_bar(data: dict, title, w=480, h=210, prefix='', suffix='', colors_list=None):
    labels = list(data.keys())
    values = [float(v) for v in data.values()]
    n = len(labels)
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    if not values or max(values) == 0:
        return d
    ml, mr, mt, mb = 65, 16, 28, 38
    cw_tot = w - ml - mr
    ch = h - mt - mb
    max_v = max(values)
    bar_w  = (cw_tot / n) * 0.62
    gap    = (cw_tot / n) * 0.38
    _grid(d, ml, mb, cw_tot, ch, max_v=max_v, prefix=prefix, suffix=suffix)
    for i, (lbl, val) in enumerate(zip(labels, values)):
        x = ml + i * (cw_tot / n) + gap / 2
        bh = (val / max_v) * ch
        col = (colors_list[i] if colors_list else PALETTE[i % len(PALETTE)])
        _bar(d, x, mb, bar_w, bh, col,
             f"{prefix}{val:,.0f}{suffix}", ch)
        _x_label(d, x + bar_w / 2, mb, str(lbl))
    d.add(Rect(0, 0, w, h, fillColor=None, strokeColor=MGRAY, strokeWidth=0.4))
    return d

def chart_hbar(data: dict, title, w=480, h=220, prefix='', suffix='', color=CYAN):
    labels = list(data.keys())
    values = [float(v) for v in data.values()]
    n = len(labels)
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    if not values or max(values) == 0:
        return d
    ml, mr, mt, mb = 130, 60, 28, 10
    cw = w - ml - mr
    ch = h - mt - mb
    max_v = max(values)
    bar_h = (ch / n) * 0.6
    gap   = (ch / n) * 0.4
    for i in range(5):
        x = ml + cw * i / 4
        d.add(Line(x, mb, x, mb + ch, strokeColor=MGRAY, strokeWidth=0.3))
        val = max_v * i / 4
        d.add(String(x, mb - 8, f"{prefix}{val:,.0f}{suffix}",
                     fontName='Helvetica', fontSize=5.5, fillColor=T_DIM, textAnchor='middle'))
    for i, (lbl, val) in enumerate(zip(labels, values)):
        y = mb + (n - 1 - i) * (ch / n) + gap / 2
        bw = max(2, (val / max_v) * cw)
        col = PALETTE[i % len(PALETTE)] if not isinstance(color, colors.Color) else color
        d.add(Rect(ml, y, bw, bar_h, fillColor=col, strokeColor=None))
        d.add(String(ml + bw + 4, y + bar_h / 2 - 3,
                     f"{prefix}{val:,.0f}{suffix}",
                     fontName='Helvetica', fontSize=6, fillColor=T_MID))
        d.add(String(ml - 4, y + bar_h / 2 - 3, str(lbl)[:18],
                     fontName='Helvetica', fontSize=6.5, fillColor=T_MID, textAnchor='end'))
    d.add(Rect(0, 0, w, h, fillColor=None, strokeColor=MGRAY, strokeWidth=0.4))
    return d

def chart_line(series: dict, title, w=480, h=210, prefix='', x_labels=None):
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    all_vals = [v for vals in series.values() for v in vals if v is not None]
    if not all_vals:
        return d
    ml, mr, mt, mb = 68, 16, 28, 38
    cw = w - ml - mr
    ch = h - mt - mb
    max_v = max(all_vals)
    min_v = min(0, min(all_vals))
    rng   = (max_v - min_v) or 1
    _grid(d, ml, mb, cw, ch, max_v=max_v, prefix=prefix)
    for si, (name, vals) in enumerate(series.items()):
        n = len(vals)
        if n < 2:
            continue
        color = PALETTE[si % len(PALETTE)]
        pts = []
        for i, v in enumerate(vals):
            if v is None:
                pts.append(None)
                continue
            px = ml + i * cw / (n - 1)
            py = mb + ((float(v) - min_v) / rng) * ch
            pts.append((px, py))
        segs = []
        cur  = []
        for p in pts:
            if p is None:
                if cur: segs.append(cur); cur = []
            else:
                cur.append(p)
        if cur: segs.append(cur)
        for seg in segs:
            for i in range(len(seg) - 1):
                d.add(Line(seg[i][0], seg[i][1], seg[i+1][0], seg[i+1][1],
                           strokeColor=color, strokeWidth=2.0))
        # legend
        lx = ml + si * 110
        d.add(Rect(lx, 4, 8, 5, fillColor=color, strokeColor=None))
        d.add(String(lx + 11, 4, name[:16], fontName='Helvetica', fontSize=7, fillColor=T_MID))
    if x_labels:
        n = max(len(v) for v in series.values() if v)
        step = max(1, n // 10)
        for i in range(0, n, step):
            px = ml + i * cw / (n - 1) if n > 1 else ml
            d.add(String(px, mb - 14, str(x_labels[i])[:7],
                         fontName='Helvetica', fontSize=5.5, fillColor=T_DIM, textAnchor='middle'))
    d.add(Rect(0, 0, w, h, fillColor=None, strokeColor=MGRAY, strokeWidth=0.4))
    return d

def chart_pie(data: dict, title, w=260, h=220):
    labels = list(data.keys())
    values = [float(v) for v in data.values()]
    total  = sum(values)
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    if total == 0:
        return d
    cx, cy = w * 0.42, h * 0.50
    r = min(w, h) * 0.30
    angle = 90
    legend_y = h - 30
    for i, (lbl, val) in enumerate(zip(labels, values)):
        sweep = (val / total) * 360
        if sweep < 0.5:
            angle += sweep
            continue
        col = PALETTE[i % len(PALETTE)]
        d.add(Wedge(cx, cy, r, angle, angle + sweep,
                    fillColor=col, strokeColor=BG, strokeWidth=1.5))
        mid = math.radians((angle + angle + sweep) / 2)
        mx  = cx + r * 0.68 * math.cos(mid)
        my  = cy + r * 0.68 * math.sin(mid)
        pct = val / total * 100
        if pct > 6:
            d.add(String(mx, my - 3, f"{pct:.0f}%",
                         fontName='Helvetica-Bold', fontSize=7,
                         fillColor=BG, textAnchor='middle'))
        angle += sweep
        # legend (right side)
        lx = w * 0.72
        li = i
        d.add(Rect(lx, legend_y - li * 15, 8, 8, fillColor=col, strokeColor=None))
        d.add(String(lx + 11, legend_y - li * 15, str(lbl)[:13],
                     fontName='Helvetica', fontSize=7, fillColor=T_MID))
    return d

def chart_heatmap(matrix, row_labels, col_labels, title, w=490, h=270):
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    nr, nc = len(row_labels), len(col_labels)
    if nr == 0 or nc == 0:
        return d
    ml, mr, mt, mb = 55, 10, 26, 20
    cw = (w - ml - mr) / nc
    ch = (h - mt - mb) / nr

    def heat(v):
        v = max(0.0, min(1.0, v))
        if v < 0.4:
            return colors.Color(0.25 * v / 0.4, 0.04, 0.04)
        elif v < 0.7:
            t = (v - 0.4) / 0.3
            return colors.Color(0.25 + 0.55 * t, 0.04 + 0.36 * t, 0.0)
        else:
            t = (v - 0.7) / 0.3
            return colors.Color(0.8 + 0.16 * t, 0.4 + 0.43 * t, 0.0 + 0.63 * t)

    for ri, row_lbl in enumerate(row_labels):
        y = h - mt - (ri + 1) * ch
        d.add(String(ml - 3, y + ch / 2 - 3, str(row_lbl)[:8],
                     fontName='Helvetica', fontSize=5.5, fillColor=T_DIM, textAnchor='end'))
        if ri < len(matrix):
            for ci, col_lbl in enumerate(col_labels):
                x   = ml + ci * cw
                val = matrix[ri][ci] if ci < len(matrix[ri]) else 0
                d.add(Rect(x, y, cw - 0.5, ch - 0.5,
                           fillColor=heat(val), strokeColor=BG, strokeWidth=0.3))
                if val > 0:
                    d.add(String(x + cw / 2, y + ch / 2 - 3, f"{val*100:.0f}",
                                 fontName='Helvetica', fontSize=5.5, fillColor=T_MAIN,
                                 textAnchor='middle'))
    for ci, col_lbl in enumerate(col_labels):
        x = ml + ci * cw + cw / 2
        d.add(String(x, mb - 10, str(col_lbl),
                     fontName='Helvetica', fontSize=5.5, fillColor=T_DIM, textAnchor='middle'))
    return d

def chart_gauge(value, max_val, title, w=190, h=175):
    d = Drawing(w, h)
    _bg(d, w, h)
    cx, cy = w / 2, h * 0.50
    r = min(w, h) * 0.33
    zones = [(0, 0.4, colors.HexColor('#3d0f15')),
             (0.4, 0.7, colors.HexColor('#2d2000')),
             (0.7, 1.0, colors.HexColor('#0d2d1e'))]
    for z0, z1, zc in zones:
        a0 = 180 - z0 * 180
        a1 = 180 - z1 * 180
        d.add(Wedge(cx, cy, r, a1, a0, fillColor=zc, strokeColor=BG, strokeWidth=1))
        d.add(Wedge(cx, cy, r * 0.58, a1, a0, fillColor=CARD, strokeColor=None))
    pct = min(1.0, max(0.0, value / max_val))
    na  = math.radians(180 - pct * 180)
    nx  = cx + r * 0.76 * math.cos(na)
    ny  = cy + r * 0.76 * math.sin(na)
    d.add(Line(cx, cy, nx, ny, strokeColor=GOLD, strokeWidth=2.5))
    d.add(Circle(cx, cy, 4, fillColor=GOLD, strokeColor=BG, strokeWidth=1))
    d.add(String(cx, cy - 22, f"{value:.0f}",
                 fontName='Helvetica-Bold', fontSize=18, fillColor=GOLD, textAnchor='middle'))
    d.add(String(cx, cy - 33, f"/ {max_val:.0f}",
                 fontName='Helvetica', fontSize=7, fillColor=T_DIM, textAnchor='middle'))
    d.add(String(w / 2, h - 14, title,
                 fontName='Helvetica-Bold', fontSize=8, fillColor=T_MAIN, textAnchor='middle'))
    d.add(String(18, cy - 4, '0', fontName='Helvetica', fontSize=7, fillColor=T_DIM))
    d.add(String(w - 20, cy - 4, str(int(max_val)),
                 fontName='Helvetica', fontSize=7, fillColor=T_DIM, textAnchor='end'))
    return d

def chart_grouped_bar(groups: dict, series_labels, title, w=480, h=220,
                      prefix='', suffix=''):
    group_labels = list(groups.keys())
    ng = len(group_labels)
    ns = len(series_labels)
    d = Drawing(w, h)
    _bg(d, w, h)
    _title_str(d, w, h, title)
    if ng == 0:
        return d
    all_vals = [v for vals in groups.values() for v in vals]
    max_v = max(all_vals) if all_vals and max(all_vals) != 0 else 1
    ml, mr, mt, mb = 65, 16, 28, 42
    cw = w - ml - mr
    ch = h - mt - mb
    gw = cw / ng
    bw = (gw * 0.80) / ns
    _grid(d, ml, mb, cw, ch, max_v=max_v, prefix=prefix, suffix=suffix)
    for gi, (glbl, vals) in enumerate(groups.items()):
        gx = ml + gi * gw + gw * 0.10
        for si, val in enumerate(vals):
            bx = gx + si * bw
            bh = max(2, (float(val) / max_v) * ch)
            d.add(Rect(bx, mb, bw * 0.88, bh,
                       fillColor=PALETTE[si % len(PALETTE)], strokeColor=None))
        short = str(glbl)[:11]
        d.add(String(gx + (ns * bw) / 2, mb - 14, short,
                     fontName='Helvetica', fontSize=6, fillColor=T_DIM, textAnchor='middle'))
    lx = ml
    for si, slbl in enumerate(series_labels):
        d.add(Rect(lx, 5, 8, 7, fillColor=PALETTE[si % len(PALETTE)], strokeColor=None))
        d.add(String(lx + 11, 5, str(slbl)[:16],
                     fontName='Helvetica', fontSize=7, fillColor=T_MID))
        lx += 95
    d.add(Rect(0, 0, w, h, fillColor=None, strokeColor=MGRAY, strokeWidth=0.4))
    return d

# ── LAYOUT HELPERS ────────────────────────────────────────────────────────────
def _cover(story, layer_name, layer_tag, desc, date_str):
    story.append(Spacer(1, 52))
    acc = Drawing(W - 58, 4)
    acc.add(Rect(0, 0, W - 58, 4, fillColor=GOLD, strokeColor=None))
    story.append(acc)
    story.append(Spacer(1, 18))
    story.append(Paragraph("VaultaLex", ST['cov_sub']))
    story.append(Paragraph("Analytics Command Center", ST['h1']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"{layer_tag}  ·  {layer_name}", ST['cov_sub']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(desc, ST['body']))
    story.append(Spacer(1, 36))
    meta = [
        ["Report Type",      layer_name],
        ["Platform",         "VaultaLex · Digital Estate Planning & Legal Documentation"],
        ["Data Period",      "January 2022 – March 2026"],
        ["Generated",        date_str],
        ["Subscribers",      "2,000 synthetic records (seed=42)"],
        ["Purpose",          "Estate consolidation · Document vault · Legal advisory"],
    ]
    t = Table(meta, colWidths=[120, 320])
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CARD),
        ('TEXTCOLOR',     (0, 0), (0, -1), T_DIM),
        ('TEXTCOLOR',     (1, 0), (1, -1), T_MAIN),
        ('FONTNAME',      (0, 0), (0, -1), 'Helvetica'),
        ('FONTNAME',      (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, -1), 9),
        ('GRID',          (0, 0), (-1, -1), 0.3, MGRAY),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
    ]))
    story.append(t)
    story.append(PageBreak())

def _sec(story, title, tag=''):
    if tag:
        story.append(Paragraph(tag, ST['tag']))
    story.append(Paragraph(title, ST['h2']))
    story.append(HRFlowable(width='100%', thickness=0.4, color=MGRAY, spaceAfter=5))

def _insight(story, text, accent=CYAN):
    inner = Table([[Paragraph(text, ST['ins'])]], colWidths=[W - 80])
    inner.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), colors.HexColor('#0f1e35')),
        ('LEFTPADDING',   (0, 0), (-1, -1), 14),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 14),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LINEBEFORE',    (0, 0), (0, -1), 4, accent),
        ('BOX',           (0, 0), (-1, -1), 0.4, MGRAY),
    ]))
    story.append(inner)
    story.append(Spacer(1, 8))

def _kpi_row(story, items):
    n = len(items)
    cw = (W - 58) / n
    cells = []
    for lbl, val, delta in items:
        cell = [Paragraph(lbl.upper(), ST['kl']), Spacer(1, 3),
                Paragraph(str(val), ST['kv'])]
        if delta:
            cell.append(Paragraph(str(delta), ST['kd']))
        cells.append(cell)
    t = Table([cells], colWidths=[cw] * n)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CARD),
        ('BOX',           (0, 0), (-1, -1), 0.4, MGRAY),
        ('INNERGRID',     (0, 0), (-1, -1), 0.4, MGRAY),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('LINEABOVE',     (0, 0), (-1, 0), 3, GOLD),
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

def _table(story, headers, rows, col_widths=None, max_rows=20):
    rows = rows[:max_rows]
    hrow = [Paragraph(h, ST['th']) for h in headers]
    data = [hrow] + [[Paragraph(str(c), ST['tc']) for c in row] for row in rows]
    if not col_widths:
        col_widths = [(W - 58) / len(headers)] * len(headers)
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#0d1221')),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [CARD, CARD2]),
        ('LINEABOVE',     (0, 0), (-1, 0), 2, GOLD),
        ('GRID',          (0, 0), (-1, -1), 0.35, MGRAY),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 10))

def _side_by_side(story, left, right, lw=None, rw=None):
    lw = lw or (W - 58) * 0.52
    rw = rw or (W - 58) - lw - 8
    t = Table([[left, right]], colWidths=[lw, rw])
    t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 4),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 4)]))
    story.append(t)
    story.append(Spacer(1, 10))

# ═════════════════════════════════════════════════════════════════════════════
# LAYER 1 — DESCRIPTIVE
# ═════════════════════════════════════════════════════════════════════════════
def build_descriptive_report(DATA, filters=None) -> bytes:
    tier_f = (filters or {}).get('tier', ['Free','Basic','Premium','Family'])
    customers       = DATA['customers']
    monthly_revenue = DATA['monthly_revenue']
    assets          = DATA['assets']
    documents       = DATA['documents']
    estate_sections = DATA['estate_sections']
    sessions        = DATA['sessions']

    cf = customers[customers['subscription_tier'].isin(tier_f)]
    mf = monthly_revenue[monthly_revenue['tier'].isin(tier_f)]
    af = assets[assets['tier'].isin(tier_f)]
    df = documents[documents['tier'].isin(tier_f)]
    esf= estate_sections[estate_sections['tier'].isin(tier_f)]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=28, rightMargin=28,
                            topMargin=44, bottomMargin=34)
    doc.layer_label = 'LAYER 01 · DESCRIPTIVE'
    story = []

    _cover(story, 'Descriptive Analytics', 'LAYER 01',
           'A comprehensive snapshot of the current platform state — active subscribers, '
           'revenue, estate completeness, asset registration, document vault activity, '
           'and the consolidation value being delivered to users.',
           datetime.now().strftime('%d %B %Y'))

    # ── KPIs ──
    _sec(story, 'Platform KPI Summary', 'KEY PERFORMANCE INDICATORS')
    active    = int(cf[cf['is_churned']==0].shape[0])
    total_mrr = int(mf[mf['month']=='2026-03']['mrr_usd'].sum())
    prev_mrr  = int(mf[mf['month']=='2026-02']['mrr_usd'].sum())
    mrr_g     = ((total_mrr - prev_mrr) / max(prev_mrr, 1)) * 100
    avg_comp  = cf['estate_completeness_score'].mean()
    avg_bene  = cf['beneficiaries_assigned'].mean()
    avg_plat  = cf['platforms_consolidated'].mean()
    total_av  = af['estimated_value_usd'].sum()

    _kpi_row(story, [
        ('Active Subscribers',     f"{active:,}",              f"{mrr_g:+.1f}% MRR MoM"),
        ('MRR',                    f"${total_mrr:,}",           f"${total_mrr*12:,} ARR"),
        ('Avg Estate Completeness',f"{avg_comp:.0%}",           "across all tiers"),
        ('Assets Registered',      f"{len(af):,}",              f"${total_av/1e6:.1f}M value"),
        ('Documents Stored',       f"{len(df):,}",              f"{avg_bene:.1f} avg beneficiaries"),
    ])

    # ── Estate Completeness by Tier ──
    _sec(story, 'Estate Completeness by Tier')
    comp_tier = cf.groupby('subscription_tier')['estate_completeness_score'].mean()
    comp_ord  = {k: float(comp_tier.get(k, 0)) for k in ['Free','Basic','Premium','Family']}
    story.append(chart_bar(comp_ord, 'Average Estate Completeness Score by Tier (%)',
                           w=int(W-56), h=190, suffix='',
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))
    story.append(Spacer(1, 8))

    # Estate section completion table
    sec_avg = esf.groupby('section')['completion'].mean().reset_index().sort_values('completion')
    sec_rows = [[r['section'], f"{r['completion']:.0%}",
                 '✓' if r['completion'] > 0.5 else '⚠']
                for _, r in sec_avg.iterrows()]
    _table(story, ['Estate Section', 'Avg Completion', 'Status'], sec_rows,
           col_widths=[220, 120, 100])

    # ── Asset Registry ──
    _sec(story, 'Registered Asset Portfolio', 'ASSET BREAKDOWN')
    at = af.groupby('asset_type').agg(count=('customer_id','count'),
                                       value=('estimated_value_usd','sum')).reset_index()
    at = at.sort_values('value', ascending=False)
    at_chart = chart_hbar(
        dict(zip(at['asset_type'], at['value'])),
        'Total Registered Asset Value by Type (USD)',
        w=int(W-56), h=230, prefix='$'
    )
    story.append(at_chart)
    story.append(Spacer(1, 8))

    at_rows = [[r['asset_type'], f"{r['count']:,}", f"${r['value']:,.0f}",
                f"${r['value']/r['count']:,.0f}"]
               for _, r in at.iterrows()]
    _table(story, ['Asset Type','Count','Total Value','Avg Value'],
           at_rows, col_widths=[170, 70, 120, 110])

    # crypto adoption
    crypto_rate = cf.groupby('subscription_tier')['has_crypto_assets'].mean()
    crypto_ord  = {k: float(crypto_rate.get(k, 0)) * 100 for k in ['Free','Basic','Premium','Family']}
    story.append(chart_bar(crypto_ord, 'Crypto Asset Holders by Tier (%)',
                           w=int(W-56), h=180, suffix='%',
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))

    # ── Document Vault ──
    _sec(story, 'Document Vault Activity', 'DOCUMENT BREAKDOWN')
    doc_c = df.groupby('doc_type').size().reset_index(name='count').sort_values('count', ascending=False)
    doc_rows = [[r['doc_type'], f"{r['count']:,}",
                 f"{df[df['doc_type']==r['doc_type']]['verified'].mean():.0%}"]
                for _, r in doc_c.iterrows()]
    _table(story, ['Document Type', 'Count', 'Verified %'],
           doc_rows, col_widths=[210, 100, 130])

    # ── MRR Growth ──
    _sec(story, 'Revenue & Subscriber Growth', 'REVENUE TREND')
    mp = mf.groupby(['month','tier'])['mrr_usd'].sum().reset_index()
    months_s = sorted(mp['month'].unique())
    mrr_series = {}
    for t in ['Basic','Premium','Family']:
        td = mp[mp['tier']==t].set_index('month')['mrr_usd']
        mrr_series[t] = [float(td.get(m, 0)) for m in months_s]
    story.append(chart_line(mrr_series, 'Monthly Recurring Revenue by Tier (USD)',
                             w=int(W-56), h=200, prefix='$',
                             x_labels=[m[2:] for m in months_s]))
    story.append(Spacer(1, 8))

    # New subscribers + CAC side by side
    ns = mf.groupby('month')['new_subscribers'].sum().reset_index().sort_values('month').tail(24)
    ns_dict = {m[2:]: int(v) for m, v in zip(ns['month'], ns['new_subscribers'])}
    cac_ch = cf.groupby('acquisition_channel')['cac_usd'].mean().sort_values()
    cac_dict = {k: float(v) for k, v in cac_ch.items()}

    _side_by_side(story,
        chart_bar(ns_dict, 'New Subscribers / Month (Last 24)', w=255, h=180),
        chart_hbar(cac_dict, 'Avg CAC by Channel (USD)', w=255, h=180, prefix='$')
    )

    # Platforms consolidated
    plat = cf.groupby('subscription_tier')['platforms_consolidated'].mean()
    plat_ord = {k: float(plat.get(k, 0)) for k in ['Free','Basic','Premium','Family']}
    story.append(chart_bar(plat_ord, 'Avg Platforms Consolidated per Subscriber by Tier',
                           w=int(W-56), h=180,
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))

    churn_rate = cf['is_churned'].mean() * 100
    crypto_pct = cf['has_crypto_assets'].mean() * 100
    will_count = len(df[df['doc_type'].isin(['Last Will & Testament','Digital Will'])])
    top_sec = sec_avg.sort_values('completion',ascending=False).iloc[0]['section']
    low_sec = sec_avg.sort_values('completion').iloc[0]['section']
    _insight(story,
        f"DESCRIPTIVE SNAPSHOT  |  {active:,} active subscribers generate ${total_mrr:,} MRR "
        f"(${total_mrr*12:,} ARR). Average estate completeness stands at {avg_comp:.0%}. "
        f"{will_count:,} wills are stored. {crypto_pct:.0f}% of subscribers hold crypto assets "
        f"— a rapidly growing segment that underscores the platform's digital-first value. "
        f"Subscribers consolidate an average of {avg_plat:.1f} platforms, validating the "
        f"central consolidation proposition. {top_sec} is the most completed estate section; "
        f"{low_sec} is the most neglected — a direct upsell signal for the legal advisory tier. "
        f"Overall churn is {churn_rate:.1f}%.")

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 2 — DIAGNOSTIC
# ═════════════════════════════════════════════════════════════════════════════
def build_diagnostic_report(DATA, filters=None) -> bytes:
    tier_f = (filters or {}).get('tier', ['Free','Basic','Premium','Family'])
    customers        = DATA['customers']
    documents        = DATA['documents']
    estate_sections  = DATA['estate_sections']
    assets           = DATA['assets']
    feature_usage    = DATA['feature_usage']
    security_events  = DATA['security_events']
    rfm              = DATA['rfm']
    cohort           = DATA['cohort']
    tier_transitions = DATA['tier_transitions']

    cf  = customers[customers['subscription_tier'].isin(tier_f)]
    df  = documents[documents['tier'].isin(tier_f)]
    esf = estate_sections[estate_sections['tier'].isin(tier_f)]
    af  = assets[assets['tier'].isin(tier_f)]
    rf  = rfm[rfm['tier'].isin(tier_f)]
    ff  = feature_usage[feature_usage['tier'].isin(tier_f)]
    sf  = security_events[security_events['tier'].isin(tier_f)]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=28, rightMargin=28,
                            topMargin=44, bottomMargin=34)
    doc.layer_label = 'LAYER 02 · DIAGNOSTIC'
    story = []

    _cover(story, 'Diagnostic Analytics', 'LAYER 02',
           'Root cause analysis of platform behaviour — estate gap drivers, RFM segmentation, '
           'cohort retention, churn diagnostics, feature-retention correlation, '
           'tier movement funnels and security posture.',
           datetime.now().strftime('%d %B %Y'))

    # ── Estate Gap Diagnosis ──
    _sec(story, 'Estate Completeness Deep-Dive', 'ESTATE GAP ANALYSIS')
    sec_tier = esf.groupby(['section','tier'])['completion'].mean().reset_index()
    groups_sec = {}
    for sec in esf['section'].unique():
        groups_sec[sec[:16]] = [
            float(sec_tier[(sec_tier['section']==sec)&(sec_tier['tier']==t)]['completion'].values[0])
            if len(sec_tier[(sec_tier['section']==sec)&(sec_tier['tier']==t)])>0 else 0
            for t in ['Free','Basic','Premium','Family']
        ]
    story.append(chart_grouped_bar(groups_sec, ['Free','Basic','Premium','Family'],
                                   'Estate Section Completion by Tier',
                                   w=int(W-56), h=230, suffix=''))
    story.append(Spacer(1, 8))

    # Will completion rate by tier
    will_ids  = df[df['doc_type'].isin(['Last Will & Testament','Digital Will'])]['customer_id'].unique()
    will_rate = cf.groupby('subscription_tier').apply(
        lambda x: x['customer_id'].isin(will_ids).mean()).reset_index()
    will_rate.columns = ['tier','rate']
    will_ord = {k: float(will_rate[will_rate['tier']==k]['rate'].values[0])*100
                if k in will_rate['tier'].values else 0
                for k in ['Free','Basic','Premium','Family']}
    story.append(chart_bar(will_ord, 'Will / Digital Will Completion Rate by Tier (%)',
                           w=int(W-56), h=180, suffix='%',
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))

    # Estate gap table
    active_cf = cf[cf['is_churned']==0]
    bene_ids  = cf[cf['beneficiaries_assigned']>0]['customer_id'].unique()
    asset_ids = af['customer_id'].unique()
    poa_ids   = df[df['doc_type']=='Power of Attorney']['customer_id'].unique()
    vault_ids = ff[ff['feature']=='Password Vault']['customer_id'].unique()
    gaps = [
        ['No Will / Digital Will', str(len(active_cf[~active_cf['customer_id'].isin(will_ids)])), 'CRITICAL'],
        ['No Beneficiaries Set',   str(len(active_cf[active_cf['beneficiaries_assigned']==0])), 'HIGH'],
        ['No Assets Registered',   str(len(active_cf[~active_cf['customer_id'].isin(asset_ids)])), 'HIGH'],
        ['No Power of Attorney',   str(len(active_cf[~active_cf['customer_id'].isin(poa_ids)])), 'MEDIUM'],
        ['Password Vault Empty',   str(len(active_cf[~active_cf['customer_id'].isin(vault_ids)])), 'MEDIUM'],
    ]
    _table(story, ['Estate Gap', 'Active Subscribers Affected', 'Priority'], gaps,
           col_widths=[210, 160, 100])

    # ── RFM Segmentation ──
    _sec(story, 'RFM Customer Segmentation', 'RECENCY · FREQUENCY · MONETARY')
    seg_order = ['Champions','Loyal Customers','Potential Loyalists','At Risk','Hibernating']
    seg_counts = rf.groupby('rfm_segment').size().reindex(seg_order).fillna(0)
    story.append(chart_bar(dict(seg_counts), 'Customer Count by RFM Segment',
                           w=int(W-56), h=190))
    story.append(Spacer(1, 8))
    rfm_agg = rf.groupby('rfm_segment').agg(
        n=('customer_id','count'), r=('recency_days','mean'),
        f=('frequency_logins','mean'), m=('monetary_value_usd','mean')
    ).reindex(seg_order).dropna()
    rfm_rows = [[seg, f"{int(r['n']):,}", f"{r['r']:.0f}d",
                 f"{r['f']:.1f}", f"${r['m']:.0f}"]
                for seg, r in rfm_agg.iterrows()]
    _table(story, ['Segment','Customers','Avg Recency','Avg Logins','Avg LTV $'],
           rfm_rows, col_widths=[130, 80, 90, 90, 90])

    # ── Cohort Retention ──
    _sec(story, 'Cohort Retention Heatmap', 'MONTHLY RETENTION CURVES')
    recent = sorted(cohort['cohort_month'].unique())[-12:]
    ch_h   = cohort[cohort['cohort_month'].isin(recent)]
    pivot  = ch_h.pivot(index='cohort_month', columns='period_month',
                        values='retention_rate').fillna(0)
    story.append(chart_heatmap(
        pivot.values.tolist(), list(pivot.index),
        [f"M+{c}" for c in pivot.columns],
        'Cohort Retention Heatmap (%) — Last 12 Cohorts',
        w=int(W-56), h=260))
    story.append(Spacer(1, 8))

    # Retention summary table
    ret_rows = []
    for coh in recent[-8:]:
        row = cohort[cohort['cohort_month']==coh]
        sz  = int(row[row['period_month']==0]['cohort_size'].values[0]) if len(row[row['period_month']==0])>0 else 0
        m1  = f"{row[row['period_month']==1]['retention_rate'].values[0]*100:.0f}%" if len(row[row['period_month']==1])>0 else 'N/A'
        m3  = f"{row[row['period_month']==3]['retention_rate'].values[0]*100:.0f}%" if len(row[row['period_month']==3])>0 else 'N/A'
        m6  = f"{row[row['period_month']==6]['retention_rate'].values[0]*100:.0f}%" if len(row[row['period_month']==6])>0 else 'N/A'
        ret_rows.append([coh, str(sz), m1, m3, m6])
    _table(story, ['Cohort','Size','M+1','M+3','M+6'],
           ret_rows, col_widths=[90, 60, 100, 100, 100])

    # ── Churn + Feature-Retention ──
    _sec(story, 'Churn Root Cause & Feature-Retention', 'CHURN DIAGNOSTICS')
    cd  = cf[cf['is_churned']==1]['churn_reason'].value_counts()
    fr  = ff.merge(cf[['customer_id','is_churned']], on='customer_id')
    fra = fr.groupby('feature').agg(n=('customer_id','count'), churned=('is_churned','sum')).reset_index()
    fra['retention'] = (1 - fra['churned'] / fra['n']) * 100
    non_ret_d = {}
    for feat in ['Document Upload','Password Vault','Asset Registry','Beneficiary Designation','Legal Advisory']:
        aids = ff[ff['feature']==feat]['customer_id'].unique()
        non  = cf[~cf['customer_id'].isin(aids)]
        non_ret_d[feat] = (1 - non['is_churned'].mean()) * 100
    groups_fr = {r['feature'][:16]: [r['retention'], non_ret_d.get(r['feature'], 0)]
                 for _, r in fra.iterrows()}
    _side_by_side(story,
        chart_hbar(dict(cd), 'Churned Customers by Reason', w=248, h=200),
        chart_grouped_bar(groups_fr, ['Adopters','Non-Adopters'],
                          'Retention: Adopters vs Non-Adopters (%)',
                          w=248, h=200, suffix='%')
    )

    # ── Tier Transitions + Security ──
    _sec(story, 'Tier Transitions & Security Posture', 'FUNNEL & SECURITY')
    tt = DATA['tier_transitions']
    tt_rows = [[r['from_tier'], r['to_tier'], r['direction'],
                str(r['customers_transitioned']),
                f"${r['revenue_impact_monthly_usd']:+,.0f}",
                f"{r['avg_days_before_transition']:.0f}d"]
               for _, r in tt.iterrows()]

    te  = len(sf)
    he  = len(sf[sf['risk_level']=='High'])
    res = sf['resolved'].mean() * 100 if te > 0 else 0
    tfa = cf['two_fa_enabled'].mean() * 100
    ts  = tfa * 0.35 + res * 0.40 + (1 - he / max(te, 1)) * 100 * 0.25
    g   = chart_gauge(ts, 100, 'Vault Security Trust Score', w=190, h=175)
    tt_t = Table(
        [[Paragraph(h, ST['th']) for h in ['From','To','Dir','N','Rev Impact','Avg Days']]] +
        [[Paragraph(str(c), ST['tc']) for c in row] for row in tt_rows],
        colWidths=[58, 58, 62, 40, 82, 55]
    )
    tt_t.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, 0), colors.HexColor('#0d1221')),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [CARD, CARD2]),
        ('LINEABOVE',     (0, 0), (-1, 0), 2, GOLD),
        ('GRID',          (0, 0), (-1, -1), 0.35, MGRAY),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING',   (0, 0), (-1, -1), 5),
    ]))
    _side_by_side(story, g, tt_t, lw=200, rw=int(W - 58 - 200 - 8))

    top_cr   = cf[cf['is_churned']==1]['churn_reason'].value_counts().index[0] if cf['is_churned'].sum()>0 else 'N/A'
    best_rf  = fra.sort_values('retention', ascending=False).iloc[0]['feature'] if len(fra)>0 else 'N/A'
    low_sec  = esf.groupby('section')['completion'].mean().idxmin()
    no_will  = len(active_cf[~active_cf['customer_id'].isin(will_ids)])
    _insight(story,
        f"DIAGNOSTIC INSIGHT  |  {top_cr} is the #1 churn driver. "
        f"Users adopting {best_rf} show the highest retention — place it first in onboarding. "
        f"{no_will:,} active subscribers have no will — this is the platform's most critical gap to close "
        f"and the clearest signal for legal advisory upsell. {low_sec} is the least-completed estate section. "
        f"Cohort data shows months 1–3 post-signup are the highest-risk dropout window. "
        f"Security Trust Score {ts:.0f}/100 — 2FA adoption ({tfa:.0f}%) is the fastest improvement lever.",
        GOLD)

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 3 — PREDICTIVE
# ═════════════════════════════════════════════════════════════════════════════
def build_predictive_report(DATA, filters=None) -> bytes:
    tier_f = (filters or {}).get('tier', ['Free','Basic','Premium','Family'])
    customers       = DATA['customers']
    monthly_revenue = DATA['monthly_revenue']
    mrr_forecast    = DATA['mrr_forecast']

    cf = customers[customers['subscription_tier'].isin(tier_f)]
    mf = monthly_revenue[monthly_revenue['tier'].isin(tier_f)]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=28, rightMargin=28,
                            topMargin=44, bottomMargin=34)
    doc.layer_label = 'LAYER 03 · PREDICTIVE'
    story = []

    _cover(story, 'Predictive Analytics', 'LAYER 03',
           'Forward-looking models — churn risk scoring, customer lifetime value, '
           '9-month MRR forecasting, upgrade propensity, testamentary readiness pipeline '
           'and legal advisory conversion potential.',
           datetime.now().strftime('%d %B %Y'))

    # ── Churn Risk ──
    _sec(story, 'Churn Risk Overview', 'CHURN PROBABILITY SCORES')
    cf2  = cf.copy()
    low  = len(cf2[cf2['churn_probability_score']<=0.25])
    med  = len(cf2[(cf2['churn_probability_score']>0.25)&(cf2['churn_probability_score']<=0.50)])
    high = len(cf2[(cf2['churn_probability_score']>0.50)&(cf2['churn_probability_score']<=0.75)])
    crit = len(cf2[cf2['churn_probability_score']>0.75])
    _kpi_row(story, [
        ('Low Risk 0–25%',     f"{low:,}",  None),
        ('Medium 25–50%',      f"{med:,}",  None),
        ('High 50–75%',        f"{high:,}", None),
        ('Critical >75%',      f"{crit:,}", 'Immediate action'),
    ])

    bins_l  = ['0–10%','10–20%','20–30%','30–40%','40–50%','50–60%','60–70%','70–80%','80–90%','90–100%']
    bin_edges = [0, .10, .20, .30, .40, .50, .60, .70, .80, .90, 1.01]
    bin_counts = {l: int(((cf2['churn_probability_score']>=bin_edges[i])&
                           (cf2['churn_probability_score']<bin_edges[i+1])).sum())
                  for i, l in enumerate(bins_l)}
    story.append(chart_bar(bin_counts, 'Churn Probability Score Distribution',
                           w=int(W-56), h=190))
    story.append(Spacer(1, 10))

    # Churn score by tier table
    cs_tier = cf.groupby('subscription_tier')['churn_probability_score'].agg(['mean','median']).reset_index()
    cs_rows = [[r['subscription_tier'], f"{r['mean']:.3f}", f"{r['median']:.3f}"]
               for _, r in cs_tier.iterrows()]
    _table(story, ['Tier','Mean Churn Score','Median Churn Score'],
           cs_rows, col_widths=[140, 160, 160])

    # ── CLV ──
    _sec(story, 'Customer Lifetime Value Predictions', 'CLV MODELLING')
    clv_tier = cf.groupby('subscription_tier')['clv_predicted_usd'].agg(['mean','median','sum']).reset_index()
    clv_ord  = {r['subscription_tier']: float(r['mean'])
                for _, r in clv_tier.sort_values('subscription_tier').iterrows()}
    clv_ord_sorted = {k: clv_ord.get(k,0) for k in ['Free','Basic','Premium','Family']}

    clv_rows = [[r['subscription_tier'], f"${r['mean']:,.0f}",
                 f"${r['median']:,.0f}", f"${r['sum']:,.0f}"]
                for _, r in clv_tier.iterrows()]
    _table(story, ['Tier','Mean CLV','Median CLV','Total Predicted CLV'],
           clv_rows, col_widths=[100, 120, 120, 135])

    story.append(chart_bar(clv_ord_sorted, 'Average Predicted CLV by Tier (USD)',
                           w=int(W-56), h=190, prefix='$',
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))
    story.append(Spacer(1, 10))

    # Risk-Value table (top 15)
    top_risk = cf.sort_values('churn_probability_score', ascending=False).head(15)\
        [['customer_id','subscription_tier','churn_probability_score',
          'clv_predicted_usd','estate_completeness_score']].copy()
    rv_rows = [[r['customer_id'], r['subscription_tier'],
                f"{r['churn_probability_score']:.3f}",
                f"${r['clv_predicted_usd']:,.0f}",
                f"{r['estate_completeness_score']:.0%}"]
               for _, r in top_risk.iterrows()]
    _table(story, ['Customer','Tier','Churn Score','Predicted CLV','Estate %'],
           rv_rows, col_widths=[90, 65, 90, 105, 90])

    # ── MRR Forecast ──
    _sec(story, 'MRR Forecast — 9-Month Projection', 'FORWARD-LOOKING REVENUE')
    hist = mf.groupby('month')['mrr_usd'].sum().reset_index().sort_values('month').tail(14)
    fct  = DATA['mrr_forecast'].groupby('forecast_month').agg(
        proj=('projected_mrr_usd','sum'),
        lo=('lower_bound_usd','sum'),
        hi=('upper_bound_usd','sum')
    ).reset_index()
    all_months  = list(hist['month']) + list(fct['forecast_month'])
    hist_vals   = list(hist['mrr_usd'])
    fct_vals    = list(fct['proj'])
    combined    = hist_vals + [None] * (len(fct_vals) - 1)
    f_combined  = [None] * (len(hist_vals) - 1) + fct_vals
    x_short     = [m[2:] for m in all_months]
    story.append(chart_line(
        {'Historical': combined, 'Forecast': f_combined},
        'MRR Historical + 9-Month Forecast (USD)',
        w=int(W-56), h=210, prefix='$', x_labels=x_short
    ))
    story.append(Spacer(1, 8))

    fct_rows = [[r['forecast_month'], f"${r['lo']:,.0f}",
                 f"${r['proj']:,.0f}", f"${r['hi']:,.0f}"]
                for _, r in fct.iterrows()]
    _table(story, ['Forecast Month','Lower Bound','Projected MRR','Upper Bound'],
           fct_rows, col_widths=[120, 110, 120, 110])

    # ── Legal Advisory + Upgrade Pipeline ──
    _sec(story, 'Legal Advisory & Testamentary Readiness Pipeline', 'PREMIUM TIER PIPELINE')
    lrc_bins = ['Not Ready','Early Stage','Developing','Near Ready','Ready']
    lrc_cut  = pd.cut(cf['legal_advisory_readiness_score'],
                      bins=[0,.2,.4,.6,.8,1.0], labels=lrc_bins)
    pipeline = lrc_cut.value_counts().reindex(lrc_bins)
    story.append(chart_bar(dict(pipeline), 'Legal Advisory Readiness Funnel',
                           w=int(W-56), h=190))
    story.append(Spacer(1, 8))

    # Upgrade propensity
    up_dist = {}
    for lbl, lo, hi in [('<20%',0,.2),('20–40%',.2,.4),('40–60%',.4,.6),('60–80%',.6,.8),('>80%',.8,1.01)]:
        up_dist[lbl] = len(cf[(cf['upgrade_propensity_score']>=lo)&(cf['upgrade_propensity_score']<hi)])
    story.append(chart_bar(up_dist, 'Upgrade Propensity Score Distribution',
                           w=int(W-56), h=180))
    story.append(Spacer(1, 8))

    tu = cf[cf['subscription_tier'].isin(['Free','Basic'])]\
        .sort_values('upgrade_propensity_score', ascending=False).head(12)\
        [['customer_id','subscription_tier','upgrade_propensity_score',
          'estate_completeness_score','clv_predicted_usd']]
    tu_rows = [[r['customer_id'], r['subscription_tier'],
                f"{r['upgrade_propensity_score']:.3f}",
                f"{r['estate_completeness_score']:.0%}",
                f"${r['clv_predicted_usd']:,.0f}"]
               for _, r in tu.iterrows()]
    _table(story, ['ID','Tier','Upgrade Score','Estate %','Predicted CLV'],
           tu_rows, col_widths=[90, 65, 95, 80, 110])

    hrc      = len(cf[cf['churn_probability_score']>0.6])
    acp      = cf[cf['subscription_tier']=='Premium']['clv_predicted_usd'].mean()
    lrc_rdy  = len(cf[cf['legal_advisory_readiness_score']>0.6])
    end_mrr  = fct.iloc[-1]['proj']
    _insight(story,
        f"PREDICTIVE INSIGHT  |  {hrc:,} subscribers carry churn probability >60% — "
        f"targeted estate-gap outreach should be actioned immediately. "
        f"Premium CLV averages ${acp:,.0f} — highest-ROI retention segment. "
        f"MRR is forecast to reach ${end_mrr:,.0f} by December 2026. "
        f"{lrc_rdy:,} subscribers exceed the Legal Advisory readiness threshold — "
        f"a concrete pipeline for the testamentary premium tier launch.")

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()


# ═════════════════════════════════════════════════════════════════════════════
# LAYER 4 — PRESCRIPTIVE
# ═════════════════════════════════════════════════════════════════════════════
def build_prescriptive_report(DATA, filters=None) -> bytes:
    tier_f = (filters or {}).get('tier', ['Free','Basic','Premium','Family'])
    customers     = DATA['customers']
    ab_tests      = DATA['ab_tests']
    documents     = DATA['documents']
    feature_usage = DATA['feature_usage']
    assets        = DATA['assets']

    cf = customers[customers['subscription_tier'].isin(tier_f)]
    df = documents[documents['tier'].isin(tier_f)]
    ff = feature_usage[feature_usage['tier'].isin(tier_f)]
    af = assets[assets['tier'].isin(tier_f)]

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=28, rightMargin=28,
                            topMargin=44, bottomMargin=34)
    doc.layer_label = 'LAYER 04 · PRESCRIPTIVE'
    story = []

    _cover(story, 'Prescriptive Analytics', 'LAYER 04',
           'Action-oriented recommendations — A/B test results, estate gap interventions, '
           'at-risk subscriber action plans, uplift modelling, legal advisory launch strategy '
           'and pricing ROI analysis.',
           datetime.now().strftime('%d %B %Y'))

    # ── A/B Tests ──
    _sec(story, 'A/B Test Performance', 'EXPERIMENT RESULTS')
    abw = ab_tests.pivot(
        index=['test_id','test_name','category','statistical_significance'],
        columns='variant', values=['conversion_rate','revenue_impact_usd']
    ).reset_index()
    abw.columns = ['test_id','test_name','category','sig',
                   'ctrl_cv','treat_cv','ctrl_rv','treat_rv']
    abw['lift']     = ((abw['treat_cv']-abw['ctrl_cv'])/abw['ctrl_cv'].replace(0,1))*100
    abw['rev_lift'] = abw['treat_rv'] - abw['ctrl_rv']
    abw['winner']   = abw['lift'].apply(lambda x: 'Treatment' if x>0 else 'Control')

    lift_dict = {r['test_name'][:22]: float(r['lift']) for _,r in abw.iterrows()}
    story.append(chart_hbar(
        {k: abs(v) for k,v in sorted(lift_dict.items(), key=lambda x: x[1], reverse=True)},
        'A/B Test Conversion Lift Magnitude (%)', w=int(W-56), h=240, suffix='%'
    ))
    story.append(Spacer(1, 8))

    ab_rows = [[r['test_name'][:30], r['category'],
                f"{r['lift']:+.1f}%", f"${r['rev_lift']:+,.0f}",
                f"{r['sig']:.0%}", r['winner']]
               for _,r in abw.sort_values('lift',ascending=False).iterrows()]
    _table(story, ['Test Name','Category','Conv Lift','Rev Lift','Sig','Winner'],
           ab_rows, col_widths=[148, 72, 62, 78, 58, 72])

    # ── Estate Gap Interventions ──
    _sec(story, 'Estate Gap Intervention Map', 'PRESCRIPTIVE ACTIONS')
    active_cf   = cf[cf['is_churned']==0]
    will_ids    = df[df['doc_type'].isin(['Last Will & Testament','Digital Will'])]['customer_id'].unique()
    bene_ids    = cf[cf['beneficiaries_assigned']>0]['customer_id'].unique()
    asset_ids   = af['customer_id'].unique()
    poa_ids     = df[df['doc_type']=='Power of Attorney']['customer_id'].unique()
    vault_ids   = ff[ff['feature']=='Password Vault']['customer_id'].unique()
    gap_data = {
        'No Will':              len(active_cf[~active_cf['customer_id'].isin(will_ids)]),
        'No Beneficiaries':     len(active_cf[active_cf['beneficiaries_assigned']==0]),
        'No Assets Registered': len(active_cf[~active_cf['customer_id'].isin(asset_ids)]),
        'No Power of Attorney': len(active_cf[~active_cf['customer_id'].isin(poa_ids)]),
        'Password Vault Empty': len(active_cf[~active_cf['customer_id'].isin(vault_ids)]),
    }
    story.append(chart_hbar(gap_data, 'Active Subscribers with Critical Estate Gaps',
                             w=int(W-56), h=210))
    story.append(Spacer(1, 8))

    # Estate completion vs churn
    comp_b = pd.cut(cf['estate_completeness_score'], bins=5,
                    labels=['0–20%','20–40%','40–60%','60–80%','80–100%'])
    cf_b   = cf.copy(); cf_b['band'] = comp_b
    churn_by_comp = cf_b.groupby('band', observed=True)['is_churned'].mean()
    story.append(chart_bar(
        {str(k): float(v)*100 for k,v in churn_by_comp.items()},
        'Churn Rate by Estate Completion Band (%) — lower completion = higher churn',
        w=int(W-56), h=180, suffix='%',
        colors_list=[RED, ORANGE, GOLD, CYAN, colors.HexColor('#00d4a0')]
    ))
    story.append(Spacer(1, 10))

    # ── At-Risk Intervention Table ──
    _sec(story, 'At-Risk Subscriber Intervention Triggers', 'CHURN PREVENTION')
    ar = cf[(cf['churn_probability_score']>0.55)&(cf['is_churned']==0)].copy()
    ar['Priority']  = ar['churn_probability_score'].apply(lambda x: 'CRITICAL' if x>0.75 else 'HIGH')
    ar['Save_Val']  = (ar['clv_predicted_usd'] * 0.30).round(2)
    ar['Action']    = ar.apply(lambda r: (
        'Legal advisory unlock + 20% discount'
        if r['legal_advisory_readiness_score'] > 0.5
        else 'Estate gap email + beneficiary prompt'
        if r['beneficiaries_assigned'] == 0
        else 'Re-engage: complete your estate plan'
    ), axis=1)
    _kpi_row(story, [
        ('At-Risk Users',    f"{len(ar):,}",               'Need intervention'),
        ('Critical (>75%)',  f"{len(ar[ar['Priority']=='CRITICAL']):,}", None),
        ('High (55–75%)',    f"{len(ar[ar['Priority']=='HIGH']):,}",    None),
        ('Total Save Value', f"${ar['Save_Val'].sum():,.0f}","30% CLV recovery"),
    ])
    ar_disp = ar.sort_values('churn_probability_score', ascending=False).head(20)
    ar_rows = [[r['customer_id'], r['subscription_tier'],
                f"{r['churn_probability_score']:.3f}",
                f"{r['estate_completeness_score']:.0%}",
                str(r['beneficiaries_assigned']),
                f"${r['Save_Val']:,.0f}",
                r['Priority'], r['Action'][:30]]
               for _,r in ar_disp.iterrows()]
    _table(story, ['ID','Tier','Churn','Estate%','Bene','Save$','Priority','Action'],
           ar_rows, col_widths=[62,45,52,52,32,62,52,100])

    # ── Uplift + Legal Advisory ──
    _sec(story, 'Uplift Modelling & Legal Advisory Launch Strategy', 'STRATEGIC RECOMMENDATIONS')
    up_tier = cf.groupby('subscription_tier')['uplift_score'].mean().reset_index()
    up_ord  = {r['subscription_tier']: float(r['uplift_score'])
               for _,r in up_tier.sort_values('subscription_tier').iterrows()}
    up_sorted = {k: up_ord.get(k,0) for k in ['Free','Basic','Premium','Family']}

    lrc_bins_l = ['Not Ready','Early Stage','Developing','Near Ready','Ready']
    lrc_cut    = pd.cut(cf['legal_advisory_readiness_score'],
                        bins=[0,.2,.4,.6,.8,1.0], labels=lrc_bins_l)
    pipeline   = lrc_cut.value_counts().reindex(lrc_bins_l)
    lrc_dict   = {k: int(v) for k,v in pipeline.items()}

    _side_by_side(story,
        chart_bar(up_sorted, 'Avg Uplift Score by Tier', w=248, h=200,
                  colors_list=[BLUE, CYAN, GOLD, ORANGE]),
        chart_bar(lrc_dict, 'Legal Advisory Readiness Pipeline', w=248, h=200)
    )

    # ── Pricing ROI ──
    _sec(story, 'Pricing Tier ROI — LTV:CAC Analysis')
    tm = cf.groupby('subscription_tier').agg(
        avg_clv=('clv_predicted_usd','mean'),
        avg_cac=('cac_usd','mean'),
        n=('customer_id','count')
    ).reset_index()
    tm['ltv_cac'] = tm['avg_clv'] / tm['avg_cac'].replace(0, 1)
    tm['order']   = tm['subscription_tier'].map({'Free':0,'Basic':1,'Premium':2,'Family':3})
    tm = tm.sort_values('order')
    ltv_dict = {r['subscription_tier']: float(r['ltv_cac']) for _,r in tm.iterrows()}
    ltv_sorted = {k: ltv_dict.get(k,0) for k in ['Free','Basic','Premium','Family']}
    story.append(chart_bar(ltv_sorted, 'LTV:CAC Ratio by Tier (higher = better acquisition ROI)',
                           w=int(W-56), h=190, suffix='x',
                           colors_list=[BLUE, CYAN, GOLD, ORANGE]))
    story.append(Spacer(1, 8))
    tm_rows = [[r['subscription_tier'], f"${r['avg_clv']:,.0f}",
                f"${r['avg_cac']:,.0f}", f"{r['ltv_cac']:.1f}x"]
               for _,r in tm.iterrows()]
    _table(story, ['Tier','Avg CLV','Avg CAC','LTV:CAC Ratio'],
           tm_rows, col_widths=[100, 130, 130, 110])

    best_ab    = abw.sort_values('lift', ascending=False).iloc[0]['test_name']
    lrc_ready  = len(cf[cf['legal_advisory_readiness_score']>0.6])
    best_tier  = tm.sort_values('ltv_cac', ascending=False).iloc[0]['subscription_tier']
    no_will_n  = gap_data.get('No Will', 0)
    _insight(story,
        f"PRESCRIPTIVE ACTIONS  |  "
        f"(1) {gap_data.get('No Will',0):,} subscribers have no will — "
        f"trigger an estate wizard prompt immediately; this is the platform's core value gap. "
        f"(2) Intervene on {len(ar):,} at-risk subscribers — personalised estate-gap "
        f"outreach can recover ${ar['Save_Val'].sum():,.0f} in CLV. "
        f"(3) Scale '{best_ab}' — highest-performing A/B test. "
        f"(4) {lrc_ready:,} subscribers are legal-advisory-ready — "
        f"prioritise them in the testamentary premium tier launch. "
        f"(5) {best_tier} delivers the best LTV:CAC — focus acquisition spend on "
        f"channels converting to this tier for maximum capital efficiency.",
        GOLD)

    doc.build(story, onFirstPage=_page, onLaterPages=_page)
    return buf.getvalue()
