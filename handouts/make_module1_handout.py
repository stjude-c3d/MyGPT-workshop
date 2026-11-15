"""Build the printable Module 1 handout (US Letter, 2 pages).

    pip install reportlab pillow
    python handouts/make_module1_handout.py      # -> handouts/module1_handout.pdf

The handout is a visual reference plus a workbook: blank boxes and lines are filled in
by hand during the workshop. Content mirrors 01-install-and-build-library/README.md and
settings_experiment.md.
"""

from pathlib import Path

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image as RLImage, KeepTogether, PageBreak, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, INK, MUTED, ORANGE, ROOT, RULE, TEAL, TINT, Box, P, build,
                         grid, make_chrome, section, write_lines)

OUT = Path(__file__).resolve().parent / "module1_handout.pdf"
chrome = make_chrome(1, "Install MyGPT and build a library", 30, "01-install-and-build-library/README.md")


# ----------------------------------------------------------------------------- page 1
def page1():
    story = []

    # name line + objectives / timeline side by side
    name = Table([[P("<b>Name</b>", "cell"), "", P("<b>Laptop OS</b>", "cell"), "",
                   P("<b>Table #</b>", "cell"), ""]],
                 colWidths=[0.5 * inch, 3.1 * inch, 0.75 * inch, 1.5 * inch, 0.6 * inch, 1.05 * inch])
    name.setStyle(TableStyle([("LINEBELOW", (1, 0), (1, 0), 0.6, MUTED),
                              ("LINEBELOW", (3, 0), (3, 0), 0.6, MUTED),
                              ("LINEBELOW", (5, 0), (5, 0), 0.6, MUTED),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    story += [name, Spacer(1, 6)]

    objectives = [
        P("<b>By the end of this module you will:</b>"),
        P("① have MyGPT (UI, backend, Ollama) running on your laptop"),
        P("② have built a document library from the BioASQ PDFs or your own files"),
        P("③ know how each pipeline setting changes what MyGPT retrieves and how confident it is"),
    ]
    timeline_cells = [
        ("0–5", "Check the stack", BLUE),
        ("5–15", "Build baseline library", ORANGE),
        ("15–28", "Settings experiment", TEAL),
        ("28–30", "Checkpoint", INK),
    ]
    tl = Table([[P(f'<font color="white"><b>{t} min</b><br/>{label}</font>', "center")
                 for t, label, _ in timeline_cells]],
               colWidths=[0.6 * inch, 1.05 * inch, 0.95 * inch, 0.7 * inch], rowHeights=[30])
    tl.setStyle(TableStyle([("BACKGROUND", (i, 0), (i, 0), c) for i, (_, _, c) in enumerate(timeline_cells)]
                           + [("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                              ("LINEAFTER", (0, 0), (-2, 0), 1.5, colors.white)]))
    top = Table([[objectives, tl]], colWidths=[CONTENT_W - 3.4 * inch, 3.4 * inch])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("BACKGROUND", (0, 0), (0, 0), TINT),
                             ("LEFTPADDING", (0, 0), (0, 0), 8),
                             ("TOPPADDING", (0, 0), (-1, -1), 5),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(top)

    # pipeline figure: top part of workflow_and_customization.png (without the customization boxes)
    src = Image.open(ROOT / "images" / "workflow_and_customization.png")
    crop = src.crop((0, 0, src.width, int(src.height * 0.635)))
    fig_path = Path(__file__).resolve().parent / ".module1_pipeline.png"
    crop.save(fig_path)
    fig_w = CONTENT_W * 0.8
    fig_h = fig_w * crop.height / crop.width
    story += [section("How MyGPT answers a question", BLUE),
              RLImage(str(fig_path), width=fig_w, height=fig_h, hAlign="CENTER"),
              P("① <b>Pre-processing</b> splits documents into chunks and indexes them (embeddings + BM25). "
                "② <b>Real-time Q&amp;A</b> retrieves the best chunks and scores them (QRS). "
                "③ <b>Generation</b>: the LLM answers from those chunks, and MyGPT scores the answer "
                "(ARS, HI).", "small")]

    # Step 1
    checks = [
        ("docker ps", "MyGPT frontend, backend and database show <b>Up</b>"),
        ("curl -s http://localhost:11434", "prints <b>Ollama is running</b>"),
        ("ollama list", "embedding model + LLM listed (nomic-embed-text, llama3 / gpt-oss)"),
        ("MyGPT UI", "opens (usually localhost:3000 or localhost) and you can sign in"),
    ]
    step1 = grid([["", P("Run / open", "head"), P("You should see", "head")]]
                 + [[Box(), P(c, "mono"), P(e, "cell")] for c, e in checks],
                 [0.25 * inch, 2.4 * inch, CONTENT_W - 2.65 * inch], header_color=BLUE)
    story += [section("Step 1 — Check the stack", BLUE, "5 min"), step1]

    # Step 2
    baseline = [
        ("Library name", "<b>workshop-library-A</b>  (module 2 uses this name in .env)"),
        ("Documents", "data/BioASQ/pdfs/  (or your own files)"),
        ("Chunking", "Fixed-size, <b>1000</b> characters, overlap <b>Yes</b>"),
        ("Embedding model", "<b>nomic-embed-text</b>  — cannot be changed after building"),
        ("Keyword search / reranker", "BM25 <b>on</b>  ·  reranker <b>qnli-electra-base</b> (default)"),
    ]
    settings = grid([["", P("Upload → Advanced settings", "head"), P("Baseline value", "head")]]
                    + [[Box(), P(k, "cellb"), P(v, "cell")] for k, v in baseline],
                    [0.25 * inch, 1.65 * inch, CONTENT_W - 1.9 * inch], header_color=ORANGE)
    record = grid([[P("#", "head"), P("Question you asked (on-topic, plus one off-topic)", "head"),
                    P("QRS", "head"), P("ARS", "head"), P("HI", "head"), P("Sources cited?", "head")]]
                  + [[P(str(i), "cellb"), "", "", "", "", ""] for i in (1, 2, 3)],
                  [0.25 * inch, 4.2 * inch, 0.55 * inch, 0.55 * inch, 0.55 * inch, CONTENT_W - 6.1 * inch],
                  header_color=ORANGE, row_h=[None, 22, 22, 22])
    key = P("<b>Reading the scores (0–100):</b> "
            '<font color="#0E9E8B"><b>QRS</b></font> = how well the question matches your library; '
            '<font color="#0E9E8B"><b>ARS</b></font> = how much the answer relies on retrieved text — '
            "<b>higher is better</b>. "
            '<font color="#E8762D"><b>HI</b></font> = hallucination index — <b>lower is better</b>. '
            "Low QRS/ARS with high HI means: check the sources.", "small")
    story.append(KeepTogether([section("Step 2 — Build the baseline library", ORANGE, "10 min"),
                               settings, Spacer(1, 5), record, Spacer(1, 3), key]))
    return story


# ----------------------------------------------------------------------------- page 2
def page2():
    story = []

    # settings reference
    ref = [
        ("Chunk size", "Upload", "Smaller = precise hits, less context; larger = more context, diluted match"),
        ("Chunk overlap", "Upload", "Stops answers being cut at chunk edges; bigger index"),
        ("Embedding model", "Upload", "Biggest effect on retrieval; multilingual model for non-English documents"),
        ("Distance function", "Upload", "Changes the distance scale — QRS/ARS cutoffs must match it"),
        ("BM25", "Upload", "Keyword search; helps with gene names, IDs, acronyms"),
        ("Reranker", "Upload / Chat", "Re-orders retrieved chunks: better precision, slower answers"),
        ("Max chunks (k)", "Chat", "More context for the LLM, but more noise and slower"),
        ("QC best / worst", "Chat", "Distance range mapped to QRS 100→0; raise QCworst to let weaker matches in"),
        ("LLM, temperature", "Chat", "Generation model and creativity; keep temperature low for facts"),
    ]
    story += [section("Settings cheat sheet", BLUE),
              grid([[P("Setting", "head"), P("Where", "head"), P("Typical effect of changing it", "head")]]
                   + [[P(a, "cellb"), P(b, "cell"), P(c, "cell")] for a, b, c in ref],
                   [1.25 * inch, 0.85 * inch, CONTENT_W - 2.1 * inch], header_color=BLUE, zebra=True)]

    # Step 3 choose experiment
    exps = [
        ("Chunk size", "1000", "750", "Do precise facts get higher QRS? Are answers fragmented?"),
        ("Overlap", "Yes", "No", "Are answers that span two chunks now incomplete?"),
        ("Embedding model", "nomic-embed-text", "bge-m3", "Change in QRS for domain terms"),
        ("Keyword search", "BM25 on", "BM25 off", "Questions with IDs, gene names or acronyms"),
        ("Reranker", "off", "on", "Source order, answer quality, latency"),
        ("Max chunks (no rebuild)", "5", "10", "Longer answers? More noise? Change in ARS?"),
    ]
    story += [section("Step 3 — Settings experiment: change ONE setting", TEAL, "13 min"),
              P("Tick one row, build library B with only that setting changed, then ask both libraries "
                "the <b>same</b> questions.", "small"), Spacer(1, 3),
              grid([["", P("Experiment", "head"), P("Library A", "head"), P("Library B", "head"),
                     P("What to look for", "head")]]
                   + [[Box(), P(a, "cellb"), P(b, "cell"), P(c, "cell"), P(d, "cell")]
                      for a, b, c, d in exps],
                   [0.25 * inch, 1.45 * inch, 1.1 * inch, 0.85 * inch, CONTENT_W - 3.65 * inch],
                   header_color=TEAL, zebra=True),
              Spacer(1, 5)]

    libb = Table([[P("<b>Library B name:</b>", "cell"), "", P("<b>Setting changed:</b>", "cell"), ""]],
                 colWidths=[1.0 * inch, 2.5 * inch, 1.1 * inch, CONTENT_W - 4.6 * inch])
    libb.setStyle(TableStyle([("LINEBELOW", (1, 0), (1, 0), 0.6, MUTED),
                              ("LINEBELOW", (3, 0), (3, 0), 0.6, MUTED),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
    story += [libb, Spacer(1, 6)]

    hdr = ["Question", "QRS A", "QRS B", "ARS A", "ARS B", "HI A", "HI B", "Better answer: A / B — why?"]
    results = grid([[P(h, "head") for h in hdr]] + [[""] * 8 for _ in range(4)],
                   [1.75 * inch] + [0.48 * inch] * 6 + [CONTENT_W - 1.75 * inch - 2.88 * inch],
                   header_color=TEAL, row_h=[None] + [23] * 4)
    story += [results]

    # reflect
    story += [section("Reflect", TEAL),
              write_lines(1, "1. Did the setting change the retrieved chunks, the scores, or both?"),
              write_lines(1, "2. Was a higher QRS always a better answer? Note one case where it wasn’t."),
              write_lines(1, "3. Which setting would you keep for your own documents?")]

    # checkpoint + troubleshooting side by side
    cp = [
        "<b>workshop-library-A</b> is on the MyGPT home page with all documents",
        "An on-topic question gives <b>QRS &gt; 50</b> and cites your documents",
        "An off-topic question gives <b>low QRS, high HI</b><br/>"
        '<font color="#5A6270">e.g. “Who are the keynote speakers at KIDS26 at St. Jude?”</font>',
        "Your results table has at least one row comparing A and B",
    ]
    cp_t = Table([[Box(9), P(c, "cell")] for c in cp], colWidths=[0.22 * inch, 3.25 * inch])
    cp_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    trouble = [
        ("Upload fails", "Backend still starting: docker logs &lt;backend&gt;, wait for migrations"),
        ("Port 11434 refused", "Start the Ollama app, or run ollama serve"),
        ("Indexing very slow", "More Docker CPU/RAM; fewer documents; nomic-embed-text"),
        ("QRS always 0", "Embedding model and QC cutoffs don’t match: use defaults or raise QCworst"),
        ("Scanned PDF, no text", "MyGPT reads the text layer only: run OCR first"),
    ]
    tr_t = Table([[P(a, "cellb"), P(b, "cell")] for a, b in trouble], colWidths=[1.05 * inch, 2.45 * inch])
    tr_t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                              ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE),
                              ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("TOPPADDING", (0, 0), (-1, -1), 2),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    bottom = Table([[[section("Checkpoint", INK, "2 min"), cp_t],
                     [section("Stuck?", ORANGE), tr_t]]],
                   colWidths=[CONTENT_W / 2, CONTENT_W / 2])
    bottom.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("BACKGROUND", (0, 0), (0, 0), TINT),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 0),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [Spacer(1, 6), bottom]
    return story


def main():
    build(OUT, page1() + [PageBreak()] + page2(), chrome, "MyGPT Workshop \u2014 Module 1 handout")
    (Path(__file__).resolve().parent / ".module1_pipeline.png").unlink(missing_ok=True)


if __name__ == "__main__":
    main()
