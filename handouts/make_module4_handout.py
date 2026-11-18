"""Build the printable Module 4 handout (US Letter, 2 pages).

    pip install reportlab pillow
    python handouts/make_module4_handout.py      # -> handouts/module4_handout.pdf

Content mirrors 04-recalibrate-weights/README.md and 04_sensitivity_analysis.ipynb.
The grey "instructor run" values come from 04_sensitivity_analysis_final.ipynb, run on
the 03c calibration dataset: 163 BioASQ questions judged against ground truth, 53 incorrect.
Attendees use the same 163 questions, so their values should be close.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Image, KeepTogether, PageBreak, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, INK, MUTED, ORANGE, RULE, TEAL, TINT, Box, P, build, checklist,
                         grid, make_chrome, name_line, objectives_and_timeline, section,
                         side_by_side, trouble_table, write_lines)

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "module4_handout.pdf"
chrome = make_chrome(4, "Recalibrate QRS, ARS and HI weights", 20, "04-recalibrate-weights/README.md")

EX = '<font color="#5A6270" size="7">'  # instructor-run example values
RED = colors.HexColor("#C8323B")
GREEN = colors.HexColor("#0E9E8B")


class Separation(Flowable):
    """Two HI number lines: a score that separates incorrect answers, and one that doesn't."""

    def __init__(self, width=CONTENT_W, height=0.92 * inch):
        super().__init__()
        self.width, self.height = width, height

    def wrap(self, *_):
        return self.width, self.height

    def _line(self, y, label, verdict, correct, incorrect):
        c = self.canv
        x0, x1 = 1.35 * inch, self.width - 1.55 * inch
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7.6)
        c.drawString(0, y - 2.5, label)
        c.setStrokeColor(RULE)
        c.setLineWidth(1)
        c.line(x0, y, x1, y)
        c.setFont("Helvetica", 6.5)
        c.setFillColor(MUTED)
        c.drawString(x0, y - 11, "HI 0")
        c.drawRightString(x1, y - 11, "100")
        for v in correct:
            c.setFillColor(GREEN)
            c.circle(x0 + v * (x1 - x0), y, 3, stroke=0, fill=1)
        for v in incorrect:
            c.setFillColor(RED)
            xx = x0 + v * (x1 - x0)
            c.setStrokeColor(RED)
            c.setLineWidth(1.6)
            c.line(xx - 3, y - 3, xx + 3, y + 3)
            c.line(xx - 3, y + 3, xx + 3, y - 3)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7.2)
        c.drawString(x1 + 10, y - 2.5, verdict)

    def draw(self):
        c = self.canv
        good_c = [0.08, 0.13, 0.17, 0.22, 0.26, 0.3, 0.34, 0.38, 0.43, 0.47]
        self._line(self.height - 14, "Useful HI", "PR-AUC ≈ 1", good_c, [0.82, 0.9])
        bad_c = [0.1, 0.19, 0.28, 0.36, 0.5, 0.58, 0.66, 0.75, 0.86, 0.93]
        self._line(self.height - 40, "Useless HI", "PR-AUC ≈ share incorrect", bad_c, [0.23, 0.71])
        # legend
        y = 4
        c.setFillColor(GREEN)
        c.circle(1.35 * inch + 3, y + 2.5, 3, stroke=0, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica", 7)
        c.drawString(1.35 * inch + 10, y, "correct answer (label 1)")
        lx = 1.35 * inch + 1.35 * inch
        c.setStrokeColor(RED)
        c.setLineWidth(1.6)
        c.line(lx, y - 0.5, lx + 6, y + 5.5)
        c.line(lx, y + 5.5, lx + 6, y - 0.5)
        c.drawString(lx + 10, y, "incorrect answer (label 0) — the positive class we want to catch")


# ----------------------------------------------------------------------------- page 1
def page1():
    story = [name_line(), Spacer(1, 6),
             objectives_and_timeline(
                 ["explain how QRS, ARS and HI are built from their signals",
                  "run a sensitivity analysis on your module 3 benchmark",
                  "pick weights for your field and check they aren’t just lucky"],
                 [("0–5", "Formulas", BLUE),
                  ("5–15", "Notebook: grid + bootstrap", ORANGE),
                  ("15–20", "Apply + discuss", TEAL)])]

    setup = [
        ("Benchmark from module 3", "<font face='Courier'>03_calibration_eval_dataset.csv</font> from 03c: the "
                                    "<b>163 BioASQ questions</b> judged against ground truth, the same set for "
                                    "everyone"),
        ("Expect the instructor’s numbers", "Your values should be close to the grey instructor values; small "
                                            "differences shift them a little. Option C (OpenAI) uses other models, so expect different numbers"),
        ("No benchmark?", "Set <font face='Courier'>FORCE_FALLBACK = True</font>: PubMedQA run from "
                          "MyGPT-evaluations"),
        ("Open the notebook", "<font face='Courier'>04-recalibrate-weights/04_sensitivity_analysis.ipynb</font> "
                              "→ run top to bottom"),
    ]
    story += [section("Before you start", BLUE, "part of 0–5 min"),
              grid([["", P("Step", "head"), P("Do this", "head")]]
                   + [[Box(), P(a, "cellb"), P(b, "cell")] for a, b in setup],
                   [0.25 * inch, 1.6 * inch, CONTENT_W - 1.85 * inch], header_color=BLUE)]

    m = lambda s: f"<sub>{s}</sub>"  # noqa: E731
    formulas = Table(
        [[P(f"<b>QRS</b> = <b>a</b>·Q{m('sem')} + <b>b</b>·Q{m('key')} + <b>c</b>·Q{m('rerank')}"),
          P(f"<b>ARS</b> = <b>x</b>·A{m('sem')} + <b>y</b>·A{m('key')} + <b>z</b>·A{m('rerank')}"),
          P("<b>HI</b> = 1 − (<b>p</b>·QRS + <b>q</b>·ARS) / (p + q)")]],
        colWidths=[CONTENT_W / 3] * 3)
    formulas.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT),
                                  ("LINEAFTER", (0, 0), (1, 0), 0.5, RULE),
                                  ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                  ("TOPPADDING", (0, 0), (-1, -1), 6),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story += [section("The formulas (MyGPT FAQ Q15–17)", ORANGE),
              formulas,
              P("Each Q and A term is a mean over the top-k retrieved chunks: <b>sem</b> = embedding similarity, "
                "<b>key</b> = BM25 keyword match, <b>rerank</b> = cross-encoder reranker. MyGPT rescales each "
                "weighted sum to 0–100. Multiplying all weights by the same positive number changes nothing, "
                "so a small integer grid (−5…5) covers the useful space.", "small")]

    w = grid(
        [[P("Weight", "head"), P("Meaning", "head"), P("Default", "head"), P("UI / API field", "head"),
          P("Your choice", "head"), P("Instructor", "head")],
         [P("<b>a, b, c</b>", "cell"), P("semantic, keyword, rerank in QRS", "cell"), P("4, −4, −1", "cell"),
          P("Qsem_a, Qkey_b, Qrank_c", "monosm"), "", P(f"{EX}4, 5, −2</font>", "cell")],
         [P("<b>x, y, z</b>", "cell"), P("semantic, keyword, rerank in ARS", "cell"), P("5, −2, 0", "cell"),
          P("Asem_x, Akey_y, Arank_z", "monosm"), "", P(f"{EX}5, −5, 4</font>", "cell")],
         [P("<b>p, q</b>", "cell"), P("how much QRS vs ARS counts in HI", "cell"), P("1, 2", "cell"),
          P("QRS_p, ARS_q", "monosm"), "", P(f"{EX}5, 5 (= 1 : 1)</font>", "cell")]],
        [0.6 * inch, 2.0 * inch, 0.7 * inch, 1.55 * inch, 1.1 * inch, CONTENT_W - 5.95 * inch],
        header_color=ORANGE, row_h=[None, 22, 22, 22])
    story += [Spacer(1, 3), w,
              P("The defaults came from a global sensitivity analysis that maximised PR-AUC on the paper’s "
                "benchmarks. Your field may differ: keyword overlap matters more for gene symbols than for "
                "policy prose.", "small")]

    story += [section("What we optimise: PR-AUC with “incorrect” as the positive class", TEAL),
              P("HI should be <b>high</b> for incorrect answers (QRS and ARS <b>low</b>). PR-AUC (average "
                "precision) rewards a score that ranks every incorrect answer above the correct ones. A random "
                "score gets PR-AUC equal to the <b>share of incorrect answers</b>, so that is the baseline to "
                "beat.", "small"),
              Spacer(1, 4), Separation()]

    load = grid(
        [[P("§1–§2 — write what you see", "head"), P("You", "head"), P("Instructor run", "head")],
         [P("Questions / incorrect answers", "cell"), "", P(f"{EX}163 questions (03c), 53 incorrect</font>", "cell")],
         [P("Random baseline (share incorrect)", "cell"), "", P(f"{EX}0.325</font>", "cell")],
         [P("PR-AUC, default weights: QRS / ARS / HI", "cell"), "",
          P(f"{EX}0.384 / 0.553 / 0.548</font>", "cell")],
         [P("PR-AUC of MyGPT’s stored HI", "cell"), "", P(f"{EX}0.574</font>", "cell")]],
        [2.45 * inch, 2.35 * inch, CONTENT_W - 4.8 * inch], header_color=TEAL, row_h=[None, 19, 19, 19, 19])
    story += [section("Steps 1–2 — Load the benchmark and score the defaults", TEAL, "5–7 min"), load]
    return story


