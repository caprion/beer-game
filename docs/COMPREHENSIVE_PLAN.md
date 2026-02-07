# Beer Game Simulation — Comprehensive Analysis & Plan

## Part 0: Notebook Verdict

**The 3 existing notebooks are overkill and should be replaced.**

| Notebook | Content | Verdict |
|----------|---------|---------|
| `00_quickstart.ipynb` | 1 code cell — runs random agents, shows `df.head()` | ❌ A 4-line Python script does this better |
| `01_profiles_mixture_template.ipynb` | 1 code cell — runs random agents, shows `df.tail()` | ❌ Identical to quickstart with different seeds |
| `02_profile_randomization_demo.ipynb` | 12 cells — profile randomizer demo | ⚠️ Has some value but is better as a script + Streamlit page |

**Why notebooks are wrong here:**
- The simulation is stateless — run and done. No iterative exploration needed.
- The frontend (Streamlit) does everything notebooks do, interactively.
- Notebooks can't be unit-tested, linted, or type-checked.
- They rot fast (kernel state, path issues, non-reproducible outputs).

**Recommended replacement:**
- `examples/quickstart.py` — 15-line script showing basic usage
- `examples/profile_comparison.py` — Run all profiles, print KPIs
- `examples/experiment_sweep.py` — Parameter sweep demo
- Keep notebooks only if we add **rich narrative educational content** (not just code cells)

---

## Part 1: What We Have (Current State)

### Project Identity
A **Python simulation toolkit** for the MIT Beer Distribution Game — a classic supply-chain exercise that demonstrates the **bullwhip effect**: how small demand changes at the retail level amplify dramatically upstream through wholesaler, distributor, and factory.

### Architecture
```
┌─────────────────────────────────────────────────────┐
│  Notebooks / Streamlit Frontend                     │
├──────────┬──────────┬──────────┬────────────────────┤
│ Agents   │ Engine   │ Metrics  │ Plots              │
│ (9 types)│ SimRunner│ bullwhip │ time-series         │
│          │ 4-echelon│ KPIs     │                     │
├──────────┴──────────┴──────────┴────────────────────┤
│  Interfaces: AgentProtocol + RoleState              │
└─────────────────────────────────────────────────────┘
```

### What's Working

| Component | Status | Details |
|-----------|--------|---------|
| **Simulation Engine** | ✅ Functional | 4-echelon chain, configurable lead times, costs, demand patterns |
| **Agent Interface** | ✅ Clean | `AgentProtocol` with `decide_order(RoleState) -> int` |
| **7 Behavioral Agents** | ✅ Implemented | Aggressive Growth-Hacker, Conservative Custodian, Myopic Firefighter, Signal Chaser, Passive Pipeline, Random Baseline, Human Agent |
| **RL Agent** | ⚠️ Basic | Tabular Q-learning, 5 discrete actions, learns online |
| **Profile Randomizer** | ✅ Solid | Weighted role-tendencies, balanced scenario generation |
| **Metrics** | ⚠️ Minimal | Bullwhip factor + basic KPIs (avg inventory, backlog, costs) |
| **Plotting** | ⚠️ Minimal | Single time-series chart, not Streamlit-compatible |
| **Streamlit Frontend** | ⚠️ Basic | Profile selection per role, raw results display |
| **Tests** | ❌ Critically lacking | 1 test, 1 agent type, no assertion on correctness |
| **Documentation** | ✅ Good | PRD, Architecture, Profiles with academic references |

### Agent Behavioral Summary

| Agent | Decision Logic | Bullwhip Effect |
|-------|---------------|-----------------|
| **Aggressive Growth-Hacker** | Amplifies demand increases (1.5×), adds safety buffer (3 units), panics on low stock | 🔴 Strong amplifier |
| **Conservative Custodian** | Orders 80% of demand, dismisses spikes, panics when backlog ≥ 5 | 🟡 Dampens then bursts |
| **Myopic Firefighter** | Crisis state-machine (shortage/overstock/calm), emotional volatility | 🔴 Erratic, volatile |
| **Signal Chaser** | Trend extrapolation over sliding window, momentum following | 🔴 Amplifies noise as signal |
| **Passive Pipeline** | Classic order-up-to policy: `target + demand + backlog - (on_hand + pipeline)` | 🟢 Stable, rational baseline |
| **Random Baseline** | `randint(low, high)`, ignores all state | ⚪ Pure noise |
| **Human Agent** | Console input or callback delegation | ⚪ Depends on human |
| **RL Agent** | Tabular Q-learning, ε-greedy, 5 discrete actions {0,5,10,15,20} | 🟢 Learns toward optimal |

---

## Part 2: What's Missing (Gap Analysis)

### Critical Gaps

