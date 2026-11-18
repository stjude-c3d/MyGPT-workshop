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

These requirements are for running the models on your laptop (option A below).

## Choose where the models run

MyGPT needs an LLM and an embedding model. Pick **one** option and use it for the whole
workshop: a library built with one embedding model can't be queried with another.

| Option | Who it's for | LLM / embedding model | What you need |
|---|---|---|---|
| **A. Ollama on your laptop** (default) | Laptops that meet the requirements above | `llama3` / `nomic-embed-text` | Ollama installed and the models pulled (steps 1–3) |
| **B. St. Jude Ollama server** | St. Jude employees whose laptop is below the requirements | `llama3` / `nomic-embed-text` on the shared server | The server URL from the instructors, and St. Jude Wi-Fi (or Cloudflare turned on when working from home). No Ollama or model downloads on your laptop |
| **C. OpenAI API** | Everyone else whose laptop is below the requirements | `gpt-6-luna` / `text-embedding-3-small` | Your own OpenAI API key with API billing enabled. No Ollama or model downloads |

Options B and C still run MyGPT (its UI, backend and database) in Docker on your laptop,
but the models run elsewhere, so far less RAM and disk is needed.

> **Option C sends data to OpenAI and costs money.** Document chunks, questions, answers
> and chat history go to OpenAI's API, and each call is billed to your key. A ChatGPT
> subscription does not include API usage. Only use documents you are allowed to send
> to OpenAI; the workshop's BioASQ PDFs are fine. Never share or commit your key.

You set the option when you install MyGPT in
[module 1](01-install-and-build-library/README.md#install-mygpt): it goes in MyGPT's
`.env_backend` file. See [Workshop settings for options B and C](#workshop-settings-for-options-b-and-c)
for the matching settings in this repository's `.env`.

## 1. Install the tools

| Tool | Check | Install |
|---|---|---|
| Git | `git --version` | <https://git-scm.com/downloads> |
| Docker Desktop | `docker --version` | <https://docs.docker.com/get-docker/> |
| Ollama (**option A only**) | open <http://localhost:11434> | <https://ollama.com/download> |

In Docker Desktop, go to **Settings → Resources** and give it at least 8 GB of memory
(option A). For options B and C, 4 GB is enough.

**Option C:** create an API key at <https://platform.openai.com/api-keys>, and enable API
billing for its project. Keep the key private; you'll paste it into MyGPT's
`.env_backend` in module 1.

## 2. Download the models (option A only; the slowest step)

```bash
ollama pull nomic-embed-text      # embedding model, about 270 MB
ollama pull bge-m3                # optional alternative embedding model
ollama pull llama3                # generation model for 8–16 GB laptops, about 4.7 GB
```

If you have 32 GB of RAM or more, you can also pull `gpt-oss:20b` (about 13 GB). The
MyGPT paper used this model.

## 3. Check inference speed (options A and B, optional)

With Ollama running and `llama3` downloaded, time a representative generation request.
For **option B**, replace `http://localhost:11434` in the commands below with the
St. Jude server URL; this also checks that you can reach the server. The server is only
reachable on St. Jude Wi-Fi, or from home with Cloudflare turned on. It hosts `llama3`
and `nomic-embed-text` under those names, so the commands work unchanged.

On Mac, run this in the Terminal:

```bash
curl -sS -o /dev/null -w 'Total: %{time_total}s\n' \
  http://localhost:11434/api/generate \
  -d '{
    "model": "llama3",
    "stream": false,
    "prompt": "Despite the diversity among GPCRs, are there similarities in their activation pathways?",
    "system": "Use only this information and answer in fewer than 200 words: Class A GPCRs have diverse ligands and activation pathways, but structural rearrangements converge near the G-protein coupling region. Common changes include contraction of the ligand-binding site and opening of the cytosolic side through TM6 movement. The detailed ligand-driven mechanism can still differ by receptor."
  }'
```

On Windows, run this PowerShell version instead:

```powershell
$body = '{"model":"llama3","stream":false,"prompt":"Despite the diversity among GPCRs, are there similarities in their activation pathways?","system":"Use only this information and answer in fewer than 200 words: Class A GPCR activation pathways are diverse but converge near the G-protein coupling region. Common changes include contraction of the ligand-binding site and opening of the cytosolic side through TM6 movement."}'
$seconds = (Measure-Command { Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -ContentType "application/json" -Body $body | Out-Null }).TotalSeconds
"Total: {0:F6}s" -f $seconds
```

This prints the total time it might take to run typical MyGPT queries. Run the same
command multiple times and average the results. Ollama generally loads the model into
memory, so the first query may take longer; subsequent queries should be faster.

Example output:

```text
Total: 9.975889s
```

If it takes more than a minute, your laptop might not have enough resources to run Ollama.
Switch to option B (St. Jude employees) or option C.

## Workshop settings for options B and C

Skip this section for option A. After you clone this repository in module 1, copy
`.env.example` to `.env`, then set these lines:

**Option B — St. Jude Ollama server**

```bash
OLLAMA_URL=<St. Jude Ollama server URL>          # local-Python alternative
DOCKER_OLLAMA_URL=<St. Jude Ollama server URL>   # JupyterLab container
```

**Option C — OpenAI API**

```bash
MYGPT_LLM=gpt-6-luna
MYGPT_EMBEDDING_MODEL=text-embedding-3-small
JUDGE_LLM=gpt-6-luna
```

Your OpenAI key stays in MyGPT's `.env_backend` only, never in this repository's `.env`.
The notebooks send every LLM call for an OpenAI model through MyGPT, which holds the
key, so they need `MYGPT_USERNAME` and `MYGPT_PASSWORD` set as in module 2.
