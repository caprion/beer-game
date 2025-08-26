## Architecture — Beer Game Behavioral Profiles

### Overview
Lightweight Python package with: (a) pluggable agents implementing behavioral policies, (b) a small discrete-time simulation engine for the four-echelon chain, (c) metrics and plotting helpers, and (d) notebooks for experiments.

The approach is inspired by `transentis/beergame` which leverages notebooks for analysis ([GitHub repo](https://github.com/transentis/beergame)).

### Package Layout
```
profiles-beergame/
  src/profiles_beergame/
    interfaces.py        # AgentProtocol, State/Action dataclasses
    engine/
      simulation.py      # SimulationRunner and core loop
    agents/
      aggressive_growth_hacker.py
      myopic_firefighter.py
      conservative_custodian.py
      signal_chaser.py
      passive_pipeline.py
      human_agent.py
      random_baseline.py
    metrics/analytics.py # bullwhip and KPI calculators
    plots/plotting.py    # matplotlib/plotly helpers
    config/defaults.py   # default params
```

### Key Concepts
- Agent: Implements `decide_order(state) -> int` using only local info.
- State: Inventory, backlog, pipeline, incoming order, received shipment, last actions, period.
- Environment: Routes orders upstream and shipments downstream with lead times.

### Simulation Loop (per period)
1) For each role, provide current state to its agent. Collect placed orders.
2) Propagate orders to upstream partner queues (subject to order lead time).
3) Determine shipments available from upstream inventories. Apply shipment lead times.
4) Update inventories, backlogs, and costs.
5) Log all variables into a structured record.

### Extensibility
- Add a new profile by adding a new file in `agents/` implementing the protocol.
- Swap demand processes and cost functions via configuration.
- Plug a human via `human_agent.HumanAgent(callback)`.

### Notebooks
- Quickstart: run a single scenario, generate KPIs and plots.
- Mixtures: compare multiple role-profile combinations side-by-side.

### Testing Strategy
- Unit tests for simple deterministic scenarios (e.g., constant demand) to validate invariants.
- Golden tests for profile decisions given a fixed state.


