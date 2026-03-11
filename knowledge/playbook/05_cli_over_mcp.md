# Chapter 5: CLI-over-MCP — Why Persistent Connections Break

> The hard-won lesson: long-lived tool connections fail under load. Request/response wins.

---

## The Problem: MCP Drops at the Worst Time

You're building an agent that needs to remember things between sessions — intentions, engrams, learned lessons. The standard approach is MCP (Model Context Protocol): connect to a server, call tools, keep state.

It works great in demos. Then in production:

- The WebSocket/stdio connection drops during a long task
- The agent calls a tool, gets a 500 because the server restarted
- You add reconnection logic, but the session state is gone
- The agent retries, creates duplicate entries, corrupts data

**MCP's persistent connection model is excellent for read-only knowledge delivery** (like this playbook). It's fragile for **stateful mutations** — creating tasks, updating status, writing memories.

---

## The Pattern: CLI Wrappers

Instead of calling MCP tools for state mutations, create a thin CLI that calls your backend's REST API directly:

```bash
# Instead of MCP tool: create_task("fix auth bug")
bin/myapp tasks create "fix auth bug" --priority high

# Instead of MCP tool: update_task(id, status="done")  
bin/myapp tasks update 42 --status done

# Instead of MCP tool: search_memory("auth patterns")
bin/myapp memory search "auth patterns" --limit 5
```

### Why This Works

| | MCP Tool Call | CLI Call |
|---|---|---|
| **Connection** | Persistent (WebSocket/stdio) | Request/response (one-shot) |
| **Failure mode** | Connection drops → all tools fail | One call fails → retry that call |
| **State** | Tied to session | Stateless — every call is self-contained |
| **Speed** | Fast (already connected) | Slightly slower (HTTP round-trip) |
| **Reliability** | Degrades over time | Consistent |

The speed difference is negligible (50ms for a local HTTP call). The reliability difference is massive.

---

## Implementation

### Step 1: REST API in Your Backend

```javascript
// Express example
app.post('/api/tasks', (req, res) => {
  const task = createTask(req.body);
  res.json(task);
});

app.put('/api/tasks/:id', (req, res) => {
  const task = updateTask(req.params.id, req.body);
  res.json(task);
});
```

### Step 2: CLI Wrapper Script

```bash
#!/usr/bin/env node
// bin/myapp — a thin CLI that calls the REST API

const API = 'http://localhost:3000/api';

const [,, resource, action, ...args] = process.argv;

switch (`${resource} ${action}`) {
  case 'tasks create':
    fetch(`${API}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: args[0], priority: args[1] })
    }).then(r => r.json()).then(console.log);
    break;
    
  case 'tasks list':
    fetch(`${API}/tasks`)
      .then(r => r.json())
      .then(tasks => console.table(tasks));
    break;
}
```

### Step 3: Reference in Your Agent Rules

```markdown
## Memory Management

Use `bin/myapp` CLI for all state operations:
- `bin/myapp tasks list` — show the board
- `bin/myapp tasks create "title"` — create a task  
- `bin/myapp tasks update <id> --status done` — close a task
- `bin/myapp memory search "query"` — search past context

🚫 Do NOT use MCP tools for mutations — they fail when the 
connection drops. The CLI is direct and reliable.
```

---

## When MCP IS the Right Choice

MCP excels at **read-only knowledge delivery**:

- Serving documentation and architecture patterns
- Semantic search across knowledge bases
- Listing available tools and capabilities
- Streaming real-time events (SSE)

The rule of thumb: **If it reads, use MCP. If it writes, use CLI.**

---

## The Hybrid Approach

Most production systems use both:

```
┌─────────────────────────────────────────────┐
│              Your Agent                      │
│                                             │
│  ┌──────────────┐    ┌──────────────────┐   │
│  │   MCP Tools   │    │   CLI Commands   │   │
│  │  (read-only)  │    │  (mutations)     │   │
│  └──────┬───────┘    └──────┬───────────┘   │
│         │                    │               │
│    WebSocket/SSE       HTTP Request          │
│    (persistent)        (one-shot)            │
│         │                    │               │
│         ▼                    ▼               │
│  ┌──────────────────────────────────────┐   │
│  │           Backend API                 │   │
│  │   Knowledge  │  Tasks  │  Memory     │   │
│  └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

Read operations flow through MCP for speed and streaming capability. Write operations go through CLI for reliability. Your agent rules file documents which to use for what.

---

*Next: [Chapter 6 — Trust the Agent →](#)*
