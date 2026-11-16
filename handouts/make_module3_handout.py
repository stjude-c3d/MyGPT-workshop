"""Build the printable Module 3 handout (US Letter, 2 pages).

    pip install reportlab pillow
    python handouts/make_module3_handout.py      # -> handouts/module3_handout.pdf

Content mirrors 03-build-evaluation-dataset/README.md and the 03a / 03b notebooks.
The grey "instructor run" values come from 03a_generate_questions_final.ipynb and
03b_label_and_judge_final.ipynb, so attendees can tell whether their numbers are in range.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, KeepTogether, PageBreak, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, INK, MUTED, ORANGE, RULE, TEAL, TINT, Box, P, build, checklist,
                         grid, make_chrome, name_line, objectives_and_timeline, section,
                         side_by_side, trouble_table, write_lines)

OUT = Path(__file__).resolve().parent / "module3_handout.pdf"
chrome = make_chrome(3, "Build an evaluation dataset", 30, "03-build-evaluation-dataset/README.md")

EX = '<font color="#5A6270" size="7">'  # instructor-run example values


def _arrow(c, x1, x2, y, color=MUTED):
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


class Pipeline(Flowable):
    """Diagram: documents -> generate -> review -> MyGPT -> label + check."""

    BOXES = [
        (INK, "Documents", "pdfs_70/", "same PDFs as library\n→ 1,500-char chunks"),
        (ORANGE, "Generate", "03a · LLM", "1 question + reference\nanswer per chunk"),
        (RED := colors.HexColor("#C8323B"), "Review", "you", "keep / edit / drop\n+ add unanswerable"),
        (BLUE, "Answer", "client.ask()", "MyGPT answer\n+ QRS, ARS, HI"),
        (TEAL, "Label + check", "03b", "human gold + LLM judge\n→ accuracy, Cohen’s κ"),
    ]

    def __init__(self, width=CONTENT_W, height=1.12 * inch):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        gap, n = 12, len(self.BOXES)
        bw = (self.width - gap * (n - 1)) / n
        bh = 0.78 * inch
        y = self.height - bh - 2
        for i, (color, title, tag, body) in enumerate(self.BOXES):
            x = i * (bw + gap)
            c.setFillColor(colors.white)
            c.setStrokeColor(color)
            c.setLineWidth(1.2)
            c.roundRect(x, y, bw, bh, 5, stroke=1, fill=1)
            c.setFillColor(color)
            c.roundRect(x, y + bh - 16, bw, 16, 5, stroke=0, fill=1)
            c.rect(x, y + bh - 16, bw, 8, stroke=0, fill=1)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 8.3)
            c.drawCentredString(x + bw / 2, y + bh - 11.5, title)
            c.setFillColor(INK)
            c.setFont("Courier-Bold", 6.9)
            c.drawCentredString(x + bw / 2, y + bh - 27, tag)
            c.setFont("Helvetica", 7.1)
            for k, line in enumerate(body.split("\n")):
                c.drawCentredString(x + bw / 2, y + bh - 39 - k * 9, line)
            if i < n - 1:
                _arrow(c, x + bw + 1, x + bw + gap - 1, y + bh / 2)
        # file outputs under the boxes
        c.setFont("Courier", 6.6)
        c.setFillColor(MUTED)
        outs = {2: "03_questions.csv", 3: "03_answers.csv", 4: "03_eval_dataset.csv"}
        for i, name in outs.items():
            c.drawCentredString(i * (bw + gap) + bw / 2, y - 10, "→ " + name)
        c.drawString(0, y - 10, "saved in workshop_outputs/:")


class KappaScale(Flowable):
    """0-1 agreement bar (Landis & Koch bands) with the 0.6 threshold and a write-in marker."""

    BANDS = [(0.0, 0.2, "slight"), (0.2, 0.4, "fair"), (0.4, 0.6, "moderate"),
             (0.6, 0.8, "substantial"), (0.8, 1.0, "almost perfect")]

    def __init__(self, width=CONTENT_W - 0.2 * inch, height=0.6 * inch, instructor=0.65):
        super().__init__()
        self.width, self.height, self.instructor = width, height, instructor

    def wrap(self, *_):
        return self.width, self.height

    def draw(self):
        c = self.canv
        bar_y, bar_h = 20, 15
        shades = ["#E7EAEE", "#D9DEE4", "#C9D0D8", "#9FD3CA", "#6BBDAF"]
        for (a, b, name), shade in zip(self.BANDS, shades):
            x0, x1 = a * self.width, b * self.width
            c.setFillColor(colors.HexColor(shade))
            c.rect(x0, bar_y, x1 - x0 - 1, bar_h, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica", 7)
            c.drawCentredString((x0 + x1) / 2, bar_y + 4.5, name)
            c.setFillColor(MUTED)
            c.setFont("Helvetica", 6.6)
            c.drawCentredString(x0, 3, f"{a:.1f}")
        c.drawCentredString(self.width - 4, 3, "1.0")
        # threshold
        tx = 0.6 * self.width
        c.setStrokeColor(colors.HexColor("#C8323B"))
        c.setLineWidth(1.6)
        c.line(tx, bar_y - 3, tx, bar_y + bar_h + 6)
        c.setFillColor(colors.HexColor("#C8323B"))
        c.setFont("Helvetica-Bold", 7)
        c.drawString(tx + 3, bar_y + bar_h + 4, "trust the judge from κ ≥ 0.6")
        # instructor marker, under the bar
        ix = self.instructor * self.width
        c.setFillColor(MUTED)
        p = c.beginPath()
        p.moveTo(ix, bar_y - 1)
        p.lineTo(ix - 3.5, bar_y - 8)
        p.lineTo(ix + 3.5, bar_y - 8)
        p.close()
        c.drawPath(p, stroke=0, fill=1)
        c.setFont("Helvetica", 6.6)
        c.drawString(ix + 5, bar_y - 8, f"instructor {self.instructor:.2f}")
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(0, bar_y + bar_h + 4, "Cohen’s κ — mark yours on the bar with an X")


# ----------------------------------------------------------------------------- page 1
def page1():
    story = [name_line(), Spacer(1, 6),
             objectives_and_timeline(
                 ["generate question + reference-answer pairs from your own documents",
                  "run them through MyGPT and collect answers with QRS, ARS and HI",
                  "label answers by hand and with an LLM judge, and measure how far to trust the judge"],
                 [("0–5", "Concepts + setup", BLUE),
                  ("5–15", "03a: generate, review, answer", ORANGE),
                  ("15–30", "03b: label, judge, checkpoint", TEAL)])]

    setup = [
        ("Modules 1–2 done", "<b>workshop-library-A</b> exists and <font face='Courier'>client.ask()</font> "
                             "worked in module 2"),
        ("JupyterLab running", "<font face='Courier'>http://localhost:8888/lab?token=mygpt-workshop</font>"),
        ("Documents readable", "PDFs in <font face='Courier'>data/BioASQ/pdfs_70/</font> "
                               "(notebook 03a sets this as <font face='Courier'>DOCS_DIR</font>)"),
        ("Judge model pulled", "<font face='Courier'>JUDGE_LLM</font> in .env (default llama3); a bigger model "
                               "judges better"),
        ("Behind or MyGPT down?", "In 03b set <font face='Courier'>USE_FALLBACK = True</font>: PubMedQA run from "
                                  "MyGPT-evaluations, 294 questions with human labels"),
    ]
    story += [section("Before you start", BLUE, "part of 0–5 min"),
              grid([["", P("Step", "head"), P("Do this", "head")]]
                   + [[Box(), P(a, "cellb"), P(b, "cell")] for a, b in setup],
                   [0.25 * inch, 1.6 * inch, CONTENT_W - 1.85 * inch], header_color=BLUE)]

    story += [section("How the benchmark is built", ORANGE),
              P("A benchmark is only as good as its labels. The LLM writes the questions, <b>you</b> decide "
                "which survive, and the judge is only trusted once it agrees with your labels.", "small"),
              Spacer(1, 4), Pipeline()]

    rules = grid(
        [[P("Label", "head"), P("Answerable question", "head"), P("Unanswerable question", "head")],
         [P("<b>1 = correct</b>", "cell"), P("Agrees with the reference answer on the key fact and is "
                                             "supported by the library", "cell"),
          P("Says the information is <b>not in the library</b>", "cell")],
         [P("<b>0 = incorrect</b>", "cell"), P("Wrong, contradicts the reference, misses the key fact, or "
                                               "unsupported", "cell"),
          P("Invents or asserts an answer anyway", "cell")]],
        [1.0 * inch, (CONTENT_W - 1.0 * inch) / 2, (CONTENT_W - 1.0 * inch) / 2], header_color=TEAL)
    mix = Table([[P("<b>Question mix:</b> factual lookups, questions that need two chunks, and "
                    "<b>~10–20 % unanswerable</b> (off-topic or near-miss). Without unanswerable questions you "
                    "cannot tell whether HI catches hallucinations.", "small")]], colWidths=[CONTENT_W])
    mix.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT), ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    story += [section("Label scheme", TEAL), rules, Spacer(1, 4), mix]

    gen = grid(
        [[P("03a §1–§2 — write what you see", "head"), P("You", "head"), P("Instructor run", "head")],
         [P("Chunks / documents read", "cell"), "", P(f"{EX}755 chunks from 70 documents</font>", "cell")],
         [P("Questions generated (<font face='Courier'>N_CHUNKS</font>)", "cell"), "",
          P(f"{EX}20 (llama3, temperature 0.2)</font>", "cell")],
         [P("One good question / one bad question (Q #)", "cell"), "",
          P(f"{EX}good: #6 EGFR amplification % · vague: #8 “third stage”</font>", "cell")]],
        [2.45 * inch, 2.35 * inch, CONTENT_W - 4.8 * inch], header_color=ORANGE, row_h=[None, 20, 20, 20])
    story += [section("Step 1 — Generate questions (03a)", ORANGE, "5–10 min"), gen]

    story += [KeepTogether([
        section("Step 2 — Add unanswerable questions + review", ORANGE),
        P("Replace the examples with <b>near-miss</b> questions for your field: plausible, but not answered by "
          "your documents. Then open <font face='Courier'>workshop_outputs/03_questions.csv</font>, delete vague "
          "or wrong rows, fix reference answers, and rerun the reload cell.", "small"),
        Spacer(1, 2),
        write_lines(1, "My unanswerable question 1:", height=15),
        write_lines(1, "My unanswerable question 2:", height=15),
        Spacer(1, 3),
        grid([[P("After review", "head"), P("Kept", "head"), P("Edited", "head"), P("Dropped", "head"),
               P("Unanswerable", "head")],
              [P("<b>You</b>", "cell"), "", "", "", ""],
              [P(f"{EX}instructor</font>", "cell"), P(f"{EX}23 total</font>", "cell"), P(f"{EX}—</font>", "cell"),
               P(f"{EX}0</font>", "cell"), P(f"{EX}3</font>", "cell")]],
             [1.4 * inch] + [(CONTENT_W - 1.4 * inch) / 4] * 4, header_color=ORANGE, row_h=[None, 20, None]),
    ])]
    return story


# ----------------------------------------------------------------------------- page 2
def page2():
    story = []

    cols = [1.85 * inch, 0.95 * inch, 0.95 * inch, 0.95 * inch, CONTENT_W - 4.7 * inch]
    scores = grid(
        [[P("03a §5 — scores by question type", "head"), P("QRS range", "head"), P("ARS range", "head"),
          P("HI range", "head"), P("Answer for unanswerable Qs", "head")],
         [P("<b>You</b> — answerable", "cell"), "", "", "", ""],
         [P("<b>You</b> — unanswerable", "cell"), "", "", "", ""],
         [P(f"{EX}instructor — answerable (20)</font>", "cell"), P(f"{EX}20–77</font>", "cell"),
          P(f"{EX}83–100</font>", "cell"), P(f"{EX}23–40</font>", "cell"),
          P(f"{EX}instructor: “The library does not contain the answer.”</font>", "cell")],
         [P(f"{EX}instructor — unanswerable (3)</font>", "cell"), P(f"{EX}64–82</font>", "cell"),
          P(f"{EX}64–78</font>", "cell"), P(f"{EX}59–73</font>", "cell"), ""]],
        cols, header_color=BLUE, row_h=[None, 21, 21, None, None])
    scores.setStyle(TableStyle([("BACKGROUND", (0, 3), (-1, 4), TINT), ("SPAN", (4, 3), (4, 4)),
                                ("VALIGN", (4, 3), (4, 4), "MIDDLE")]))
    story += [section("Step 3 — Run every question through MyGPT (03a §5)", BLUE, "10–15 min"),
              scores, Spacer(1, 3),
              P("<b>Discuss:</b> which score separates answerable from unanswerable questions in your run? "
                "In the instructor run QRS overlaps, but HI does not.", "small")]

    tally = grid(
        [[P("03b §2 — hand labels", "head"), P("Labelled", "head"), P("Correct (1)", "head"),
          P("Incorrect (0)", "head"), P("Hardest one to decide (Q #, why)", "head")],
         [P("<b>You</b>", "cell"), "", "", "", ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}23</font>", "cell"), P(f"{EX}21</font>", "cell"),
          P(f"{EX}2</font>", "cell"), P(f"{EX}#9 GBM recurrence: partly matches the reference</font>", "cell")]],
        [1.5 * inch, 0.8 * inch, 0.85 * inch, 0.85 * inch, CONTENT_W - 4.0 * inch], header_color=TEAL,
        row_h=[None, 22, None])
    tally.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT)]))
    story += [section("Step 4 — Hand-label at least 20 answers (03b §2)", TEAL, "15–20 min"),
              P("Type <b>1</b>, <b>0</b>, <b>s</b> (skip) or <b>q</b> (quit). Labels save after every answer. "
                "Prefer a spreadsheet? Fill <font face='Courier'>human_label</font> in "
                "<font face='Courier'>03_to_label.csv</font>.", "small"),
              Spacer(1, 2), tally]

    # Judge: confusion matrix (you) + instructor
    def cm(title, vals, grey):
        f = (lambda v: P(f"{EX}{v}</font>", "center")) if grey else (lambda v: "")
        t = Table([[P(f"<b>{title}</b>", "cell"), P("<b>judge 0</b>", "center"), P("<b>judge 1</b>", "center")],
                   [P("<b>human 0</b>", "cell"), f(vals[0]), f(vals[1])],
                   [P("<b>human 1</b>", "cell"), f(vals[2]), f(vals[3])]],
                  colWidths=[0.75 * inch, 0.62 * inch, 0.62 * inch], rowHeights=[None, 22, 22])
        t.setStyle(TableStyle([("GRID", (1, 1), (-1, -1), 0.6, MUTED),
                               ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#E3F2EF")),
                               ("BACKGROUND", (2, 2), (2, 2), colors.HexColor("#E3F2EF")),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
        return t

    metrics = grid(
        [[P("03b §4", "head"), P("You", "head"), P("Instructor", "head")],
         [P("Rows with both labels", "cell"), "", P(f"{EX}23</font>", "cell")],
         [P("Accuracy", "cell"), "", P(f"{EX}0.96</font>", "cell")],
         [P("Cohen’s κ", "cellb"), "", P(f"{EX}0.65</font>", "cell")],
         [P("Judge model", "cell"), "", P(f"{EX}llama3</font>", "cell")]],
        [1.3 * inch, 0.85 * inch, 0.75 * inch], header_color=TEAL, row_h=[None, 18, 18, 18, 18])
    judge_row = Table([[cm("You", ["", "", "", ""], False), cm("Instructor", ["1", "1", "0", "21"], True), metrics]],
                      colWidths=[2.15 * inch, 2.15 * inch, CONTENT_W - 4.3 * inch])
    judge_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                   ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story += [section("Step 5 — Run the LLM judge and check it (03b §3–§4)", TEAL, "20–27 min"),
              P("Green cells are agreement. Accuracy can look high just because most answers are correct; "
                "κ corrects for agreement by chance.", "small"),
              Spacer(1, 3), judge_row, Spacer(1, 4), KappaScale(), Spacer(1, 2),
              write_lines(2, "Disagreements (03b §4): was the judge wrong, or your label?  Q # / who was right:",
                          height=15),
              Spacer(1, 2),
              Table([[Box(), P("<b>κ ≥ 0.6</b>: judge labels fill the rows you did not label", "cell"),
                      Box(), P("<b>κ &lt; 0.6</b>: use a stronger JUDGE_LLM, add few-shot examples, "
                               "or label more by hand", "cell")]],
                    colWidths=[0.2 * inch, 3.1 * inch, 0.2 * inch, CONTENT_W - 3.5 * inch],
                    style=[("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2)]),
              P(f"{EX}Instructor run: saved 23 labelled rows (2 incorrect) → 03_eval_dataset.csv, "
                "judge labels used: True.</font>", "small")]

    cp = checklist([
        "At least <b>20 reviewed questions</b>, including some unanswerable ones",
        "At least <b>20 rows hand-labelled</b>",
        "Accuracy and κ printed, and you can say whether the judge is good enough",
        "<font face='Courier'>workshop_outputs/03_eval_dataset.csv</font> saved with a "
        "<font face='Courier'>label</font> column (module 4 reads it)",
    ])
    tr = trouble_table([
        ("Vague questions", "“What does the document say?” — lower temperature, bigger LLM, or tighten the "
                            "prompt in 03a"),
        ("Judge says all correct", "Typical of small models: stronger JUDGE_LLM or more few-shot examples"),
        ("Judge replies don’t parse", "Model ignores JSON mode; the regex fallback runs — check judge_raw"),
        ("Generation too slow", "Set N_CHUNKS to 10–15 in 03a"),
        ("κ is nan", "All labels are the same class: label more rows, include unanswerable ones"),
    ])
    story += [Spacer(1, 6), side_by_side(cp, tr, section("Checkpoint", INK), section("Stuck?", ORANGE))]
    return story


def main():
    build(OUT, page1() + [PageBreak()] + page2(), chrome, "MyGPT Workshop — Module 3 handout")


if __name__ == "__main__":
    main()
