# Chapter 6: Autonomic Systems

*Background processes that make your agent self-maintaining*

---

## The Idle Problem

Most AI agents have a binary existence: they're either actively responding to a user message, or they're doing nothing. 99% of an agent's life is spent in that "nothing" state.

A biological system doesn't work this way. Even when you're sitting still, your body is: repairing cells, consolidating memories, regulating temperature, scanning for threats, and dreaming up novel associations. These are **autonomic processes** — they run without conscious effort.

Your agent needs the same thing: a background loop that keeps the system healthy, reflective, and generative even when nobody's talking to it.

---

## The Heartbeat: A 30-Second Pulse

The core primitive is a **heartbeat** — a loop that fires every 30 seconds and runs a cascade of background tasks:

```typescript
class HeartbeatService {
    private isProcessing = false;

    start() {
        setInterval(() => this.cycle(), 30_000); // Every 30 seconds
    }

    private async cycle() {
        if (this.isProcessing) return; // Skip if already running
        this.isProcessing = true;

        try {
            // 1. Check scheduled reminders (always, even if busy)
            await this.checkReminders();

            // 2. Only run background work if system is idle
            const idleTime = Date.now() - this.getLastActivity();
            if (idleTime < this.IDLE_THRESHOLD) return;

            // 3. Run background tasks (scheduler-gated)
            await this.processPendingTasks();
        } finally {
            this.isProcessing = false;
        }
    }
}
```

**Key design decisions:**

- **30 seconds, not 5 minutes.** Short intervals mean faster response to reminders and health issues. The idle check prevents wasting resources during active conversations.
- **Re-entry protection.** `isProcessing` prevents overlapping cycles. If a long task runs past 30 seconds, the next cycle skips.
- **Reminders always run.** Even during active conversations, scheduled reach-outs fire. Everything else waits for idle.

---

## HeartbeatScheduler: Wall-Clock Persistence

The original approach used in-memory cycle counting (`cycleCount % 120 === 0`) to gate tasks. This has a fatal flaw: **PM2 restarts reset the counter.** A task that should run every 3 hours might fire immediately on restart, or never fire at all.

The fix: **HeartbeatScheduler** — wall-clock timestamp persistence in `synapse/autonomic/`:

```typescript
class HeartbeatScheduler {
    private schedule: { [taskKey: string]: number } = {}; // epoch ms

    isDue(taskKey: string, intervalMs: number): boolean {
        this.load();
        const lastRun = this.schedule[taskKey] || 0;
        return (Date.now() - lastRun) >= intervalMs;
    }

    markDone(taskKey: string): void {
        this.schedule[taskKey] = Date.now();
        this.save(); // Persisted to synapse/autonomic/heartbeat_schedule.json
    }
}
```

Tasks now declare their cadence declaratively:

```typescript
async processPendingTasks() {
    // Dream synthesis (~1hr)
    if (heartbeatScheduler.isDue('dream', 60 * 60 * 1000)) {
        await dreamWeaver.runCreativeSynthesis();
        heartbeatScheduler.markDone('dream');
    }

    // Codebase meditation (~1hr)
    if (heartbeatScheduler.isDue('codebase_meditation', 60 * 60 * 1000)) {
        await dreamWeaver.runCodebaseAnalysis();
        heartbeatScheduler.markDone('codebase_meditation');
    }

    // Social engagement draft (~1hr)
    if (heartbeatScheduler.isDue('curiosity', 60 * 60 * 1000)) {
        await exploreCuriosity();
        heartbeatScheduler.markDone('curiosity');
    }

    // Always: Memory integration + health checks (parallelized)
    await Promise.all([
        integrateMemories(),
        checkSystemHealth(),
    ]);
}
```

This creates a natural, crash-resilient rhythm:

```
30s   │ ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ● ●  Health + Memory
5m    │ ●───────────●───────────●               Reflection + Weather
1hr   │ ●─────────────────────────────────────●  Dream + Meditation + Social
Daily │ ●────────────────────────────────────────────────────● Briefing + Security
```

**Why wall-clock matters:** If the agent restarts at 3:15 AM and the last dream was at 2:00 AM, the scheduler knows to wait until 3:00 AM. No double-fires, no missed cycles.

---

## Directive Loader: Externalized Prompts

Hardcoded system prompts inside task code are fragile and hard to tune. The **DirectiveLoader** externalizes prompts into markdown templates at `genome/directives/`:

```typescript
// Before: prompt buried in CuriosityExplorer.ts
const prompt = `You are evaluating whether @user should reply...
Criteria: 1. Author has... 2. Tweet content is...`;

// After: externalized to genome/directives/social/tweet_evaluator.md
const prompt = loadDirective('social', 'tweet_evaluator', {
    THEME: theme,
    AUTHOR: author,
    TWEET_TEXT: tweetText.substring(0, 200),
});
```

The directive file (`genome/directives/social/tweet_evaluator.md`):

