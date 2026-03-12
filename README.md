# Sophia Labs — MCP Server

> Two MCP servers for building cognitive AI agents: a 9-chapter architecture blueprint + a 7-chapter coding agent playbook.

[![Smithery](https://smithery.ai/badge/sophia-blueprint/architecture)](https://smithery.ai/servers/sophia-blueprint/architecture)
[![Live](https://img.shields.io/badge/endpoint-live-brightgreen)](https://sophialabs.gantlett.io/blueprint/mcp)
[![Website](https://img.shields.io/badge/website-sophialabs.gantlett.io-blue)](https://sophialabs.gantlett.io)

## What Is This?

Two MCP endpoints serving production-tested patterns for building cognitive AI agents, extracted from a system running 24/7 for 6+ months:

| Product | Endpoint | Tools | Topics |
|---------|----------|-------|--------|
| **Architecture Blueprint** | `/blueprint/mcp` | 4 | Bio-digital architecture, routing, memory, autonomics, identity |
| **Coding Agent Playbook** | `/devops/mcp` | 3 | Agent coordination, rules files, workflows, GitOps, CLI patterns |

Each product has its own Gumroad license key. Buy one or both.

## Connect in 30 Seconds

### Architecture Blueprint (Cursor / VS Code)

Add to `.cursor/mcp.json` or `.vscode/mcp.json`:

```json
{
  "mcpServers": {
    "sophia-blueprint": {
      "url": "https://sophialabs.gantlett.io/blueprint/mcp",
      "headers": { "Authorization": "Bearer YOUR_BLUEPRINT_KEY" }
    }
  }
}
```

### Coding Agent Playbook (Cursor / VS Code)

```json
{
  "mcpServers": {
    "sophia-playbook": {
      "url": "https://sophialabs.gantlett.io/devops/mcp",
      "headers": { "Authorization": "Bearer YOUR_DEVOPS_KEY" }
    }
  }
}
```

### Claude Code

```bash
# Blueprint
claude mcp add sophia-blueprint --transport http https://sophialabs.gantlett.io/blueprint/mcp

# Playbook
claude mcp add sophia-playbook --transport http https://sophialabs.gantlett.io/devops/mcp
```

> **Free chapters** work without a key. License keys unlock the full content.

## Tools

### Architecture Blueprint — `/blueprint/mcp`

| Tool | Description |
|------|-------------|
| `sophia_blueprint_list()` | List all 9 chapters with titles and descriptions |
| `sophia_blueprint_chapter("3")` | Get full content of any chapter by number or keyword |
| `sophia_blueprint_search("heartbeat")` | Semantic search across all chapters |
| `sophia_blueprint_pattern("fleet bridge")` | Look up specific architectural patterns |

### Coding Agent Playbook — `/devops/mcp`

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

**Get license keys**: [sophialabs.gumroad.com](https://sophialabs.gumroad.com)

## Self-Hosting

```bash
git clone https://github.com/mgantlett/sophia-blueprint-mcp.git
cd sophia-blueprint-mcp
pip install -r requirements.txt
python server.py
```

## Links

- **Landing Page**: [sophialabs.gantlett.io](https://sophialabs.gantlett.io)
- **Full PDFs + License Keys**: [sophialabs.gumroad.com](https://sophialabs.gumroad.com)
- **The Project**: [Sophia Backlog](https://github.com/mgantlett/sophia-backlog) — the production system these patterns are extracted from
- **Updates**: [@markgantlett](https://x.com/markgantlett)

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [Sophia Labs](https://sophialabs.gantlett.io) — cognitive AI architecture, distilled.*
