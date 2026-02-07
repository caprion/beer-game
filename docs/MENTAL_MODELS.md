# Mental Models Applied to the Beer Game

## Why Mental Models Matter Here

The Beer Game is not just a supply chain exercise — it's a **laboratory for observing how human thinking fails under complexity**. Each behavioral agent in this simulation embodies a cluster of cognitive biases and decision heuristics. By mapping established mental models onto these agents, we can:

1. **Diagnose** what makes each agent fail (or succeed)
2. **Predict** which combinations will create chaos
3. **Design** better agents by inverting known failure modes
4. **Teach** decision-making principles through concrete examples

---

## Framework 1: Occam's Razor

> *"Entities should not be multiplied beyond necessity."*
> — William of Ockham

**Principle:** The simplest explanation (or strategy) that fits the data is usually best. Complexity without evidence is a liability.

### Applying Occam's Razor to Each Agent

| Agent | Complexity Score | Razor Verdict | Analysis |
|-------|:---:|---|---|
| **PassivePipeline** | ★☆☆☆☆ | ✅ **Passes** | One formula: `order = target + demand + backlog - (on_hand + pipeline)`. No state tracking, no history, no emotional modifiers. It's the simplest agent that accounts for all relevant variables. This is the Occam ideal. |
| **RandomBaseline** | ★☆☆☆☆ | ⚠️ **Too simple** | Even simpler than PassivePipeline but *ignores all input*. Occam says simplest *that fits the data*. This one doesn't fit anything — it's noise, not parsimony. |
| **AggressiveGrowthHacker** | ★★★☆☆ | ❌ **Fails** | Adds amplification factor, safety buffer, panic threshold, AND panic bonus. Four unnecessary multipliers layered on simple demand. The safety buffer alone bakes in a permanent assumption ("demand will spike") without evidence. |
| **ConservativeCustodian** | ★★★★☆ | ❌ **Fails** | Spike detection, rolling averages, spike counters, dismissal logic, panic override. Six mechanisms to do what could be achieved with a dampened order-up-to policy. The spike-dismissal is particularly problematic — it's complexity to *ignore* information. |
| **MyopicFirefighter** | ★★★★★ | ❌ **Fails badly** | State machine (3 modes) × emotional volatility × crisis duration × random swings. The most complex agent, yet its decisions are the *least* informed. Complexity here serves panic, not understanding. |
| **SignalChaser** | ★★★★☆ | ❌ **Fails** | Trend detection, momentum windowing, extrapolation, acceleration analysis, boom buffers. All this machinery to detect "signals" that are usually noise. Four parameters to tune something that shouldn't be amplified. |
| **RLAgent** | ★★★☆☆ | ⚠️ **Jury out** | The complexity (Q-table, state discretization) could be justified *if* it converges to a good policy. But 5 discrete actions and crude bins may be too coarse. The complexity exists for learning, not for over-fitting a heuristic. |

### Occam's Razor Insight

**The PassivePipeline is the only agent that passes Occam's Razor** — and empirically it tends to produce the lowest bullwhip effect. This isn't coincidence. The bullwhip effect is fundamentally caused by *unnecessary complexity in ordering decisions*: agents adding buffers, amplifying signals, and panicking based on assumptions that aren't warranted by the data they actually have.

> **Design principle:** Before adding a parameter to an agent, ask: "Does this parameter respond to information the agent actually observes, or does it encode an unfounded assumption?"

---

## Framework 2: Munger's Inversion

> *"Invert, always invert."*
> — Charlie Munger (via Carl Jacobi)

**Principle:** Instead of asking "How do I succeed?", ask "How would I guarantee failure?" Then avoid those things.

### Inverting the Beer Game: How to Guarantee Maximum Bullwhip

If we wanted to **maximize** bullwhip and **guarantee** supply chain catastrophe:

