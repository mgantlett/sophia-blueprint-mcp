# Chapter 9: Productionizing

*Going from prototype to always-on*

---

## The Prototype Trap

You've built the architecture. Routing works. Agents collaborate. Memory persists. The heartbeat runs. In development, everything is beautiful.

Then you try to run it 24/7 and discover: processes crash silently, logs fill the disk, memory leaks accumulate, and there's no way to restart without losing state. **Productionizing is a separate engineering challenge.**

---

## Process Management: PM2

For an always-on agent, you need a process supervisor that handles restarts, log rotation, and multi-process management. PM2 is the standard for Node.js:

```javascript
// ecosystem.config.cjs
module.exports = {
    apps: [
        {
            name: 'sophia-soma',
            script: './substrate/soma/index.ts',
            interpreter: 'npx',
            interpreter_args: 'tsx',
            watch: false,
            max_restarts: 10,
            min_uptime: '30s',
            env: {
                NODE_ENV: 'production',
                SYNAPSE_ROOT: './synapse'
            }
        },
        {
            name: 'sophia-membrane',
            script: 'npm',
            args: 'run membrane:start',
            cwd: './substrate/membrane',
        },
        {
            name: 'sophia-nexus',
            script: './substrate/nexus/main.py',
            interpreter: 'python3',
        },
        // ... additional services
    ]
};
```

```bash
# Start the full stack
pm2 start ecosystem.config.cjs

# Monitor all processes
pm2 monit

# View logs
pm2 logs sophia-soma --lines 100

# Restart a single service
pm2 restart sophia-soma

# Save process list for auto-start on reboot
pm2 save
pm2 startup
```

**Key patterns:**
- **`max_restarts: 10`** prevents infinite restart loops
- **`min_uptime: '30s'`** ensures crashes within 30s count toward the restart limit
- **`watch: false`** in production — no filesystem watchers eating CPU
- **Separate processes** for Soma (brain), Membrane (UI), Nexus (Python bridge)

---

## Domain-Based Log Rotation

Don't dump all logs into one file. Use **domain-based rotating logs:**

```
synapse/logs/
├── soma_brain.log          ← Cognitive decisions, routing, inference
├── soma_error.log          ← Errors only (filtered)
├── membrane.log            ← UI events, SSE connections
├── nexus_mcp.log           ← MCP server, browser automation
├── performance.log         ← Latency, token counts, costs
└── archive/                ← Rotated old logs
```

```typescript
// Domain-aware logger
class Logger {
    private domains: Map<string, WriteStream> = new Map();

    log(domain: string, level: string, message: string, data?: any) {
        const stream = this.getStream(domain);
        const entry = `[${new Date().toISOString()}] [${level}] ${message}`;

        stream.write(entry + '\n');

        // Also write errors to the error domain
        if (level === 'ERROR') {
            this.getStream('soma_error').write(entry + '\n');
        }

        // Rotate if file exceeds 10MB
        this.checkRotation(domain);
    }

    private checkRotation(domain: string) {
        const filePath = `synapse/logs/${domain}.log`;
        const stats = fs.statSync(filePath);
        if (stats.size > 10 * 1024 * 1024) { // 10MB
            const archiveName = `${domain}_${Date.now()}.log`;
            fs.renameSync(filePath, `synapse/logs/archive/${archiveName}`);
        }
    }
}
```

---

## The verify:fast Pipeline

Before any deployment, run the verification pipeline:

```bash
# package.json
{
    "scripts": {
        "verify:fast": "npm run lint && npm run typecheck && npm run test:unit",
        "lint": "eslint substrate/ --ext .ts,.tsx",
        "typecheck": "tsc --noEmit",
        "test:unit": "vitest run --reporter=verbose"
    }
}
```

```bash
# Run before every merge
npm run verify:fast

# Expected output:
# ✓ Lint: 0 errors, 0 warnings
# ✓ TypeCheck: 0 errors
# ✓ Tests: 47 passed, 0 failed
```

**Rules:**
- 🚫 Never merge without `verify:fast` passing
- 🚫 Never deploy on a Friday
- ✅ Run from `develop` branch during development
- ✅ Run before merging to `main`

---

## Version Management

Use semantic versioning with a disciplined changelog:

```bash
# package.json version bump
npm version patch  # 2.2.1 → 2.2.2 (bug fixes)
npm version minor  # 2.2.2 → 2.3.0 (new features)
npm version major  # 2.3.0 → 3.0.0 (breaking changes)
```

```markdown
# CHANGELOG.md
## [2.3.0] — 2026-03-06

### Added
- MarketingPulse autonomic task (#147)
- DreamWeaver codebase meditation mode

### Fixed
- Routing disagreement logging missing tier field
- Memory deduplication false positives on short engrams

### Changed
- Heartbeat dream interval: 360 → 60 cycles (more frequent dreaming)
```

**Architecture doc parity:** The `ARCHITECTURE.md` version field MUST match `package.json`. The `/ship` workflow enforces this — no version mismatch gets deployed.

---

## Always-On Checklist

Before declaring your agent "production-ready":

- [ ] **PM2 ecosystem config** with restart limits
- [ ] **Startup script** — agent starts on system boot (`pm2 startup`)
- [ ] **Log rotation** — no log file grows unbounded
- [ ] **Budget limits** — CostGovernor prevents surprise bills
- [ ] **Health monitoring** — heartbeat detects and reports service failures
- [ ] **Graceful shutdown** — SIGTERM handler cleans up connections, saves state
- [ ] **Backup strategy** — synapse directory backed up regularly
- [ ] **Verification pipeline** — `verify:fast` runs before every deploy
- [ ] **Error alerting** — critical errors notify you (Discord, email, push)
- [ ] **Version tracking** — CHANGELOG and ARCHITECTURE stay current

---

## What You've Built

If you've followed this blueprint, you now have:

1. **A bio-digital cognitive architecture** — not a chatbot with tools
2. **Persistent, evolving identity** — personality that drifts over time
3. **20x faster routing** — without an LLM call for most messages
4. **Specialized expert agents** — with proper tool access control
5. **Zone-governed shared memory** — that scales across processes
6. **Self-maintaining autonomics** — heartbeat scheduler, self-repair, dreaming, social engagement
7. **Real-time observability** — see inside your agent's mind via NervousSystem
8. **96% cost reduction** — via tiered model strategy
9. **Production-grade reliability** — process management, logging, versioning

This isn't an AI wrapper. It's a living system.

---

*Thank you for reading. For the full source code, companion repo, and consulting services: [sophialabs.gumroad.com](https://sophialabs.gumroad.com)*
