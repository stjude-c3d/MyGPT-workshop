"""Shared layout for the printable module handouts (US Letter, ReportLab).

Each make_moduleN_handout.py imports from here so every handout has the same header
band, colours, tables, tick boxes and handwriting lines.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent

# MyGPT figure palette
BLUE = colors.HexColor("#1170B8")
ORANGE = colors.HexColor("#E8762D")
TEAL = colors.HexColor("#0E9E8B")
INK = colors.HexColor("#1F2328")
MUTED = colors.HexColor("#5A6270")
RULE = colors.HexColor("#C9CED6")
TINT = colors.HexColor("#F2F5F8")

W, H = letter
MARGIN = 0.5 * inch
CONTENT_W = W - 2 * MARGIN

base = dict(fontName="Helvetica", fontSize=8.6, leading=11, textColor=INK)
S = {
    "body": ParagraphStyle("body", **base),
    "small": ParagraphStyle("small", **{**base, "fontSize": 7.6, "leading": 9.4, "textColor": MUTED}),
    "cell": ParagraphStyle("cell", **{**base, "fontSize": 7.8, "leading": 9.6}),
    "cellb": ParagraphStyle("cellb", **{**base, "fontName": "Helvetica-Bold", "fontSize": 7.8, "leading": 9.6}),
    "head": ParagraphStyle("head", **{**base, "fontName": "Helvetica-Bold", "fontSize": 7.6,
                                      "leading": 9.4, "textColor": colors.white}),
    "h2": ParagraphStyle("h2", **{**base, "fontName": "Helvetica-Bold", "fontSize": 11, "leading": 14,
                                  "spaceBefore": 5, "spaceAfter": 2}),
    "mono": ParagraphStyle("mono", **{**base, "fontName": "Courier", "fontSize": 8, "leading": 10}),
    "monosm": ParagraphStyle("monosm", **{**base, "fontName": "Courier", "fontSize": 7.2, "leading": 9}),
    "center": ParagraphStyle("center", **{**base, "alignment": TA_CENTER, "fontSize": 7.6, "leading": 9.4}),
}


def hexstr(color):
    return color.hexval().replace("0x", "#")


class Box(Flowable):
    """Empty tick box drawn as a square (the built-in fonts have no hollow-box glyph)."""

    def __init__(self, size=7.5, color=INK):
        super().__init__()
        self.size, self.color = size, color
        self.width = self.height = size

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(0.8)
        self.canv.rect(0, 0, self.size, self.size, stroke=1, fill=0)


def P(text, style="body"):
    return Paragraph(text, S[style])


def section(title, color, minutes=None):
    """Coloured section title with an optional time chip."""
    label = f'<font color="{hexstr(color)}">■</font>&nbsp; {title}'
    if minutes:
        label += f'&nbsp;&nbsp;<font size="8" color="#5A6270">{minutes}</font>'
    return P(label, "h2")


def grid(data, widths, header_color=INK, zebra=False, row_h=None):
    t = Table(data, colWidths=widths, rowHeights=row_h, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_color),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1.8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.8),
    ]
    if zebra:
        for r in range(2, len(data), 2):
            style.append(("BACKGROUND", (0, r), (-1, r), TINT))
    t.setStyle(TableStyle(style))
    return t


def write_lines(n, label=None, width=CONTENT_W, height=15):
    """Ruled lines for handwriting."""
    rows = [[P(label, "cellb")]] if label else []
    rows += [[""] for _ in range(n)]
    t = Table(rows, colWidths=[width], rowHeights=[None] * (1 if label else 0) + [height] * n)
    t.setStyle(TableStyle([
        ("LINEBELOW", (0, 1 if label else 0), (-1, -1), 0.5, RULE),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return t


def fill_in(pairs, widths):
    """Label + underline blanks on one row, e.g. [("Name", 3.1*inch), ...]."""
    cells, cols, lines = [], [], []
    for i, (label, blank_w) in enumerate(pairs):
        cells += [P(f"<b>{label}</b>", "cell"), ""]
        cols += [widths[i], blank_w]
        lines.append(("LINEBELOW", (2 * i + 1, 0), (2 * i + 1, 0), 0.6, MUTED))
    t = Table([cells], colWidths=cols)
    t.setStyle(TableStyle(lines + [("LEFTPADDING", (0, 0), (-1, -1), 2),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    return t


def name_line():
    return fill_in([("Name", 3.1 * inch), ("Laptop OS", 1.5 * inch), ("Table #", 1.05 * inch)],
                   [0.5 * inch, 0.75 * inch, 0.6 * inch])


def objectives_and_timeline(objectives, timeline):
    """objectives: list of strings; timeline: list of (minutes, label, colour)."""
    numerals = "①②③④⑤"
    left = [P("<b>By the end of this module you will:</b>")]
    left += [P(f"{numerals[i]} {o}") for i, o in enumerate(objectives)]
    widths = [max(0.6, 0.075 * len(label) + 0.25) * inch for _, label, _ in timeline]
    scale = 3.3 * inch / sum(widths)
    tl = Table([[P(f'<font color="white"><b>{t} min</b><br/>{label}</font>', "center")
                 for t, label, _ in timeline]],
               colWidths=[w * scale for w in widths], rowHeights=[30])
    tl.setStyle(TableStyle([("BACKGROUND", (i, 0), (i, 0), c) for i, (_, _, c) in enumerate(timeline)]
                           + [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LINEAFTER", (0, 0), (-2, 0), 1.5, colors.white)]))
    top = Table([[left, tl]], colWidths=[CONTENT_W - 3.4 * inch, 3.4 * inch])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("BACKGROUND", (0, 0), (0, 0), TINT),
                             ("LEFTPADDING", (0, 0), (0, 0), 8),
                             ("TOPPADDING", (0, 0), (-1, -1), 5),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return top


def side_by_side(left, right, left_title, right_title, tint_left=True):
    """Two panels on one row (e.g. Checkpoint | Stuck?). left/right are flowables."""
    t = Table([[[left_title, left], [right_title, right]]], colWidths=[CONTENT_W / 2, CONTENT_W / 2])
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"),
             ("LEFTPADDING", (0, 0), (-1, -1), 6),
             ("TOPPADDING", (0, 0), (-1, -1), 0),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]
    if tint_left:
        style.append(("BACKGROUND", (0, 0), (0, 0), TINT))
    t.setStyle(TableStyle(style))
    return t


def checklist(items, width=3.25 * inch):
    t = Table([[Box(9), P(c, "cell")] for c in items], colWidths=[0.22 * inch, width])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def trouble_table(rows, widths=(1.05 * inch, 2.45 * inch)):
    t = Table([[P(a, "cellb"), P(b, "cell")] for a, b in rows], colWidths=list(widths))
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2),
                           ("TOPPADDING", (0, 0), (-1, -1), 2),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    return t


def make_chrome(module, title, minutes, readme, total_pages=2):
    """Header band + footer drawn on every page."""

    def chrome(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(BLUE)
        canvas.rect(0, H - 0.62 * inch, W, 0.62 * inch, stroke=0, fill=1)
        canvas.setFillColor(ORANGE)
        canvas.rect(0, H - 0.66 * inch, W * 0.42, 0.04 * inch, stroke=0, fill=1)
        canvas.setFillColor(TEAL)
        canvas.rect(W * 0.42, H - 0.66 * inch, W * 0.58, 0.04 * inch, stroke=0, fill=1)

        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(MARGIN, H - 0.24 * inch,
                          f"KIDS26  ·  MyGPT WORKSHOP  ·  MODULE {module} OF 5")
        canvas.setFont("Helvetica-Bold", 15)
        canvas.drawString(MARGIN, H - 0.47 * inch, title)
        canvas.setFont("Helvetica-Bold", 11)
        canvas.drawRightString(W - MARGIN, H - 0.47 * inch, f"{minutes} min")

        canvas.setFillColor(MUTED)
        canvas.setFont("Helvetica", 7)
        canvas.drawString(MARGIN, 0.32 * inch, f"github.com/stjude-c3d/MyGPT-workshop  ·  {readme}")
        canvas.drawRightString(W - MARGIN, 0.32 * inch, f"Page {doc.page} of {total_pages}")
        canvas.restoreState()

    return chrome


def build(out, story, chrome, title, top_margin=0.82 * inch):
    doc = SimpleDocTemplate(str(out), pagesize=letter, leftMargin=MARGIN, rightMargin=MARGIN,
                            topMargin=top_margin, bottomMargin=0.5 * inch,
                            title=title, author="MyGPT Workshop, KIDS26")
    doc.build(story, onFirstPage=chrome, onLaterPages=chrome)
    print("wrote", out)
