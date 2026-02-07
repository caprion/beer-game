# Beer Game — Supply Chain Simulation Toolkit

An interactive simulation of the Beer Distribution Game for studying bullwhip effects,
information asymmetry, and behavioral decision-making in supply chains.

## What is this

The Beer Distribution Game is a supply chain simulation developed at MIT Sloan. Four roles
(Retailer, Wholesaler, Distributor, Factory) pass orders upstream and shipments downstream,
with delays creating information asymmetry. Small demand changes at retail amplify into
wild swings at the factory — the **bullwhip effect**.

This toolkit lets you:
- Run simulations with 13 different agent profiles (behavioral, analytical, adaptive)
- Compare agents head-to-head on cost, bullwhip, and service level
- Test information sharing modes (classic vs neighbor visibility)
- Explore demand patterns (constant, step, seasonal, noisy, shock)
- Interact via a Streamlit dashboard or Python scripts

## Quick Start

### Prerequisites

- Python 3.10+

### Install

```bash
git clone https://github.com/caprion/beer-game.git
cd beer-game/profiles-beergame
pip install -e .
```

### Run the dashboard

```bash
pip install streamlit plotly
cd beer-game
streamlit run frontend/app.py
```

### Run from Python

```python
from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.agents.stabilizer import StabilizerAgent
from profiles_beergame.agents.signal_chaser import SignalChaserAgent

agents = {
    "retailer": SignalChaserAgent(),
    "wholesaler": StabilizerAgent(),
    "distributor": StabilizerAgent(),
    "factory": StabilizerAgent(),
}

config = SimulationConfig(periods=52, information_sharing="adjacent")
runner = SimulationRunner(agents, constant_demand(4), config)
df = runner.run()

from profiles_beergame.metrics.analytics import compute_bullwhip, compute_system_cost
print(compute_bullwhip(df))
print(f"System cost: {compute_system_cost(df):,.0f}")
```

## Agent Profiles

### Rational / Smart Agents

| Agent | Strategy | Bullwhip |
|-------|----------|----------|
| **Stabilizer** | Exponential smoothing + rate-limiting on order changes. Uses neighbor info when available. | Very low |
| **Bayesian Updater** | Maintains prior belief about demand, updates with evidence each period. | Low |
| **Inverter** (Munger's Inversion) | Identifies worst outcomes and steers away from both. Rate-limits changes. | Very low |
| **Antifragile Adapter** | Tracks prediction errors, grows safety buffer under volatility, shrinks when accurate. | Low (improves under stress) |
| **Info-Aware Agent** | Purpose-built for information sharing — blends own demand with neighbor signals. | Minimal |
| **Passive Pipeline** | Simple target-inventory gap-closing. Stable but not adaptive. | Low-moderate |

### Moderate Agents

| Agent | Strategy | Bullwhip |
|-------|----------|----------|
| **Production Smoother** | Rolling average of recent demand, clamped to capacity bounds. | Low |
| **Rational Analyst** | Smooths demand estimates but ignores pipeline (double-ordering blind spot). | Moderate |

### Behavioral / Bullwhip-Amplifying Agents

| Agent | Strategy | Bullwhip |
|-------|----------|----------|
| **Aggressive Growth-Hacker** | Amplifies demand, large safety buffers, panic on low inventory. | High |
| **Conservative Custodian** | Under-orders consistently, then panic-orders when backlog spikes. | Moderate-high |
| **Myopic Firefighter** | Swings between zero orders and panic orders. Emotional volatility. | Very high |
| **Signal Chaser** | Detects "trends" in noise, extrapolates aggressively. | High |

### Baseline

| Agent | Strategy | Bullwhip |
|-------|----------|----------|
| **Random Baseline** | Uniform random orders. Pure noise. | Unpredictable |

## Information Sharing Modes

- **No Sharing (classic):** Each role sees only its own inventory, backlog, and incoming demand. This is the traditional Beer Game setup.
- **Neighbor Sharing (adjacent):** Each role can see its neighbor's inventory, backlog, and last order. Smart agents (Stabilizer, Antifragile, Info-Aware) use this data. Behavioral agents ignore it.

## Demand Patterns

| Pattern | Description |
|---------|-------------|
| **Constant** | Steady demand every period |
| **Step** | Demand jumps from one level to another at a specific period |
| **Seasonal** | Sinusoidal demand cycle |
| **Noisy** | Constant base with random uniform noise |
| **Shock** | Normal demand with a sudden temporary spike |

## Dashboard

The Streamlit frontend has three tabs:

1. **Single Simulation** — Pick agents per role, configure demand and info sharing, run and view KPIs + charts
2. **Profile Comparison** — Run every agent as a homogeneous team, rank by cost and bullwhip
3. **Info Symmetry Experiment** — Same agents under No Sharing vs Neighbor Sharing, compare outcomes

## Project Structure

```
beer-game/
  frontend/
    app.py                    # Streamlit dashboard (3 tabs)
    pages/help.py             # Agent docs and concepts
    .streamlit/config.toml    # Theme configuration
  profiles-beergame/
    src/profiles_beergame/
      interfaces.py           # AgentProtocol, RoleState, NeighborState
      engine/
        simulation.py         # SimulationRunner, SimulationConfig
        demand_patterns.py    # step, seasonal, noisy, shock generators
      agents/                 # 13 agent implementations
      metrics/analytics.py    # bullwhip, cost, service level, oscillation
      plots/plotting.py       # matplotlib/plotly helpers
  examples/
    quickstart.py             # Basic simulation script
    profile_comparison.py     # Compare all agents
    info_symmetry_experiment.py
  notebooks/                  # Jupyter notebooks
  tests/test_agents.py        # 42 tests
  docs/                       # PRD, profiles, plans, mental models
```

## KPIs

| Metric | Definition |
|--------|-----------|
| **Bullwhip Factor** | `Var(orders) / Var(incoming_demand)` per role. >1 means amplification. |
| **System Total Cost** | Sum of holding + backlog costs across all roles and periods |
| **Fill Rate** | Fraction of periods where demand was fully met |
| **Order Oscillation** | Mean absolute period-over-period order change |

## Tests

```bash
cd beer-game
python -m pytest tests/ -q
# 42 passed
```

## Design

The frontend uses the **Indian Earth** design language:
- **Palette:** Warm cream (#faf6f0), deep earth (#3d2b1f), terracotta (#c2452d), forest green (#1a5c4c)
- **Typography:** Libre Baskerville (headings), IBM Plex Sans (body)
- **Currency:** INR

## Deploy to Streamlit Cloud

1. Push to GitHub: `git push origin main`
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo `caprion/beer-game`
4. Set main file path to `frontend/app.py`
5. App deploys automatically on every push

## References

- [Beer Distribution Game (MIT Sloan)](https://en.wikipedia.org/wiki/Beer_distribution_game)
- Sterman, J.D. (1989). Modeling managerial behavior: Misperceptions of feedback.
- Lee, H.L., Padmanabhan, V., & Whang, S. (1997). The bullwhip effect in supply chains.
- Croson, R. & Donohue, K. (2006). Behavioral causes of the bullwhip effect.
