"""
Quickstart — Beer Game Simulation
=================================
Run a minimal simulation, display results and KPIs.
"""

from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.metrics.analytics import compute_bullwhip, summarize_kpis, compute_system_cost


def main():
    agents = {
        "retailer": AggressiveGrowthHackerAgent(amplification_factor=1.5),
        "wholesaler": PassivePipelineAgent(target_inventory=12),
        "distributor": PassivePipelineAgent(target_inventory=12),
        "factory": PassivePipelineAgent(target_inventory=12),
    }

    config = SimulationConfig(periods=30, random_seed=42)
    runner = SimulationRunner(agents, constant_demand(4), config)
    df = runner.run()

    print("=== Simulation Results (last 5 periods) ===")
    print(df.tail(20).to_string(index=False))

    print("\n=== Bullwhip Factors ===")
    print(compute_bullwhip(df).to_string(index=False))

    print("\n=== KPI Summary ===")
    print(summarize_kpis(df).to_string(index=False))

    print(f"\n=== System Total Cost: {compute_system_cost(df):.2f} ===")


if __name__ == "__main__":
    main()
