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
