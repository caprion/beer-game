# Decision-Making Frameworks for Supply Chain Simulation

## Why This Document Exists

The Beer Game simulation is a microcosm of real-world decision-making under uncertainty. This document maps additional decision frameworks beyond behavioral profiles — giving us a richer vocabulary for analyzing what goes wrong, and a principled basis for designing better agents and experiments.

---

## 1. Cynefin Framework (Dave Snowden)

Classifies situations by the relationship between cause and effect.

### Beer Game Through Cynefin

| Domain | Definition | Beer Game Mapping |
|--------|-----------|-------------------|
| **Clear** (Simple) | Cause → effect obvious. Best practice exists. | Constant demand, no delays. PassivePipeline is optimal. Trivial. |
| **Complicated** | Cause → effect discoverable by analysis. Good practice exists. | Standard beer game: delays exist but are known. Optimal base-stock policy is calculable. |
| **Complex** | Cause → effect only visible in retrospect. Emergent patterns. | Beer game with mixed behavioral agents. The bullwhip *emerges* from interactions no single agent intends. |
| **Chaotic** | No cause-effect relationship discoverable. Novel practice needed. | Supply disruptions + emotional agents. MyopicFirefighter pushes the system here. |

### Implication for Agent Design

- **Clear/Complicated domains**: Formula-based agents (PassivePipeline, base-stock) work
- **Complex domain**: Adaptive agents needed (RL, Bayesian) that can probe-sense-respond
- **Chaotic domain**: The priority is to *move out of chaos* — stabilize first, then optimize

> Most Beer Game players think they're in the Complicated domain (solvable with the right formula). They're actually in the Complex domain (emergent system behavior). This mismatch is why formulas like the Growth-Hacker's amplification factor fail.

---

## 2. OODA Loop (John Boyd)

**Observe → Orient → Decide → Act**, then repeat faster than your environment changes.

### Each Agent's OODA Speed and Quality

| Agent | Observe | Orient | Decide | Act | OODA Quality |
|---|---|---|---|---|---|
| **PassivePipeline** | Current state | Target gap calculation | Algebraic | Order the gap | ✅ Clean, fast loop |
| **Growth-Hacker** | Demand change | "It's going up!" | Amplify + buffer | Over-order | ❌ Orientation bias contaminates loop |
| **Custodian** | Demand vs average | "Probably anomaly" | Dismiss | Under-order | ❌ Orientation rejects observations |
| **Firefighter** | Inventory pain | "CRISIS!" | Panic/freeze | Extreme order | ❌ Orientation is emotional, not analytical |
| **Signal Chaser** | Trend in window | "Trend will continue" | Extrapolate | Chase | ❌ Orientation hallucinates signal |
| **RL Agent** | Discretized state | Q-table lookup | ε-greedy | Learned action | ⚠️ Slow learning but improving loop |

### Key OODA Insight

**The "Orient" step is where every failing agent breaks down.** They all observe the same `RoleState`. But their orientation — the mental model they bring to the data — distorts what they decide. Boyd's insight is that the Orient phase is the most dangerous because it's where biases enter silently.

> **Design principle**: An agent's orient phase should be auditable. Can you explain *why* it interprets the data the way it does?

---

## 3. Ergodicity (Ole Peters / Nassim Taleb)

> *"The time average is not the same as the ensemble average."*

### The Ergodicity Problem in the Beer Game

Traditional analysis averages across many runs: "On average, the Growth-Hacker has cost X." But each *individual* run matters because supply chains don't get reset.

| Metric | Ensemble Average (across runs) | Time Average (within one run) |
|---|---|---|
| **Growth-Hacker cost** | Moderate (averages out over many seeds) | **Catastrophic in some runs** — one panic spiral can bankrupt |
| **PassivePipeline cost** | Moderate | **Consistently moderate** — no catastrophic sequences |
| **Firefighter cost** | High average | **Wildly variable** — some runs fine, some disastrous |

### Implication