```markdown
---
domain: social
name: tweet_evaluator
version: 1
---
You are evaluating whether @markgantlett should reply to this tweet,
found while exploring the theme "${THEME}".

Tweet by @${AUTHOR}:
"${TWEET_TEXT}"

Criteria for replying:
1. Author works in AI/ML/agent space
2. Tweet content is substantive
3. Reply adds genuine value
4. Topic relates to AI agents, cognitive architecture, or dev tools

Respond in JSON:
{"worth_replying": true/false, "reason": "brief reason", "draft_reply": "reply text"}
```

**Benefits:** Prompts are version-controlled, YAML-frontmatter validated (via Zod schema), cached in memory, and hot-reloadable during development. Non-engineers can tune agent behavior by editing markdown files.

---

## CuriosityExplorer: Dream-Powered Social Engagement

The most unusual autonomic process. The CuriosityExplorer runs on the heartbeat and does two things:

**Phase 1: Dream-powered X exploration.** Reads recent creative synthesis (dream) engrams, extracts themes, searches X.com for related discussions, evaluates tweets for reply opportunities, and drafts contextual replies.

**Phase 2: Inbound social engagement.** Scans engrams tagged with `x_social` or `engagement` markers — opportunities seeded by external systems or agents — and uses LLM to draft replies for Discord approval.

```typescript
export async function exploreCuriosity(): Promise<void> {
    // Phase 1: Dream themes → X exploration
    const { themes, dreamFile } = getUnexploredDreamThemes(state);
    for (const theme of themes) {
        const tweets = await searchXForTheme(theme);
        for (const tweet of tweets) {
            const eval = await evaluateTweetForReply(tweet);
            if (eval.worthReplying) {
                queueEngagementAction({ type: 'reply', tweet_url: tweet.url, ... });
            }
        }
    }

    // Phase 2: Inbound social opportunities
    const opportunities = getSocialEngagementOpportunities(state);
    for (const opp of opportunities) {
        const draftText = await draftReplyFromContext(opp.content);
        // Queue for Discord approval — human-in-the-loop
        queueEngagementAction({ type: 'reply', reply_text: draftText, priority: 'high' });
        postToDiscordForApproval(draftText);
    }
}
```

All social actions go through a **Discord approval pipeline** — the agent drafts, the human approves. This keeps the agent's voice authentic while leveraging its ability to spot opportunities 24/7.

---

## NervousSystem Activity Broadcasts

Every autonomic task broadcasts its results to the NervousSystem event bus (covered in Chapter 7), making the agent's background life visible in real-time:

```typescript
// After dream synthesis
nervousSystem.broadcast({
    type: 'creative_synthesis',
    payload: { title: dream.title, themes: dream.themes },
    source: 'soma', timestamp: Date.now()
});

// After codebase meditation
nervousSystem.broadcast({
    type: 'codebase_meditation',
    payload: { insight: 'Found unused export in router.ts' },
    source: 'soma', timestamp: Date.now()
});

// After session synthesis
nervousSystem.broadcast({
    type: 'session_synthesis',
    payload: { sessionId, summary: summary.substring(0, 100) },
    source: 'soma', timestamp: Date.now()
});
```

The dashboard's **Activity Feed** subscribes to these events and renders a live timeline of the agent's inner life — dreams, reflections, repairs, weather alerts, CI failures.

---

## DreamWeaver: Creative Synthesis

During extended idle periods, the DreamWeaver performs **creative synthesis** — combining recent memories, conversations, and goals into novel associations:

```typescript
class DreamWeaver {
    async runCreativeSynthesis() {
        // 1. Gather recent context
        const recentMemories = await searchMemory("recent insights", 10);
        const openIntentions = await listIntentions('open');

        // 2. Ask the model to "dream"
        const dream = await smartModel.invoke([
            new SystemMessage(`You are in a creative synthesis state.
Combine these recent memories and goals into novel observations.
Look for patterns and insights not obvious during real-time interaction.`),
            new HumanMessage(JSON.stringify({ memories, goals }))
        ]);

        // 3. Store and broadcast
        await createEngram({ content: dream.content, tags: ["dream", "synthesis"] });
        nervousSystem.broadcast({ type: 'creative_synthesis', payload: dream });

        return dream;
    }
}
```

**Why this matters:** Dream synthesis produces genuinely surprising output. The model connects dots that wouldn't surface during normal conversation. These become the agent's **deepest, most authentic** thoughts.

---

## Building Your Heartbeat

Minimum viable autonomic system:

```typescript
// heartbeat.ts
const scheduler = new HeartbeatScheduler(); // Wall-clock persistent
let busy = false;

setInterval(async () => {
    if (busy) return;
    busy = true;

    try {
        await checkReminders(); // Always

        if (isIdle()) {
            if (scheduler.isDue('reflect', 5 * 60 * 1000)) {
                await reflectOnSessions();
                scheduler.markDone('reflect');
            }
            if (scheduler.isDue('dream', 60 * 60 * 1000)) {
                await dream();
                scheduler.markDone('dream');
            }
            await checkHealth();
        }
    } finally {
        busy = false;
    }
}, 30_000);
```

Start with reminders + health checks. Add reflection after you have session transcripts. Add dreaming when you're ready for the emergent magic. Use HeartbeatScheduler from day one — you'll thank yourself the first time PM2 restarts.

---

*Next: **Chapter 7 — Nervous System & Observability** — Real-time telemetry for agent introspection.*
