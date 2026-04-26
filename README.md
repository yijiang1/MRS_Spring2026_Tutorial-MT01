# MRS Spring 2026 — Tutorial MT01

**Deploying Agentic AI in Materials Characterization Workflows**
Yi's session: *Adapting Foundation Models for Domain Science* (April 26, 2026 · Honolulu)

Repo: <https://github.com/yijiang1/MRS_Spring2026_Tutorial-MT01>

This folder contains hands-on notebooks for the audience to work through during
and after the session. Each notebook stands alone — pick whichever ones map to
what you want to build — but they are also designed to read in order, with
later notebooks reusing patterns from earlier ones.

## Quick start

```bash
git clone https://github.com/yijiang1/MRS_Spring2026_Tutorial-MT01.git
cd MRS_Spring2026_Tutorial-MT01
# then either open a notebook in Jupyter/Colab, or jump to claude_code_skills/
```

---

## Suggested teaching order

| # | Notebook | What you'll learn | Time |
|---|----------|-------------------|------|
| 0 | [`00_llm_api_setup.ipynb`](00_llm_api_setup.ipynb) | Talking to OpenAI, Anthropic, Google APIs from Python | 10 min |
| 1 | [`01_prompt_engineering.ipynb`](01_prompt_engineering.ipynb) | Zero-shot, few-shot, chain-of-thought, system prompts on a materials extraction task | 15 min |
| 2 | [`02_structured_outputs.ipynb`](02_structured_outputs.ipynb) | Forced-tool JSON, Pydantic validation + retry, confidence + evidence extraction | 15 min |
| 3 | [`03_rag_literature.ipynb`](03_rag_literature.ipynb) | RAG from scratch over a small materials abstract corpus; ungrounded vs grounded contrast | 15 min |
| 4 | [`04_agent_microscopy.ipynb`](04_agent_microscopy.ipynb) | A from-scratch agent loop driving an image-processing pipeline (threshold → segment → measure) on a synthetic microscopy image | 20 min |
| 5 | [`05_mcp_server.ipynb`](05_mcp_server.ipynb) | Build an MCP server, connect via stdio, drive it from a Claude agent | 15 min |
| 6 | [`06_multi_agent_eval_caching.ipynb`](06_multi_agent_eval_caching.ipynb) | Planner + specialist sub-agents, eval harness with traces, prompt caching cost demo | 20 min |
| 7 | [`07_langgraph_agent.ipynb`](07_langgraph_agent.ipynb) | The same agent rebuilt in LangGraph: state, conditional edges, persistence, streaming | 20 min |

**Total runtime end-to-end:** ~2 hours of audience work.

For a 1-hour tutorial slot, a sensible cut is **0 → 1 → 2 → 4 → 5** (foundational
+ structured outputs + agent + MCP). The multi-agent and LangGraph notebooks
(#6, #7) are best treated as take-homes.

---

## Bonus segment — Claude Code + Skills

Materials in [`claude_code_skills/`](claude_code_skills/) cover the
*interactive CLI* angle that doesn't fit in notebooks: how Claude Code reads
your filesystem and runs shell commands, and how Skills package
group-specific capabilities as plain markdown files. Includes a one-page
cheat sheet, a "starter pack" sandbox folder, two ready-to-copy example
skills, a skill-authoring walkthrough, and a rehearsable 8-10 min live demo
script. Designed to slot in alongside the notebooks — **not** to replace
them.

---

## Setup

### Option A — Google Colab (recommended for the audience)
Each notebook has a commented `!pip install ...` line at the top. Uncomment and
run the first cell. Paste your API key when prompted.

### Option B — Local Jupyter
```bash
python -m venv .venv && source .venv/bin/activate
pip install jupyter anthropic openai google-genai pydantic \
            sentence-transformers numpy scipy mcp \
            langgraph langchain-anthropic
jupyter lab
```

### API keys
- **Anthropic** — primary provider used by all notebooks: <https://console.anthropic.com>
- **OpenAI / Google** — only needed for notebook 0: <https://platform.openai.com>, <https://aistudio.google.com>

Notebooks read keys from environment variables (`ANTHROPIC_API_KEY`, etc.) and
fall back to an interactive prompt.

---

## What each notebook teaches

**0. LLM API Setup** — *the prerequisite.* Side-by-side use of the three major
LLM APIs. Skip if your audience has used any LLM API before.

**1. Prompt Engineering** — Zero-shot vs few-shot vs chain-of-thought, all on
the same materials-science extraction task so the deltas are visible. Good
for participants who have only used LLMs through chat UIs.

**2. Structured Outputs** — How to actually get *parseable* output from an LLM.
Forced tool use, Pydantic validation with retry, and adding `confidence` +
`evidence_quote` for human review. The seam between *language* and *code*.

**3. RAG over Literature** — The full retrieve-then-generate loop in ~200 lines:
chunking, sentence-transformers embeddings, cosine retrieval, citation-aware
generation. Demonstrates the "model says no" failure mode for off-corpus
questions.

**4. Agent for Microscopy** — A from-scratch agent loop. Synthetic microscopy
image, four image-processing tools (`inspect_image`, `threshold_image`,
`segment_particles`, `measure_particles`), and the message-passing loop the
model uses to chain them. *The canonical "build an agent in a notebook"
exercise.*

**5. MCP Server** — Build a tiny FastMCP server exposing peak-finder and
crystal-lookup tools, then have a Claude agent drive it. Same pattern that
powers Claude Desktop, Claude Code, and Cursor's tool integrations. *The
"USB-C for agents" notebook.*

**6. Multi-Agent + Eval + Caching** — Three production patterns in one:
   - Sonnet planner dispatching to two Haiku specialists.
   - A tiny eval harness with trajectory inspection.
   - Anthropic prompt caching with measured token-count comparison.

**7. LangGraph** — The same agent from #4, rebuilt as a `StateGraph` with
`ToolNode`, `tools_condition`, and `MemorySaver`. Adds free conversation
persistence keyed by `thread_id`, plus a custom safety-check branch.

---

## Re-generating the notebooks

Each notebook has a paired `generate_notebook_<name>.py` script. To edit
content, modify the script and re-run it — don't hand-edit the `.ipynb` JSON.

```bash
python generate_notebook_structured_outputs.py
# -> 02_structured_outputs.ipynb
```

To pre-bake outputs (recommended before sharing with the audience so they can
read along even without a key):

```bash
jupyter nbconvert --to notebook --execute --inplace 0*.ipynb
```

---

## Notes for instructors

- **Latency:** notebook 6 (multi-agent) is the slowest — budget ~30 s per query
  because of the planner → specialist → planner round trip.
- **Common gotcha:** the MCP notebook spawns a subprocess. In Jupyter (not
  Colab) you may need `import nest_asyncio; nest_asyncio.apply()` if the
  kernel complains about a running event loop.
- **Models:** all notebooks pin model IDs at the top. When a new Sonnet/Haiku
  ships, search-and-replace `claude-sonnet-4-6` / `claude-haiku-4-5-20251001`
  in the generator scripts and re-run.