1. **Testing** — Only 1 test across the entire codebase. No agent decision-logic tests, no metric validation, no edge cases.

2. **Analytics depth** — No service level / fill rate, no total cost aggregation, no demand amplification ratio breakdown, no cross-scenario comparison utilities.

3. **Frontend** — Streamlit app doesn't display KPIs/bullwhip, has no demand pattern customization, no session persistence, no export. Plots call `plt.show()` directly (not Streamlit-compatible).

4. **RL Agent** — Only 5 discrete actions, no continuous action space, no pre-trained policy loading, no training visualization, no integration with frontend/randomizer.

5. **No multiplayer** — Human agent is console-only. No web-based interactive play.

6. **No advanced scenarios** — No supply disruptions, no information-sharing experiments, no multi-chain topologies.

7. **No experiment framework** — No batch run orchestration, no statistical analysis, no result persistence/database.

### Missing Profiles (from PROFILES.md but not implemented)

| Profile | Documented | Implemented |
|---------|-----------|-------------|
| Rational By-the-Book Analyst | ✅ In PROFILES.md | ❌ Not coded |
| Stabilizer / System Thinker | ✅ In PROFILES.md | ❌ Not coded |
| Production Smoother (Factory) | ✅ In PROFILES.md | ❌ Not coded |

---

## Part 3: The Comprehensive Plan

### Phase 0 — Foundation Hardening (Week 1-2)
> *Make what we have reliable*

#### 0.1 Test Suite
- [ ] **Unit tests for all 7 behavioral agents** — Feed known `RoleState`, assert expected order quantities
- [ ] **Simulation engine invariants** — Constant demand + PassivePipeline → steady state; inventory conservation
- [ ] **Metric tests** — Known bullwhip values for deterministic scenarios
- [ ] **ProfileRandomizer tests** — Coverage guarantees, seed reproducibility
- [ ] **Edge cases** — Zero demand, huge demand spikes, negative inventory guards, boundary parameters
- [ ] **CI setup** — pytest + coverage reporting (target ≥ 80%)

#### 0.2 Bug Fixes & Code Quality
- [ ] Fix RL agent `state.params` key dependency (will crash if params not provided)
- [ ] Fix `plotting.py` to return figures instead of calling `plt.show()` (Streamlit compatibility)
- [ ] Add docstrings to PassivePipelineAgent and all `__init__.py` exports
- [ ] Type-check pass with mypy (strict)
- [ ] Linting with ruff/black formatting

#### 0.3 Missing Agents
- [ ] **Rational Analyst Agent** — Order = last_demand + (target_inventory - current_inventory), ignoring pipeline → systematic double-ordering
- [ ] **Stabilizer / System Thinker Agent** — Exponential smoothing, accounts for pipeline, deliberate dampening
- [ ] **Production Smoother Agent** (factory-specific) — Rolling average production, ignores spikes, min/max clamps

---

### Phase 1 — Analytics & Visualization (Week 2-3)
> *Deploy deep insight generation*

#### 1.1 Enhanced Metrics
- [ ] **Service Level** — Fill rate = shipped / (demand + backlog); period-level & aggregate
- [ ] **Total Cost** — Cumulative holding + backlog cost per role and system-wide
- [ ] **Order Oscillation Index** — Frequency of order direction reversals
- [ ] **Demand Amplification Ratio** — Per-role, per-period variance ratios
- [ ] **Inventory Turnover** — Demand served / average inventory
- [ ] **Cash-to-Cash Cycle Proxy** — Pipeline duration × cost rates
- [ ] **Cross-scenario comparison** — Side-by-side KPI DataFrames with statistical tests

#### 1.2 Visualization Library
- [ ] **Bullwhip bar chart** — Variance amplification across roles
- [ ] **Cost waterfall** — Holding vs backlog, stacked per role
- [ ] **Phase-space plots** — Inventory vs backlog trajectories
- [ ] **Heatmaps** — Parameter sensitivity grids (e.g., lead_time × safety_buffer → bullwhip)
- [ ] **Animated supply chain** — Period-by-period flow animation (optional, Plotly/D3)
- [ ] **All charts return Figure objects** — Compatible with Streamlit, Jupyter, and static export

---

### Phase 2 — Frontend Upgrade (Week 3-4)
> *Make it interactive and insightful*

#### 2.1 Streamlit Enhancements
- [ ] **Dashboard layout** — Multi-tab: Setup | Results | KPIs | Compare
- [ ] **Demand pattern selector** — Constant, step, seasonal, custom CSV upload
- [ ] **KPI cards** — Bullwhip factors, total costs, service levels displayed prominently
- [ ] **Interactive charts** — Plotly-based, hover details, zoom
- [ ] **Scenario comparison** — Run N scenarios side-by-side, diff table
- [ ] **Session persistence** — `st.session_state` for results history
- [ ] **Export** — CSV download of results, PNG/PDF of charts
- [ ] **Parameter presets** — "Classic Beer Game", "High Variability", "Long Lead Times"

