# Module 4 — Recalibrate QRS, ARS and HI weights for your domain (20 min)

## Objectives

- Understand how MyGPT combines semantic, keyword and rerank signals into QRS and ARS,
  and how those two make HI.
- Use your labelled benchmark from module 3 to run a global sensitivity analysis over
  the weights.
- Choose weights that best separate correct from incorrect answers, and check that they
  are stable, not just lucky.

## Before you start

- `workshop_outputs/03_calibration_eval_dataset.csv` from module 3 (03c): the 163
  original BioASQ questions, judged against their ground truths. Every attendee uses
  this same set, so your numbers should be close to the instructor reference run below.
  Small differences in MyGPT answers or judge labels can shift them a little.
- If the file is missing, the notebook warns and uses the pilot `03_eval_dataset.csv`,
  or the PubMedQA fallback if there is no pilot either. Those sets are much smaller, so
  treat their weights as illustrative.

| Time | Activity |
|---|---|
| 0–5 min | Concepts: the formulas |
| 5–15 min | Notebook: baseline → grid search → p:q sweep → bootstrap |
| 15–20 min | Apply the weights in MyGPT and discuss |

## Concepts

From the MyGPT FAQ ([Q15–17](https://github.com/stjude/MyGPT/blob/main/FAQs.md)):

$$QRS = a\,\overline{Q_{sem}} + b\,\overline{Q_{key}} + c\,\overline{Q_{rerank}}$$
$$ARS = x\,\overline{A_{sem}} + y\,\overline{A_{key}} + z\,\overline{A_{rerank}}$$
$$HI = 1 - \frac{p\,QRS}{p+q} - \frac{q\,ARS}{p+q}$$

Each bar is a mean over the top-k retrieved chunks. MyGPT then rescales the raw weighted
sum to 0–100. Only the ratios between weights matter: multiplying a set by the same
positive number gives the same ranking, so p:q = 5:5 is the same as 1:1.

On your own benchmark, MyGPT returns the aggregate QRS and ARS components but no ARS
rerank component, so the notebook sets A<sub>rerank</sub> to 0 and **z has no effect**.
The PubMedQA fallback rebuilds it from per-chunk data.

| Weight | Meaning | Default (backend `models.py`) | UI / API field |
|---|---|---|---|
| a, b, c | Semantic, keyword and rerank weights in QRS | 4, −4, −1 | `Qsem_a`, `Qkey_b`, `Qrank_c` |
| x, y, z | Semantic, keyword and rerank weights in ARS | 5, −2, 0 | `Asem_x`, `Akey_y`, `Arank_z` |
| p, q | How much QRS vs ARS counts in HI | 1, 2 | `QRS_p`, `ARS_q` |

The defaults were chosen by a **global sensitivity analysis that maximised PR-AUC** on
the paper's benchmarks. Your field may differ. Keyword overlap matters more for gene
symbols than for policy prose, for example. That is why recalibration helps.

**What we optimise:** HI should be high for incorrect answers. We treat "incorrect" as
the positive class and measure **PR-AUC** (average precision) of each score. PR-AUC
suits this because incorrect answers are usually the minority. The baseline (a random
score) equals the share of incorrect answers.

**Stability check:** the notebook resamples the 163 questions 200 times and recommends
the new weights only if their HI PR-AUC beats the defaults in at least 90 % of
resamples. Otherwise it keeps the defaults.

## Hands-on

After the module 3b κ check, run 03c to query the original BioASQ questions and apply
the validated LLM judge to their ground truths. Then open
[`04_sensitivity_analysis.ipynb`](04_sensitivity_analysis.ipynb) and run it from top to
bottom:

1. Load `03_calibration_eval_dataset.csv` (or the pilot `03_eval_dataset.csv`, or the
   PubMedQA fallback) and rebuild the per-question components.
2. Score the **default** weights: PR-AUC of QRS, ARS and HI, plus MyGPT's stored HI.
3. Grid search (a, b, c) and (x, y, z), shown as heat maps.
4. Sweep p:q for HI.
5. Bootstrap the stability check and save
   `workshop_outputs/04_recalibrated_weights.json`.
6. Apply the weights in the MyGPT UI (**chat settings → relevance weights**). If you
   prefer the API, the last cell runs `client.update_dataset(...)`; it's commented out
   so you choose when to change your library.

**Instructor reference run** (03c calibration set: 163 BioASQ questions, 53 incorrect,
random baseline 0.325):

| | Default weights | Recalibrated |
|---|---|---|
| QRS (a, b, c) | 4, −4, −1 → PR-AUC 0.384 | 4, 5, −2 → 0.562 |
| ARS (x, y, z) | 5, −2, 0 → 0.553 | 5, −5, 4 → 0.563 |
| HI (p, q), bootstrap mean [95% CI] | 1, 2 → 0.547 [0.407, 0.667] | 5, 5 → 0.600 [0.478, 0.709] |

The recalibrated weights won 91 % of resamples, so the notebook recommends them. The main
change is a positive keyword weight in QRS: BioASQ questions name genes and drugs, so
keyword overlap helps.

## Checkpoint

- [ ] Default PR-AUC printed for QRS, ARS and HI, and default vs. recalibrated HI PR-AUC
      from the bootstrap.
- [ ] Heat map shows where good weights lie (a broad ridge, or a single spike?).
- [ ] `04_recalibrated_weights.json` saved, with the bootstrap stability shown.
- [ ] You can explain in one sentence why your field prefers these weights.

## Troubleshooting

| Symptom | Fix |
|---|---|
| "calibration dataset not found" warning | Run 03c first. Without it, the notebook uses the much smaller pilot set; treat those weights as illustrative |
| All PR-AUCs ≈ baseline | Too few incorrect labels, or the components are missing (all NaN). Check `df[COMP].describe()` |
| Changing z does nothing | Expected on your own benchmark: A<sub>rerank</sub> is 0 (see Concepts) |
| Several p:q settings tie | Only the ratio matters; any p = q gives the same HI |
| Heat map is flat | QRS isn't informative for your set; ARS/HI may matter more. That is a real finding |
| Your best weights differ from the instructor's | Small differences in MyGPT answers or judge labels can change the single best cell. Compare where the bright ridge lies, not the exact weights |

## Going further

- Use the same approach to tune **QC/AC best/worst cutoffs**:
  [QRS-ARS-cutoff pipeline](https://github.com/stjude/MyGPT-evaluations/tree/main/QRS-ARS-cutoff).
- Hold out a test split, and only report test-set PR-AUC for the chosen weights.
