# Chapter 3: Workflow Templates

> Turn multi-step operations into reliable, repeatable agent workflows with markdown files.

---

## The Problem: Agents Forget Steps

Your agent knows how to `git commit`. But does it know to:

1. Run tests first?
2. Check for dirty files from other sessions?
3. Stage only its own files?
4. Review what's staged before committing?
5. Pull before pushing?
6. Close the task in the tracker?

Every time you tell it manually, you're wasting tokens and risking missed steps. **Workflows solve this.**

---

## The Format

A workflow is a markdown file with YAML frontmatter and numbered steps:

```markdown
---
description: Push work to develop — commit and push
---

# /push

> Commit your work and push. Lightweight — no version bumps.

## Step 1: Verify
\`\`\`bash
npm run test
\`\`\`

## Step 2: Check What's Dirty
\`\`\`bash
git status
\`\`\`

## Step 3: Stage YOUR Files
\`\`\`bash
git add <file1> <file2>
\`\`\`

## Step 4: Review Before Committing
\`\`\`bash
git diff --cached --name-only
\`\`\`

## Step 5: Commit
\`\`\`bash
git commit -m "feat(scope): describe what changed"
\`\`\`

## Step 6: Push
\`\`\`bash
git pull --rebase origin develop
git push origin develop
\`\`\`
```

The agent reads this file and executes each step in order. It's like a runbook that the agent follows autonomously.

### Where to put them

```
.agent/
├── rules/
│   └── RULES.md        # Persistent agent protocol
└── workflows/
    ├── push.md          # Commit and push
    ├── ship.md          # Release to production
    ├── claim-task.md    # Claim a task from the board
    └── context-handshake.md  # Bootstrap with context
```

---

## The Essential Workflows

### `/context-handshake` — Bootstrap the Agent

The first thing any session should do. Like a developer checking Slack and the board before opening their editor.

```markdown
---
description: Bootstrap agent with project awareness
---

# Context Handshake

## 1. Check Git Status
\`\`\`bash
git status
\`\`\`
> Know what's dirty. If there are uncommitted changes from
> another session, note them and don't touch them.

## 2. Check the Board
\`\`\`bash
# Use your task tracker's CLI
gh issue list --state open
# or: jira list --project MYPROJECT
# or: cat .tasks/board.md
\`\`\`
> What's open? What's in-progress? Pick your task.

## 3. Read Architecture
\`\`\`
View file: docs/ARCHITECTURE.md
\`\`\`

## 4. Report & Start
Summarize to the user:
- Date/time
- Open tasks (highlight high priority)
- In-progress tasks (what other sessions are working on)
- Any dirty files from other sessions
- "Ready to work — awaiting task"
```

### `/claim-task` — Claim Before You Code

Prevents two sessions from working on the same thing:

```markdown
---
description: Claim a task and start working
---

# Claim Task

## 1. Pick a Task
Check the task board. Choose one that doesn't overlap
with in-progress work from other sessions.

## 2. Mark It
\`\`\`bash
# Update your task tracker
gh issue edit <id> --add-label "in-progress"
# or update your local board
\`\`\`

## 3. Announce
Tell the user: "I'm working on **<task>**.
I'll be editing files in `src/api/`."

## 4. Code & Verify
\`\`\`bash
npm run test
\`\`\`

## 5. Push
When done, use `/push` to commit and push.
```

### `/ship` — Release to Production

The full ceremony: merge develop → main, version bump, tag, push:

```markdown
---
description: Ship a release — promote develop to main
---

# Ship

> Only ship when develop is stable and tested.

## Step 1: Verify
\`\`\`bash
npm run test
npm run build
\`\`\`

## Step 2: Merge to main
\`\`\`bash
git checkout main
git merge develop --no-ff -m "release: promote develop to main"
\`\`\`

## Step 3: Version Bump
\`\`\`bash
npm version patch  # or minor, or major
\`\`\`

## Step 4: Push
\`\`\`bash
git push origin main && git push --tags
\`\`\`

## Step 5: Return to develop
\`\`\`bash
git checkout develop
git merge main
git push origin develop
\`\`\`
```

### `/swarm-cycle` — The Full Loop

The meta-workflow that ties everything together:

```
/context-handshake → /claim-task → code + test → /push → (/ship when stable)
```

Each agent session follows this cycle independently. Coordination happens through the task board and git status — not through direct communication between sessions.

---

## The Turbo Annotation

For steps you trust the agent to auto-run without approval:

```markdown
// turbo-all

## Step 1: Run Tests
\`\`\`bash
npm run test
\`\`\`
```

The `// turbo` annotation means "this step is safe to auto-execute." Use it for read-only operations and tests. Never use it for destructive operations like `git push --force`.

Variations:
- `// turbo` — auto-run only the next step
- `// turbo-all` — auto-run all steps in this workflow

---

## Writing Your Own Workflows

The pattern is simple:

1. **Identify a multi-step operation** you repeat across sessions
2. **Write it as numbered steps** with bash commands
3. **Add safety gates** — verification steps before destructive actions
4. **Add context** — explain WHY each step matters so the agent adapts

Good workflow candidates:
- Database migrations
- Environment setup
- Deploy to staging
- Run integration tests
- Create a pull request
- Rotate secrets

---

## Why Markdown, Not Scripts?

| Approach | Problem |
|----------|---------|
| **Shell scripts** | Agent can't adapt — it's all-or-nothing execution |
| **CI/CD pipelines** | Too rigid, can't handle the "check first, decide" pattern |
| **Markdown workflows** | Agent reads, understands, adapts to context |

The agent can skip a step if it doesn't apply, add extra verification if something looks wrong, and explain what it's doing. A shell script can't do that.

---

*Next: [Chapter 4 — develop/master GitOps for AI Teams →](#)*
