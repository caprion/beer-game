# Beer Game Behavioral Profiles — Simulation Toolkit

A lightweight, pluggable simulation framework for the Beer Distribution Game that enables experimentation with different behavioral profiles to study bullwhip effects and supply chain dynamics.

## 🎯 Overview

This project implements a configurable simulation of the famous Beer Distribution Game, allowing you to:
- **Experiment with behavioral profiles**: Test different decision-making patterns across supply chain roles
- **Study bullwhip effects**: Observe how small demand changes amplify upstream
- **Mix human and AI agents**: Combine automated agents with human-in-the-loop decision making
- **Analyze supply chain dynamics**: Visualize inventory, orders, backlogs, and costs over time

The simulation supports four supply chain roles (Retailer → Wholesaler → Distributor → Factory) with configurable lead times, costs, and demand patterns.

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git (for cloning)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "Beer Game"
   ```

2. **Create and activate virtual environment**:
   ```bash
   # Windows
python -m venv .venv
.\.venv\Scripts\activate
   
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   cd profiles-beergame
   pip install -r requirements.txt
   ```

4. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

### Running Your First Simulation

1. **Start Jupyter Lab**:
   ```bash
   jupyter lab
   ```

2. **Open the quickstart notebook**:
   Navigate to `notebooks/00_quickstart.ipynb` and run the cells to see a basic simulation with random agents.

## 📁 Project Structure

```
Beer Game/
├── README.md                    # This file
├── docs/                        # Documentation
│   ├── PRD.md                  # Product Requirements Document
│   ├── PROFILES.md             # Behavioral profiles documentation
│   ├── PLAN.md                 # Development plan
│   └── ARCHITECTURE.md         # System architecture
├── profiles-beergame/          # Main Python package
│   ├── src/profiles_beergame/
│   │   ├── interfaces.py       # Agent protocol and state definitions
│   │   ├── engine/
│   │   │   └── simulation.py   # Core simulation engine
│   │   ├── agents/             # Behavioral agent implementations
│   │   │   ├── random_baseline.py
│   │   │   ├── passive_pipeline.py
│   │   │   └── human_agent.py
│   │   ├── metrics/
│   │   │   └── analytics.py    # KPI calculations (bullwhip, costs)
│   │   └── plots/
│   │       └── plotting.py     # Visualization utilities
│   ├── requirements.txt        # Python dependencies
│   └── pyproject.toml         # Package configuration
├── notebooks/                  # Jupyter notebooks for experiments
│   ├── 00_quickstart.ipynb    # Basic usage example
│   ├── 01_profiles_mixture_template.ipynb
│   └── 02_profile_randomization_demo.ipynb  # Profile randomization examples
└── tools/                      # Utility scripts
    └── extract_profiles.py
```

## 🎮 Usage Guide

### Basic Simulation

```python
from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.agents.random_baseline import RandomBaselineAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent

# Create agents for each role
agents = {
    'retailer': RandomBaselineAgent(low=2, high=8, seed=1),
    'wholesaler': PassivePipelineAgent(target_inventory=12),
    'distributor': PassivePipelineAgent(target_inventory=12),
    'factory': RandomBaselineAgent(low=3, high=7, seed=4)
}

# Configure simulation parameters
config = SimulationConfig(
    periods=52,                 # Number of weeks to simulate
    order_lead_time=1,         # Weeks for orders to reach upstream
    shipment_lead_time=2,      # Weeks for shipments to reach downstream
    initial_inventory=12,      # Starting inventory for all roles
    holding_cost=0.5,          # Cost per unit held in inventory
    backlog_cost=1.0,          # Cost per unit of unmet demand
    random_seed=42             # For reproducible results
)

# Run simulation
runner = SimulationRunner(agents, constant_demand(4), config)
results = runner.run()  # Returns pandas DataFrame with detailed logs

print(results.head())
```

### Available Agent Types

#### 1. RandomBaselineAgent
Simple stochastic agent for baseline comparisons:
```python
agent = RandomBaselineAgent(low=0, high=10, seed=42)
```

#### 2. PassivePipelineAgent
Maintains target inventory levels with minimal changes:
```python
agent = PassivePipelineAgent(target_inventory=12)
```

#### 3. AggressiveGrowthHackerAgent
Over-orders to avoid stockouts, amplifies demand signals:
```python
agent = AggressiveGrowthHackerAgent(amplification_factor=1.5, safety_buffer=3)
```

#### 4. ConservativeCustodianAgent
Risk-averse, prefers low inventory even with occasional stockouts:
```python
agent = ConservativeCustodianAgent(conservation_factor=0.8, max_inventory_target=8)
```

#### 5. MyopicFirefighterAgent
Reactive, emotional decision-making with inconsistent approach:
```python
agent = MyopicFirefighterAgent(emotional_volatility=0.3, panic_threshold=3)
```

#### 6. SignalChaserAgent
Extrapolates recent trends aggressively, misinterprets noise as signals:
```python
agent = SignalChaserAgent(trend_sensitivity=2.0, extrapolation_factor=1.8)
```

#### 7. HumanAgent
Enables human-in-the-loop decision making:
```python
# Interactive input
agent = HumanAgent()

