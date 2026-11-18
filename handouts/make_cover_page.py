"""Build the cover page for the combined workshop handouts (US Letter, 1 page).

    pip install reportlab pillow pypdf
    python handouts/make_cover_page.py           # -> handouts/cover_page.pdf
    python handouts/make_cover_page.py --duplex  # page numbers for double-sided printing

The contents list shows each handout's page number in workshop_handouts.pdf. Page
counts are read from the built handout PDFs, so build those first
(combine_handouts.py --build does this in the right order).
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "cover_page.pdf"
W, H = letter
M = 0.75 * inch

NAVY = colors.HexColor("#2C4659")
RED = colors.HexColor("#C8323B")
BLUE = colors.HexColor("#1170B8")
ORANGE = colors.HexColor("#E8762D")
TEAL = colors.HexColor("#0E9E8B")
INK = colors.HexColor("#1F2328")
MUTED = colors.HexColor("#5A6270")
RULE = colors.HexColor("#C9CED6")
TINT = colors.HexColor("#F2F5F8")

TITLE_LINES = ["MyGPT: Building your own", "RAG Swiss Army knife", "for reliable knowledge discovery"]

# (label, title, minutes, colour, handout PDF)
CONTENTS = [
    ("", "Workshop overview", None, NAVY, "intro_handout.pdf"),
    ("1", "Install MyGPT and build a library", 30, RED, "module1_handout.pdf"),
    ("2", "Query your library with the MyGPT API", 20, BLUE, "module2_handout.pdf"),
    ("3", "Build an evaluation dataset", 30, ORANGE, "module3_handout.pdf"),
    ("4", "Recalibrate QRS, ARS and HI weights", 20, TEAL, "module4_handout.pdf"),
    ("5", "MCP server + skills for AI coding", 20, NAVY, "module5_handout.pdf"),
]
DEFAULT_PAGES = {"intro_handout.pdf": 1}  # used if a handout PDF isn't built yet; modules are 2 pages


def page_numbers(duplex=False):
    """Start page of each handout in the combined PDF (the cover is page 1).

    With duplex, a blank page pads any handout that ends on a front side, the same rule
    combine_handouts.py --duplex uses, so every handout starts on a new sheet.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None
    done, out = 1, []  # pages so far: the cover
    for *_, pdf in CONTENTS:
        if duplex and done % 2:
            done += 1
        out.append(done + 1)
        path = HERE / pdf
        if PdfReader and path.exists():
            done += len(PdfReader(path).pages)
        else:
            done += DEFAULT_PAGES.get(pdf, 2)
    return out


def image(c, name, x, y, h):
    """Draw an asset at height h with its aspect ratio; returns the width."""
    from PIL import Image

    iw, ih = Image.open(ASSETS / name).size
    w = h * iw / ih
    c.drawImage(str(ASSETS / name), x, y, width=w, height=h, mask="auto")
    return w