# ----------------------------------------------------------------------------- page 2
def page2():
    story = []

    top = grid(
        [[P("§3 grid search", "head"), P("Best weights", "head"), P("PR-AUC", "head"),
          P("Heat-map shape (tick one)", "head")],
         [P("<b>You</b> — QRS (a, b, c)", "cell"), "", "",
          Table([[Box(), P("broad ridge", "cell"), Box(), P("single spike", "cell"), Box(), P("flat", "cell")]],
                colWidths=[0.17 * inch, 0.75 * inch, 0.17 * inch, 0.75 * inch, 0.17 * inch, 0.4 * inch],
                style=[("LEFTPADDING", (0, 0), (-1, -1), 1), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")])],
         [P("<b>You</b> — ARS (x, y, z)", "cell"), "", "",
          Table([[Box(), P("broad ridge", "cell"), Box(), P("single spike", "cell"), Box(), P("flat", "cell")]],
                colWidths=[0.17 * inch, 0.75 * inch, 0.17 * inch, 0.75 * inch, 0.17 * inch, 0.4 * inch],
                style=[("LEFTPADDING", (0, 0), (-1, -1), 1), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")])],
         [P(f"{EX}instructor — QRS</font>", "cell"), P(f"{EX}4, 5, −2</font>", "cell"),
          P(f"{EX}0.562</font>", "cell"),
          P(f"{EX}ridge at positive b (default 0.384): keyword match helps here</font>", "cell")],
         [P(f"{EX}instructor — ARS</font>", "cell"), P(f"{EX}5, −5, 4</font>", "cell"),
          P(f"{EX}0.563</font>", "cell"),
          P(f"{EX}default (0.553) already on the ridge; z has no effect</font>", "cell")]],
        [1.85 * inch, 1.05 * inch, 0.7 * inch, CONTENT_W - 3.6 * inch], header_color=ORANGE,
        row_h=[None, 19, 19, None, None])
    top.setStyle(TableStyle([("BACKGROUND", (0, 3), (-1, 4), TINT)]))
    story += [section("Step 3 — Grid search over (a, b, c) and (x, y, z)", ORANGE, "7–10 min"),
              top]

    pq = grid(
        [[P("§4 p : q sweep", "head"), P("Best p : q", "head"), P("HI PR-AUC", "head"),
          P("What does it mean? (e.g. “HI ignores ARS”)", "head")],
         [P("<b>You</b>", "cell"), "", "", ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}5 : 5</font>", "cell"), P(f"{EX}0.597</font>", "cell"),
          P(f"{EX}only the ratio matters: every p = q ties, so QRS and ARS count equally</font>", "cell")]],
        [1.3 * inch, 0.9 * inch, 0.9 * inch, CONTENT_W - 3.1 * inch], header_color=ORANGE, row_h=[None, 19, None])
    pq.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT)]))
    story += [section("Step 4 — Sweep p : q for HI", ORANGE, "10–12 min"), pq]

    # How the weights are picked: the instructor run's heat maps from 04_sensitivity_analysis_final.ipynb
    fig_h = 1.5 * inch
    heat_qa = Image(str(ASSETS / "m4_heatmap_cell9.png"), width=fig_h * 1065 / 440, height=fig_h)
    heat_pq = Image(str(ASSETS / "m4_heatmap_cell12.png"), width=fig_h * 456 / 381, height=fig_h)
    how = [
        ("①", "Score every weight set", "each (a, b, c) on −5…5 → QRS → PR-AUC; a pixel is the best over c (or z)"),
        ("②", "Keep the brightest", "yellow = best; red × = default. Here QRS gains most by making b positive"),
        ("③", "Then weight HI", "try every p : q with those QRS and ARS; yellow diagonal = p = q"),
        ("④", "Check the shape", "a wide yellow area means many ties, so the “best” is partly luck"),
    ]
    figs_w = heat_qa.drawWidth + 0.08 * inch + heat_pq.drawWidth
    text_w = CONTENT_W - figs_w - 0.15 * inch
    steps = Table([[P(f'<font color="#E8762D" size="10"><b>{n}</b></font>', "cell"),
                    P(f"<b>{t}</b>: {d}", "cell")] for n, t, d in how],
                  colWidths=[0.2 * inch, text_w - 0.2 * inch])
    steps.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 1),
                               ("TOPPADDING", (0, 0), (-1, -1), 1),
                               ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    figs = Table([[heat_qa, heat_pq]], colWidths=[heat_qa.drawWidth + 0.08 * inch, heat_pq.drawWidth])
    figs.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                              ("VALIGN", (0, 0), (-1, -1), "TOP")]))
    row = Table([[figs, steps]], colWidths=[figs_w + 0.15 * inch, text_w])
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [KeepTogether([section("How the new weights are picked — instructor run", ORANGE), row])]

    boot = grid(
        [[P("§5 bootstrap (200 resamples)", "head"), P("HI PR-AUC default  mean [95% CI]", "head"),
          P("HI PR-AUC recalibrated  mean [95% CI]", "head"), P("Win rate", "head")],
         [P("<b>You</b>", "cell"), "", "", ""],
         [P(f"{EX}instructor</font>", "cell"), P(f"{EX}0.547 [0.407, 0.667]</font>", "cell"),
          P(f"{EX}0.600 [0.478, 0.709]</font>", "cell"), P(f"{EX}91 %</font>", "cell")]],
        [1.6 * inch, 2.15 * inch, 2.35 * inch, CONTENT_W - 6.1 * inch], header_color=TEAL, row_h=[None, 19, None])
    boot.setStyle(TableStyle([("BACKGROUND", (0, 2), (-1, 2), TINT)]))
    reality = Table([[P("<b>What the instructor run shows.</b> HI PR-AUC rises from 0.547 to 0.600 and the new weights "
                        "win 91 % of resamples, past the 90 % bar, so the notebook recommends them. The main change is "
                        "a <b>positive keyword weight b</b> in QRS: BioASQ questions name genes and drugs, so keyword "
                        "overlap helps. If your best weights differ slightly, compare where the bright ridge lies, not "
                        "the exact cell.", "cell")]],
                    colWidths=[CONTENT_W])
    reality.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#E3F2EF")),
                                 ("LINEBEFORE", (0, 0), (0, 0), 3, TEAL),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 8),
                                 ("TOPPADDING", (0, 0), (-1, -1), 5),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story += [section("Step 5 — Is the improvement real? Bootstrap + save", TEAL, "12–15 min"),
              boot, Spacer(1, 2),
              P("New weights are recommended only if they win ≥ 90 % of resamples; saved to "
                "<font face='Courier'>04_recalibrated_weights.json</font>.  Recommendation: "
                "&nbsp;<b>recalibrated</b> &nbsp;/&nbsp; <b>keep defaults</b> &nbsp;(circle one)", "small"),
              Spacer(1, 4), reality]

    apply = Table([[P("<b>UI:</b> open <b>chat settings → relevance weights</b>, turn <i>use default</i> off for "
                      "QRS / ARS / HI, and enter your eight weights.", "cell")],
                   [P("<b>API:</b> uncomment the last cell: <font face='Courier'>client.update_dataset(Qsem_a=…, "
                      "Qkey_b=…, …, QRS_p=…, ARS_q=…)</font>. This changes the library’s stored settings.", "cell")]],
                  colWidths=[CONTENT_W])
    apply.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT),
                               ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.white),
                               ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    story += [KeepTogether([section("Step 6 — Apply in MyGPT and discuss", INK, "15–20 min"), apply,
                            Spacer(1, 2),
                            write_lines(1, "Discuss: did your field prefer more keyword (b, y) or semantic (a, x) "
                                           "weight than the defaults? Was the gain stable?")])]

    cp = checklist([
        "Default vs. recalibrated PR-AUC printed for QRS, ARS and HI",
        "Heat map read: broad ridge, single spike, or flat",
        "<font face='Courier'>04_recalibrated_weights.json</font> saved, with the bootstrap win rate",
        "You can say in one sentence why your field prefers these weights",
    ])
    tr = trouble_table([
        ("All PR-AUCs ≈ baseline", "Too few incorrect labels, or components all NaN: check "
                                   "df[COMP].describe()"),
        ("Heat map is flat", "QRS isn’t informative for your set; ARS / HI may matter more. A real finding"),
        ("Weights differ from instructor", "Small answer or label differences: compare the ridge, not the cell"),
        ("“calibration dataset not found”", "Run 03c first; the pilot fallback is too small to trust"),
    ])
    story += [Spacer(1, 6), side_by_side(cp, tr, section("Checkpoint", INK), section("Stuck?", ORANGE))]
    return story


def main():
    build(OUT, page1() + [PageBreak()] + page2(), chrome, "MyGPT Workshop — Module 4 handout")


if __name__ == "__main__":
    main()
