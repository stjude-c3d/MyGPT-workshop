"""Build the printable Module 5 handout (US Letter, 2 pages).

    pip install reportlab pillow
    python handouts/make_module5_handout.py      # -> handouts/module5_handout.pdf

Content mirrors 05-mcp-server-ai-coding/README.md and the KIDS26 Team 20 repository
(github.com/stjude-biohackathon/KIDS26-Team20). The example readiness scores (The Turing
Way 93/100, MyGPT 80/100) are from the St. Jude BioHackathon 2026 Team 20 presentation.
"""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Image, KeepTogether, PageBreak, Spacer, Table, TableStyle

from handout_kit import (BLUE, CONTENT_W, INK, MUTED, ORANGE, RULE, TEAL, TINT, Box, P, build, checklist,
                         grid, make_chrome, name_line, objectives_and_timeline, section,
                         side_by_side, trouble_table, write_lines)

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
OUT = HERE / "module5_handout.pdf"
chrome = make_chrome(5, "MCP server + skills for AI coding", 20, "05-mcp-server-ai-coding/README.md")

EX = '<font color="#5A6270" size="7">'  # reference values
NAVY = colors.HexColor("#2C4659")
RED = colors.HexColor("#C8323B")


# ----------------------------------------------------------------------------- page 1
def page1():
    story = [name_line(), Spacer(1, 6),
             objectives_and_timeline(
                 ["explain what an MCP tool and an agent skill each add",
                  "connect Team 20’s Turing Way MCP server to Copilot",
                  "get cited guidance and a 100-point repo readiness score"],
                 [("0–4", "Concepts", BLUE),
                  ("4–13", "Server + skills in Copilot", ORANGE),
                  ("13–20", "Exercises + check", TEAL)])]

    why = Table([[P("<b>Why this exists.</b> The Turing Way is the open handbook for reproducible, ethical and "
                    "collaborative data science; as a PDF it is about 1,000 pages. At the St. Jude BioHackathon "
                    "2026, Team 20 asked: <i>how can we apply these principles while we are coding?</i> Their "
                    "answer connects an AI coding agent, through an MCP server, to MyGPT preloaded with the "
                    "handbook, so every coding question can be checked against it and answered with cited best "
                    "practices.", "cell")]], colWidths=[CONTENT_W])
    why.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT), ("LINEBEFORE", (0, 0), (0, 0), 3, TEAL),
                             ("LEFTPADDING", (0, 0), (-1, -1), 8), ("TOPPADDING", (0, 0), (-1, -1), 5),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story += [Spacer(1, 6), why]

    setup = [
        ("Tools installed", "<b>uv</b>, VS Code, GitHub Copilot Chat with <b>Agent</b> mode; Git"),
        ("Clone Team 20’s repo", "<font face='Courier'>git clone https://github.com/stjude-biohackathon/"
                                 "KIDS26-Team20.git</font>"),
        ("Install + self-check", "<font face='Courier'>cd KIDS26-Team20 &amp;&amp; uv sync --extra dev --frozen"
                                 "</font> then <font face='Courier'>uv run python scripts/project.py doctor</font>"),
        ("Optional: full RAG", "Docker Desktop running (module 1) for Path B"),
    ]
    story += [section("Before you start", BLUE, "part of 0–4 min"),
              grid([["", P("Step", "head"), P("Do this", "head")]]
                   + [[Box(), P(a, "cellb"), P(b, "cell")] for a, b in setup],
                   [0.25 * inch, 1.45 * inch, CONTENT_W - 1.7 * inch], header_color=BLUE)]

    fig_w = 3.3 * inch
    fig = Image(str(ASSETS / "turing_way_mcp_workflow.png"), width=fig_w, height=fig_w * 526 / 606)
    read = [
        ("Harness", "GitHub Copilot in VS Code: you chat, the LLM plans, writes code, then debugs and verifies "
                    "in a sandbox."),
        ("Three things it can reach", "your <b>source code</b>, the <b>MCP server</b> and its tools, and the "
                                      "<b>skills</b>."),
        ("MCP server → MyGPT", "the tools query MyGPT, which holds the Turing Way handbook, so answers come "
                               "from retrieved, cited passages (RAG)."),
        ("Skills", "playbooks written from Turing Way best practices and protocols (the readiness score, "
                   "the review, the pathfinder)."),
        ("Result", "an answer that cites the Turing Way page it came from, or “I can’t answer from the "
                   "approved sources.”"),
    ]
    text_w = CONTENT_W - fig_w - 0.2 * inch
    legend = Table([[P(f'<font color="#E8762D"><b>{n}</b></font>', "cell"), P(f"<b>{t}:</b> {d}", "cell")]
                    for n, (t, d) in zip("12345", read)], colWidths=[0.18 * inch, text_w - 0.18 * inch])
    legend.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 1),
                                ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                ("LINEBELOW", (0, 0), (-1, -2), 0.4, RULE)]))
    fig_row = Table([[fig, legend]], colWidths=[fig_w + 0.2 * inch, text_w])
    fig_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [section("How the pieces fit", ORANGE),
              P("Workflow figure from Team 20’s St. Jude BioHackathon 2026 presentation.", "small"),
              Spacer(1, 2), fig_row]

    pieces = grid(
        [[P("Piece", "head"), P("What it is", "head"), P("Where in Team 20’s repo", "head")],
         [P("<b>MCP tool</b>", "cell"), P("A typed function the assistant can <b>call</b> to fetch data or act, "
                                          "over a standard protocol", "cell"),
          P("src/learning_assistant/server.py", "monosm")],
         [P("<b>Skill</b>", "cell"), P("A playbook the assistant <b>reads</b> when your request matches its "
                                       "description: steps, rules, failure behaviour", "cell"),
          P(".agents/skills/&lt;name&gt;/SKILL.md", "monosm")],
         [P("<b>Corpus</b>", "cell"), P("The only sources answers may cite", "cell"),
          P("corpus/sources.yaml → Turing Way @ bb3f7ab", "monosm")]],
        [0.85 * inch, 3.9 * inch, CONTENT_W - 4.75 * inch], header_color=ORANGE, zebra=True)
    story += [Spacer(1, 2), pieces]

    tw = grid(
        [[P("Turing Way principle", "head"), P("How this setup applies it", "head")],
         [P("Reproducible environments", "cellb"), P("Pinned corpus commit, uv.lock, Docker Compose, offline tests",
                                                      "cell")],
         [P("Version control", "cellb"), P("Skills and server code are reviewed in Git like any research code",
                                           "cell")],
         [P("Data management + ethics", "cellb"), P("Approved-source gate: St. Jude sources stay off until "
                                                     "licence and ownership review", "cell")],
         [P("Open, citable outputs", "cellb"), P("Every answer carries its source, or says it cannot answer",
                                                 "cell")],
         [P("Human review of AI output", "cellb"), P("Skills tell you to verify; a score is a readiness snapshot, "
                                                     "not an official certification", "cell")]],
        [1.75 * inch, CONTENT_W - 1.75 * inch], header_color=TEAL, zebra=True)
    story += [section("Turing Way concepts you will see", TEAL), tw]
    return story


