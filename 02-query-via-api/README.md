# Module 2 — Query your library with the MyGPT API (20 min)

## Objectives

- Sign in to the MyGPT backend and call its REST API from Python.
- Run the full RAG round trip yourself: retrieve → generate → score.
- Batch-query a list of questions and save the results for module 3.

## Before you start

- Module 1 is done: `workshop-library` exists and `.env` has `MYGPT_DATASET`,
  `MYGPT_USERNAME` and `MYGPT_PASSWORD` set.
- The workshop container is running (`docker compose up -d`) and JupyterLab is open at
  <http://localhost:8888/lab?token=mygpt-workshop>.

| Time | Activity |
|---|---|
| 0–5 min | Concepts + sign in |
| 5–15 min | Notebook: single query, then a batch |
| 15–20 min | CLI script + checkpoint |

## Concepts

The UI is just one client of the Django backend. Anything you can do in the UI, you can
script. These are the endpoints used here (full reference in
[development.md](https://github.com/stjude/MyGPT/blob/main/development.md)):

| Endpoint | Purpose | Returns |
|---|---|---|
| `POST /token/` | Exchange username/password for a JWT | `access`, `refresh` |
| `POST /api/get_datasets/` | List libraries | `dataset_name`, `dataset_size`, … |
| `POST /api/get_documents/` | List documents in a library | `documents`, `dataset_type` |
| `POST /api/get_context/` | Retrieve chunks for a question | `context`, `sources`, **QRS** (`relevance_score`), `semantic_score`, `keyword_score`, `rerank_score` |
| `POST /api/ollama_generate/` | Generate text with the LLM | `response` |
| `POST /api/save_answer/` | Store an answer and score it | **ARS** (`relevance_score`), `hallucination_index_by_equation`, `hallucination_index_by_ml` |

The shared helper [`common/mygpt_client.py`](../common/mygpt_client.py) wraps these
calls. `client.ask(question)` runs all three steps and returns a single row of results.

## Hands-on

1. Open [`02_query_api.ipynb`](02_query_api.ipynb) and run it from top to bottom.
2. Try the command-line version, run inside the container from your laptop's terminal:

   ```bash
   docker compose exec workshop python 02-query-via-api/scripts/query_library.py --question "What is version control?"
   ```

   ```bash
   docker compose exec workshop python 02-query-via-api/scripts/query_library.py \
          --questions data/sample_questions.csv --out workshop_outputs/02_query_results.csv
   ```

   You can also open a **Terminal** in JupyterLab and run `python 02-query-via-api/...`
   directly.

3. **Optional:** use `--dataset workshop-library-b` to rerun the batch on your module 1
   comparison library and compare the two CSVs.

## Checkpoint

- [ ] `client.list_datasets()` shows `workshop-library`.
- [ ] `workshop_outputs/02_query_results.csv` exists, with columns `QRS`, `ARS` and `HI`.
- [ ] The off-topic control question has the lowest QRS in the batch.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `Connection refused` / `Name or service not known` from the notebook | Inside the container, MyGPT is at `host.docker.internal:8000`, not `localhost`. Check that `client.base_url` shows that address and that MyGPT is up on your laptop (`curl localhost:8000/admin/`). If MyGPT runs elsewhere, set `DOCKER_MYGPT_BASE_URL` in `.env` and run `docker compose up -d` again |
| `401 Unauthorized` | Wrong `MYGPT_USERNAME`/`MYGPT_PASSWORD`, or the user doesn't exist. Rerun `create_superuser.sh` |
| `400` from `get_context` | `MYGPT_DATASET` doesn't match the library name exactly, or `MYGPT_EMBEDDING_MODEL` differs from the one used to build it |
| Request times out | LLM is too large for your RAM. Switch `MYGPT_LLM` to a smaller model (`llama3:latest`, `llama3.2`) |
| `save_answer` returns 500 | Call `get_context` for the same question first; `ask()` does this for you |

## Going further

- `MyGPT/scripts/python_api_client.py`: the reference client this helper is based on.
- MyGPT-evaluations `*/scripts/collect_context.py` → `collect_answers.py` →
  `save_answers.py` run the same three steps at benchmark scale.
