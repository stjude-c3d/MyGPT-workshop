"""Combine the cover, intro and module handouts into one printable PDF.

    pip install reportlab pillow pypdf
    python handouts/combine_handouts.py            # combine the existing PDFs
    python handouts/combine_handouts.py --build    # rebuild every handout and the cover first

Writes handouts/workshop_handouts.pdf with one bookmark per handout.

For double-sided printing, add --duplex: a blank page follows the cover and the 1-page
overview, so each gets its own sheet and every module starts on a new sheet. The cover's
contents list is redrawn with the matching page numbers.

    python handouts/combine_handouts.py --duplex --out handouts/workshop_handouts_duplex.pdf
"""

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
OUT = HERE / "workshop_handouts.pdf"
TITLE = "MyGPT: Building your own RAG Swiss Army knife for reliable knowledge discovery — handouts"

COVER = ("Cover", "cover_page.pdf", "make_cover_page.py")
# (bookmark title, PDF, script that builds it), in print order after the cover
HANDOUTS = [
    ("Workshop overview", "intro_handout.pdf", "make_intro_handout.py"),
    ("Module 1 — Install MyGPT and build a library", "module1_handout.pdf", "make_module1_handout.py"),
    ("Module 2 — Query your library with the MyGPT API", "module2_handout.pdf", "make_module2_handout.py"),
    ("Module 3 — Build an evaluation dataset", "module3_handout.pdf", "make_module3_handout.py"),
    ("Module 4 — Recalibrate QRS, ARS and HI weights", "module4_handout.pdf", "make_module4_handout.py"),
    ("Module 5 — MCP server + skills for AI coding", "module5_handout.pdf", "make_module5_handout.py"),
]


def build_all():
    # the cover reads the handouts' page counts for its contents list, so it goes last
    for _, _, script in HANDOUTS + [COVER]:
        subprocess.run([sys.executable, str(HERE / script)], cwd=HERE, check=True)


def combine(out=OUT, cover=True, duplex=False):
    parts = ([COVER] if cover else []) + HANDOUTS
    missing = [pdf for _, pdf, _ in parts if not (HERE / pdf).exists()]
    if missing:
        sys.exit(f"Missing: {', '.join(missing)}. Run with --build, or build them first.")

    paths = {pdf: HERE / pdf for _, pdf, _ in parts}
    tmp = None
    if cover and duplex:
        # redraw the cover so its contents list shows the duplex page numbers
        from make_cover_page import build_cover

        tmp = tempfile.TemporaryDirectory()
        paths[COVER[1]] = Path(tmp.name) / COVER[1]
        build_cover(paths[COVER[1]], duplex=True)

    writer = PdfWriter()
    for title, pdf, _ in parts:
        reader = PdfReader(paths[pdf])
        if duplex and len(writer.pages) % 2:
            # previous handout ended on a front side: leave its back blank
            box = reader.pages[0].mediabox
            writer.add_blank_page(width=box.width, height=box.height)
        start = len(writer.pages)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_outline_item(title=title, page_number=start)
        print(f"  p.{start + 1:>2}  {title}  ({len(reader.pages)} page{'s' if len(reader.pages) > 1 else ''})")

    writer.add_metadata({"/Title": TITLE, "/Author": "MyGPT Workshop, KIDS26"})
    writer.page_mode = "/UseOutlines"
    with open(out, "wb") as fh:
        writer.write(fh)
    if tmp:
        tmp.cleanup()
    print(f"wrote {out} ({len(writer.pages)} pages)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="rebuild every handout and the cover before combining")
    ap.add_argument("--no-cover", action="store_true", help="leave out the cover page")
    ap.add_argument("--duplex", action="store_true",
                    help="for double-sided printing: blank backs after the cover and overview, "
                         "so each handout starts on a new sheet")
    ap.add_argument("--out", type=Path, default=OUT, help=f"output PDF (default: {OUT.name})")
    args = ap.parse_args()
    if args.build:
        build_all()
    combine(args.out, cover=not args.no_cover, duplex=args.duplex)


if __name__ == "__main__":
    main()