#### 2.2 Human-in-the-Loop (Web)
- [ ] **Streamlit HumanAgent integration** — Use `st.number_input` per period for human role
- [ ] **Step-through mode** — Advance one period at a time, show state before decision
- [ ] **Decision replay** — After simulation, show what human decided vs what agents would have

---

### Phase 3 — Experiment Framework (Week 4-6)
> *Systematic research infrastructure*

#### 3.1 Batch Runner
- [ ] **Experiment config (YAML/JSON)** — Define scenario grids: profiles × demand_patterns × lead_times × seeds
- [ ] **Parallel execution** — `multiprocessing` or `joblib` for large sweeps
- [ ] **Result persistence** — SQLite/Parquet storage of all run results
- [ ] **Statistical analysis** — Mean, CI, significance tests across runs
- [ ] **Reproducibility** — Full seed control, config hashing, run manifests

#### 3.2 Scenario Library
- [ ] **Classic Beer Game** — Constant demand = 4, standard params, all PassivePipeline
- [ ] **Demand Shock** — Step function at week 5: 4 → 8
- [ ] **Seasonal** — Sinusoidal demand with configurable amplitude/period
- [ ] **Disruption** — Factory shutdown for N weeks, partial capacity reduction
- [ ] **Information Sharing** — Modified agents that receive downstream demand info
- [ ] **Stochastic demand** — Poisson, normal, or mixed distributions

#### 3.3 Tournament Mode
- [ ] **Round-robin** — Every profile combination tested, ranked by total cost
- [ ] **Leaderboard** — Best-performing profiles per role
- [ ] **Custom agent upload** — Users submit agent code, run against standard scenarios

---

### Phase 4 — Advanced AI / RL (Week 6-8)
> *From tabular to modern RL*

#### 4.1 RL Improvements
- [ ] **Continuous action space** — SAC/PPO with Gymnasium wrapper
- [ ] **State normalization** — Proper feature scaling for neural networks
- [ ] **Multi-agent RL** — Independent learners, or centralized-training-decentralized-execution (CTDE)
- [ ] **Curriculum learning** — Train against increasingly complex demand patterns
- [ ] **Pre-trained policies** — Save/load trained models, ship defaults
- [ ] **Training dashboard** — Loss curves, reward tracking, policy visualization

#### 4.2 Gymnasium Environment Wrapper
- [ ] **`BeerGameEnv(gym.Env)`** — Standard Gym interface for single-agent RL
- [ ] **`BeerGameMultiAgentEnv`** — PettingZoo-compatible multi-agent environment
- [ ] **Configurable observation/action spaces** — Continuous vs discrete, information levels
- [ ] **Reward shaping options** — Cost-based, service-level-based, bullwhip-penalty

#### 4.3 LLM Agent (Experimental)
- [ ] **LLM-based decision maker** — Use GPT/Claude to reason about state and place orders
- [ ] **Prompt engineering study** — Which prompting strategies reduce bullwhip?
- [ ] **Hybrid agent** — LLM for strategy, rule-based for execution

---

### Phase 5 — Multi-Player & Educational Platform (Week 8-12)
> *From toolkit to platform*

#### 5.1 Networked Multiplayer
- [ ] **WebSocket game server** — FastAPI + WebSocket for real-time play
- [ ] **Game rooms** — Create/join games with unique codes
- [ ] **Role assignment** — Players pick or get assigned roles
- [ ] **AI backfill** — Empty seats filled by behavioral agents
- [ ] **Live dashboard** — Shared view of supply chain state (configurable visibility)

#### 5.2 Educational Features
- [ ] **Guided exercises** — Step-by-step tutorials with learning objectives
- [ ] **Pre/post assessment** — Measure understanding of bullwhip before and after play
- [ ] **Debrief mode** — After game, reveal all hidden information, show where decisions diverged from optimal
- [ ] **Challenge scenarios** — Progressively harder demand patterns with scoring
- [ ] **Classroom dashboard** — Instructor view of all teams' progress

#### 5.3 Advanced Topologies
- [ ] **N-echelon chains** — Configurable supply chain length (not just 4)
- [ ] **Branching supply chains** — Multiple retailers sharing one wholesaler
- [ ] **Dual sourcing** — Roles can order from multiple upstream partners
- [ ] **Capacity constraints** — Factory production limits, warehouse size limits

---

### Phase 6 — Performance & Portability (Week 12+)
> *Scale and optimize*

