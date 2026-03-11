# Chapter 2: The Agent Rules File

> Give your coding agent persistent identity, standards, and context — across every conversation.

---

## The Problem: Groundhog Day

Every time you start a new chat session with your coding agent, it forgets everything:

- Your project structure
- Your coding standards
- Your git workflow
- The mistakes it made last time

You end up repeating the same instructions: *"Don't use `git add .`"*, *"Always run tests first"*, *"Use conventional commits"*.

**The fix: a rules file.** A persistent markdown document that your agent reads on every boot.

---

## The `.agent/` Directory Convention

Most modern IDEs support agent instruction files:

| IDE / Agent | Rules File Location | Format |
|-------------|-------------------|--------|
| **Cursor** | `.cursor/rules/` or `.cursorrules` | Markdown |
| **Windsurf** | `.windsurfrules` | Markdown |
| **Antigravity** | `.agent/rules/GEMINI.md` | Markdown + YAML frontmatter |
| **Claude Code** | `CLAUDE.md` | Markdown |
| **GitHub Copilot** | `.github/copilot-instructions.md` | Markdown |

The files differ in location, but the concept is identical: **a markdown file that becomes part of every prompt.**

We use `.agent/rules/` as a portable convention. It works with any agent that supports persistent instructions.

---

## Anatomy of a Rules File

A good rules file has 5 sections:

### 1. Context Handshake (Boot Sequence)

Tell the agent what to read before starting work:

```markdown
## Boot Sequence

Before every task:
1. Run `git status` — know what's dirty
2. Check the task board — what's in progress?
3. Read `docs/ARCHITECTURE.md` — know the system topology
4. Check current date — libraries may have major updates
5. Announce what you're working on
```

This prevents the agent from diving into code without context. It's the equivalent of an experienced dev checking Slack and the board before opening their editor.

### 2. Anti-Redundancy Rules

```markdown
## Before Coding

- **Search first**: grep the codebase before writing new code
- **Check existing patterns**: look for similar implementations
- **Don't duplicate**: if a utility exists, use it
```

Without this, agents will happily write a new date formatting function when there's already one in `utils/`.

### 3. Coding Standards

```markdown
## Coding Standards

- Stage ONLY the files you changed (never `git add .`)
- Run `npm run test` before committing
- Use conventional commits: `type(scope): message`
- No `console.log` debugging left in commits
- No `TODO` comments without a tracked task
```

Be specific. Vague rules like "write clean code" are useless. Concrete rules like "never `git add .`" are enforceable.

### 4. Architecture Map

```markdown
## Project Structure

- `src/api/` — REST endpoints (Express)
- `src/services/` — Business logic layer
- `src/models/` — Database models (Prisma)
- `src/utils/` — Shared utilities
- `tests/` — Test files mirror src/ structure
```

This prevents the agent from putting files in wrong directories. It also helps the agent understand what already exists before creating something new.

### 5. Do Not List (Negative Space)

The most powerful section. Tell the agent what NOT to do:

```markdown
## 🚫 NEVER

- Never use external paths (`~/.config/`) for project artifacts
- Never leave TODO comments without a tracked task
- Never bypass the test suite before committing
- Never modify files in `vendor/` or `legacy/`
- Never add scripts to the root directory (use `scripts/`)
- Never add backward-compat fallbacks — update all consumers in one commit
```

**Why this works**: Agents without negative constraints will try to "help" by adding fallback chains, backward-compatible layers, and safety nets that actually mask bugs.

---

## Starter Template

Here's a minimal rules file to drop into any project:

```markdown
---
trigger: always_on  
---

# Project Agent Protocol

## Boot Sequence
1. `git status` — check for dirty files from other sessions
2. Check task board / issue tracker for in-progress work
3. Announce what you'll be working on

## Coding Rules
- **NEVER** `git add .` — stage only your files explicitly
- **ALWAYS** run tests before committing
- **ALWAYS** use conventional commits: `type(scope): message`
- **ALWAYS** `git pull --rebase` before pushing
- Clean up `console.log` before committing

## Project Structure
[Document your key directories here]

## 🚫 Do Not
- Don't bypass tests
- Don't modify files another session is working on
- Don't commit with generic messages like "update" or "fix"
- Don't add fallback chains for renamed fields — update all consumers
```

---

## Advanced: Multi-Agent Identity

If you're running multiple agent sessions, each one can have identity context:

```json
// .agent/fleet-identity.json
{
  "agentId": 0,
  "role": "Prime",
  "branch": "develop",
  "focus": "general"
}
```

This lets each session know its role. Session 0 (Prime) handles general work. Session 1 might focus on frontend. Session 2 on backend. The rules file can reference this identity to scope behavior.

---

## The ROI

Teams using agent rules files report:
- **60% fewer "oops" commits** (wrong files staged, debugging left in)
- **Faster onboarding** — new agent sessions have context immediately
- **Consistency** — every session follows the same standards
- **Compounding knowledge** — the rules file improves over time as you add lessons learned

The rules file is a living document. Every time your agent makes a mistake, add a rule to prevent it. After a few weeks, your agent genuinely behaves like a senior dev.

---

*Next: [Chapter 3 — Workflow Templates →](#)*
