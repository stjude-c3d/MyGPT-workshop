"""Build the printable Module 2 handout (US Letter, 2 pages).

    pip install reportlab pillow
    python handouts/make_module2_handout.py      # -> handouts/module2_handout.pdf

Content mirrors 02-query-via-api/README.md and 02_query_api.ipynb. The grey
"instructor run" values come from 02_query_api_final.ipynb, so attendees can tell
whether their numbers are in the right range.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, KeepTogether, PageBreak, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, INK, MUTED, ORANGE, RULE, TEAL, TINT, Box, P, build, checklist,
                         grid, make_chrome, name_line, objectives_and_timeline, section,
                         side_by_side, trouble_table, write_lines)

OUT = Path(__file__).resolve().parent / "module2_handout.pdf"
chrome = make_chrome(2, "Query your library with the MyGPT API", 20, "02-query-via-api/README.md")

EX = '<font color="#5A6270" size="7">'  # instructor-run example values


class RoundTrip(Flowable):
    """Diagram: container -> sign in -> retrieve -> generate -> score."""

    def __init__(self, width=CONTENT_W, height=1.45 * inch):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, *_):
        return self.width, self.height

    def _box(self, x, y, w, h, color, num, title, endpoint, result):
        c = self.canv
        c.setFillColor(colors.white)
        c.setStrokeColor(color)
        c.setLineWidth(1.2)
        c.roundRect(x, y, w, h, 5, stroke=1, fill=1)
        c.setFillColor(color)
        c.roundRect(x, y + h - 17, w, 17, 5, stroke=0, fill=1)
        c.rect(x, y + h - 17, w, 8, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawCentredString(x + w / 2, y + h - 12, f"{num}  {title}")
        c.setFillColor(INK)
        c.setFont("Courier-Bold", 6.9)
        c.drawCentredString(x + w / 2, y + h - 29, endpoint)
        c.setFont("Helvetica", 7.4)
        for i, line in enumerate(result.split("\n")):
            c.drawCentredString(x + w / 2, y + h - 42 - i * 9.5, line)

    def _arrow(self, x1, x2, y, color=MUTED):
        c = self.canv
        c.setStrokeColor(color)
        c.setFillColor(color)
        c.setLineWidth(1.2)
        c.line(x1, y, x2 - 4, y)
        p = c.beginPath()
        p.moveTo(x2, y)
        p.lineTo(x2 - 5, y + 3)
        p.lineTo(x2 - 5, y - 3)
        p.close()
        c.drawPath(p, stroke=0, fill=1)

    def draw(self):
        c = self.canv
        gap, n = 14, 4
        bw = (self.width - gap * (n - 1)) / n
        bh = 0.88 * inch
        y = self.height - bh - 4
        boxes = [
            (INK, "0", "Sign in", "POST /token/", "username + password\n→ JWT access token"),
            (BLUE, "①", "Retrieve", "POST /api/get_context/", "top-k chunks (sources)\n→ QRS + sem / key / rerank"),
            (ORANGE, "②", "Generate", "POST /api/ollama_generate/", "question + chunks to LLM\n→ answer text"),
            (TEAL, "③", "Score", "POST /api/save_answer/", "answer vs. chunks\n→ ARS + HI (ML, equation)"),
        ]
        for i, b in enumerate(boxes):
            x = i * (bw + gap)
            self._box(x, y, bw, bh, *b)
            if i < n - 1:
                self._arrow(x + bw + 2, x + bw + gap - 1, y + bh / 2)

        # bracket under 1-3: client.ask()
        x1, x2, by = bw + gap, self.width, y - 8
        c.setStrokeColor(MUTED)
        c.setLineWidth(0.8)
        c.line(x1 + 4, by, x2 - 4, by)
        c.line(x1 + 4, by, x1 + 4, by + 4)
        c.line(x2 - 4, by, x2 - 4, by + 4)
        c.setFillColor(INK)
        c.setFont("Courier-Bold", 7.6)
        c.drawCentredString((x1 + x2) / 2, by - 10, "client.ask(question)")
        c.setFont("Helvetica", 7.2)
        c.setFillColor(MUTED)
        c.drawCentredString((x1 + x2) / 2, by - 19, "runs ①–③ and returns one row: answer, QRS, ARS, HI, HI_equation")
        c.drawString(0, by - 10, "JupyterLab container →")
        c.drawString(0, by - 19, "host.docker.internal:8000")


# ----------------------------------------------------------------------------- page 1
def page1():
    story = [name_line(), Spacer(1, 6),
             objectives_and_timeline(
                 ["sign in to the MyGPT backend and call its REST API from Python",
                  "run the RAG round trip yourself: retrieve → generate → score",
                  "batch-query questions and save the results for module 3"],
                 [("0–5", "Concepts + sign in", BLUE),
                  ("5–15", "Notebook: single query, then batch", ORANGE),
                  ("15–20", "CLI + checkpoint", TEAL)])]

    setup = [
        ("Library from module 1 exists", "MyGPT home page shows <b>workshop-library-A</b>; MyGPT + your models running"),
        ("Edit <font face='Courier'>.env</font>",
         "<font face='Courier'>MYGPT_DATASET=workshop-library-A</font>, MYGPT_USERNAME, MYGPT_PASSWORD "
         "— leave the URLs unchanged. Option B or C (SETUP.md): also set your model lines"),
        ("Start the container", "<font face='Courier'>docker compose pull</font> then "
                                "<font face='Courier'>docker compose up -d</font>"),
        ("Open JupyterLab", "<font face='Courier'>http://localhost:8888/lab?token=mygpt-workshop</font>"),
        ("Open the notebook", "<font face='Courier'>02-query-via-api/02_query_api.ipynb</font> → run top to bottom"),
    ]
    story += [section("Before you start", BLUE, "part of 0–5 min"),
              grid([["", P("Step", "head"), P("Do this", "head")]]
                   + [[Box(), P(a, "cellb"), P(b, "cell")] for a, b in setup],
                   [0.25 * inch, 1.75 * inch, CONTENT_W - 2.0 * inch], header_color=BLUE)]

    story += [section("The RAG round trip you will run", ORANGE),
              P("The MyGPT UI is just one client of the Django backend: anything you do in the UI, you can "
                "script. The shared helper <font face='Courier'>common/mygpt_client.py</font> wraps these calls.",
                "small"),
              Spacer(1, 4), RoundTrip()]

    endpoints = [
        ("POST /token/", "Exchange username/password for a JWT", "access, refresh"),
        ("POST /api/get_datasets/", "List libraries", "dataset_name, dataset_size"),
        ("POST /api/get_documents/", "List documents in a library", "documents, dataset_type"),
        ("POST /api/get_context/", "Retrieve chunks for a question",
         "context, sources, <b>QRS</b> (relevance_score), semantic / keyword / rerank_score"),
        ("POST /api/ollama_generate/", "Generate text with the LLM", "response"),
        ("POST /api/save_answer/", "Store and score an answer",
         "<b>ARS</b> (relevance_score), hallucination_index_by_ml / _by_equation"),
    ]
    story += [section("Endpoint cheat sheet", BLUE),
              grid([[P("Endpoint", "head"), P("Purpose", "head"), P("Returns", "head")]]
                   + [[P(a, "monosm"), P(b, "cell"), P(c, "cell")] for a, b, c in endpoints],
                   [1.75 * inch, 1.85 * inch, CONTENT_W - 3.6 * inch], header_color=BLUE, zebra=True),
              P("In <font face='Courier'>client.ask()</font>, <b>HI</b> = hallucination_index_by_ml; the "
                "equation-based value is <b>HI_equation</b>.", "small")]

    # Section 1 record
    connect = grid(
        [[P("Notebook §1 — Connect: write what you see", "head"), P("You", "head"),
          P("Instructor run", "head")],
         [P("Backend URL / signed in?", "cell"), "", P(f"{EX}host.docker.internal:8000 · True</font>", "cell")],
         [P("Library name", "cell"), "", P(f"{EX}workshop-library-A</font>", "cell")],
         [P("Documents in library (<font face='Courier'>get_documents</font>)", "cell"), "",
          P(f"{EX}papers — 397 documents</font>", "cell")]],
        [2.7 * inch, 2.4 * inch, CONTENT_W - 5.1 * inch], header_color=INK, row_h=[None, 20, 20, 20])
    story += [section("Step 1 — Connect", INK, "5 min"), connect]

    key = grid([[P("Score", "head"), P("Measures", "head"), P("Good sign", "head"), P("Where it comes from", "head")],
                [P("QRS", "cellb"), P("How well the question matches your library", "cell"),
                 P("<b>high</b>", "cell"), P("get_context → relevance_score", "monosm")],
                [P("ARS", "cellb"), P("How much the answer relies on the retrieved chunks", "cell"),
                 P("<b>high</b>", "cell"), P("save_answer → relevance_score", "monosm")],
                [P("HI", "cellb"), P("Hallucination index: answer not supported by the library", "cell"),
                 P("<b>low</b>", "cell"), P("save_answer → hallucination_index_by_ml", "monosm")],
                [P("HI_equation", "cellb"), P("Same idea, computed from QRS and ARS with weights p, q (module 4)", "cell"),
                 P("<b>low</b>", "cell"), P("save_answer → hallucination_index_by_equation", "monosm")]],
               [0.85 * inch, 3.0 * inch, 0.7 * inch, CONTENT_W - 4.55 * inch], header_color=TEAL, zebra=True)
    story += [section("Reading the scores (0–100)", TEAL), key]
    return story


# ----------------------------------------------------------------------------- page 2
def page2():
    story = []

    q_on = "Do glioblastoma tumors have a high degree of lymphocyte infiltration?"
    cols = [1.55 * inch] + [0.62 * inch] * 4 + [CONTENT_W - 1.55 * inch - 2.48 * inch]
    step2 = grid(
        [[P("§2 step by step", "head"), P("QRS / ARS", "head"), P("semantic", "head"),
          P("keyword", "head"), P("rerank", "head"), P("Notes (top source doc + page, answer agrees?)", "head")],
         [P("<b>2a Retrieve</b> → QRS", "cell"), "", "", "", "", ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}69</font>", "cell"), P(f"{EX}75</font>", "cell"),
          P(f"{EX}45</font>", "cell"), P(f"{EX}80</font>", "cell"),
          P(f"{EX}BioASQ_Batch_001, p.4</font>", "cell")],
         [P("<b>2c Score</b> → ARS", "cell"), "", "", "", P("—", "center"), ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}94</font>", "cell"), P(f"{EX}64.25</font>", "cell"),
          P(f"{EX}6.08</font>", "cell"), P(f"{EX}—</font>", "center"),
          P(f"{EX}answer: “low degree of lymphocyte infiltration”</font>", "cell")]],
        cols, header_color=ORANGE, row_h=[None, 22, None, 22, None])
    step2.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT), ("BACKGROUND", (0, 4), (-1, 4), TINT)]))
    hi = grid([[P("2c Score → hallucination index", "head"), P("HI (ML)", "head"), P("HI_equation", "head"),
                P("Does the answer match the top source?  Y / N", "head")],
               [P("<b>You</b>", "cell"), "", "", ""],
               [P(f"{EX}instructor</font>", "cell"), P(f"{EX}25</font>", "cell"), P(f"{EX}0</font>", "cell"),
                P(f"{EX}yes — the answer restates the retrieved chunk</font>", "cell")]],
              [1.55 * inch, 0.9 * inch, 0.9 * inch, CONTENT_W - 3.35 * inch], header_color=ORANGE,
              row_h=[None, 22, None])
    hi.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT)]))
    story += [section("Step 2 — Retrieve → generate → score, one call at a time", ORANGE, "5 min"),
              P(f"Question: <i>{q_on}</i> (or your own)", "small"), Spacer(1, 3),
              step2, Spacer(1, 4), hi]

    # Section 3 off-topic control vs on-topic
    ctrl = grid(
        [[P("§3 client.ask()", "head"), P("QRS", "head"), P("ARS", "head"), P("HI", "head"),
          P("HI_eq", "head"), P("Answer (short)", "head")],
         [P("Off-topic: <i>What is the boiling point of tungsten?</i>", "cell"), "", "", "", "", ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}64</font>", "cell"), P(f"{EX}64</font>", "cell"),
          P(f"{EX}73</font>", "cell"), P(f"{EX}27</font>", "cell"),
          P(f"{EX}“The library does not contain the answer.”</font>", "cell")]],
        [2.3 * inch] + [0.5 * inch] * 4 + [CONTENT_W - 4.3 * inch], header_color=ORANGE, row_h=[None, 24, None])
    ctrl.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT)]))
    story += [section("Step 3 — Off-topic control question", ORANGE),
              ctrl,
              P("<b>Discuss:</b> compare with step 2. Which score flagged the off-topic question most clearly "
                "— QRS, HI or the answer text itself?", "small")]

    # Section 4 batch
    batch = grid([[P("#", "head"), P("Question (first words)", "head"), P("QRS", "head"), P("ARS", "head"),
                   P("HI", "head"), P("Answer looks right?  Y / N / ?", "head")]]
                 + [[P(str(i), "cellb"), "", "", "", "", ""] for i in range(1, 6)],
                 [0.25 * inch, 2.75 * inch, 0.55 * inch, 0.55 * inch, 0.55 * inch,
                  CONTENT_W - 4.65 * inch],
                 header_color=TEAL, row_h=[None] + [19] * 5)
    story += [section("Step 4 — Batch: first 5 BioASQ questions", TEAL, "5 min"),
              batch,
              P(f"{EX}Instructor run: QRS 49–90, ARS 93–100, HI 24–38. Saved to "
                "workshop_outputs/02_query_results.csv — remove .head(5) to run all 25.</font>", "small")]

    cli = Table([[P("docker compose exec workshop python 02-query-via-api/scripts/query_library.py "
                    "--question \"Do glioblastoma tumors have a high degree of lymphocyte infiltration?\"", "monosm")],
                 [P("docker compose exec workshop python 02-query-via-api/scripts/query_library.py "
                    "--questions data/BioASQ/questions_25.csv --out workshop_outputs/02_query_results.csv",
                    "monosm")],
                 [P("Add <font face='Courier'>--list</font> to list libraries, "
                    "<font face='Courier'>--dataset workshop-library-B</font> to query your comparison library.",
                    "small")]],
                colWidths=[CONTENT_W])
    cli.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 1), TINT),
                             ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.white),
                             ("LEFTPADDING", (0, 0), (-1, -1), 6),
                             ("TOPPADDING", (0, 0), (-1, -1), 2),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    story += [KeepTogether([section("Step 5 — Same thing from the command line", TEAL, "15–20 min"), cli])]

    story += [section("Exercises", TEAL),
              write_lines(1, "1. Rerun the batch with client.ask(q, max_chunks=10). Do ARS and HI change?"),
              write_lines(1, "2. Which question has a high QRS but a poor answer? (Module 3 measures this.)")]

    cp = checklist([
        "Connected to <b>workshop-library-A</b> and <font face='Courier'>get_documents</font> lists its documents",
        "<font face='Courier'>workshop_outputs/02_query_results.csv</font> exists with QRS, ARS, HI columns",
        "You compared the off-topic control with the on-topic questions "
        "(QRS alone may not flag it: check HI and the answer)",
    ])
    tr = trouble_table([
        ("Connection refused", "In the container MyGPT is host.docker.internal:8000; check MyGPT is up"),
        ("401 Unauthorized", "Wrong MYGPT_USERNAME / PASSWORD; rerun create_superuser.sh"),
        ("400 from get_context", "MYGPT_DATASET or embedding model doesn’t match the library"),
        ("Request times out", "A: smaller MYGPT_LLM · B: St. Jude Wi-Fi or Cloudflare on · C: check OpenAI key and billing"),
    ])
    story += [Spacer(1, 6), side_by_side(cp, tr, section("Checkpoint", INK), section("Stuck?", ORANGE))]
    return story


def main():
    build(OUT, page1() + [PageBreak()] + page2(), chrome, "MyGPT Workshop — Module 2 handout")


if __name__ == "__main__":
    main()
