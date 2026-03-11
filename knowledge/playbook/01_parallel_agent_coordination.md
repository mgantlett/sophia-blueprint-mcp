# Chapter 1: Parallel Agent Coordination

> **This chapter is FREE.** Share it, fork it, drop it in your `.agent/` directory.

---

## The Problem Nobody Talks About

You opened three Cursor tabs to parallelize your work. One is refactoring the API, another is fixing the auth flow, and the third is updating the docs.

Then one of them runs `git add .` and commits the other two sessions' half-finished work.

Congratulations — you now have a broken commit containing three unrelated, incomplete changes from three different contexts. `git revert` won't save you because the changes are interleaved.

**This is the #1 failure mode of multi-agent development.** Not hallucinations. Not bad code. Coordination.

---

## The Fix: Work Like Experienced Devs

The solution isn't Docker containers, worktrees, or lock files. We tried all of those. They add complexity, break hot-reload, and create merge hell when you need to reconcile.

The fix is embarrassingly simple: **treat your AI sessions like experienced developers sharing a codebase.**

Experienced devs don't need file locks. They communicate, review their changes, and commit only what's theirs.

### The Setup

```
┌──────────────────────────────────────────────┐
│  One IDE (Cursor, Windsurf, VS Code, etc.)   │
│                                              │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Chat 1  │ │ Chat 2  │ │ Chat 3  │        │
│  │ API fix │ │ Auth    │ │ Docs    │        │
│  └────┬────┘ └────┬────┘ └────┬────┘        │
│       │           │           │              │
│       └───────────┼───────────┘              │
│                   ▼                          │
│       ┌───────────────────┐                  │
│       │ Shared Filesystem │  One branch      │
│       │   One staging     │  One git index   │
│       └───────────────────┘                  │
└──────────────────────────────────────────────┘
```

- **One working directory** — all sessions share it
- **One branch** (`develop`) — all work goes here
- **One staging area** — this is where conflicts happen if you're not careful
- **`main`/`master`** — production, never commit directly

---

## The 7 Rules

### Rule 1: Announce Your Work

When you start a task, the agent should tell you what it's working on and check if other sessions have overlapping work.

If you have a task board or intention system, check it:

```
"I see Session 2 is working on auth routes. I'll avoid those files."
```

If you don't have a task system, `git status` is your task board — uncommitted changes from other sessions tell you what's in progress.

### Rule 2: Check What's Dirty Before Starting

```bash
git status
```

If there are uncommitted changes from another session, **do not touch them.** They belong to someone else. Note them and work around them.

This is the equivalent of walking up to a colleague's desk, seeing their open files, and not randomly editing them.

### Rule 3: Stage Only YOUR Files

```bash
# ✅ CORRECT — explicit paths
git add src/api/routes.ts src/api/middleware.ts

# 🚫 WRONG — grabs everything, including other sessions' work
git add .
git add -A
```

This is the single most important rule. If your agent does `git add .`, it will grab every other session's uncommitted work. Teach it to stage explicitly.

### Rule 4: Review Before Committing

```bash
git diff --cached --name-only
```

Read the list. **Are ALL of these files yours?** If you see files you didn't touch, unstage them:

```bash
git reset HEAD <file-you-didnt-touch>
```

### Rule 5: Small, Focused Commits

One concern per commit. If you fixed a bug AND refactored a utility, make two commits:

```bash
git commit -m "fix(auth): validate token expiry before refresh"
git commit -m "refactor(utils): extract date formatting helpers"
```

Conventional commit format (`type(scope): message`) makes history scannable and allows automated changelogs.

### Rule 6: Pull Before Push

```bash
git pull --rebase origin develop
```

Another session may have pushed while you were working. Rebase keeps history linear and surfaces conflicts early.

### Rule 7: Clean Up After Yourself

Before committing, check for debugging artifacts:

- `console.log` / `print()` debugging statements
- Commented-out code blocks  
- Temp files in the repo root

Your agent should be trained to strip these before commit.

---

## Conflict Resolution

If `git status` shows files modified by both your session and another:

1. **Don't panic.** Git tracks changes at the file level.
2. **Ask the user.** Say: *"I see `routes.ts` has uncommitted changes that aren't mine. Should I leave it alone?"*
3. **Never silently overwrite** another session's work.

The instinct of most AI agents is to "help" by resolving conflicts automatically. This is exactly wrong. The correct behavior is to **stop and report.**

---

## Quick Reference

| Situation | What to Do |
|---|---|
| Starting work | `git status` → check for dirty files |
| Before committing | `git diff --cached --name-only` → review staged files |
| See unfamiliar changes | Tell the user, don't touch them |
| Ready to push | `git pull --rebase` first |
| Finished with a task | Commit, push, close the task |

---

## Why Not Worktrees / Docker / Lock Files?

We spent 3 months trying infrastructure-heavy solutions:

| Approach | Problem |
|----------|---------|
| **Git worktrees** | Divergent branches that take hours to reconcile |
| **Docker per agent** | No hot-reload, massive resource overhead |
| **File lock system** | Agents forget to release locks, everything stalls |
| **Pre-commit hooks** | Agents disable them when they get in the way |

The instruction-based approach replaced **1,100 lines of infrastructure** with **8 clean markdown files** that any agent can follow. The key insight: agents that can read and follow instructions don't need mechanical guardrails — they need *culture*.

---

*Next: [Chapter 2 — The Agent Rules File →](#)*
