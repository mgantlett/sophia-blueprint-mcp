# Chapter 7: Nervous System & Observability

*Real-time telemetry for agent introspection*

---

## Why Agents Need a Nervous System

When your agent makes a decision, can you see *why*? When it routes a message, slows down, or burns through API budget — can you watch it happen in real time?

Most agents are black boxes. You find out something went wrong from a log file, hours later. A **nervous system** gives your agent real-time observability — an internal event bus that broadcasts every cognitive decision to anyone listening.

---

## The Event Bus: SSE Broadcasting

The NervousSystem is a Server-Sent Events (SSE) bus that broadcasts agent activity to connected clients:

```typescript
class NervousSystem {
    private clients: Set<Response> = new Set();

    // Connect a client (dashboard, monitor, logger)
    subscribe(res: Response) {
        res.writeHead(200, {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive'
        });
        this.clients.add(res);
        res.on('close', () => this.clients.delete(res));
    }

    // Broadcast an event to all connected clients
    emit(event: NeuralEvent) {
        const data = JSON.stringify(event);
        for (const client of this.clients) {
            client.write(`event: ${event.type}\ndata: ${data}\n\n`);
        }
    }
}
```

Events flow from every system component:

```typescript
// Routing decision
nervousSystem.emit({
    type: 'routing_decision',
    data: { input: "play jazz", route: 'operations', tier: 2, confidence: 0.89, latency: 82 }
});

// Inference call
nervousSystem.emit({
    type: 'inference_complete',
    data: { model: 'gemini-flash', tokens: 1247, cost: 0.0003, duration: 1840 }
});

// Mood shift
nervousSystem.emit({
    type: 'mood_update',
    data: { mood: 'Curious', energy: 0.78, curiosity: 92 }
});

// Self-repair
nervousSystem.emit({
    type: 'system_alert',
    data: { alertType: 'healer_triggered', service: 'ollama', action: 'restart' }
});
```

---

## NeuroTracker: Per-Inference Telemetry

Every inference call passes through the NeuroTracker, which records cost, latency, and token usage:

```typescript
function wrapWithTelemetry(model, modelName) {
    return {
        async invoke(messages, config) {
            const start = Date.now();
            const result = await model.invoke(messages, config);
            const duration = Date.now() - start;

            const tokens = result.usage_metadata?.totalTokens || 0;
            const cost = calculateCost(modelName, tokens);

            // Track cumulative stats
            neuroTracker.recordInference({ modelName, tokens, cost, duration });

            // Broadcast to nervous system
            nervousSystem.emit({
                type: 'inference_complete',
                data: { modelName, tokens, cost, duration }
            });

            // Feed into CostGovernor
            costGovernor.trackCall(modelName, tokens);

            return result;
        }
    };
}
```

The NeuroTracker maintains aggregate state:

```typescript
interface NeuroState {
    mood: string;
    energy: number;          // 0-100 (derived from budget remaining)
    curiosity: number;       // 0-100 (drives proactive behavior)
    activeNode: string;      // Current processing state
    currentThought: string;  // Human-readable status
    totalInferences: number;
    totalCost: number;
    totalTokens: number;
    sessionCost: number;
}
```

---

## Routing Decision Logger

Every routing decision is logged for later analysis (feeds into the shadow comparison from Chapter 3):

```typescript
interface RoutingDecision {
    timestamp: Date;
    input: string;
    tier: 1 | 2 | 3;
    route: string;
    confidence: number;
    latency: number;
    llmAgreed?: boolean;  // Did the LLM shadow agree?
}
```

Over time, this produces a dataset showing which messages are routed at which tier, and where the semantic router disagrees with the LLM. This is your training signal for improving routes.

---

## Dashboard Integration

The Membrane (React dashboard) connects to the NervousSystem via SSE and renders real-time visualizations:

- **Cognitive HUD** — Current mood, energy, active agent, cost ticker
- **Neural Activity Feed** — Live stream of routing decisions, inferences, events
- **Cost Graph** — Daily spend with budget threshold line
- **Fleet Monitor** — Status of all active agents (from fleet.db)

```typescript
// React hook for SSE connection
function useNeuralFeed() {
    const [events, setEvents] = useState([]);

    useEffect(() => {
        const source = new EventSource('/api/neural-feed');
        source.onmessage = (e) => {
            setEvents(prev => [...prev.slice(-100), JSON.parse(e.data)]);
        };
        return () => source.close();
    }, []);

    return events;
}
```

The dashboard makes the agent's inner life visible. When Sophia dreams, you see it. When she self-repairs, you see it. When she's running low on budget, the energy bar drops. This transparency is what separates a cognitive agent from a chatbot.

---

*Next: **Chapter 8 — Model Strategy** — Right model for the right job.*
