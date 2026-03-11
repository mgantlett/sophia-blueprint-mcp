# Chapter 4: develop/master GitOps for AI Teams

> Why you need a staging branch when AI writes code, and how to set up a clean flow.

---

## The Problem: AI Commits Directly to main

Most developers working solo with a coding agent commit directly to `main`. It works fine — until:

- The agent introduces a regression you don't catch
- You need to demo something stable while mid-refactor
- Multiple sessions push conflicting changes
- You want to ship a release with confidence

**The fix: a two-branch model.** `develop` for daily work, `main` for production.

---

## The Two-Branch Model

```
            ┌─────────────────────────────────┐
            │         main (production)        │
            │  Only via merge from develop     │
            │  Tagged releases: v2.8.0, etc.   │
            └──────────────┬──────────────────┘
                           │ /ship promote
            ┌──────────────▼──────────────────┐
            │       develop (workspace)        │
            │  All agent sessions work here    │
            │  /push sends work here           │
            └──────────────────────────────────┘
```

### Rules

1. **All work goes to `develop`.** Every `/push` goes here.
2. **`main` = production.** Never commit directly. Only via `/ship promote`.
3. **Ship when stable.** After testing on develop, promote to main with a version bump.

---

## The Commit Flow

### What a Good Commit Looks Like

```bash
# 1. Stage ONLY the files you touched
git add src/services/auth.ts src/utils/token.ts

# 2. Verify before commit
npm run test

# 3. Commit with conventional format
git commit -m "fix(auth): validate token expiry before refresh"
```

### Conventional Commits

Use the `type(scope): message` format:

| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code change that doesn't add/fix functionality |
| `docs` | Documentation only |
| `chore` | Build, tooling, dependency updates |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |

**Why this matters**: Conventional commits enable automated changelogs, semantic versioning, and scannable git history. When your agent writes `"update stuff"`, you've lost all traceability.

### Version Bumping

Map commit types to version bumps:

- `fix:` / `refactor:` / `perf:` / `chore:` → **patch** (1.2.3 → 1.2.4)
- `feat:` → **minor** (1.2.3 → 1.3.0)
- `BREAKING CHANGE:` → **major** (1.2.3 → 2.0.0) — requires human approval

---

## Codebase Hygiene

### The "Don't" List

Train your agent with explicit negative rules:

```markdown
## 🚫 NEVER
- Never leave `TODO` comments without a tracked task
- Never bypass tests before committing
- Never add backward-compat fallbacks — update all consumers in one commit
- Never add scripts to the root directory (use `scripts/`)
- Never commit with generic messages like "update" or "fix"
```

**Why negative rules work**: Agents are eager to "help" by adding fallback chains and backward-compat layers. These mask bugs. A field rename that's covered by `newField || oldField` can hide data issues for weeks. The mandate: update all producers AND consumers in one commit.

### Dead Code Detection

Schedule periodic hygiene passes:

```bash
# Find unused exports (JS/TS projects)
npx knip

# Find files not imported by anything
# Custom script or tree-shaking analysis

# Find stale files (not modified in 90+ days)
find src/ -name "*.ts" -mtime +90
```

**Trust git history.** Delete dead code outright — `git log` preserves everything. Don't create `legacy/` or `archive/` directories; they become graveyards that never get cleaned.

### File Size Rules

Large files are a code smell. Set thresholds:

- `.ts`/`.tsx` files: warn at 400 lines, refactor at 600
- Route files: warn at 400 lines (split by resource)
- Components: warn at 500 lines (extract sub-components)

Your agent can check this automatically as part of the pre-commit flow.

---

## Pre-Push Verification

Run a fast verification gate before pushing:

```bash
# TypeScript: type-check + lint
npx tsc --noEmit && npx eslint src/

# Python: type-check + lint  
mypy src/ && ruff check src/

# General: run tests
npm run test
```

This should complete in under 30 seconds. If your test suite takes minutes, create a `verify:fast` script that runs only lint + type-check + critical tests.

---

*Next: [Chapter 5 — CLI-over-MCP Pattern →](#)*
