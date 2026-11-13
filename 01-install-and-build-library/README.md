# Module 1 — Install MyGPT and build a library (30 min)

## Objectives

- Get MyGPT (UI, backend, Ollama) running on your laptop.
- Build a document library from your own files.
- Learn how each pipeline setting changes what MyGPT retrieves and how confident it is.

## Before you start

- You have finished [SETUP.md](../SETUP.md) steps 1–3: Docker running, models pulled,
  superuser created.
- You have 5–20 documents in `data/my_docs/`, or you ran
  `docker compose exec workshop python data/get_sample_docs.py`.
- The workshop container is running (`docker compose up -d`). You won't use it until
  module 2, but starting it now catches problems early.

| Time | Activity |
|---|---|
| 0–5 min | Check that the stack is running |
| 5–15 min | Build the library with default settings |
| 15–28 min | Settings experiment ([worksheet](settings_experiment.md)) |
| 28–30 min | Checkpoint |

## Concepts

MyGPT has three parts: a **React UI**, a **Django backend** that does chunking,
embedding, retrieval and scoring, and an **Ollama LLM server**. Building a library
runs this pipeline once per document:

```
document ─► text extraction ─► chunking ─► embedding ─► vector DB (Chroma) + BM25 index
```

At question time:

```
question ─► semantic search + keyword (BM25) search ─► optional reranker ─► top-k chunks
         ─► LLM answer ─► QRS (question relevance), ARS (answer relevance), HI (hallucination index)
```

### Pipeline settings and their effects

| Setting | Where | What it controls | Typical effect of changing it |
|---|---|---|---|
| **Chunking method** | Upload → Advanced | Fixed-size, or recursive (keeps document structure) | Recursive keeps sections whole; fixed-size is more predictable |
| **Chunk size** | Upload → Advanced | Characters per chunk (recommended: 1000) | Smaller chunks give precise hits but less context per hit; larger chunks dilute the match |
| **Chunk overlap** | Upload → Advanced | Characters shared between neighbouring chunks | Overlap stops answers being cut in half at chunk edges, at the cost of a bigger index |
| **Embedding model** | Upload → Advanced | How text becomes vectors (`nomic-embed-text`, `bge-m3`, `MedCPT`, …) | The biggest effect on retrieval quality; use a multilingual model for non-English documents. **Can't be changed after the library is built** |
| **Distance function** | Upload → Advanced | Cosine, L2 or inner product for semantic search | Changes the distance scale, so QRS/ARS cutoffs must match it |
| **BM25** | Upload → Advanced | Adds keyword search alongside vector search | Helps with gene names, IDs and acronyms that embeddings miss |
| **Reranker** | Upload → Advanced / chat settings | Cross-encoder that re-orders retrieved chunks | Better precision, slower answers |
| **Max chunks (k)** | Chat settings | Number of chunks passed to the LLM | More context, but more noise and slower generation |
| **QC best / worst** | Chat settings | Distance range mapped to QRS 100 → 0 | Raising QCworst lets weaker matches through ([FAQ 18](https://github.com/stjude/MyGPT/blob/main/FAQs.md)) |
| **LLM, temperature, top-k/p** | Chat settings | Generation model and creativity | Low temperature for factual Q&A |

The pre-calculated QC/AC cutoffs for each embedding model are in the
[QRS-ARS-cutoff README](https://github.com/stjude/MyGPT-evaluations/blob/main/QRS-ARS-cutoff/README.md).

## Hands-on

### Step 1 — Check the stack (5 min)

```bash
docker ps                          # MyGPT frontend, backend, db + mygpt-workshop should be "Up"
curl -s http://localhost:11434     # "Ollama is running"
ollama list                        # nomic-embed-text and llama3 (or gpt-oss) listed
```

Open the MyGPT UI (the URL is printed by `run_docker.sh`, usually
<http://localhost:3000> or <http://localhost>) and sign in.

### Step 2 — Build a baseline library (10 min)

1. Click **Upload / Create library**.
2. Name it `workshop-library`. This must match `MYGPT_DATASET` in `.env`.
3. Choose **Advanced settings** and use the baseline values:
   - Chunking: fixed-size, **1000** characters, overlap **200**
   - Embedding model: **nomic-embed-text**
   - BM25: **on**, reranker: **off**
4. Upload your documents and wait until indexing finishes.
5. Ask 3 questions from [`data/sample_questions.csv`](../data/sample_questions.csv), or
   your own. Note the QRS, ARS and HI for each.

### Step 3 — Settings experiment (13 min)

Work through [settings_experiment.md](settings_experiment.md). Build **one** extra
library with one setting changed, ask the same questions, and record the scores.
Change one variable at a time, so any difference comes from that setting.

## Checkpoint

- [ ] `workshop-library` appears on the MyGPT home page with all your documents.
- [ ] One on-topic question gives QRS > 50 and cites your documents.
- [ ] One off-topic question (for example the tungsten question) gives low QRS and high HI.
- [ ] Your worksheet table has at least one row comparing two settings.

## Troubleshooting

| Symptom | Fix |
|---|---|
| UI loads but upload fails | Backend not ready. Run `docker logs <backend-container>` and wait for migrations to finish |
| `connection refused` on port 11434 | Start the Ollama app, or run `ollama serve` |
| Indexing is very slow | Give Docker more CPU/RAM; use fewer or smaller documents; use `nomic-embed-text` |
| QRS is always 0 | Embedding model and QC cutoffs don't match. Use defaults or raise QCworst ([FAQ 18](https://github.com/stjude/MyGPT/blob/main/FAQs.md)) |
| Scanned PDFs return nothing | MyGPT only extracts the text layer. Run OCR first |

## Going further

- MyGPT FAQs 19, 40 and 41 (library options and recommended settings):
  <https://github.com/stjude/MyGPT/blob/main/FAQs.md>
- Import a Zotero collection as a library instead of uploading files.
