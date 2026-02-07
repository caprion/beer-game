## Architecture

### Package Layout

```
profiles-beergame/
  src/profiles_beergame/
    interfaces.py              # AgentProtocol, RoleState, NeighborState dataclasses
    engine/
      simulation.py            # SimulationRunner, SimulationConfig, constant_demand
      demand_patterns.py       # step_demand, seasonal_demand, noisy_demand, shock_demand
    agents/
      passive_pipeline.py      # Target-inventory gap closer
      stabilizer.py            # Exponential smoothing + rate-limiting (info-aware)
      bayesian_updater.py      # Bayesian demand estimation
      inverter.py              # Munger's Inversion — avoid worst outcomes
      antifragile_adapter.py   # Grows buffer under volatility
      info_aware.py            # Purpose-built for neighbor info sharing
      production_smoother.py   # Rolling average with capacity bounds
      rational_analyst.py      # Smoothed demand, ignores pipeline
      aggressive_growth_hacker.py
      conservative_custodian.py
      myopic_firefighter.py
      signal_chaser.py
      random_baseline.py
      human_agent.py           # Human-in-the-loop via callback
      profile_randomizer.py    # Random scenario generation
      rl_agent.py              # Placeholder for RL (future)
    metrics/
      analytics.py             # compute_bullwhip, summarize_kpis, compute_service_level,
                               # compute_order_oscillation, compute_system_cost, compare_scenarios
    plots/
      plotting.py              # matplotlib/plotly helpers

frontend/
  app.py                       # Streamlit dashboard (3 tabs)
  pages/help.py                # Agent documentation page
  .streamlit/config.toml       # Indian Earth theme config
```

### Key Abstractions

**AgentProtocol** — Any agent implements `decide_order(state: RoleState) -> int`.
The state contains inventory, backlog, pipeline, incoming order, received shipment,
period index, role name, and optionally upstream/downstream neighbor state.

**NeighborState** — When `information_sharing="adjacent"`, each role receives its
neighbor's inventory, backlog, and last placed order via `RoleState.upstream_state`
and `RoleState.downstream_state`.

**SimulationConfig** — Periods, lead times, initial inventory, costs, random seed,
and `information_sharing` mode (`"none"` or `"adjacent"`).

### Simulation Loop (per period)

1. Build `RoleState` for each role (optionally with neighbor info)
2. Call each agent's `decide_order()` to collect placed orders
3. Propagate orders upstream through order lead-time queues
4. Determine shipments from upstream inventories
5. Apply shipment lead times
6. Update inventories, backlogs, costs
7. Log all variables into a structured record

### Demand Patterns

Demand functions are callables `(period: int) -> int`:
- `constant_demand(base)` — same every period
- `step_demand(initial, final, step_period)` — level shift
- `seasonal_demand(base, amplitude, period)` — sinusoidal
- `noisy_demand(base, noise, seed)` — uniform noise
- `shock_demand(base, shock_period, shock_duration, shock_magnitude)` — temporary spike

### Analytics

- **Bullwhip factor:** `Var(placed_orders) / Var(incoming_demand)` per role
- **System cost:** Sum of holding + backlog costs across all roles and periods
- **Service level:** Fill rate (fraction of periods with zero backlog)
- **Order oscillation:** Mean absolute period-over-period order change
- **Scenario comparison:** Runs multiple agent configs, returns ranked DataFrame

### Frontend

Streamlit app with three tabs:
1. **Single Simulation** — configure agents, demand, info sharing per role
2. **Profile Comparison** — homogeneous teams ranked by cost/bullwhip
3. **Info Symmetry Experiment** — No Sharing vs Neighbor Sharing paired comparison

Design system: Indian Earth palette with Libre Baskerville + IBM Plex Sans fonts.
CSS injected via `st.html()`. Base theme in `.streamlit/config.toml`.

### Testing

42 unit tests covering all 13 agents, engine mechanics, demand patterns, analytics,
and information sharing. Run with `python -m pytest tests/ -q`.