# Or with custom callback
def my_decision_logic(state):
    return state.incoming_order + 2  # Simple rule

agent = HumanAgent(prompt_func=my_decision_logic)
```

### Analyzing Results

```python
from profiles_beergame.metrics.analytics import compute_bullwhip, summarize_kpis
from profiles_beergame.plots.plotting import plot_time_series

# Calculate bullwhip effect
bullwhip = compute_bullwhip(results)
print("Bullwhip factors by role:")
print(bullwhip)

# Summarize key performance indicators
kpis = summarize_kpis(results)
print("\nKPI Summary:")
print(kpis)

# Visualize time series
plot_time_series(results)
```

### Demand Patterns

Create custom demand functions:
```python
def step_demand(step_period=20, initial=4, final=8):
    def _demand(t):
        return final if t >= step_period else initial
    return _demand

def seasonal_demand(base=4, amplitude=2, period=12):
    import math
    def _demand(t):
        return int(base + amplitude * math.sin(2 * math.pi * t / period))
    return _demand

# Use in simulation
runner = SimulationRunner(agents, step_demand(20, 4, 8), config)
```

## 🧠 Behavioral Profiles

The system supports various behavioral profiles based on supply chain psychology research:

### Core Profiles
- **Aggressive Growth-Hacker**: Over-orders to avoid stockouts, amplifies demand signals
- **Conservative Custodian**: Risk-averse, prefers low inventory even with occasional stockouts  
- **Myopic Firefighter**: Reactive decision-making, swings between extremes
- **Signal Chaser**: Extrapolates recent trends aggressively
- **Passive Pipeline**: Maintains stable inventory targets with minimal adjustments

### Role-Specific Tendencies
- **Retailer**: Often exhibits "Signal Chaser" behavior, overreacting to sales fluctuations
- **Wholesaler/Distributor**: Tend toward "Passive Pipeline", simply forwarding orders
- **Factory**: May act as "Production Smoother", prioritizing stable manufacturing

See `docs/PROFILES.md` for detailed behavioral descriptions and psychological foundations.

## 🎛️ Configuration Options

### SimulationConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `periods` | 52 | Number of simulation periods (weeks) |
| `order_lead_time` | 1 | Weeks for orders to reach upstream partner |
| `shipment_lead_time` | 2 | Weeks for shipments to reach downstream |
| `initial_inventory` | 12 | Starting inventory for all roles |
| `initial_pipeline` | 4 | Initial orders in transit |
| `holding_cost` | 0.5 | Cost per unit of inventory per period |
| `backlog_cost` | 1.0 | Cost per unit of unmet demand per period |
| `random_seed` | 42 | Seed for reproducible random behavior |

### Agent State Information

Each agent receives a `RoleState` object containing:
- `period_index`: Current simulation week
- `role`: Agent's position in supply chain
- `incoming_order`: Demand received this period
- `received_shipment`: Inventory received this period  
- `inventory_on_hand`: Current available inventory
- `backlog`: Unmet demand from previous periods
- `pipeline_on_order`: Total inventory ordered but not yet received
- `last_placed_order`: Previous period's order quantity

### Profile Randomization System

Create diverse behavioral combinations automatically:

```python
from profiles_beergame.agents.profile_randomizer import ProfileRandomizer, create_random_agents, create_mixed_scenario

# Create completely random scenario
randomizer = ProfileRandomizer(seed=42)
scenario = randomizer.create_random_scenario()
agents = randomizer.create_agents_dict(scenario)

# Or use quick function
agents = create_random_agents(seed=42)

# Create mixed scenarios with specific profiles
agents = create_mixed_scenario(
    retailer_profile="aggressive_growth_hacker",
    wholesaler_profile="conservative_custodian", 
    distributor_profile="passive_pipeline",
    factory_profile=None,  # Random for factory
    seed=123
)

# Run comparative experiments
scenarios = randomizer.create_balanced_scenarios(num_scenarios=10)
for i, scenario in enumerate(scenarios):
    print(f"Scenario {i+1}:")
    print(randomizer.describe_scenario(scenario))