#### 6.1 Rust Core (aligns with workspace name `beergame_rust`)
- [ ] **Rust simulation engine** — Port `SimulationRunner` to Rust for 100×+ speedup
- [ ] **PyO3 bindings** — Python API wrapping Rust core
- [ ] **WASM compilation** — Run simulations client-side in the browser
- [ ] **Benchmarks** — Compare Python vs Rust for 10K-run parameter sweeps

#### 6.2 Scalability
- [ ] **Cloud batch runner** — AWS Lambda / Azure Functions for massive parameter sweeps
- [ ] **Result database** — PostgreSQL/TimescaleDB for historical experiment storage
- [ ] **API service** — REST/GraphQL API for running simulations programmatically
- [ ] **Docker deployment** — Containerized Streamlit + API + DB

---

## Part 4: Priority Roadmap

```
Priority  │ Phase                        │ Effort  │ Impact
──────────┼──────────────────────────────┼─────────┼──────────
P0        │ 0: Foundation Hardening      │ 1-2 wk  │ ★★★★★ Reliability
P0        │ 1: Analytics & Visualization │ 1-2 wk  │ ★★★★★ Core value
P1        │ 2: Frontend Upgrade          │ 1-2 wk  │ ★★★★☆ Usability
P1        │ 3: Experiment Framework      │ 2-3 wk  │ ★★★★☆ Research
P2        │ 4: Advanced RL               │ 2-3 wk  │ ★★★☆☆ Innovation
P2        │ 5: Multiplayer & Education   │ 3-4 wk  │ ★★★★☆ Platform
P3        │ 6: Rust Core & Scale         │ 4+ wk   │ ★★★☆☆ Performance
```

---

## Part 5: Quick Wins (Can Start Today)

| # | Task | Time | Files Touched |
|---|------|------|---------------|
| 1 | Fix `plotting.py` to return `Figure` (don't call `.show()`) | 15 min | `plots/plotting.py` |
| 2 | Add bullwhip + KPI display to Streamlit frontend | 30 min | `frontend/app.py` |
| 3 | Write 10 deterministic agent unit tests | 1 hr | `tests/test_agents.py` |
| 4 | Implement Rational Analyst agent | 30 min | `agents/rational_analyst.py` |
| 5 | Implement Stabilizer agent | 30 min | `agents/stabilizer.py` |
| 6 | Add demand pattern selector to frontend | 30 min | `frontend/app.py` |
| 7 | Add cost waterfall chart | 30 min | `plots/plotting.py` |
| 8 | Fix RL agent `params` crash | 10 min | `agents/rl_agent.py` |

---

## Part 6: Research Questions This Platform Can Answer

Once the plan is executed, the platform can explore:

1. **Which behavioral profile combinations minimize system-wide costs?**
2. **How much does information sharing reduce the bullwhip effect?**
3. **Can an RL agent learn to compensate for irrational partners?**
4. **What is the optimal lead-time reduction investment?**
5. **How do supply disruptions propagate differently with different agent mixes?**
6. **Does LLM-based reasoning outperform rule-based agents?**
7. **What training curriculum produces the best RL policy fastest?**
8. **How do multi-retailer topologies change bullwhip dynamics?**
9. **What is the value of a single "system thinker" in a chain of reactive agents?**
10. **Can we replicate real-world company supply chain behaviors using profile combinations?**

---

## Appendix: Related Documentation

| Document | Purpose |
|----------|---------|
| [MENTAL_MODELS.md](MENTAL_MODELS.md) | Occam's Razor, Inversion, Second-Order Thinking, Circle of Competence, Incentives, Map≠Territory, Feedback Loops, Antifragility — applied to every agent |
| [FRAMEWORKS.md](FRAMEWORKS.md) | Cynefin, OODA, Ergodicity, Goodhart's Law, Lindy Effect, Via Negativa, Skin in the Game, Comparative Advantage — with experiment agendas |
| [PROFILES.md](PROFILES.md) | Behavioral profiles with academic references |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and extensibility |
| [PRD.md](PRD.md) | Product requirements and acceptance criteria |

## Appendix: Technology Stack

| Layer | Current | Planned |
|-------|---------|---------|
| Simulation Engine | Python (custom) | Python + Rust (PyO3) |
| Agent Framework | Protocol-based | + Gymnasium, PettingZoo |
| RL | Tabular Q-learning | SAC/PPO (Stable-Baselines3) |
| Analytics | pandas + custom | + scipy.stats, statsmodels |
| Visualization | matplotlib | + Plotly, D3.js |
| Frontend | Streamlit (basic) | Streamlit (full) + FastAPI |
| Multiplayer | None | WebSocket (FastAPI) |
| Storage | None | SQLite → PostgreSQL |
| CI/CD | None | GitHub Actions, pytest, mypy |
| Deployment | Local | Docker, WASM |
