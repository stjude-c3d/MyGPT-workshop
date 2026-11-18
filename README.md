# MyGPT: Building your own RAG Swiss Army knife for reliable knowledge discovery

*KIDS26 workshop · St. Jude Children's Research Hospital*

Hands-on workshop material for **MyGPT**, St. Jude's open-source, privacy-first
retrieval-augmented generation (RAG) platform, presented at the KIDS26 conference.

In about two hours you will build a document library from your own files, query it
from code, build a benchmark for it, tune its confidence scores for your field, and
connect it to an AI coding assistant through MCP.

| Resource | Link |
|---|---|
| MyGPT source | <https://github.com/stjude/MyGPT> |
| MyGPT evaluation pipelines | <https://github.com/stjude/MyGPT-evaluations> |
| Turing Way MCP server and skills (KIDS26 Team 20) | <https://github.com/stjude-biohackathon/KIDS26-Team20> |
| MyGPT paper | Patel et al. (2026), *Nature Communications*, [10.1038/s41467-026-78509-6](https://doi.org/10.1038/s41467-026-78509-6) |

## Agenda

| # | Module | Time | Format |
|---|---|---|---|
| 0 | [Prerequisites](SETUP.md) — install tools and choose where the models run | 20 min, at home | Checklist |
| 1 | [Install MyGPT and build a library](01-install-and-build-library/README.md) | 30 min | README + worksheet |
| 2 | [Query the library through the backend API](02-query-via-api/README.md) | 20 min | Notebook + script |
| 3 | [Build an evaluation dataset](03-build-evaluation-dataset/README.md) | 30 min | 2 notebooks |
| 4 | [Recalibrate QRS, ARS and HI weights](04-recalibrate-weights/README.md) | 20 min | Notebook |
| 5 | [MCP server and skills for AI coding (Turing Way)](05-mcp-server-ai-coding/README.md) | 20 min | README + configs |

## How the modules connect

Each module writes its results to `workshop_outputs/` (ignored by Git), and the next
module reads them:

```
Module 1 ──► library name (in .env)
Module 2 ──► workshop_outputs/02_query_results.csv
Module 3 ──► pilot + Cohen's κ ──► (optional) 03c BioASQ run + judge ──► 03_calibration_eval_dataset.csv
Module 4 ──► workshop_outputs/04_recalibrated_weights.json ──► MyGPT chat settings
Module 5 ──► Turing Way MCP server + skills in GitHub Copilot
```

If you fall behind or a step fails, modules 3 and 4 can use a **fallback dataset**:
the scored PubMedQA run published in MyGPT-evaluations. You can pick up at any module.

## Repository layout

```
MyGPT-workshop/
├── README.md                    # this file
├── SETUP.md                     # laptop prerequisites and model options
├── compose.yaml                 # starts JupyterLab in Docker (prebuilt image from ghcr.io)
├── Dockerfile                   # how the workshop image is built
├── requirements.txt / .lock     # Python packages (the .lock pins exact versions for the image)
├── .env.example                 # copy to .env and fill in
├── .github/workflows/           # builds and publishes the image to ghcr.io
├── common/mygpt_client.py       # shared MyGPT REST client used by modules 2–4
├── data/                        # BioASQ inputs (excluded from Docker image) and fallback cache
├── 01-install-and-build-library/
├── 02-query-via-api/
├── 03-build-evaluation-dataset/
├── 04-recalibrate-weights/
└── 05-mcp-server-ai-coding/
```

Each module folder has a `README.md` with the same sections: **Objectives → Before you
start → Concepts → Hands-on → Checkpoint → Troubleshooting → Going further**.

## Quick start

Start with [Module 1](01-install-and-build-library/README.md) to install MyGPT and
build the library. JupyterLab is first needed in module 2; follow its
[container setup](02-query-via-api/README.md#start-the-workshop-container) then.

MyGPT runs on your laptop; JupyterLab runs in the `ghcr.io/stjude-c3d/mygpt-workshop`
container and talks to it. By default Ollama also runs on your laptop (option A):

```
your laptop
├── MyGPT (Docker)           :8000  ◄──┐
├── Ollama (native app)      :11434 ◄──┤ host.docker.internal
└── mygpt-workshop (Docker)  :8888  ───┘  JupyterLab, your clone mounted at /workspace
```

If your laptop is below the requirements in [SETUP.md](SETUP.md#choose-where-the-models-run),
the models run elsewhere instead: on the St. Jude Ollama server (option B, St. Jude
employees) or through the OpenAI API (option C, your own key). MyGPT and JupyterLab
stay on your laptop either way.

Can't use Docker? See [Module 2 → Alternative: local Python](02-query-via-api/README.md#alternative-local-python).

## Image maintenance

The image is built by [`.github/workflows/docker-image.yml`](.github/workflows/docker-image.yml)
for `linux/amd64` and `linux/arm64`, then pushed to `ghcr.io/stjude-c3d/mygpt-workshop`:

| Event | Tags pushed |
|---|---|
| Push to `main` that touches the image | `latest`, `sha-<short>` |
| Tag `v1.2.3` | `1.2.3`, `v1.2.3`, `sha-<short>` |
| Pull request | builds only, no push |

To change the Python packages, edit `requirements.txt`, then regenerate the lock inside
the base image:

```bash
docker run --rm -v "$PWD/requirements.txt:/r.txt:ro" python:3.12-slim \
  sh -c "pip install -q -r /r.txt >/dev/null && pip freeze" > requirements.lock
```

After the first publish, a GitHub org admin must make the package **public**
(Package settings → Change visibility) so attendees can pull without signing in.
Before the workshop, push a tag such as `v2026.1`, and set
`WORKSHOP_IMAGE_TAG=2026.1` in `.env` to pin everyone to that build.

## Responsible use

- Use only documents you are allowed to process. MyGPT runs locally, but **do not**
  put clinical, human-subject or confidential data into a workshop laptop setup.
- Never commit `.env` or any credentials. `.gitignore` excludes them.
- LLM-judge labels and recalibrated weights are only as good as the human labels you
  check them against. Treat them as evidence, not ground truth.

## Citation

If you use MyGPT in your work, please cite:

> Patel J, *et al.* Democratizing reliable knowledge-seeking with MyGPT: A Privacy-First,
> Open-Source Retrieval-Augmented Generation Platform. *Nature Communications* (2026).
> doi:10.1038/s41467-026-78509-6
