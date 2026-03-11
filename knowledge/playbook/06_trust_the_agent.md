# Chapter 6: Trust the Agent — Senior Habits Over Guardrails

> Why lock files, pre-commit hooks, and heavy guardrails are 2024 thinking.

---

## The 1,100-Line Lesson

We started building our multi-agent system the "sensible" way:

- **Git worktrees** — each agent gets its own checkout (200+ lines of orchestration scripts)
- **File locking** — agents acquire locks before editing (150 lines + a lock server)
- **Docker isolation** — each agent runs in its own container (300+ lines of Docker configs)
- **Pre-commit hooks** — lint, test, format on every commit (100+ lines of hook scripts)
- **Branch-per-agent** — each agent works on its own branch (constant merge conflicts)

Total: **1,100+ lines of infrastructure** to coordinate AI agents.

Then we replaced all of it with **8 markdown files** that any agent can read and follow:

```
.agent/
├── rules/
│   └── RULES.md              # ~175 lines
└── workflows/
    ├── context-handshake.md   # ~70 lines
    ├── push.md                # ~75 lines
    ├── ship.md                # ~85 lines
    ├── claim-task.md          # ~40 lines
    ├── swarm-cycle.md         # ~30 lines
    ├── verify-system.md       # ~40 lines
    └── maintain-codebase.md   # ~50 lines
```

**Total: ~565 lines of markdown.** Half the lines, zero infrastructure, works with any agent on any IDE.

---

## The Philosophy Shift

### 2024 Thinking: Constrain the Agent

```
Problem: Agent does wrong thing
Solution: Add a gate that prevents wrong thing
Result: More gates → more complexity → agent fights gates → more gates
```

This is the "toddler-proofing" approach. You assume the agent will do harmful things, so you build mechanical barriers:

- Pre-commit hooks that reject bad commits
- File locks that prevent concurrent access
- Branch isolation that prevents shared-workspace conflicts
- Docker containers that prevent filesystem contamination

Each gate is reasonable in isolation. Together, they create a system where the agent spends more time fighting infrastructure than writing code.

### 2025+ Thinking: Teach the Agent

```
Problem: Agent does wrong thing
Solution: Add a rule explaining why it's wrong
Result: Agent follows instructions → fewer mistakes → trust compounds
```

This is the "experienced developer" approach. You assume the agent can follow instructions (it can — that's literally what LLMs do), so you give it good instructions:

- A rules file that explains the standards
- Workflows that encode multi-step operations
- Negative rules that explain what NOT to do and why
- Quick reference tables for common situations

---

## The Singleton Rule

In a multi-agent system, each service or interface should have exactly one owner:

```
┌─────────────────────────────────────────┐
│              Service Ownership           │
│                                         │
│  Session 0 (Prime):  API routes, auth   │
│  Session 1:          Frontend, UI       │
│  Session 2:          Background jobs    │
│                                         │
│  Rule: Only one session edits a service │
│  at a time. This is communicated, not   │
│  enforced mechanically.                 │
└─────────────────────────────────────────┘
```

The ownership is declared in the `/claim-task` step, not enforced by a lock. If Session 2 sees that Session 0 is editing the API routes, it picks different work. No lock server required.

---

## Zone Ownership

For larger projects, define ownership zones:

```markdown
## File Ownership Zones

### Shared (any session can edit)
- `docs/` — documentation
- `tests/` — test files
- `.agent/` — agent configuration

### Owned (claim before editing)
- `src/api/` — API routes  
- `src/services/` — business logic
- `src/models/` — database models
- `src/components/` — UI components

### Protected (human-only)
- `.env` — secrets (never committed)
- `config/production.json` — production config
- `package.json` — dependencies (coordinate changes)
```

The agent reads these zones and knows:
- **Shared**: edit freely, no conflict risk
- **Owned**: check if another session is working here first
- **Protected**: don't touch without explicit human approval

---

## Trust Calibration

Not all operations deserve the same trust level:

| Operation | Trust Level | Agent Behavior |
|-----------|------------|----------------|
| Read files | Full auto | No approval needed |
| Run tests | Full auto | Always run freely |
| Edit code | High trust | Auto-run if in owned zone |
| Stage files | Medium trust | Always use explicit paths |
| Commit | Medium trust | Require review of staged files |
| Push to develop | Medium trust | Auto-run after verification passes |
| Push to main | Low trust | Always require human approval |
| Delete files | Low trust | Always require human approval |
| Modify secrets | Zero trust | Human-only |

The `// turbo` annotation in workflows maps directly to this trust model. Steps with `// turbo` are auto-run. Steps without it pause for approval.

---

## The Compounding Effect

Instruction-based coordination gets better over time:

1. **Week 1**: Agent makes mistakes. You add rules to prevent them.
2. **Week 4**: Agent follows rules consistently. You add workflow optimizations.
3. **Week 8**: Agent anticipates problems. The rules file contains institutional knowledge.
4. **Week 12**: New team members get the same quality from day one — the knowledge is in the files, not in your head.

Infrastructure-based constraints don't compound. A file lock is the same file lock in week 1 and week 52. But a rules file that captures 6 months of lessons learned makes every new agent session start with that accumulated wisdom.

---

## Getting Started

1. **Drop the `.agent/` directory into your project** (use the starter template from Chapter 2)
2. **Add the 3 essential workflows** (`/push`, `/ship`, `/context-handshake`)
3. **Remove one guardrail** — pick your most annoying pre-commit hook and replace it with a rule
4. **Iterate** — every time the agent makes a new mistake, add a rule instead of a gate

The goal isn't to remove all safety — it's to move safety from mechanical barriers to cultural norms. Just like experienced dev teams do.

---

## Summary: The Playbook

| Chapter | Key Takeaway |
|---------|-------------|
| 1. Parallel Agent Coordination | Stage only YOUR files, never `git add .` |
| 2. Agent Rules File | Persistent instructions beat repeated prompting |
| 3. Workflow Templates | Multi-step operations as agent-readable markdown |
| 4. develop/master GitOps | Two branches, conventional commits, hygiene |
| 5. CLI-over-MCP | Reads via MCP, writes via CLI |
| 6. Trust the Agent | Instructions scale; guardrails don't |

---

*The Coding Agent Playbook — by Sophia Labs*
*sophialabs.gantlett.io/playbook*
