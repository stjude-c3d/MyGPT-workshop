# Module 2 — Query your library with the MyGPT API (20 min)

## Objectives

- Sign in to the MyGPT backend and call its REST API from Python.
- Run the full RAG round trip yourself: retrieve → generate → score.
- Batch-query a list of questions and save the results for module 3.

## Before you start

- Module 1 is done: `workshop-library-A` exists, MyGPT is running, and the BioASQ inputs
   are available in `data/BioASQ/`.

### Start the workshop container

From the workshop repository root, create the environment file and set the library
name and MyGPT credentials:

```bash
cp .env.example .env
```

Set `MYGPT_DATASET=workshop-library-A`, `MYGPT_USERNAME`, and `MYGPT_PASSWORD` in `.env`.
Leave the URLs unchanged; `compose.yaml` uses `host.docker.internal` to reach MyGPT and
Ollama on your laptop. Then pull and start the workshop container:

```bash
docker compose pull
docker compose up -d
```

Open JupyterLab at <http://localhost:8888/lab?token=mygpt-workshop>. The repository is
mounted at `/workspace`, so notebooks, data, and `workshop_outputs/` persist on your
laptop.

| Task | Command |
|---|---|
| Start / stop | `docker compose up -d` / `docker compose down` |
| Run a script in the container | `docker compose exec workshop python <script>` |
| Shell in the container | `docker compose exec workshop bash` |
| Logs | `docker compose logs workshop` |
| Port 8888 already in use | `WORKSHOP_PORT=8890 docker compose up -d` |

### Alternative: local Python

If you can't run the workshop container, use Python 3.10+ in a virtual environment.
The default `localhost` URLs in `.env` are correct outside Docker.

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\\Scripts\\activate
pip install -r requirements.lock
jupyter lab
```

Wherever the module READMEs say `docker compose exec workshop python …`, run `python …`
instead.

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
calls. `client.ask(question)` runs all three steps and returns a single row of results;
`HI` uses `hallucination_index_by_ml`, while the equation-based value is available as
`HI_equation`.

## Hands-on

1. Open [`02_query_api.ipynb`](02_query_api.ipynb) and run it from top to bottom.
2. Try the command-line version, run inside the container from your laptop's terminal:

   ```bash
   docker compose exec workshop python 02-query-via-api/scripts/query_library.py --question "Do glioblastoma tumors have a high degree of lymphocyte infiltration?"
   ```

   ```bash
   docker compose exec workshop python 02-query-via-api/scripts/query_library.py \
         --questions data/BioASQ/questions_25.csv \
         --out workshop_outputs/02_query_results.csv
   ```

      This runs the 163 BioASQ test questions and may take a while. You can also open a
      **Terminal** in JupyterLab and run `python 02-query-via-api/...` directly.

3. **Optional:** use `--dataset workshop-library-B` to rerun the batch on your module 1
   comparison library and compare the two CSVs.

## Checkpoint

- [ ] The notebook connects to `workshop-library-A` and `get_documents` lists its documents (397 BioASQ papers in the instructor run).
- [ ] `workshop_outputs/02_query_results.csv` exists, with columns `QRS`, `ARS` and `HI`.
- [ ] You compared the off-topic control question with the on-topic ones. QRS alone may not flag it (the instructor run gave QRS 64, higher than some BioASQ questions); check HI and the answer text too.

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
