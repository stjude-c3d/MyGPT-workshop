# Pre-workshop setup

Please finish this checklist **before** the workshop. Downloading Docker images and LLM
weights over conference Wi-Fi can take longer than the whole session.

## Laptop requirements

| | Minimum | Recommended |
|---|---|---|
| RAM | 8 GB | 16 GB or more |
| Free disk | 15 GB | 25 GB |
| CPU | 8 cores | Apple Silicon, or a recent x86 CPU |
| OS | macOS, Linux, or Windows 10/11 with WSL2 | |

## 1. Install the tools

| Tool | Check | Install |
|---|---|---|
| Git | `git --version` | <https://git-scm.com/downloads> |
| Docker Desktop | `docker --version` | <https://docs.docker.com/get-docker/> |
| Ollama | open <http://localhost:11434> | <https://ollama.com/download> |
| uv (needed for module 5) | `uv --version` | <https://docs.astral.sh/uv/getting-started/installation/> |
| VS Code + GitHub Copilot (module 5) | — | <https://code.visualstudio.com/>, then sign in to Copilot |

In Docker Desktop, go to **Settings → Resources** and give it at least 8 GB of memory.

## 2. Download the models (the slowest step)

```bash
ollama pull nomic-embed-text      # embedding model, about 270 MB
ollama pull llama3                # generation model for 8–16 GB laptops, about 4.7 GB
```

If you have 32 GB of RAM or more, you can also pull `gpt-oss:20b` (about 13 GB). The
MyGPT paper used this model.

## 3. Install MyGPT

Follow the MyGPT installation guide for your OS, using the **pre-built images**
option:

- macOS: <https://github.com/stjude/MyGPT/blob/main/installation/macOS/README.md>
- Linux: <https://github.com/stjude/MyGPT/blob/main/installation/linux/README.md>
- Windows: <https://github.com/stjude/MyGPT/blob/main/installation/windows/README.md>

Then create a backend user. You will use it to sign in to the API in modules 2–4:

```bash
cd MyGPT/installation/macOS/prebuilt_images   # use your OS folder
bash create_superuser.sh
```

Check that it worked: <http://localhost:8000/admin/> should accept that username and
password.

## 4. Set up this repository (Docker)

```bash
git clone https://github.com/stjude-c3d/MyGPT-workshop.git
cd MyGPT-workshop
cp .env.example .env
docker compose pull          # downloads the prebuilt workshop image, about 1.5 GB
docker compose up -d
```

Edit `.env`: set `MYGPT_USERNAME` and `MYGPT_PASSWORD` to the user you just created.
Leave the URLs alone. Inside the container, `compose.yaml` points them at
`host.docker.internal`, which reaches MyGPT and Ollama on your laptop.

Open JupyterLab at <http://localhost:8888/lab?token=mygpt-workshop>. Your clone is
mounted at `/workspace`, so anything you save there (notebooks, `data/`,
`workshop_outputs/`) stays on your laptop after the container stops.

Everyday commands:

| Task | Command |
|---|---|
| Start / stop | `docker compose up -d` / `docker compose down` |
| Run a script in the container | `docker compose exec workshop python <script>` |
| Shell in the container | `docker compose exec workshop bash` |
| Logs (e.g. to find the Jupyter URL) | `docker compose logs workshop` |
| Port 8888 already in use | `WORKSHOP_PORT=8890 docker compose up -d` |

## 5. Choose your documents

Bring **5–20 documents** (PDF, DOCX or TXT) that you are allowed to process, such as
your own papers, lab protocols or public guidelines. Put them in `data/my_docs/` so
the container can see them too. If you have none, download the Turing Way sample
library:

```bash
docker compose exec workshop python data/get_sample_docs.py   # saves to data/sample_docs/
```

## 6. Clone the Turing Way MCP repository (module 5)

```bash
git clone https://github.com/stjude-biohackathon/KIDS26-Team20.git
cd KIDS26-Team20
uv sync --extra dev --frozen
uv run python scripts/project.py doctor
```

## Final check

```bash
docker compose exec workshop python -c "from common.mygpt_client import MyGPTClient; c = MyGPTClient.from_env(); print(c.list_datasets())"
```

An empty list `[]` means you are ready. A connection error means MyGPT is not running;
see [module 1 troubleshooting](01-install-and-build-library/README.md#troubleshooting).

## Alternative: local Python

If you can't run the workshop container, use a virtual environment with Python 3.10+.
Outside Docker, the `localhost` URLs in `.env` are correct as they are.

```bash
python3 -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.lock                     # exact versions used in the image
jupyter lab
```

Wherever the module READMEs say `docker compose exec workshop python …`, run `python …`
instead.

## Updating the image (maintainers)

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
