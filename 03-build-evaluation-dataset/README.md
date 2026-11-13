# Module 3 — Build an evaluation dataset from your library (30 min)

## Objectives

- Generate question/reference-answer pairs from your own documents.
- Run them through MyGPT and collect answers with QRS, ARS and HI.
- Label answers by hand **and** with an LLM judge, then measure how far you can trust
  the judge (agreement with your labels, Cohen's κ).

## Before you start

- Modules 1–2 are done: the library exists and `client.ask()` works.
- The documents you used for the library are in the repo folder, so the container can
  read them: `data/my_docs/`, or `data/sample_docs/` for the sample library. Set
  `DOCS_DIR` in 03a to match.
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
   - Add your own unanswerable questions.
   - Review the questions in `workshop_outputs/03_questions.csv`: delete bad rows, edit
     unclear ones.
   - Run each question through MyGPT and save `workshop_outputs/03_answers.csv`.
2. **[03b_label_and_judge.ipynb](03b_label_and_judge.ipynb)**
   - Hand-label at least 20 answers in the notebook, or fill in the `human_label`
     column of `workshop_outputs/03_to_label.csv` in a spreadsheet.
   - Run the LLM judge on every row.
   - Compare judge and human labels, then save `workshop_outputs/03_eval_dataset.csv`
     for module 4.

[`templates/labels_template.csv`](templates/labels_template.csv) shows the expected
columns if you'd rather label in Excel or Google Sheets.

## Checkpoint

- [ ] At least 20 reviewed questions, including some unanswerable ones.
- [ ] At least 20 rows hand-labelled.
- [ ] Judge-vs-human agreement and κ printed; you can say whether the judge is good
      enough.
- [ ] `workshop_outputs/03_eval_dataset.csv` saved with a `label` column.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Generated questions are vague ("What does the document say?") | Lower the temperature, use a bigger LLM, or tighten the prompt in 03a |
| Judge marks almost everything correct | Typical for small models. Use a stronger `JUDGE_LLM`, or add few-shot examples to the judge prompt |
| Every judge reply fails to parse | The model ignores JSON mode. The notebook falls back to a regex; check the `judge_raw` column |
| Generation takes too long | Reduce `N_CHUNKS` in 03a to 10–15 |

## Going further

- Several judges (different LLMs), with a majority vote.
- Separate scores for *correctness* and *groundedness*.
- BioASQ and PubMedQA in MyGPT-evaluations are larger public benchmarks with the same
  structure.
