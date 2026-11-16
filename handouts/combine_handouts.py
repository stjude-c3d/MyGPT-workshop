"""Combine the intro and module handouts into one printable PDF.

    pip install reportlab pillow pypdf
    python handouts/combine_handouts.py            # combine the existing PDFs
    python handouts/combine_handouts.py --build    # rebuild every handout first

Writes handouts/workshop_handouts.pdf with one bookmark per handout. Each module
handout has an even number of pages, so with --blank-after-intro every module starts
on a new sheet when printed double-sided.
"""

import argparse
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

HERE = Path(__file__).resolve().parent
OUT = HERE / "workshop_handouts.pdf"
TITLE = "MyGPT: Building your own RAG Swiss Army knife for reliable knowledge discovery — handouts"

# (bookmark title, PDF, script that builds it), in print order
HANDOUTS = [
    ("Workshop overview", "intro_handout.pdf", "make_intro_handout.py"),
    ("Module 1 — Install MyGPT and build a library", "module1_handout.pdf", "make_module1_handout.py"),
    ("Module 2 — Query your library with the MyGPT API", "module2_handout.pdf", "make_module2_handout.py"),
    ("Module 3 — Build an evaluation dataset", "module3_handout.pdf", "make_module3_handout.py"),
    ("Module 4 — Recalibrate QRS, ARS and HI weights", "module4_handout.pdf", "make_module4_handout.py"),
    ("Module 5 — MCP server + skills for AI coding", "module5_handout.pdf", "make_module5_handout.py"),
]


def build_all():
    for _, _, script in HANDOUTS:
        subprocess.run([sys.executable, str(HERE / script)], cwd=HERE, check=True)


def combine(out=OUT, blank_after_intro=False):
    missing = [pdf for _, pdf, _ in HANDOUTS if not (HERE / pdf).exists()]
    if missing:
        sys.exit(f"Missing: {', '.join(missing)}. Run with --build, or build them first.")

    writer = PdfWriter()
    for i, (title, pdf, _) in enumerate(HANDOUTS):
        start = len(writer.pages)
        reader = PdfReader(HERE / pdf)
        for page in reader.pages:
            writer.add_page(page)
        writer.add_outline_item(title=title, page_number=start)
        print(f"  p.{start + 1:>2}  {title}  ({len(reader.pages)} page{'s' if len(reader.pages) > 1 else ''})")
        if i == 0 and blank_after_intro and len(reader.pages) % 2:
            box = reader.pages[0].mediabox
            writer.add_blank_page(width=box.width, height=box.height)

    writer.add_metadata({"/Title": TITLE, "/Author": "MyGPT Workshop, KIDS26"})
    writer.page_mode = "/UseOutlines"
    with open(out, "wb") as fh:
        writer.write(fh)
    print(f"wrote {out} ({len(writer.pages)} pages)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--build", action="store_true", help="rebuild every handout before combining")
    ap.add_argument("--blank-after-intro", action="store_true",
                    help="insert a blank page after the 1-page intro for double-sided printing")
    ap.add_argument("--out", type=Path, default=OUT, help=f"output PDF (default: {OUT.name})")
    args = ap.parse_args()
    if args.build:
        build_all()
    combine(args.out, args.blank_after_intro)


if __name__ == "__main__":
    main()
