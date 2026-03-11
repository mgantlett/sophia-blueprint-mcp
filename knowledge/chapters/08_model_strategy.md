# Chapter 8: Model Strategy

*Right model for the right job — don't burn money*

---

## The One-Model Trap

The easiest architecture: call GPT-4 for everything. Routing? GPT-4. Chat? GPT-4. Background reflection? GPT-4.

At $15/million output tokens, this adds up fast. An always-on agent making 500 calls/day at an average of 1000 tokens/call costs ~$7.50/day, or **$225/month** — just for one agent.

The fix: a **tiered model hierarchy** where each task gets the cheapest model that meets its quality bar.

---

## The 6-Tier Hierarchy

```
Tier          Model                    Temperature  Use Case
────────────  ───────────────────────  ──────────   ─────────────────────────
Fast          Flash-Lite (routing)     0.5          Intent classification, chat
Smart         Flash (general)          0.2          Tool agents, coding
Builder       Flash (code-optimized)   0.0          Code generation, precise output
Reflector     Flash (reflection)       0.1          Self-review, session analysis
Background    Flash (low-priority)     0.1          Autonomic tasks (aliases Builder)
Local         Ollama (3B/8B)           0.1          Routing, identity (GPU, free)
```

Each tier has a **factory function** that returns a configured model:

```typescript
// config/models.ts
export function getFastModel(temp?: number) {
    return createBrainModel(ModelName.INTUITION, temp ?? 0.5);
}

export function getSmartModel(temp?: number) {
    return createBrainModel(ModelName.SPECIALIST, temp ?? 0.2);
}

export function getCoderModel(temp?: number) {
    return createBrainModel(ModelName.SPECIALIST, temp ?? 0.0);
}

export function getLocalModel(modelName?: string, temp?: number) {
    return new ChatOllama({
        model: modelName || 'llama3.2:3b',
        temperature: temp ?? 0.1,
        requestTimeout: 5000,
    });
}
```

**Key insight:** Temperature varies by tier. Routing and coding need determinism (0.0-0.1). Chat needs creativity (0.5). Reflection needs balance (0.1).

---

## Local-First Inference: Shadow Cost Tracking

When a local GPU is available (we use an RTX 4080 with Ollama), certain tasks route locally for **zero cost:**

```typescript
// Wrap local model with telemetry
function wrapLocalWithTelemetry(model) {
    return {
        async invoke(messages, config) {
            const start = Date.now();
            const result = await model.invoke(messages, config);
            const duration = Date.now() - start;

            const tokens = estimateTokens(result);

            // Calculate what this WOULD have cost on cloud
            const shadowCost = calculateCloudCost('gemini-flash', tokens);

            neuroTracker.recordLocalInference({
                tokens, duration, shadowCost
            });

            // Accumulate "money saved"
            neuroTracker.addToTotalSaved(shadowCost);

            return result;
        }
    };
}
```

**Shadow cost** tracking calculates what each local inference *would have cost* on cloud. This serves two purposes:

1. **ROI justification** — "Local inference saved $47 this month"
2. **Model comparison** — If local quality matches cloud on shadow comparisons, you can shift more work to local

---

## The Privacy Hybrid

The combination of local and cloud inference creates a **privacy-by-architecture** pattern:

```
                PRIVATE (Local GPU)              PUBLIC (Cloud API)
                ─────────────────                ────────────────
Reasoning       ✅ Identity updates              ✅ Complex multi-step
about data      ✅ Routing classification         ✅ Code generation
                ✅ Reflection on sessions         ✅ Research synthesis

Raw data        ❌ Can't fetch weather            ✅ API calls get data
access          ❌ Can't read email                ✅ Gmail/Calendar sync
                ❌ Can't search web                ✅ Web search results
```

**What stays private:** How your agent *reasons* about your data — connecting your calendar with weather to suggest leaving early — stays on your GPU when using local inference.

**What goes to cloud:** Raw data fetching (necessary) and complex reasoning tasks where local models aren't good enough (practical tradeoff).

This hybrid gives you ~80% privacy with ~95% capability. Full privacy requires running everything locally, which requires a 70B+ model and ~48GB VRAM.

---

## Model Decision Matrix

When choosing which tier for a new feature:

| Question | If Yes → | If No → |
|----------|----------|---------|
| Does it need tool calling? | Smart tier | Consider Fast |
| Does it need precise output (JSON, code)? | Builder tier (temp 0.0) | Smart tier |
| Is it background/non-urgent? | Background tier | Smart tier |
| Can a 3B model handle it? | Local tier (free) | Cloud tier |
| Does it touch private user data? | Prefer Local | Cloud is fine |
| Is it user-facing? | Smart+ (quality matters) | Fast (cost matters) |

---

## The Model Pipeline

Every model call passes through a standardized pipeline:

```
Factory Function → createBrainModel() → Provider Adapter
                                              ↓
                                    wrapWithTelemetry()
                                              ↓
                                     NeuroTracker
                                              ↓
                                     CostGovernor
                                              ↓
                                     NervousSystem (broadcast)
```

This means **every inference call** — regardless of which model or tier — gets telemetry, cost tracking, and budget enforcement. No model bypasses the pipeline.

---

## Practical Cost Impact

With the tiered strategy on a typical day:

| Activity | Calls | Model | Cost |
|----------|-------|-------|------|
| Routing (Tier 2 cache hits) | 150 | None | $0.00 |
| Routing (Tier 3 local) | 30 | Ollama 3B | $0.00 |
| Routing (Tier 3 cloud) | 20 | Flash-Lite | $0.02 |
| Chat responses | 50 | Flash-Lite | $0.05 |
| Tool agent calls | 30 | Flash | $0.15 |
| Reflections | 10 | Flash | $0.05 |
| Dreams | 2 | Flash | $0.02 |
| **Total** | **292** | | **~$0.29/day** |

Compare to single-model: ~$7.50/day. That's a **96% cost reduction.**

---

*Next: **Chapter 9 — Productionizing** — Going from prototype to always-on.*