When choosing an agent for a *real* supply chain (one that can't be "re-run"), you shouldn't pick the one with the best average — you should pick the one that **avoids ruin in any single run.**

This is why the Custodian's spike-dismissal is dangerous: it works *on average*, but in the one run where the spike was real, it causes catastrophic backlog.

> **Experiment**: Track the *worst-case* cost across 100 runs for each agent, not just the mean. The ranking changes dramatically.

---

## 4. Goodhart's Law

> *"When a measure becomes a target, it ceases to be a good measure."*

### Goodhart in the Beer Game

The simulation optimizes `holding_cost + backlog_cost`. But watch what happens when agents "target" these metrics:

| Agent | What It Targets | What Goes Wrong |
|---|---|---|
| **Growth-Hacker** | Minimize backlog at all costs | Holding costs skyrocket; system-wide whip amplifies |
| **Custodian** | Minimize holding cost | Backlog costs spike during panic; delays cascade |
| **Firefighter** | Whatever cost is highest *right now* | Alternates between the two failure modes |

### The Deeper Problem

The real "measure" we care about is **system-wide cost** and **supply chain stability**. But each agent can only see its **local cost**. Optimizing local cost makes global cost worse — this is the fundamental coordination failure.

> **Experiment idea**: Give agents a "system cost" signal (sum of all 4 roles' costs). Does this change behavior? Does it reduce bullwhip? This tests whether Goodhart's Law can be broken with broader visibility.

---

## 5. Lindy Effect

> *"The longer something has survived, the longer it will survive."*

### Applied to Strategies

| Strategy Age | Strategy | Lindy Prediction |
|---|---|---|
| ~70 years | Base-stock / order-up-to (PassivePipeline) | **Will endure.** Used since 1950s, still standard in OR. |
| ~30 years | Trend-following (SignalChaser) | **Moderate.** Works in finance sometimes, not in supply chains. |
| ~5 years | RL for inventory | **Jury out.** Too new to have Lindy evidence. Promising but unproven at scale. |
| ~2 years | LLM-based reasoning | **Very speculative.** No Lindy evidence at all. |

### Implication

**Our baseline agent (PassivePipeline) has the most Lindy credibility.** Any new agent should be benchmarked against it, not against the other behavioral agents. Beating a firefighter is easy; beating a 70-year-old proven policy is the real test.

---

## 6. Via Negativa (Taleb / Subtractive Knowledge)

> *"We know more about what is wrong than what is right."*

### What to Remove from Agent Design

Instead of asking "What should an agent add to its decision?", ask "What should we subtract from the agents that fail?"

| Remove This | From These Agents | Why |
|---|---|---|
| Safety buffer | Growth-Hacker | Adds cost without responding to actual variance |
| Spike dismissal | Custodian | Ignoring data is never reliably safe |
| Emotional volatility | Firefighter | Random noise added to decisions, by definition unexplained |
| Trend extrapolation | Signal Chaser | Assumes persistence of patterns that may be random |
| Panic mode | All except Pipeline, Random | Discontinuous jumps are the primary bullwhip driver |

### The Via Negativa Agent

Take any failing agent. Remove one mechanism at a time. Measure improvement. This gives us a **decomposition of harm**: which component contributes most to bullwhip?

> **Experiment**: For each agent, create variants with one mechanism disabled. Rank mechanisms by harm contribution. This is the experimental version of Occam's Razor.

---

## 7. Skin in the Game

> *"Don't tell me what you think, tell me what you have in your portfolio."*
> — Nassim Taleb

### Who Bears the Consequences?

In the real Beer Game, each player bears only their own costs. But their ordering decisions inflict costs on the *entire chain*.

| Agent's Order | Who Pays Holding Cost | Who Pays Backlog Cost |
|---|---|---|
| Over-order at Retailer | Retailer (more inventory) | Wholesaler (must produce more, then faces overstock later) |
| Under-order at Distributor | Distributor (saves on holding) | Factory (loses production continuity), Wholesaler (can't fulfill) |
| Panic order anywhere | Everyone upstream (capacity scramble) | Everyone downstream when correction hits |

### The Moral Hazard

Agents that over-order (Growth-Hacker) externalize costs upstream. Agents that under-order (Custodian) externalize costs downstream. **No agent bears the full system cost of its decisions.**

> **Experiment**: Implement a "shared cost" mode where each agent's reward includes 25% of each other role's cost. Does this reduce bullwhip? This directly tests whether skin-in-the-game improves system outcomes.

---

## 8. Comparative Advantage (Ricardo)

### Each Agent's Comparative Advantage

Not every agent is equally bad everywhere. Some are better suited to specific roles:

| Agent | Best Role | Worst Role | Why |
|---|---|---|---|
| **PassivePipeline** | Any (esp. middle) | None | Universally stable |
| **Growth-Hacker** | Factory | Retailer | At factory, over-production buffers the chain. At retailer, amplifies consumer noise into the chain |
| **Custodian** | Retailer | Factory | At retailer, dampens consumer noise initially. At factory, under-production starves everyone |
| **Signal Chaser** | (None are good) | Retailer | At retailer, every sales fluctuation becomes amplified demand signal upstream |
| **Firefighter** | (None are good) | Distributor | At distributor, emotional swings whipsaw both sides |

> **Experiment**: For each profile, find the role placement that minimizes system cost. This produces a "comparative advantage matrix" — the Beer Game's answer to Ricardo's trade theory.

---

## Summary: Framework Decision Matrix

When analyzing a new agent or scenario, apply these frameworks in order:

| Step | Framework | Question |
|---|---|---|
| 1 | **Occam's Razor** | Is this agent simpler than alternatives with equal performance? |
| 2 | **Inversion** | What would this agent need to do to guarantee failure? Does it do any of those things? |
| 3 | **Circle of Competence** | Does this agent assume things beyond its observable state? |
| 4 | **Second-Order Thinking** | What happens to the *system* when this agent acts? |
| 5 | **Cynefin** | Is this agent matched to the actual complexity domain? |
| 6 | **Ergodicity** | Does this agent avoid ruin in worst-case runs, not just average runs? |
| 7 | **Via Negativa** | Can we remove a component and improve performance? |
| 8 | **Skin in the Game** | Does this agent bear the full cost of its decisions? |
