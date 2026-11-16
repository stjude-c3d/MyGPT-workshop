# Module 4 — Recalibrate QRS, ARS and HI weights for your domain (20 min)

## Objectives

- Understand how MyGPT combines semantic, keyword and rerank signals into QRS and ARS,
  and how those two make HI.
- Use your labelled benchmark from module 3 to run a global sensitivity analysis over
  the weights.
- Choose weights that best separate correct from incorrect answers, and check that they
  are stable, not just lucky.

## Before you start

- `workshop_outputs/03_eval_dataset.csv` from module 3. Otherwise the notebook uses the
  PubMedQA fallback.
- About 20-25 labelled rows, with at least 3-5 incorrect, gives a usable signal. With fewer,
  treat the results as illustrative.

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
sum to 0–100.

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

**Overfitting guard:** with small benchmarks, many weight combinations look equally
good. The notebook bootstraps the data and only recommends weights that stay in the top
10 % across resamples.

## Hands-on

Open [`04_sensitivity_analysis.ipynb`](04_sensitivity_analysis.ipynb) and run it from top
to bottom:

1. Load your benchmark (or the fallback) and rebuild the per-question components.
2. Score the **default** weights: PR-AUC of QRS, ARS and HI.
3. Grid search (a, b, c) and (x, y, z), shown as heat maps.
4. Sweep p:q for HI.
5. Bootstrap the stability check and save
   `workshop_outputs/04_recalibrated_weights.json`.
6. Apply the weights in the MyGPT UI (**chat settings → relevance weights**). If you
   prefer the API, the last cell runs `client.update_dataset(...)`; it's commented out
   so you choose when to change your library.

## Checkpoint

- [ ] Default vs. recalibrated PR-AUC printed for QRS, ARS and HI.
- [ ] Heat map shows where good weights lie (a broad ridge, or a single spike?).
- [ ] `04_recalibrated_weights.json` saved, with the bootstrap stability shown.
- [ ] You can explain in one sentence why your field prefers these weights.

## Troubleshooting

| Symptom | Fix |
|---|---|
| All PR-AUCs ≈ baseline | Too few incorrect labels, or the components are missing (all NaN). Check `df[components].describe()` |
| Heat map is flat | QRS isn't informative for your set; ARS/HI may matter more. That is a real finding |
| Best weights change on every run | The benchmark is too small. Report the default weights, not the "best" ones |

## Going further

- Use the same approach to tune **QC/AC best/worst cutoffs**:
  [QRS-ARS-cutoff pipeline](https://github.com/stjude/MyGPT-evaluations/tree/main/QRS-ARS-cutoff).
- Hold out a test split, and only report test-set PR-AUC for the chosen weights.
