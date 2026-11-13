"""Download a small sample library from The Turing Way (CC-BY-4.0).

Chapters are pinned to the same commit the KIDS26 Team 20 MCP server uses
(corpus/sources.yaml in stjude-biohackathon/KIDS26-Team20), so module 5 talks
about the same content you index in module 1.

    python data/get_sample_docs.py

Files are saved as .txt in data/sample_docs/ (ignored by Git).
Licence: The Turing Way Community, CC-BY-4.0, https://the-turing-way.netlify.app
"""

from pathlib import Path

import requests

COMMIT = "bb3f7abb56a40cd92a654fb51e4ec91f429cca2a"
BASE = f"https://raw.githubusercontent.com/the-turing-way/the-turing-way/{COMMIT}/book/website"
CHAPTERS = [
    "reproducible-research/overview.md",
    "reproducible-research/vcs.md",
    "reproducible-research/renv.md",
    "reproducible-research/rdm.md",
    "reproducible-research/testing.md",
    "reproducible-research/code-quality.md",
]

out = Path(__file__).resolve().parent / "sample_docs"
out.mkdir(exist_ok=True)

for chapter in CHAPTERS:
    res = requests.get(f"{BASE}/{chapter}", timeout=60)
    res.raise_for_status()
    name = "turing-way_" + chapter.replace("/", "_").replace(".md", ".txt")
    header = f"Source: The Turing Way ({BASE}/{chapter}), CC-BY-4.0\n\n"
    (out / name).write_text(header + res.text, encoding="utf-8")
    print(f"saved {name}")

print(f"\n{len(CHAPTERS)} documents in {out}")