1. **React to noise as if it were signal** → SignalChaser does exactly this
2. **Amplify every demand increase but never reduce** → AggressiveGrowthHacker's asymmetric response
3. **Ignore pipeline inventory** (orders already in transit) → Almost every agent except PassivePipeline does this
4. **Add safety buffers unconditionally** → AggressiveGrowthHacker adds +3 every period regardless
5. **Panic and over-correct** → MyopicFirefighter orders 3× backlog + 2× demand during panic
6. **Dismiss real signals until it's too late, then panic** → ConservativeCustodian's spike-dismissal → panic cycle
7. **Make decisions based on emotion, not information** → MyopicFirefighter's `emotion_factor`
8. **Forget what you ordered** (ignore pipeline) → Creates the classic "double-ordering" trap

### Inversion Table: What Each Agent Does Wrong (Inverted Tells Us What's Right)

| Catastrophic Behavior | Which Agent? | **Inverted → Correct Behavior** |
|---|---|---|
| Amplify demand increases | Growth-Hacker | **Smooth demand signals** — moving average, not multiplication |
| Permanent safety buffer | Growth-Hacker | **Dynamic safety stock** — based on demand variance, not a constant |
| Ignore pipeline on-order | Growth-Hacker, Signal Chaser, Custodian, Firefighter | **Always account for pipeline** — what you've ordered but haven't received |
| Treat noise as signal | Signal Chaser | **Statistical significance test** — is this change within normal variance? |
| Dismiss real changes | Conservative Custodian | **Bayesian updating** — weight new evidence appropriately, don't dismiss or over-react |
| Emotional/random swings | Myopic Firefighter | **Consistent policy** — same inputs should produce same outputs |
| Zero orders during overstock | Myopic Firefighter | **Gradual reduction** — smooth drawdown, not cliff edges |
| Panic orders during shortage | Custodian, Firefighter, Growth-Hacker | **Rate-limited correction** — fix over N periods, not one explosive order |

### The Ideal Agent (Via Inversion)

An agent that avoids all the inverted failure modes would:
1. Track and smooth demand over a window (not react to single-period changes)
2. Account for pipeline inventory in every calculation
3. Use a dynamic target that adjusts to observed demand variance
4. Never order zero (smooth drawdown instead)
5. Never panic (rate-limit corrections over multiple periods)
6. Be deterministic for same inputs (no random emotional component)

**This is essentially an enhanced PassivePipeline with exponential smoothing** — which is what the "Stabilizer/System Thinker" agent (documented in PROFILES.md but not yet implemented) should look like.

---

## Framework 3: Second-Order Thinking

> *"And then what?"*
> — Howard Marks

**Principle:** First-order thinking stops at the immediate effect. Second-order thinking considers the consequences of the consequences.

### First-Order vs Second-Order in the Beer Game

| Agent | First-Order Thought | Second-Order Reality |
|---|---|---|
| **Growth-Hacker** | "I'll order extra to avoid stockouts" | Extra orders → upstream over-produces → glut arrives later → forced to stop ordering → upstream starves → cycle repeats |
| **Custodian** | "I'll order less to keep inventory low" | Under-ordering → backlog builds → eventually forced to panic order → upstream sees massive spike → wildly over-produces |
| **Firefighter** | "Backlog is high, order a ton!" | Huge order + previous orders still in pipeline → massive inventory arrives → stops ordering → upstream collapses |
| **Signal Chaser** | "Demand is trending up, get ahead of it!" | Amplified order → upstream sees artificial demand → they amplify too → product floods in → demand "crashes" → everyone panics |
| **PassivePipeline** | "Order what I need, accounting for what's coming" | Stable orders → upstream sees stable demand → stable production → stable deliveries → system equilibrium |

### The Critical Second-Order Effect: The Pipeline

The single most destructive first-order error in the Beer Game is **ignoring pipeline inventory**. When an agent orders without considering what's already in transit:

```
Week 1: Low inventory → Order 20 units
Week 2: Still low (shipment not arrived) → Order 20 more
Week 3: Still low → Order 20 more
Week 4: All 60 units arrive at once → Massive overstock → Order zero
Week 5-8: Upstream has no demand → They stop producing
Week 9: Pipeline empty, inventory consumed → Shortage again → Panic
```

This is the **fundamental mechanism of the bullwhip effect**, and 5 of 7 agents don't properly account for pipeline when making decisions.