# ----------------------------------------------------------------------------- page 2
def page2():
    story = []

    path_a = Table([[P("<b>Path A — stdio (recommended).</b> <font face='Courier'>code .</font> in "
                       "<font face='Courier'>KIDS26-Team20</font> → open <font face='Courier'>.vscode/mcp.json</font> "
                       "→ click <b>Start</b> above <font face='Courier'>stjude-learning-assistant</font> → Copilot Chat "
                       "→ <b>Agent</b> → tools icon. To reach your module 1 MyGPT, add "
                       "<font face='Courier'>\"MYGPT_BASE_URL\": \"http://localhost:8000\"</font> to the server’s "
                       "<font face='Courier'>env</font> (option C: <font face='Courier'>\"MYGPT_MODEL_ID\": \"gpt-6-luna\"</font>).",
                       "cell")],
                    [P("<b>Path B — Docker, full Turing Way RAG (optional).</b> "
                       "<font face='Courier'>LEARNING_ASSISTANT_HOST_PORT=8100 MYGPT_BACKEND_HOST_PORT=8101 docker "
                       "compose up --build</font>, then copy <font face='Courier'>examples/vscode-mcp-http.json</font> "
                       "to <font face='Courier'>.vscode/mcp.json</font>. Health: "
                       "<font face='Courier'>http://127.0.0.1:8100/health</font>. Needs Ollama’s nomic-embed-text "
                       "(option B: add <font face='Courier'>MYGPT_OLLAMA_URL=&lt;server URL&gt;</font>; not for "
                       "option C).", "cell")]],
                   colWidths=[CONTENT_W])
    path_a.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), TINT),
                                ("LINEBELOW", (0, 0), (-1, 0), 0.8, colors.white),
                                ("LEFTPADDING", (0, 0), (-1, -1), 6)]))
    tools = ["list_resources", "get_resource", "list_mygpt_datasets", "list_mygpt_documents",
             "query_mygpt_context", "get_rag_status", "get_turing_way_review_evidence",
             "get_turing_way_evidence_packets", "validate_turing_way_review", "render_validated_turing_way_review"]
    trow = [[Box(), P(tools[i], "monosm"), Box(), P(tools[i + 5], "monosm")] for i in range(5)]
    tick = Table(trow, colWidths=[0.2 * inch, 2.35 * inch, 0.2 * inch, CONTENT_W - 2.75 * inch])
    tick.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    story += [section("Step 1 — Start the MCP server and connect Copilot", ORANGE, "4–10 min"), path_a,
              Spacer(1, 3), P("<b>Tick the tools you see</b> in Copilot’s tools list (10 in total):", "small"), tick]

    skills = [("turing-way-pathfinder", "pick a pathway + cited checklist"),
              ("turing-way-guidance", "cited learning path"),
              ("turing-way-review", "maturity rating + fixes"),
              ("turing-way-certified", "10-criterion score out of 100"),
              ("turing-healthcheck", "scored repo healthcheck"),
              ("mygpt-library", "find MyGPT datasets / docs")]
    srow = [[Box(), P(f"<font face='Courier'>{skills[i][0]}</font>  <font color='#5A6270'>{skills[i][1]}</font>",
                      "cell"),
             Box(), P(f"<font face='Courier'>{skills[i + 3][0]}</font>  <font color='#5A6270'>{skills[i + 3][1]}"
                      "</font>", "cell")] for i in range(3)]
    stab = Table(srow, colWidths=[0.2 * inch, CONTENT_W / 2 - 0.2 * inch, 0.2 * inch, CONTENT_W / 2 - 0.2 * inch])
    stab.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 2),
                              ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)]))
    story += [section("Step 2 — Load the skills into Copilot", ORANGE, "10–13 min"),
              P("Settings: turn on <font face='Courier'>chat.useAgentSkills</font> and add "
                "<font face='Courier'>\"chat.agentSkillsLocations\": {\".agents/skills\": true}</font> "
                "(<font face='Courier'>examples/vscode-settings.json</font>). Reload the window, then type "
                "<b>/</b> in Agent mode. <b>Tick the skills you see:</b>", "small"), stab]

    ex = grid(
        [[P("Step 3 — prompt in Agent mode", "head"), P("Skill / tools used", "head"),
          P("Turing Way page it cited", "head")],
         [P("<b>Pathfinder:</b> <i>“Help me choose my Turing Way path. I’m a wet-lab postdoc starting to analyse "
            "RNA-seq data in Python.”</i>", "cell"), "", ""],
         [P("<b>Ground a coding task:</b> <i>“Using the Turing Way guidance, how should I capture the environment "
            "for this workshop’s notebooks? Cite your sources.”</i>", "cell"), "", ""]],
        [3.5 * inch, 1.6 * inch, CONTENT_W - 5.1 * inch], header_color=TEAL, row_h=[None, 30, 30])
    story += [section("Step 3 — Exercises", TEAL, "13–20 min"), ex,
              P("Check the tool calls in the chat: the answer should come from "
                "<font face='Courier'>get_resource</font> / <font face='Courier'>query_mygpt_context</font>, "
                "not from the model’s memory.", "small")]

    crit = ["Project purpose and scope", "Version control and provenance", "Open collaboration",
            "Reproducible environments", "Data and workflow provenance", "Testing and validation",
            "Automation and CI", "Documentation and usability", "Licensing, attribution, reuse",
            "Ethics, accessibility, sustainability"]
    rows = [[P("Criterion", "head"), P("/10", "head"), P("Criterion", "head"), P("/10", "head")]]
    for i in range(5):
        rows.append([P(f"{i + 1}. {crit[i]}", "cell"), "", P(f"{i + 6}. {crit[i + 5]}", "cell"), ""])
    rows.append([P("<b>Total  (out of 100)</b>", "cell"), "",
                 P(f"{EX}Reference (BioHackathon 2026): The Turing Way <b>93</b> · MyGPT source code "
                   "<b>80</b></font>", "cell"), ""])
    card = grid(rows, [CONTENT_W / 2 - 0.6 * inch, 0.6 * inch] * 2, header_color=NAVY,
                row_h=[None] + [17] * 6)
    card.setStyle(TableStyle([("SPAN", (2, 6), (3, 6)), ("BACKGROUND", (0, 6), (-1, 6), TINT)]))
    story += [KeepTogether([
        section("Step 4 — Readiness score out of 100", NAVY, "stretch"),
        P("Add the <font face='Courier'>MyGPT-workshop</font> folder to the workspace and ask "
          "<i>“Is this repository Turing Way certified, and what does it still need?”</i> The "
          "<font face='Courier'>turing-way-certified</font> skill scores ten criteria 0–10 (total out of 100) and "
          "writes <font face='Courier'>TURING_WAY_CERTIFICATION.md</font> + PDF. It is a readiness snapshot, "
          "<b>not</b> an official certification. Copy its scores:", "small"),
        Spacer(1, 2), card])]

    cp = checklist([
        "<font face='Courier'>stjude-learning-assistant</font> tools appear in Copilot Agent mode",
        "One answer cites a Turing Way page that came from an MCP tool call",
        "At least one Turing Way skill was triggered (the chat shows it was loaded)",
        "You can explain the difference between an MCP <b>tool</b> and a <b>skill</b>",
    ])
    tr = trouble_table([
        ("uv not found", "Install uv, then restart VS Code so its PATH updates"),
        ("No resources listed", "GitHub rate limit / no network: LEARNING_ASSISTANT_OFFLINE=true, or set "
                                "GITHUB_TOKEN"),
        ("Skills not offered", "Check chat.useAgentSkills + skills location; reload the window"),
        ("get_rag_status fails", "MyGPT unreachable or no Turing Way dataset: use Path B or skip RAG tools"),
        ("Anything else", "uv run python scripts/project.py doctor"),
    ])
    story += [Spacer(1, 6), side_by_side(cp, tr, section("Checkpoint", INK), section("Stuck?", ORANGE))]
    return story


def main():
    build(OUT, page1() + [PageBreak()] + page2(), chrome, "MyGPT Workshop — Module 5 handout")


if __name__ == "__main__":
    main()
