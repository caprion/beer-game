"""
Information Symmetry vs Asymmetry Experiment
=============================================
Tests the hypothesis: does giving agents visibility into their neighbors'
positions change the bullwhip effect?

Three modes:
  - none:     Classic beer game — each agent sees only own state
  - adjacent: Each agent sees upstream + downstream neighbor state
  - full:     Each agent sees all roles' states

We run the same agent combinations under all three modes and compare.
"""

from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.engine.demand_patterns import step_demand, seasonal_demand, shock_demand
from profiles_beergame.metrics.analytics import compute_bullwhip, summarize_kpis, compute_service_level, compute_system_cost, compare_scenarios
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent
from profiles_beergame.agents.signal_chaser import SignalChaserAgent
from profiles_beergame.agents.myopic_firefighter import MyopicFirefighterAgent
from profiles_beergame.agents.stabilizer import StabilizerAgent
from profiles_beergame.agents.antifragile_adapter import AntifragileAdapterAgent
from profiles_beergame.agents.info_aware import InfoAwareAgent


def make_agents():
    """A 'realistic' mix: different behavioral profiles per role."""
    return {
        "retailer": SignalChaserAgent(trend_sensitivity=2.0),
        "wholesaler": PassivePipelineAgent(target_inventory=12),
        "distributor": AggressiveGrowthHackerAgent(amplification_factor=1.5),
        "factory": MyopicFirefighterAgent(emotional_volatility=0.3, seed=42),
    }


def make_smart_agents():
    """Mental-model-derived agents that CAN use neighbor info."""
    return {
        "retailer": StabilizerAgent(target_inventory=12),
        "wholesaler": StabilizerAgent(target_inventory=12),
        "distributor": AntifragileAdapterAgent(target_inventory=12),
        "factory": StabilizerAgent(target_inventory=12),
    }


def make_info_aware_agents():
    """Agents purpose-built for information sharing."""
    return {
        "retailer": InfoAwareAgent(target_inventory=12, info_weight=0.7),
        "wholesaler": InfoAwareAgent(target_inventory=12, info_weight=0.7),
        "distributor": InfoAwareAgent(target_inventory=12, info_weight=0.7),
        "factory": InfoAwareAgent(target_inventory=12, info_weight=0.7),
    }


def run_info_experiment(demand_fn, demand_label: str):
    """Run same agents across all 3 information modes and compare."""
    print(f"\n{'='*70}")
    print(f"Demand Pattern: {demand_label}")
    print(f"{'='*70}")

    results = {}

    for agent_label, agent_factory in [
        ("behavioral_mix", make_agents),
        ("smart_agents", make_smart_agents),
        ("info_aware", make_info_aware_agents),
    ]:
        for info_mode in ["none", "adjacent"]:
            label = f"{agent_label}_{info_mode}"
            agents = agent_factory()
            config = SimulationConfig(
                periods=52,
                information_sharing=info_mode,
                random_seed=42,
            )
            runner = SimulationRunner(agents, demand_fn, config)
            df = runner.run()
            results[label] = df

    # Compare all scenarios
    comparison = compare_scenarios(results)
    print("\nScenario Comparison:")
    print(comparison.to_string(index=False))

    # Detailed bullwhip for each
    for label, df in results.items():
        bw = compute_bullwhip(df)
        print(f"\n  {label} — Bullwhip by role:")
        for _, row in bw.iterrows():
            bar = "█" * int(min(20, row["bullwhip_factor"] * 5))
            print(f"    {row['role']:>12s}: {row['bullwhip_factor']:6.2f} {bar}")


if __name__ == "__main__":
    print("=" * 70)
    print("INFORMATION SYMMETRY vs ASYMMETRY EXPERIMENT")
    print("Does visibility into neighbors' positions reduce bullwhip?")
    print("=" * 70)

    # Experiment 1: Constant demand (baseline — should show minimal effect)
    run_info_experiment(constant_demand(4), "Constant (4 units)")

    # Experiment 2: Step demand (the classic bullwhip trigger)
    run_info_experiment(step_demand(initial=4, final=8, step_period=10), "Step (4→8 at week 10)")

    # Experiment 3: Seasonal demand
    run_info_experiment(seasonal_demand(base=4, amplitude=3, period=12), "Seasonal (4±3, period=12)")

    # Experiment 4: Demand shock
    run_info_experiment(shock_demand(base=4, shock_period=15, shock_duration=3, shock_magnitude=12), "Shock (12 units for 3 weeks)")

    print("\n" + "=" * 70)
    print("KEY QUESTION: Do smart agents benefit MORE from information sharing")
    print("than behavioral agents? (Hypothesis: yes, because they USE the info)")
    print("=" * 70)
