    ## Product Requirements Document (PRD) — Beer Game Behavioral Profiles

### Overview
The goal is to enable simulations of the Beer Distribution Game with configurable behavioral profiles per supply chain role, to study how combinations of behaviors generate different bullwhip patterns. The system will support automated agents (rule-based profiles) and an optional human-in-the-loop role.

Reference: `transentis/beergame` repository as conceptual inspiration and for workflow style using notebooks ([GitHub repo](https://github.com/transentis/beergame)).

### Goals
- Enable selection of a behavioral profile per role (Retailer, Wholesaler, Distributor, Factory).
- Provide a clear Agent API so each profile is a pluggable agent with deterministic, testable logic.
- Run week-by-week simulations and log state transitions (orders, deliveries, inventory, backlog, costs).
- Visualize bullwhip and other KPIs via notebooks.
- Allow optional human player for any role via interactive input or injected callback.

### Non-Goals
- ~~Building a rich UI/web app in the first iteration.~~ (Done — Streamlit dashboard with 3 tabs)
- Implementing advanced RL agents (may be future work).

### Primary Users
- Educators/facilitators running Beer Game sessions.
- Analysts researching bullwhip dynamics.
- Learners experimenting with behavioral combinations.

### Core Use Cases
1) Run full-automation with chosen profiles for all roles and visualize bullwhip.
2) Mix human player for one role with automated profiles for others.
3) Compare scenarios across parameter sweeps (lead-times, noise, demand patterns).

### Behavioral Profiles (initial set)
- Aggressive Growth-Hacker: amplifies increases in demand, over-orders relative to signals.
- Myopic Firefighter: reacts strongly to backlog/inventory pain with short-term focus.
- Conservative Custodian: prioritizes stability and low variance; orders cautiously.
- Signal Chaser: extrapolates recent demand trends aggressively (momentum following).
- Passive Pipeline: maintains pipeline and inventory targets; minimal changes otherwise.
- Random Baseline: simple stochastic policy for comparison.

NOTE: Final logic details to be transcribed from the "Beer Game - Profiles.docx" document. Each profile will be implemented as deterministic functions with tunable parameters.

### Functional Requirements
- FR1: Agent API exposing `decide_order(state) -> int` where `state` includes current inventory, backlog, pipeline, incoming order, last shipments, period index, role, and optional exogenous info.
- FR2: Simulation engine processes roles in weekly ticks, propagating orders upstream and shipments downstream with lead times.
- FR3: Demand model supports deterministic time series and stochastic processes (e.g., base + noise), configurable per scenario.
- FR4: Costing model computes holding and backlog costs per role.
- FR5: Logging produces a tidy data frame of all flows/states each period.
- FR6: Visualization utilities plot orders, inventory, backlog, shipments, and bullwhip factors.
- FR7: Human-in-the-loop option: on decision step, call a provided callback or prompt to return an order quantity.

### Bullwhip Definition and KPIs
- Bullwhip factor per role: variance(upstream orders) / variance(downstream demand). Compute over steady-state window.
- Additional KPIs: average service level, mean/variance of inventory/backlog, average cost per period, order oscillation index.

### Configurability
- Lead times (order, shipment), initial inventory, pipeline, backlog.
- Profile parameters (aggressiveness, smoothing factors, target levels).
- Demand process parameters.
- Random seeds for reproducibility.

### Data Model (high-level)
- Period log row: {period, role, incoming_order, placed_order, fulfilled_shipment, backlog, inventory, on_order_pipeline, received_shipment, cost_holding, cost_backlog}.

### Acceptance Criteria
- AC1: Can run a 50–100 week simulation with any mix of the initial profiles and produce plots.
- AC2: Bullwhip factor plotted and tabulated for all roles.
- AC3: Swapping a role's profile changes outputs predictably (unit tests for simple cases).
- AC4: Optional human input works for a single role without breaking the engine.

### Open Questions
- Confirm exact profile list, names, and formulas from the DOCX.
- Confirm default costs and lead times.
- Decide whether to bundle Mesa/BPTK or keep a lightweight custom engine initially.