def draw(c, duplex=False):
    # background + top band with the five module colours
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, stroke=0, fill=1)
    c.setFillColor(NAVY)
    c.rect(0, H - 0.55 * inch, W, 0.55 * inch, stroke=0, fill=1)
    for i, col in enumerate([RED, BLUE, ORANGE, TEAL, NAVY]):
        c.setFillColor(col)
        c.rect(i * W / 5, H - 0.66 * inch, W / 5, 0.07 * inch, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(M, H - 0.35 * inch, "KIDS26  ·  ST. JUDE CHILDREN’S RESEARCH HOSPITAL")
    c.drawRightString(W - M, H - 0.35 * inch, "HANDS-ON WORKSHOP")

    # logo + title
    top = H - 1.0 * inch
    logo_h = 1.75 * inch
    logo_w = image(c, "mygpt_logo_stacked.png", M, top - logo_h, logo_h)
    tx = M + logo_w + 0.4 * inch
    room = W - M - tx
    size = 30
    while size > 18 and max(stringWidth(t, "Helvetica-Bold", size) for t in TITLE_LINES) > room:
        size -= 0.5
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", size)
    y = top - size + 2
    for line in TITLE_LINES:
        c.drawString(tx, y, line)
        y -= size + 4
    c.setFillColor(RED)
    c.rect(tx, y + size - 6, 0.9 * inch, 3, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica", 12)
    c.drawString(tx, y + size - 24, "Participant workbook  ·  5 modules  ·  about 2 hours")

    # name / table fields
    fy = top - logo_h - 0.75 * inch
    c.setFillColor(TINT)
    c.roundRect(M, fy - 0.2 * inch, W - 2 * M, 0.62 * inch, 6, stroke=0, fill=1)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(M + 0.2 * inch, fy, "Name")
    c.drawString(W - M - 2.35 * inch, fy, "Table #")
    c.setStrokeColor(MUTED)
    c.setLineWidth(0.7)
    c.line(M + 0.75 * inch, fy - 2, W - M - 2.6 * inch, fy - 2)
    c.line(W - M - 1.7 * inch, fy - 2, W - M - 0.2 * inch, fy - 2)

    # contents
    cy = fy - 0.85 * inch
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(M, cy, "In this workbook")
    c.setFillColor(RED)
    c.rect(M, cy - 8, 0.5 * inch, 2.5, stroke=0, fill=1)
    row_h = 0.5 * inch
    y = cy - 0.55 * inch
    for (label, title, mins, col, _), page in zip(CONTENTS, page_numbers(duplex)):
        r = 0.16 * inch
        c.setFillColor(col)
        c.circle(M + r, y + 4, r, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(M + r, y, label or "i")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 13)
        name = f"Module {label} — {title}" if label else title
        c.drawString(M + 0.5 * inch, y, name)
        nx = M + 0.5 * inch + stringWidth(name, "Helvetica-Bold", 13) + 8
        if mins:
            c.setFillColor(col)
            c.setFont("Helvetica-Bold", 9.5)
            c.drawString(nx, y + 1, f"{mins} min")
            nx += stringWidth(f"{mins} min", "Helvetica-Bold", 9.5) + 8
        # dotted leader to the page number
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 12)
        pw = stringWidth(str(page), "Helvetica-Bold", 12)
        c.drawRightString(W - M, y, str(page))
        c.setStrokeColor(RULE)
        c.setDash(1, 3)
        c.line(nx + 4, y + 2, W - M - pw - 8, y + 2)
        c.setDash()
        y -= row_h

    # stickers
    # heights chosen so the lettering on all three stickers looks the same size
    stickers = [("sticker_privacy_first.png", 1.45 * inch),
                ("sticker_your_data.png", 1.7 * inch),
                ("sticker_in_control.png", 1.15 * inch)]
    from PIL import Image

    widths = [h * Image.open(ASSETS / n).size[0] / Image.open(ASSETS / n).size[1] for n, h in stickers]
    gap = (W - 2 * M - sum(widths)) / 2
    sx, mid = M, 0.95 * inch + 1.7 * inch / 2  # vertically centred on one line
    for (n, h), w in zip(stickers, widths):
        image(c, n, sx, mid - h / 2, h)
        sx += w + gap

    # footer
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    c.line(M, 0.72 * inch, W - M, 0.72 * inch)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 8)
    c.drawString(M, 0.52 * inch, "Workshop materials: github.com/stjude-c3d/MyGPT-workshop")
    c.drawRightString(W - M, 0.52 * inch, "MyGPT paper: doi.org/10.1038/s41467-026-78509-6")


def build_cover(out=OUT, duplex=False):
    c = canvas.Canvas(str(out), pagesize=letter)
    c.setTitle("MyGPT Workshop — cover")
    c.setAuthor("MyGPT Workshop, KIDS26")
    draw(c, duplex)
    c.showPage()
    c.save()
    print("wrote", out)


def main():
    import argparse

    ap = argparse.ArgumentParser(description="Build the handout cover page.")
    ap.add_argument("--duplex", action="store_true",
                    help="page numbers for combine_handouts.py --duplex (blank backs after cover and overview)")
    ap.add_argument("--out", type=Path, default=OUT, help=f"output PDF (default: {OUT.name})")
    args = ap.parse_args()
    build_cover(args.out, args.duplex)


if __name__ == "__main__":
    main()
