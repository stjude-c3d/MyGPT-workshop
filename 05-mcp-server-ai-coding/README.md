# Module 5 — MyGPT + Turing Way MCP server and skills for AI coding (20 min)

## Objectives

- Understand what an MCP server and an agent skill each add to an AI coding assistant.
- Run the **Turing Way MCP server** built by KIDS26 Team 20 and connect it to
  **GitHub Copilot** in VS Code.
- Use the Turing Way skills to get cited guidance and review a research repository —
  for example, this workshop repo.

Source: <https://github.com/stjude-biohackathon/KIDS26-Team20> (MIT; the Turing Way
corpus is CC-BY-4.0, pinned to one commit).

## Before you start

- You did [SETUP.md](../SETUP.md) step 6: `KIDS26-Team20` cloned, `uv sync` run, and
  `doctor` checked.
- VS Code with GitHub Copilot Chat, signed in, with **Agent** mode available.
- **Optional, for full RAG:** Docker Desktop running (from module 1).

| Time | Activity |
|---|---|
| 0–4 min | Concepts: MCP, skills, Turing Way |
| 4–10 min | Start the MCP server and connect it to Copilot |
| 10–13 min | Load the skills into Copilot |
| 13–20 min | Exercises + checkpoint |

## Concepts

```
 GitHub Copilot (Agent mode)
   │  reads SKILL.md  ──►  "how to do the task" (workflow, rules, failure behaviour)
   │  calls MCP tools ──►  turing-way MCP server ──► Turing Way corpus (pinned, cited)
   │                                       └─────► MyGPT library API (RAG over the corpus)
   ▼
 Answer with citations, or "I can't answer from the approved sources"
```

| Piece | What it is | In Team 20's repo |
|---|---|---|
| **MCP server** | Gives the assistant typed **tools** and data over a standard protocol (stdio or HTTP) | `src/learning_assistant/server.py` |
| **Skill** | A `SKILL.md` playbook the assistant loads when a request matches its description | `.agents/skills/<name>/SKILL.md` |
| **Corpus** | The only sources answers may cite | `corpus/sources.yaml` → The Turing Way at commit `bb3f7ab…` |

**MCP tools** exposed by the server:

| Tool | Purpose |
|---|---|
| `list_resources`, `get_resource` | Browse and read Turing Way pages (GitHub, or the offline snapshot) |
| `list_mygpt_datasets`, `list_mygpt_documents` | Read-only views of a MyGPT deployment |
| `query_mygpt_context` | Retrieve cited MyGPT evidence for a question |
| `get_rag_status` | Check that MyGPT can retrieve Turing Way evidence |
| `get_turing_way_review_evidence`, `get_turing_way_evidence_packets`, `validate_turing_way_review`, `render_validated_turing_way_review` | Evidence gathering and validation used by the review skills |

**Skills** you will use: `turing-way-pathfinder`, `turing-way-guidance`,
`turing-way-review`, `mygpt-library`, and `skill-template` (for writing your own).

### Turing Way concepts this setup demonstrates

| Turing Way principle | How the MCP + skills setup applies it |
|---|---|
| Reproducible research / computational environments | Pinned corpus commit, `uv.lock`, Docker Compose, deterministic offline tests |
| Version control | Skills and server code are reviewed in Git, like any research code |
| Research data management and ethics | Approved-source gate: St. Jude sources stay disabled until licence/ownership review |
| Open and citable outputs | Every answer carries its source; the assistant says when it cannot answer |
| Human review of AI output | Skills tell you to verify; see Team 20's `docs/ai-guidance.md` |

## Hands-on

All commands run inside your `KIDS26-Team20` clone.

### Step 1 — Start the MCP server and connect it to Copilot (6 min)

