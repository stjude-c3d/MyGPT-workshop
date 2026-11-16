# Module 3 — Build an evaluation dataset from your library (30 min)

## Objectives

- Generate question/reference-answer pairs from your own documents.
- Run them through MyGPT and collect answers with QRS, ARS and HI.
- Label answers by hand **and** with an LLM judge, then measure how far you can trust
  the judge (agreement with your labels, Cohen's κ).

## Before you start

- Modules 1–2 are done: the library exists and `client.ask()` works.
- Notebook 03a generates questions from the 70 BioASQ PDFs in
  `data/BioASQ/pdfs_70/`, which the container can read. They are a subset of the
  397 PDFs in `data/BioASQ/pdfs/` that you uploaded in module 1, so every generated
  question is answerable from the library. To use other documents, change
  `DOCS_DIR` in 03a.
- **Behind or MyGPT not working?** Set `USE_FALLBACK = True` in notebook 3b. It uses the
  scored PubMedQA run from MyGPT-evaluations (294 questions with human correctness labels).

| Time | Activity |
|---|---|
| 0–5 min | Concepts |
| 5–15 min | `03a_generate_questions.ipynb`: generate questions, review them, run them through MyGPT |
| 15–27 min | `03b_label_and_judge.ipynb`: hand-label, run the LLM judge, measure agreement |
| 27–30 min | Checkpoint |

## Concepts

A benchmark is only useful if its labels are correct. This module builds one in three
layers:

```
documents ─► LLM-generated Q + reference answer ─► human review (keep / edit / drop)
          ─► MyGPT answers + QRS/ARS/HI
          ─► labels: human (gold, small)  +  LLM judge (cheap, large)
          ─► check: does the judge agree with humans? (accuracy, Cohen's κ, confusion matrix)
```

- **Question types to include:** factual lookups, questions that need two chunks, and
  ~10–20 % **unanswerable** questions (off-topic, or not in your documents). Without
  unanswerable questions you can't tell whether HI catches hallucinations.
- **Label scheme:** `1 = correct` (the answer agrees with the reference and is supported),
  `0 = incorrect` (wrong, unsupported, or answers a question the library can't answer).
  For an unanswerable question, the correct answer says the information is not in the
  library.
- **Trusting the judge:** hand-label at least 20 items. If Cohen's κ ≥ 0.6, use judge labels
  for the rest. If not, improve the judge prompt or label more by hand.

This is the same Collect Context → Collect Answers → Score → Format → Combine flow used
in [MyGPT-evaluations](https://github.com/stjude/MyGPT-evaluations), at workshop scale.

## Hands-on

1. **[03a_generate_questions.ipynb](03a_generate_questions.ipynb)**
   - Chunk your documents and ask the LLM to write a question and reference answer for
     each sampled chunk.
   - Review `workshop_outputs/03_questions.csv`, then run each question through MyGPT.
2. **[03b_label_and_judge.ipynb](03b_label_and_judge.ipynb)**
   - Hand-label at least 20 answers in the notebook, or fill in the `human_label`
     column of `workshop_outputs/03_to_label.csv` in a spreadsheet.
   - Run the LLM judge on every row.
   - Compare judge and human labels. Continue with the optional calibration workflow only
     after you are satisfied with the judge agreement.

### Optional: calibrate weights with the BioASQ questions

This optional step is not part of the 30-minute core exercise. It reuses the LLM judge
validated in 03b and does not ask for more manual labels or another Cohen's κ check.

3. **[03c_create_calibration_dataset.ipynb](03c_create_calibration_dataset.ipynb)**
   - Load the original BioASQ questions and ground truths from
     `data/BioASQ/questions_all_164.csv` (the current file contains 163 complete rows).
   - Run every question through MyGPT, then apply the validated LLM judge against its
     yes/no or factoid ground truth. The combined notebook checkpoints API answers and
     judge progress so interrupted runs can resume.
   - The output `workshop_outputs/03_calibration_eval_dataset.csv` is the input for
     module 4. No generated questions or added irrelevant controls are used.

[`templates/labels_template.csv`](templates/labels_template.csv) shows the expected
columns if you'd rather label in Excel or Google Sheets.

## Checkpoint

- [ ] At least 20 reviewed pilot questions, including some unanswerable ones.
- [ ] At least 20 rows hand-labelled.
- [ ] Judge-vs-human agreement and κ printed; you can say whether the judge is good
      enough.
- [ ] (Optional, for module 4) The BioASQ questions have been run and judge-labeled in
      03c; `workshop_outputs/03_calibration_eval_dataset.csv` is saved.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Generated questions are vague ("What does the document say?") | Lower the temperature, use a bigger LLM, or tighten the prompt in 03a |
| Judge marks almost everything correct | Typical for small models. Use a stronger `JUDGE_LLM`, or add few-shot examples to the judge prompt |
| Every judge reply fails to parse | The model ignores JSON mode. The notebook falls back to a regex; check the `judge_raw` column |
| Generation takes too long | Reduce `N_CHUNKS` in 03a; 03c is optional and takes longer |

## Going further

- Several judges (different LLMs), with a majority vote.
- Separate scores for *correctness* and *groundedness*.
- BioASQ and PubMedQA in MyGPT-evaluations are larger public benchmarks with the same
  structure.
