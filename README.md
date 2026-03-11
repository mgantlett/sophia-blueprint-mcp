# Sophia Architecture Blueprint — MCP Server

> 9-chapter cognitive AI agent architecture blueprint. Query battle-tested patterns directly from your coding agent via MCP.

[![Smithery](https://smithery.ai/badge/sophia-blueprint/architecture)](https://smithery.ai/servers/sophia-blueprint/architecture)
[![Live](https://img.shields.io/badge/endpoint-live-brightgreen)](https://sophialabs.gantlett.io/blueprint/mcp)

## What Is This?

An MCP server that serves a **9-chapter architecture blueprint** for building cognitive AI agents. These patterns are extracted from a production system (Sophia) that has been running 24/7 for 6+ months — not theory.

**Topics covered**: Bio-digital architecture, identity evolution, multi-tier routing, expert swarm orchestration, memory systems, autonomic loops, nervous system observability, model strategy, and productionizing.

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

## 4 Tools Available

| Tool | Description |
|------|-------------|
| `sophia_blueprint_list()` | List all 9 chapters with titles and descriptions |
| `sophia_blueprint_chapter("3")` | Get full content of any chapter by number or keyword |
| `sophia_blueprint_search("heartbeat")` | Semantic search across all chapters |
| `sophia_blueprint_pattern("fleet bridge")` | Look up specific architectural patterns |

## Chapters

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

**Free chapters** (1 & 3) are available immediately — no auth required.  
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

- 🌐 **Landing Page**: [sophialabs.gantlett.io](https://sophialabs.gantlett.io)
- 📘 **Full PDF**: [sophialabs.gumroad.com](https://sophialabs.gumroad.com)
- 🐦 **Updates**: [@markgantlett](https://x.com/markgantlett)

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Sophia Labs](https://gantlett.io) — powered by a cognitive AI agent that wrote its own architecture docs.*
