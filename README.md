# Sophia Labs — MCP Server

> 9-chapter architecture blueprint + 7-chapter coding agent playbook. Query battle-tested AI agent patterns directly from your coding agent via MCP.

[![Smithery](https://smithery.ai/badge/sophia-blueprint/architecture)](https://smithery.ai/servers/sophia-blueprint/architecture)
[![Live](https://img.shields.io/badge/endpoint-live-brightgreen)](https://sophialabs.gantlett.io/blueprint/mcp)
[![Website](https://img.shields.io/badge/website-sophialabs.gantlett.io-blue)](https://sophialabs.gantlett.io)

## What Is This?

An MCP server that serves two products for building cognitive AI agents:

- **Architecture Blueprint** (9 chapters) — Bio-digital architecture, identity evolution, multi-tier routing, expert swarm orchestration, memory systems, autonomic loops, nervous system observability, model strategy, and productionizing.
- **Coding Agent Playbook** (7 chapters) — Parallel agent coordination, agent rules files, workflow templates, GitOps for AI teams, CLI-over-MCP patterns, and trust-based autonomy.

These patterns are extracted from a production system (Sophia) that has been running 24/7 for 6+ months — not theory.

## Connect in 30 Seconds

### Cursor / VS Code

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "sophia-blueprint": {
      "url": "https://sophialabs.gantlett.io/blueprint/mcp"
    }
  }
}
```

### Claude Code

```bash
claude mcp add sophia-blueprint --transport http https://sophialabs.gantlett.io/blueprint/mcp
```

### Windsurf / Generic MCP Client

```bash
npx -y @anthropic-ai/mcp-remote https://sophia-knowledge-921954819222.us-central1.run.app/sse
```

## 8 Tools Available

### Architecture Blueprint Tools

| Tool | Description |
|------|-------------|
| `sophia_blueprint_list()` | List all 9 chapters with titles and descriptions |
| `sophia_blueprint_chapter("3")` | Get full content of any chapter by number or keyword |
| `sophia_blueprint_search("heartbeat")` | Semantic search across all chapters |
| `sophia_blueprint_pattern("fleet bridge")` | Look up specific architectural patterns |

### Coding Agent Playbook Tools

| Tool | Description |
|------|-------------|
| `sophia_playbook_list()` | List all 7 playbook chapters with titles |
| `sophia_playbook_chapter("2")` | Get full content of any playbook chapter |
| `sophia_playbook_search("workflow")` | Search across playbook chapters |

## Chapters

### Architecture Blueprint

| # | Title | Access |
|---|-------|--------|
| 01 | The Bio-Digital Metaphor | **FREE** |
| 02 | Identity & Personality | License |
| 03 | Multi-Tier Routing | **FREE** |
| 04 | Expert Swarm Architecture | License |
| 05 | Memory Architecture | License |
| 06 | Autonomic Systems | License |
| 07 | Nervous System & Observability | License |
| 08 | Model Strategy | License |
| 09 | Productionizing | License |

### Coding Agent Playbook

| # | Title | Access |
|---|-------|--------|
| 00 | From 2020 to 2026 | **FREE** |
| 01 | Parallel Agent Coordination | License |
| 02 | The Agent Rules File | **FREE** |
| 03 | Workflow Templates | License |
| 04 | GitOps for AI Teams | License |
| 05 | CLI Over MCP | License |
| 06 | Trust the Agent | License |

**Free chapters** are available immediately — no auth required.
**Full access**: Get a license key at [sophialabs.gumroad.com](https://sophialabs.gumroad.com).

## Self-Hosting

```bash
# Clone and run locally
git clone https://github.com/mgantlett/sophia-blueprint-mcp.git
cd sophia-blueprint-mcp
pip install -r requirements.txt
python server.py
```

Or with Docker:

```bash
docker build -t sophia-blueprint .
docker run -p 8080:8080 sophia-blueprint
```

## Tech Stack

- **FastMCP** (Python) — Streamable HTTP transport
- **Google Cloud Run** — Production hosting
- **Sentence Transformers** — Semantic search embeddings
- **Gumroad** — License key validation

## Links

- **Landing Page**: [sophialabs.gantlett.io](https://sophialabs.gantlett.io)
- **Full PDFs**: [sophialabs.gumroad.com](https://sophialabs.gumroad.com)
- **The Project**: [Sophia Backlog](https://github.com/mgantlett/sophia-backlog) — the production system these patterns are extracted from
- **Updates**: [@markgantlett](https://x.com/markgantlett)

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Sophia Labs](https://sophialabs.gantlett.io) — cognitive AI architecture, distilled.*
