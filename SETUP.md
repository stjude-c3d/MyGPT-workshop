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
In Docker Desktop, go to **Settings → Resources** and give it at least 8 GB of memory.

## 2. Download the models (the slowest step)

```bash
ollama pull nomic-embed-text      # embedding model, about 270 MB
ollama pull bge-m3                # optional alternative embedding model
ollama pull llama3                # generation model for 8–16 GB laptops, about 4.7 GB
```

If you have 32 GB of RAM or more, you can also pull `gpt-oss:20b` (about 13 GB). The
MyGPT paper used this model.

## 3. Check local inference speed (optional)

With Ollama running and `llama3` downloaded, time a representative generation request:

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

This prints the total time it might take to run typical MyGPT queries. Run the same
command multiple times and average the results. Ollama generally loads the model into
memory, so the first query may take longer; subsequent queries should be faster.

Example output:

```text
Total: 9.975889s
```

If it takes more than a minute, your laptop might not have enough resources to run Ollama.