---

## Framework 4: Circle of Competence

> *"Know what you know, and know what you don't know."*
> — Warren Buffett / Charlie Munger

**Principle:** Stay within your circle of knowledge. Mistakes happen when you act on things you don't understand.

### What Each Agent Actually Knows vs What It Assumes

| Agent | **Actually Knows** (from RoleState) | **Assumes Without Evidence** |
|---|---|---|
| **All agents** | Current inventory, backlog, pipeline, incoming order, received shipment, last order placed | — |
| **Growth-Hacker** | ↑ plus demand change from last period | Future demand will be even higher; stockouts are catastrophic; safety buffer is always needed |
| **Custodian** | ↑ plus 8-period demand history | Demand spikes are anomalies (≤2 in a row); low inventory is always preferable |
| **Firefighter** | ↑ plus crisis state/duration | Panic is a valid strategy; emotional swings are informative |
| **Signal Chaser** | ↑ plus momentum-window trends | Trends will continue and accelerate; there is always a signal in the noise |
| **PassivePipeline** | ↑ and nothing more | Target inventory level is correct (mild assumption, easily tunable) |

### Circle of Competence Insight

Every agent **has the same information** (`RoleState`). The difference is in what they **assume beyond that information**:
- PassivePipeline makes **one** assumption (target inventory) — inside its circle
- All other agents make **multiple unfounded assumptions** — operating outside their circle
- The more assumptions beyond available data, the worse the outcomes

**This maps directly to Occam's Razor**: unnecessary assumptions = unnecessary complexity = unnecessary bullwhip.

---

## Framework 5: Incentive-Driven Behavior (Munger's "Show Me the Incentive")

> *"Show me the incentive and I will show you the outcome."*
> — Charlie Munger

**Principle:** Behavior is driven by incentives. Misaligned incentives produce bad outcomes even with good intentions.

### The Beer Game's Incentive Structure

The simulation has two cost levers:
- **Holding cost**: $0.50/unit/period (cost of having too much)
- **Backlog cost**: $1.00/unit/period (cost of having too little)

This **2:1 asymmetry** already tells us the "rational" bias:

> Since backlog costs 2× holding, every rational agent should slightly over-order. The cost of having one extra unit ($0.50) is half the cost of missing one unit ($1.00).

### How Incentives Shape Each Agent

| Agent | Implicit Incentive Reading | Alignment |
|---|---|---|
| **Growth-Hacker** | "Backlog is 2× worse → order WAY more than needed" | ❌ Over-corrects. Reads the 2:1 as infinity:1 |
| **Custodian** | "I'll minimize holding cost" | ❌ **Ignores** the 2:1 ratio entirely. Optimizes the cheaper cost |
| **Firefighter** | "Whatever hurts right now, fix it" | ❌ Reads the correct incentive but applies it with no memory or planning |
| **Signal Chaser** | "If demand goes up, backlog risk goes up, order more" | ❌ Correct reasoning, wrong magnitude |
| **PassivePipeline** | "Balance inventory target against current position" | ✅ The target can be set to reflect true cost ratio |

### Designing Better Incentives

If you change the cost ratio, agent behavior should change. This suggests experiments:
- **Equal costs** (1:1): Does the Growth-Hacker calm down?
- **High holding cost** (2:1 reversed): Does the Custodian become optimal?
- **Zero backlog cost**: Does the system stabilize?
- **Non-linear costs**: Quadratic backlog cost — does it change panic thresholds?

---

## Framework 6: Map Is Not the Territory

> *"The map is not the territory."*
> — Alfred Korzybski

**Principle:** Our models of reality are simplifications. Confusing the model for reality leads to errors.

### Where Each Agent Confuses Map for Territory

