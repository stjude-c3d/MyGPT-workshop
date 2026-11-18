"""Build the one-page workshop overview handout (US Letter).

    pip install reportlab pillow
    python handouts/make_intro_handout.py        # -> handouts/intro_handout.pdf

Logos and stickers live in handouts/assets/.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Flowable, Image, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, H, INK, MARGIN, MUTED, ORANGE, RULE, TEAL, TINT, W, P, build,
                         checklist, hexstr, section)

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "intro_handout.pdf"

WORKSHOP_TITLE = "MyGPT: Building your own RAG Swiss Army knife for reliable knowledge discovery"
TITLE_LINES = ["MyGPT: Building your own RAG Swiss Army knife", "for reliable knowledge discovery"]

# Logo colours
NAVY = colors.HexColor("#2C4659")
RED = colors.HexColor("#C8323B")

MODULES = [
    (1, "Install MyGPT and build a library", 30, RED,
     "Install MyGPT on your laptop and build a library from your documents, learning how each "
     "pipeline setting (chunking, embeddings, BM25, reranker) shapes the results.",
     "workshop-library-A + B, settings worksheet"),
    (2, "Query your library with the MyGPT API", 20, BLUE,
     "Script the RAG round trip against the MyGPT backend APIs: retrieve → generate → score, "
     "then batch-query questions from Python and the command line.",
     "02_query_results.csv with QRS, ARS, HI"),
    (3, "Build an evaluation dataset", 30, ORANGE,
     "Derive questions from your library, label answers by hand or with an LLM judge, and check the "
     "judge against human labels (Cohen’s κ) to make a trustworthy benchmark.",
     "03_eval_dataset.csv — your labelled benchmark"),
    (4, "Recalibrate QRS, ARS and HI weights", 20, TEAL,
     "Run a global sensitivity analysis on your benchmark to choose confidence-score weights for "
     "your domain, and check with bootstrapping that the gain is real.",
     "04_recalibrated_weights.json"),
    (5, "MCP server + skills for AI coding", 20, NAVY,
     "Run the Turing Way MCP server (KIDS26 Team 20) and add its skills to GitHub Copilot, so coding "
     "help is grounded in cited, reproducible-research guidance.",
     "Copilot connected to the Turing Way MCP + skills"),
]


class Badge(Flowable):
    """Filled circle with the module number."""

    def __init__(self, n, color, d=0.42 * inch):
        super().__init__()
        self.n, self.color, self.d = n, color, d
        self.width = self.height = d

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.circle(self.d / 2, self.d / 2, self.d / 2, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 15)
        c.drawCentredString(self.d / 2, self.d / 2 - 5.2, str(self.n))


class Timeline(Flowable):
    """Proportional bar of the five modules (minutes)."""

    def __init__(self, width=CONTENT_W, height=0.36 * inch):
        super().__init__()
        self.width, self.height = width, height

    def draw(self):
        c = self.canv
        total = sum(m[2] for m in MODULES)
        x, t = 0, 0
        bar_y, bar_h = 11, self.height - 11
        for n, _, mins, color, *_ in MODULES:
            w = self.width * mins / total
            c.setFillColor(color)
            c.rect(x, bar_y, w - 2, bar_h, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 8.5)
            c.drawCentredString(x + (w - 2) / 2, bar_y + bar_h / 2 - 3, f"Module {n} · {mins} min")
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 6.8)
            c.drawString(x, 1, f"{t}′")
            x += w
            t += mins
        c.drawRightString(self.width, 1, f"{t}′")


def header(canvas, doc):
    canvas.saveState()
    # logo, left
    logo_h = 0.62 * inch
    lw = logo_h * 832 / 272
    canvas.drawImage(str(ASSETS / "mygpt_logo_horizontal.png"), MARGIN, H - 0.5 * inch - logo_h,
                     width=lw, height=logo_h, mask="auto")
    # title block, right
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(W - MARGIN, H - 0.42 * inch, "KIDS26  ·  ST. JUDE CHILDREN’S RESEARCH HOSPITAL")
    # workshop title on two lines, sized to fit beside the logo
    room = CONTENT_W - lw - 0.3 * inch
    size = 17
    while size > 11 and max(stringWidth(t, "Helvetica-Bold", size) for t in TITLE_LINES) > room:
        size -= 0.5
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", size)
    for i, line in enumerate(TITLE_LINES):
        canvas.drawRightString(W - MARGIN, H - 0.66 * inch - i * (size + 3), line)
    canvas.setFillColor(INK)
    canvas.setFont("Helvetica", 9.5)
    canvas.drawRightString(W - MARGIN, H - 1.17 * inch,
                           "Hands-on workshop  ·  5 modules  ·  about 2 hours  ·  bring your laptop")
    # colour rule
    y = H - 1.36 * inch
    segs = [RED, BLUE, ORANGE, TEAL, NAVY]
    for i, col in enumerate(segs):
        canvas.setFillColor(col)
        canvas.rect(MARGIN + i * CONTENT_W / 5, y, CONTENT_W / 5, 3, stroke=0, fill=1)
    # footer
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(MARGIN, 0.32 * inch, "Workshop materials: github.com/stjude-c3d/MyGPT-workshop")
    canvas.drawRightString(W - MARGIN, 0.32 * inch,
                           "Patel et al., Nature Communications (2026), doi:10.1038/s41467-026-78509-6")
    canvas.restoreState()


def module_rows():
    rows = []
    for n, title, mins, color, desc, output in MODULES:
        body = [P(f'<font size="10.5"><b>{title}</b></font>&nbsp;&nbsp;'
                  f'<font size="8" color="{hexstr(color)}"><b>{mins} min</b></font>'),
                Spacer(1, 1.5), P(desc, "cell")]
        out = [P(f'<font size="6.8" color="#5A6270"><b>YOU LEAVE WITH</b></font>', "cell"),
               P(output, "cellb")]
        rows.append([Badge(n, color), body, out])
    t = Table(rows, colWidths=[0.6 * inch, CONTENT_W - 2.55 * inch, 1.95 * inch])
    style = [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 7),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
             ("LEFTPADDING", (0, 0), (0, -1), 4),
             ("LINEBELOW", (0, 0), (-1, -2), 0.5, RULE),
             ("BACKGROUND", (2, 0), (2, -1), TINT)]
    for i, m in enumerate(MODULES):
        style.append(("LINEBEFORE", (2, i), (2, i), 2.5, m[3]))
    t.setStyle(TableStyle(style))
    return t


def story():
    intro = P("<b>MyGPT</b> is St. Jude’s open-source, privacy-first retrieval-augmented generation (RAG) "
              "platform. It answers questions from <i>your</i> library of publications, cites the exact "
              "source passages, and reports how much to trust each answer with three scores: question "
              "relevance (<b>QRS</b>), answer relevance (<b>ARS</b>) and hallucination index (<b>HI</b>). "
              "By default everything runs on your own laptop, so your documents never leave it.<br/><br/>"
              "In this workshop you take MyGPT from install to evaluation: build a library, script it, "
              "benchmark it, tune its confidence scores for your field, and plug it into an AI coding "
              "assistant. Each module’s output feeds the next.")
    top = intro

    before = checklist([
        "<b>Docker Desktop</b>, Git, VS Code + GitHub Copilot, uv",
        "Pick where the models run: <b>A</b> Ollama on your laptop (16 GB RAM, 25 GB disk; "
        "<font face='Courier'>ollama pull nomic-embed-text</font> and <font face='Courier'>llama3</font>) · "
        "<b>B</b> St. Jude Ollama server (St. Jude staff; St. Jude Wi-Fi or Cloudflare on) · "
        "<b>C</b> OpenAI API (your own key, API billing on)",
        "Smaller laptop? Options B and C need no model downloads",
    ], width=3.2 * inch)
    links = Table([[P(f"<b>{a}</b><br/><font face='Courier' size='7.2'>{b}</font>", "cell")] for a, b in [
        ("Workshop", "github.com/stjude-c3d/MyGPT-workshop"),
        ("Setup guide", "…/MyGPT-workshop → SETUP.md"),
        ("MyGPT", "github.com/stjude/MyGPT"),
        ("Evaluations", "github.com/stjude/MyGPT-evaluations"),
        ("Turing Way MCP", "github.com/stjude-biohackathon/KIDS26-Team20"),
    ]], colWidths=[3.0 * inch])
    links.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 2),
                               ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                               ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE)]))
    # sticker + QR code for the paper
    st = 1.1 * inch
    qr = 1.05 * inch
    paper = [P('<font size="10.5" color="#2C4659"><b>Read the MyGPT paper</b></font>'),
             Spacer(1, 3),
             P("Patel J, <i>et al.</i> Democratizing reliable knowledge-seeking with MyGPT: a privacy-first, "
               "open-source retrieval-augmented generation platform. <i>Nature Communications</i> (2026).",
               "cell"),
             Spacer(1, 3),
             P("<font face='Courier' size='7.4'>doi.org/10.1038/s41467-026-78509-6</font>", "cell")]
    stickers = Table([[Image(str(ASSETS / "sticker_in_control.png"), width=st * 945 / 538, height=st),
                       Image(str(ASSETS / "qr_mygpt_paper.png"), width=qr, height=qr * 500 / 502),
                       paper]],
                     colWidths=[2.35 * inch, 1.25 * inch, 2.75 * inch])
    stickers.setStyle(TableStyle([("ALIGN", (0, 0), (1, 0), "CENTER"),
                                  ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                  ("LINEBEFORE", (1, 0), (1, 0), 0.5, RULE)]))
    bottom = Table([[[section("Before you arrive", RED), before, Spacer(1, 6),
                      P("Full setup steps are in SETUP.md. Option A: pull the models <b>before</b> the day; "
                        "conference Wi-Fi is too slow for multi-GB downloads.", "small")],
                     [section("Resources", BLUE), links]]],
                   colWidths=[CONTENT_W / 2, CONTENT_W / 2])
    bottom.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("BACKGROUND", (0, 0), (0, 0), TINT),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))

    return [top, Spacer(1, 6),
            section("Your path through the workshop", NAVY), Spacer(1, 4), Timeline(), Spacer(1, 4),
            module_rows(), Spacer(1, 8), bottom, Spacer(1, 8), stickers]


def main():
    build(OUT, story(), header, WORKSHOP_TITLE, top_margin=1.52 * inch)


if __name__ == "__main__":
    main()