**Path A — stdio, lightweight (recommended for the workshop).** The repo already
contains [`.vscode/mcp.json`](https://github.com/stjude-biohackathon/KIDS26-Team20/blob/main/.vscode/mcp.json),
which registers the server `stjude-learning-assistant`
(`uv run learning-assistant stdio`).

1. `code .` in the `KIDS26-Team20` folder.
2. Open `.vscode/mcp.json` and click **Start** above the server entry. You can also run
   **MCP: List Servers → stjude-learning-assistant → Start** from the Command Palette.
3. Open Copilot Chat, switch to **Agent** mode, click the **tools** icon, and check
   that the `stjude-learning-assistant` tools are listed.

To let the MyGPT tools reach the MyGPT you installed in module 1, add these entries to
the server's `env` block in `.vscode/mcp.json`:

```json
"MYGPT_BASE_URL": "http://localhost:8000",
"MYGPT_MODEL_ID": "llama3:latest"
```

**Path B — Docker, full Turing Way RAG stack (optional).** This runs the MCP server over
HTTP and gives it its own MyGPT backend with the full Turing Way corpus indexed. Follow
Team 20's [docs/DOCKER.md](https://github.com/stjude-biohackathon/KIDS26-Team20/blob/main/docs/DOCKER.md).
Your workshop MyGPT already uses port 8000, so choose free ports:

```bash
LEARNING_ASSISTANT_HOST_PORT=8100 MYGPT_BACKEND_HOST_PORT=8101 docker compose up --build
```

Then point Copilot at the HTTP endpoint with
[`examples/vscode-mcp-http.json`](examples/vscode-mcp-http.json) (copy it to
`.vscode/mcp.json`). Check the server at <http://127.0.0.1:8100/health>.

### Step 2 — Load the skills into Copilot (3 min)

The canonical skills live in `.agents/skills/`. Each `SKILL.md` declares
`compatibility: opencode, claude-code, github-copilot`.

1. In VS Code settings, turn on **Chat: Use Agent Skills** (`chat.useAgentSkills`).
2. Make sure Copilot searches `.agents/skills`. Merge
   [`examples/vscode-settings.json`](examples/vscode-settings.json) into
   `KIDS26-Team20/.vscode/settings.json`.
3. Reload the window. In Agent mode, type `/` or ask "which skills do you have?". You
   should see the Turing Way skills.

> VS Code's skill settings are still changing between releases. If the skills don't
> show up, check the [agent skills guide](https://code.visualstudio.com/docs/copilot/customization/agent-skills)
> for your version.

### Step 3 — Exercises (7 min)

1. **Pathfinder:** *"Help me choose my Turing Way path. I'm a wet-lab postdoc starting to
   analyse RNA-seq data in Python."* Expect a short, scored checklist with citations.
2. **Ground a coding task:** *"Using the Turing Way guidance, how should I capture the
   environment for the notebooks in this workshop? Cite your sources."* Check that
   Copilot calls `list_resources`/`get_resource`, and doesn't answer from memory.
3. **Review a repository:** open the `MyGPT-workshop` folder (add it to the workspace)
   and ask *"Use the turing-way-review skill to review this repository."* You get a
   rating out of six with prioritised fixes.
4. **Stretch — write a skill:** copy `.agents/skills/skill-template` to
   `.agents/skills/mygpt-eval-helper`, describe a workflow from module 3, and validate it:

   ```bash
   uv run python scripts/validate_skills.py
   ```

## Checkpoint

- [ ] The `stjude-learning-assistant` tools appear in Copilot Agent mode.
- [ ] One answer clearly cites a Turing Way page that came from an MCP tool call.
- [ ] At least one Turing Way skill was triggered (the chat shows it was loaded).
- [ ] You can explain the difference between an MCP **tool** and a **skill**.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `uv: command not found` when the server starts | Install uv; restart VS Code so its PATH is updated |
| Server starts but lists no resources | GitHub rate limit or no network. Set `LEARNING_ASSISTANT_OFFLINE=true` to use the bundled snapshot, or set `GITHUB_TOKEN` in your shell |
| Port 8000 already in use (Path B) | Use the `LEARNING_ASSISTANT_HOST_PORT`/`MYGPT_BACKEND_HOST_PORT` overrides shown above |
| Skills not offered | Check `chat.useAgentSkills` and the skills location setting; reload the window |
| `get_rag_status` fails | MyGPT isn't reachable or has no Turing Way dataset. Use Path B, or skip the RAG tools |
| Something else | `uv run python scripts/project.py doctor`, and Team 20's `docs/troubleshooting.md` |

## Going further

- Team 20's `START_HERE.md`, `docs/SETUP.md` (OpenCode path), and
  `docs/ai-guidance.md`.
- MyGPT's own MCP server, `MyGPT/MCP-server/`, exposes MyGPT datasets/documents plus
  PubMed and PDB lookups. Run it with `installation/<os>/prebuilt_images/run_mcp_server.sh`.
- The Turing Way: <https://the-turing-way.netlify.app>
