"""
Profile Comparison — All agents head-to-head
=============================================
Runs every agent type as a homogeneous 4-role team and compares
bullwhip, cost, and service level.   This is the core experiment
for validating the mental models analysis.
"""

from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig
from profiles_beergame.engine.demand_patterns import step_demand
from profiles_beergame.metrics.analytics import (
    compute_bullwhip, summarize_kpis, compute_system_cost,
    compute_service_level, compare_scenarios,
)
from profiles_beergame.agents.random_baseline import RandomBaselineAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.agents.conservative_custodian import ConservativeCustodianAgent
from profiles_beergame.agents.myopic_firefighter import MyopicFirefighterAgent
from profiles_beergame.agents.signal_chaser import SignalChaserAgent
from profiles_beergame.agents.rational_analyst import RationalAnalystAgent
from profiles_beergame.agents.stabilizer import StabilizerAgent
from profiles_beergame.agents.production_smoother import ProductionSmootherAgent
from profiles_beergame.agents.bayesian_updater import BayesianUpdaterAgent
from profiles_beergame.agents.inverter import InverterAgent
from profiles_beergame.agents.antifragile_adapter import AntifragileAdapterAgent


AGENT_FACTORIES = {
    "random_baseline":        lambda: RandomBaselineAgent(low=2, high=8, seed=42),
    "passive_pipeline":       lambda: PassivePipelineAgent(target_inventory=12),
    "aggressive_growth_hacker": lambda: AggressiveGrowthHackerAgent(),
    "conservative_custodian": lambda: ConservativeCustodianAgent(),
    "myopic_firefighter":     lambda: MyopicFirefighterAgent(seed=42),
    "signal_chaser":          lambda: SignalChaserAgent(),
    "rational_analyst":       lambda: RationalAnalystAgent(),
    "stabilizer":             lambda: StabilizerAgent(),
    "production_smoother":    lambda: ProductionSmootherAgent(),
    "bayesian_updater":       lambda: BayesianUpdaterAgent(),
    "inverter":               lambda: InverterAgent(),
    "antifragile_adapter":    lambda: AntifragileAdapterAgent(),
}


def main():
    demand_fn = step_demand(initial=4, final=8, step_period=10)
    config = SimulationConfig(periods=52, random_seed=42)

    results = {}
    for name, factory in AGENT_FACTORIES.items():
        agents = {role: factory() for role in ["retailer", "wholesaler", "distributor", "factory"]}
        runner = SimulationRunner(agents, demand_fn, config)
        results[name] = runner.run()

    # Summary comparison
    comparison = compare_scenarios(results)
    comparison = comparison.sort_values("system_total_cost")

    print("=" * 90)
    print("PROFILE COMPARISON — Homogeneous teams, step demand (4→8 at week 10)")
    print("=" * 90)
    print(comparison.to_string(index=False))

    # Detailed view: best and worst
    best = comparison.iloc[0]["scenario"]
    worst = comparison.iloc[-1]["scenario"]
    print(f"\n🏆 Best:  {best} (cost={comparison.iloc[0]['system_total_cost']:.1f})")
    print(f"💥 Worst: {worst} (cost={comparison.iloc[-1]['system_total_cost']:.1f})")

    # Bullwhip detail for top 3 and bottom 3
    print("\n--- Bullwhip Detail ---")
    for name in list(comparison["scenario"][:3]) + list(comparison["scenario"][-3:]):
        bw = compute_bullwhip(results[name])
        max_bw = bw["bullwhip_factor"].max()
        print(f"  {name:>30s}: max_bullwhip={max_bw:.2f}")


if __name__ == "__main__":
    main()