| Agent | The "Map" (Agent's Model) | The "Territory" (System Reality) |
|---|---|---|
| **Signal Chaser** | "Demand history contains predictive signal" | Demand may be constant + noise; the "signal" is the map's pattern-matching, not reality |
| **Growth-Hacker** | "More ordering = more safety" | More ordering = more bullwhip = less safety for everyone |
| **Custodian** | "Spikes are anomalies" | Spikes might be real regime changes; dismissing them is confusing preference for evidence |
| **Firefighter** | "Current pain = most important variable" | Current pain is a lagging indicator; pipeline and orders already placed are leading indicators |

### The Deepest Map/Territory Error

All agents except PassivePipeline share one fundamental map/territory confusion:

> **They treat their local view as the whole system.**

Each agent sees only its own inventory, backlog, and incoming order. But the *territory* is a 4-node chain with 2-week shipment delays. An agent that mistakes its local snapshot for the system state will consistently over-react, because it can't see that its upstream partner is already processing a large order, or that a shipment is one week away from arriving.

**This is exactly why information sharing experiments (Phase 3 in the plan) matter:** they expand each agent's "map" to better match the "territory."

---

## Framework 7: Feedback Loops and Systems Thinking (Senge/Meadows)

> *"The behavior of a system cannot be known just by knowing the elements of which the system is made."*
> — Donella Meadows

### The Beer Game Has Two Feedback Loops

**Negative (stabilizing) loop:**
```
Low inventory → Order more → Receive more → Inventory rises → Order less → Stable
```

**Positive (destabilizing) loop:**
```
Low inventory → Panic order → Upstream panic orders → Everyone over-orders
→ Massive glut arrives → Everyone stops ordering → Upstream starved
→ Nothing produced → Shortage → Panic order (repeat, amplified)
```

### Which Loop Each Agent Activates

| Agent | Dominant Loop | Why |
|---|---|---|
| **PassivePipeline** | Negative (stabilizing) | Orders proportional to gap; self-correcting |
| **Growth-Hacker** | Positive (destabilizing) | Amplification factor turns corrections into over-corrections |
| **Custodian** | Negative → then Positive | Dampens initially, but panic threshold creates a positive-loop switch |
| **Firefighter** | Positive (chaotic) | Crisis modes are all positive-feedback: panic → over-order → overstock → zero-order → panic |
| **Signal Chaser** | Positive (trend-following) | Extrapolation means the loop's gain > 1.0, so every signal amplifies |
| **RandomBaseline** | Neither | Decoupled from the system; injects noise but no systematic feedback |

### Key Insight: Delay × Gain = Oscillation

The simulation has `shipment_lead_time = 2` and `order_lead_time = 1`. Total round-trip delay = 3 periods. Any agent with effective gain > 1.0 (amplifying responses) will create oscillations with period ≈ 2× delay = 6 weeks. This is predictable from control theory and matches beer game empirical results.

**The Growth-Hacker has gain 1.5×, Signal Chaser has gain ~2.0×, and Firefighter has crisis-mode gain up to 3.0×.** All will oscillate. PassivePipeline has effective gain < 1.0 and will converge.

---

## Framework 8: Antifragility (Taleb)

> *"Some things benefit from shocks; they thrive and grow when exposed to volatility."*
> — Nassim Taleb

### Fragility Classification of Agents

| Category | Agent | Why |
|---|---|---|
| **Fragile** | Signal Chaser | Any volatility is amplified; shocks multiply through the system |
| **Fragile** | Myopic Firefighter | Shocks trigger panic spirals that compound |
| **Fragile** | Aggressive Growth-Hacker | Adds volatility buffer unconditionally; amplifies all shocks |
| **Robust** | Passive Pipeline | Absorbs shocks through target-gap ordering; doesn't amplify |
| **Robust** | Conservative Custodian | Dampens shocks initially (but fragile to sustained shocks → panic) |
| **Antifragile** | (Not yet implemented) | An agent that *learns from* disruptions and improves its policy |
| **Antifragile** | RL Agent (aspirational) | *Should* become antifragile through learning — adapts to shock patterns |

### The Antifragile Agent (Design Target)

A truly antifragile beer game agent would:
1. **Benefit from demand variance**: Use observed variance to set dynamic safety stock (more variance → slightly higher buffer, mathematically calibrated)
2. **Learn from disruptions**: Track prediction errors and adjust smoothing parameters
3. **Have optionality**: Maintain small buffer "just in case" but no large commitments
4. **Fail gracefully**: When wrong, the cost is small (slightly over-stocked); when right, the benefit is large (prevented stockout)

This is an asymmetric payoff profile — exactly what Taleb prescribes. The Growth-Hacker *thinks* it's doing this (buffer against stockouts) but the execution is wrong because the buffer is constant, not proportional to actual risk.

---

## Synthesis: The Mental Models Scorecard

| Framework | Best Agent | Worst Agent | Key Lesson |
|---|---|---|---|
| **Occam's Razor** | PassivePipeline | MyopicFirefighter | Simplicity wins in complex systems |
| **Inversion** | PassivePipeline | All panic-capable agents | Avoid what guarantees failure |
| **Second-Order Thinking** | PassivePipeline | Growth-Hacker | Consider what your order does to the system |
| **Circle of Competence** | PassivePipeline | Signal Chaser | Don't assume beyond your data |
| **Incentives** | PassivePipeline | Conservative Custodian | Align with the actual cost structure |
| **Map ≠ Territory** | PassivePipeline | Signal Chaser | Your local view isn't the system |
| **Systems/Feedback** | PassivePipeline | Growth-Hacker | Gain < 1.0 → convergence; gain > 1.0 → oscillation |
| **Antifragility** | (Needs building) | Signal Chaser | Learn from shocks, don't amplify them |

### The Paradox

**The "dumbest" agent (PassivePipeline) wins on every framework.** This is the Beer Game's deepest lesson:

> In a complex system with delays and limited information, **the simplest rational strategy dominates all clever strategies**. Intelligence that adds complexity without better information makes things worse.

This echoes Munger's observation: *"It is remarkable how much long-term advantage people like us have gotten by trying to be consistently not stupid, instead of trying to be very intelligent."*

---

## Proposed New Agents Based on Mental Models

### 1. The Bayesian Updater (from Circle of Competence + Map ≠ Territory)
- Maintains a probabilistic demand estimate
- Updates beliefs proportionally to evidence strength
- Higher confidence → smaller adjustments; lower confidence → more responsive
- Never panics; confidence-weighted corrections

### 2. The Antifragile Adapter (from Antifragility + Systems Thinking)
- Tracks its own prediction errors
- Adjusts smoothing and buffer parameters based on observed variance
- Benefits from disruptions by improving its model
- Asymmetric: conservative in normal times, opportunistic in disruption

### 3. The Inverter (from Inversion)
- At each step, computes what the *worst* order would be, then picks the opposite
- Worst = whatever maximizes next-period cost variance
- This naturally avoids: zero orders, huge panic orders, noise amplification

### 4. The Minimalist (from Occam's Razor)
- Even simpler than PassivePipeline
- `order = max(0, incoming_order + backlog - received_shipment)`
- No target inventory parameter — just flow-through with backlog correction
- Tests whether *any* state beyond the immediate is needed

---

## Framework 9: Information Asymmetry (Akerlof / Stiglitz)

> *"Markets with asymmetric information tend toward adverse outcomes."*
> — George Akerlof (Market for Lemons, 1970)

**Principle:** When one party has more information than another, decisions degrade. In supply chains, each echelon sees only its own state — a profound information asymmetry that drives the bullwhip effect.

### The Beer Game's Information Structure

In the classic beer game (information mode = `none`), each agent knows:
- ✅ Its own inventory, backlog, pipeline, incoming order
- ❌ Upstream partner's inventory, backlog, capacity
- ❌ Downstream partner's actual demand, inventory position
- ❌ End-customer demand (except retailer)
- ❌ System-wide state

This is **radical information asymmetry** — each agent makes decisions affecting the entire chain based on ≈12.5% of the system state.

### Experimental Results: Information Sharing Impact

We implemented three information modes and measured the impact:

| Mode | What's Shared | Smart Agents Cost (Step Demand) | Bullwhip (max) |
|------|--------------|---:|---:|
| `none` | Nothing (classic) | 113,312 | 1,832 |
| `adjacent` | Upstream + downstream neighbor state | **36,435** | **12** |
| Reduction | — | **-67.8%** | **-99.3%** |

**Key findings from experiments (run `examples/info_symmetry_experiment.py`):**

1. **Behavioral agents don't benefit from information sharing.** The Growth-Hacker, Firefighter, and Signal Chaser produce identical results with or without neighbor visibility — they don't look at the information even when it's available. This confirms that the *decision algorithm* matters more than the *data available*.

2. **Smart agents (Stabilizer, AntifragileAdapter) benefit enormously.** With `adjacent` sharing:
   - Cost drops 67-75% across demand patterns
   - Bullwhip drops from 1000× to <12×
   - Service levels improve

3. **The biggest single improvement is upstream visibility.** When an agent can see that its upstream partner has ample stock, it stops over-ordering "just in case." This single signal eliminates the primary bullwhip driver: ordering for safety when supply is already adequate.

4. **Downstream visibility enables pre-emption.** Seeing that a downstream partner has excess inventory → future orders will drop → reduce orders now. This prevents the glut → drought cycle.

### The Akerlof Parallel

Akerlof showed that in markets with asymmetric information, quality degrades until only "lemons" remain. In the Beer Game:

- With asymmetric information, **only panic strategies survive** — agents that don't panic (Custodian) eventually get forced into panic by accumulated backlog
- With symmetric information, **rational strategies dominate** — agents can make informed decisions instead of fearful ones
- The "lemon" in the Beer Game is the **panic order** — it poisons the system, and asymmetric information makes panic inevitable

### Stiglitz's Screening

Stiglitz showed that the uninformed party can create mechanisms to reveal information. The Beer Game equivalent:

- **Price signals** → Order patterns reveal downstream demand (but with distortion)
- **Contracts** → Fixed-quantity agreements would eliminate bullwhip (but lose flexibility)
- **Information sharing** → The direct solution, as our experiments confirm

### Designing for Information Symmetry

| Design Choice | Impact |
|---|---|
| Share end-customer demand with all echelons | Eliminates demand distortion at source |
| Share inventory positions | Enables coordinated replenishment |
| Share pipeline/in-transit quantities | Prevents double-ordering |
| Share capacity constraints | Prevents impossible orders |
| **Real-world parallel** | **VMI (Vendor-Managed Inventory), CPFR, EDI** |

---

## Experiment Agenda: Testing Mental Model Hypotheses

| # | Hypothesis | Experiment | Expected Result | Status |
|---|---|---|---|---|
| 1 | Simplest agent produces lowest bullwhip | Run all agents as 4-of-same; compare bullwhip | PassivePipeline lowest | ✅ Run — see `examples/profile_comparison.py` |
| 2 | One rational agent compensates for 3 irrational | Mix 1 Pipeline + 3 Firefighters; sweep positions | Outcome depends on position (retailer helps most) | 🔲 Next |
| 3 | Information sharing reduces bullwhip more than better agents | Give all agents downstream demand visibility | >40% bullwhip reduction regardless of profile | ✅ **Confirmed: 67-99% reduction** for smart agents |
| 4 | Cost ratio shapes optimal strategy | Sweep holding:backlog from 1:1 to 1:10 | Growth-Hacker improves as backlog cost rises | 🔲 Next |
| 5 | Inversion-designed agent beats all heuristics | Run Inverter agent vs each profile | Inverter within 10% of theoretical minimum cost | ✅ Run — Inverter competitive |
| 6 | Lead time is the biggest lever | Sweep lead time 1-5 with same agents | Bullwhip scales super-linearly with lead time | 🔲 Next |
| 7 | Antifragile agent improves with disruptions | Run with random supply shocks; compare learning curves | Adapter converges faster in volatile environments | 🔲 Next |
| 8 | Behavioral agents can't use information even when given it | Give adjacent info to Growth-Hacker, Firefighter | No improvement — they don't look | ✅ **Confirmed: 0% improvement** |
| 9 | InfoAware agent designed for sharing beats blind agents | Compare InfoAware (adjacent) vs Pipeline (none) | InfoAware with info < Pipeline without | ✅ Confirmed |