```

## 🔬 Advanced Usage

### Implementing Custom Agents

Create your own behavioral profiles by implementing the `AgentProtocol`:

```python
from profiles_beergame.interfaces import AgentProtocol, RoleState

class MyCustomAgent(AgentProtocol):
    def __init__(self, aggressiveness=1.5, smoothing=0.8):
        self.aggressiveness = aggressiveness
        self.smoothing = smoothing
        self.order_history = []
    
    def decide_order(self, state: RoleState) -> int:
        # Your decision logic here
        base_order = state.incoming_order
        
        # Apply smoothing based on history
        if self.order_history:
            avg_recent = sum(self.order_history[-3:]) / len(self.order_history[-3:])
            base_order = int(self.smoothing * avg_recent + (1-self.smoothing) * base_order)
        
        # Adjust for inventory position
        inventory_gap = max(0, 12 - state.inventory_on_hand - state.pipeline_on_order)
        order = int(base_order + self.aggressiveness * inventory_gap)
        
        self.order_history.append(order)
        return max(0, order)
```

### Batch Experiments

Run multiple scenarios for statistical analysis:

```python
import pandas as pd

def run_experiment(agent_configs, num_runs=10):
    results = []
    for run in range(num_runs):
        agents = {role: agent_class(**config) for role, (agent_class, config) in agent_configs.items()}
        runner = SimulationRunner(agents, constant_demand(4), SimulationConfig(random_seed=run))
        df = runner.run()
        df['run'] = run
        results.append(df)
    return pd.concat(results, ignore_index=True)

# Example: Compare different agent combinations
configs = {
    'retailer': (RandomBaselineAgent, {'low': 2, 'high': 8}),
    'wholesaler': (PassivePipelineAgent, {'target_inventory': 12}),
    'distributor': (PassivePipelineAgent, {'target_inventory': 12}),
    'factory': (RandomBaselineAgent, {'low': 3, 'high': 7})
}

experiment_data = run_experiment(configs, num_runs=20)
```

## 📊 Key Performance Indicators

### Bullwhip Effect
- **Definition**: Variance amplification from downstream to upstream
- **Calculation**: `var(role_orders) / var(retailer_demand)`
- **Interpretation**: Values > 1 indicate demand amplification

### Service Level Metrics
- **Inventory**: Average stock levels and variance
- **Backlog**: Unmet demand frequency and magnitude
- **Costs**: Holding costs vs. shortage costs trade-off

### Order Pattern Analysis
- **Volatility**: Standard deviation of order quantities
- **Oscillation**: Frequency of order direction changes
- **Responsiveness**: Correlation between demand changes and order adjustments

## 🛠️ Development & Extension

### Adding New Profiles

1. Create new agent file in `profiles-beergame/src/profiles_beergame/agents/`
2. Implement `AgentProtocol` interface
3. Add unit tests for decision logic
4. Update documentation

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-profile`
3. Make changes and add tests
4. Submit pull request with detailed description

### Testing

```bash
# Run tests (when implemented)
pytest tests/

# Type checking
mypy src/profiles_beergame/

# Code formatting
black src/profiles_beergame/
```

## 📚 Educational Use

This toolkit is designed for:
- **Supply Chain Management courses**: Demonstrate bullwhip effect and coordination challenges
- **Behavioral Economics research**: Study decision-making under uncertainty
- **Operations Research**: Test inventory policies and optimization strategies
- **Game Theory**: Analyze multi-agent interactions and information asymmetries

### Suggested Exercises

1. **Profile Comparison**: Run same scenario with different agent types, compare bullwhip factors
2. **Mixed Strategies**: Combine human players with AI agents, observe interaction effects
3. **Parameter Sensitivity**: Vary lead times, costs, and demand patterns
4. **Information Sharing**: Modify agents to access upstream/downstream information
5. **Disruption Response**: Introduce supply interruptions or demand shocks

## 🔗 References

- [Original Beer Game (MIT Sloan)](https://en.wikipedia.org/wiki/Beer_distribution_game)
- [Sterman, J.D. (1989). Modeling managerial behavior: Misperceptions of feedback in a dynamic decision making experiment](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.35.3.321)
- [Lee, H.L., Padmanabhan, V., & Whang, S. (1997). The bullwhip effect in supply chains](https://sloan.mit.edu/shared/ods/documents?PublicationDocumentID=4156)

## 📄 License

[Add your license information here]

## 🤝 Support

For questions, issues, or contributions:
- Create an issue on GitHub
- Check the documentation in the `docs/` folder
- Review example notebooks in `notebooks/`

---

*Happy experimenting with supply chain dynamics! 🍺📈*