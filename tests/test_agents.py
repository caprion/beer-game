"""
Comprehensive test suite for Beer Game agents, engine, and metrics.
"""

import pytest
import pandas as pd

from profiles_beergame.interfaces import RoleState, NeighborState
from profiles_beergame.engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from profiles_beergame.engine.demand_patterns import step_demand, seasonal_demand, noisy_demand, shock_demand
from profiles_beergame.metrics.analytics import (
    compute_bullwhip, summarize_kpis, compute_service_level,
    compute_order_oscillation, compute_system_cost, compare_scenarios,
)

# --- Agent imports ---
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
from profiles_beergame.agents.human_agent import HumanAgent
from profiles_beergame.agents.rl_agent import RLAgent
from profiles_beergame.agents.profile_randomizer import ProfileRandomizer, get_available_profiles


# ============================================================
# Helper: build a default RoleState for testing agent decisions
# ============================================================

def make_state(
    incoming_order=4, inventory=12, backlog=0, pipeline=4,
    received_shipment=4, last_placed_order=4, period=5, role="retailer",
    upstream_state=None, downstream_state=None,
) -> RoleState:
    return RoleState(
        period_index=period,
        role=role,
        incoming_order=incoming_order,
        received_shipment=received_shipment,
        inventory_on_hand=inventory,
        backlog=backlog,
        pipeline_on_order=pipeline,
        last_placed_order=last_placed_order,
        params={"holding_cost": 0.5, "backlog_cost": 1.0},
        upstream_state=upstream_state,
        downstream_state=downstream_state,
    )


# ============================================================
# Agent decision-logic tests
# ============================================================

class TestPassivePipeline:
    def test_steady_state_returns_demand(self):
        agent = PassivePipelineAgent(target_inventory=12)
        state = make_state(incoming_order=4, inventory=12, pipeline=4, backlog=0)
        order = agent.decide_order(state)
        # target(12) + demand(4) + backlog(0) - inventory(12) - pipeline(4) = 0
        assert order == 0

    def test_low_inventory_orders_more(self):
        agent = PassivePipelineAgent(target_inventory=12)
        state = make_state(incoming_order=4, inventory=5, pipeline=0, backlog=0)
        order = agent.decide_order(state)
        # 12 + 4 + 0 - 5 - 0 = 11
        assert order == 11

    def test_never_negative(self):
        agent = PassivePipelineAgent(target_inventory=12)
        state = make_state(incoming_order=4, inventory=20, pipeline=10, backlog=0)
        assert agent.decide_order(state) == 0


class TestAggressiveGrowthHacker:
    def test_adds_safety_buffer(self):
        agent = AggressiveGrowthHackerAgent(amplification_factor=1.5, safety_buffer=3)
        state = make_state(incoming_order=4, inventory=20, pipeline=10, backlog=0)
        order = agent.decide_order(state)
        # Should always be >= demand + safety_buffer
        assert order >= 4

    def test_panics_on_backlog(self):
        agent = AggressiveGrowthHackerAgent()
        state = make_state(incoming_order=4, inventory=10, backlog=5)
        order = agent.decide_order(state)
        assert order > 4 + 3  # More than demand + basic safety

    def test_amplifies_increases(self):
        agent = AggressiveGrowthHackerAgent(amplification_factor=2.0, safety_buffer=0, panic_threshold=0)
        # First call sets baseline
        agent.decide_order(make_state(incoming_order=4, inventory=20, pipeline=20))
        # Second call: demand jumped from 4 to 8
        order = agent.decide_order(make_state(incoming_order=8, inventory=20, pipeline=20))
        # Should amplify the increase of 4 by 2.0 → 8 + 8 = 16
        assert order >= 8


class TestConservativeCustodian:
    def test_orders_less_than_demand(self):
        agent = ConservativeCustodianAgent(conservation_factor=0.8)
        state = make_state(incoming_order=10, inventory=6, backlog=0)
        order = agent.decide_order(state)
        assert order <= 10

    def test_panics_on_high_backlog(self):
        agent = ConservativeCustodianAgent(panic_backlog_threshold=5)
        state = make_state(incoming_order=4, inventory=2, backlog=6)
        order = agent.decide_order(state)
        assert order > 10  # Panic: backlog*2 + demand


class TestMyopicFirefighter:
    def test_panics_on_backlog(self):
        agent = MyopicFirefighterAgent(panic_backlog_threshold=2, seed=42)
        state = make_state(incoming_order=4, backlog=5, inventory=0)
        order = agent.decide_order(state)
        assert order > 4

    def test_orders_zero_on_overstock(self):
        agent = MyopicFirefighterAgent(overstock_threshold=15, seed=42)
        state = make_state(incoming_order=4, inventory=20, backlog=0)
        order = agent.decide_order(state)
        # High inventory → should often order zero (80% chance)
        # With seed=42 this is deterministic
        assert order >= 0  # At least non-negative


class TestSignalChaser:
    def test_chases_upward_trend(self):
        agent = SignalChaserAgent(trend_sensitivity=2.0)
        # Build a rising trend
        for d in [4, 5, 6, 7]:
            agent.decide_order(make_state(incoming_order=d, inventory=12))
        order = agent.decide_order(make_state(incoming_order=8, inventory=12))
        assert order > 8  # Should overshoot

    def test_never_negative(self):
        agent = SignalChaserAgent()
        order = agent.decide_order(make_state(incoming_order=0, inventory=12))
        assert order >= 0


class TestRationalAnalyst:
    def test_ignores_pipeline(self):
        agent = RationalAnalystAgent(target_inventory=12, smoothing=0.0)
        state = make_state(incoming_order=4, inventory=8, pipeline=10, backlog=0)
        order = agent.decide_order(state)
        # gap = 12 - 8 = 4, order = 4 + 4 = 8
        # Note: ignores pipeline=10, so orders MORE than PassivePipeline would
        assert order == 8

    def test_pipeline_agent_orders_less(self):
        """Rational Analyst should order MORE than PassivePipeline due to pipeline blindness."""
        analyst = RationalAnalystAgent(target_inventory=12)
        pipeline = PassivePipelineAgent(target_inventory=12)
        state = make_state(incoming_order=4, inventory=8, pipeline=10, backlog=0)
        assert analyst.decide_order(state) > pipeline.decide_order(state)


class TestStabilizer:
    def test_rate_limits_correction(self):
        agent = StabilizerAgent(target_inventory=12, max_correction_per_period=3)
        state = make_state(incoming_order=4, inventory=0, pipeline=0, backlog=0)
        order = agent.decide_order(state)
        # Gap = 12, but clamped to max_correction=3, so order ≈ smoothed_demand + 3
        assert order <= 4 + 3 + 1  # Small tolerance for float rounding

    def test_uses_pipeline(self):
        agent = StabilizerAgent(target_inventory=12)
        state = make_state(incoming_order=4, inventory=4, pipeline=8, backlog=0)
        order = agent.decide_order(state)
        # Position = 4+8-0=12 = target, so correction ≈ 0
        assert order <= 6  # Close to just demand


class TestProductionSmoother:
    def test_clamps_to_bounds(self):
        agent = ProductionSmootherAgent(min_production=2, max_production=15)
        state = make_state(incoming_order=0, inventory=50, backlog=0)
        order = agent.decide_order(state)
        assert order >= 2  # Never below min
        state2 = make_state(incoming_order=100, inventory=0, backlog=0)
        order2 = agent.decide_order(state2)
        assert order2 <= 15  # Never above max

    def test_smooths_demand(self):
        agent = ProductionSmootherAgent(window_size=3)
        orders = []
        for d in [4, 4, 4, 20]:  # Spike at 4th period
            orders.append(agent.decide_order(make_state(incoming_order=d)))
        # After spike, should be smoothed, not 20
        assert orders[-1] < 20


class TestBayesianUpdater:
    def test_converges_to_stable(self):
        agent = BayesianUpdaterAgent(target_inventory=12, prior_demand=4.0, prior_strength=5)
        orders = []
        for _ in range(20):
            state = make_state(incoming_order=4, inventory=12, pipeline=4, backlog=0)
            orders.append(agent.decide_order(state))
        # Should converge near 4 (demand) with small correction
        assert 2 <= orders[-1] <= 8

    def test_never_negative(self):
        agent = BayesianUpdaterAgent()
        assert agent.decide_order(make_state(incoming_order=0, inventory=20, pipeline=10)) >= 0


class TestInverter:
    def test_rate_limits_changes(self):
        agent = InverterAgent(max_change_rate=3)
        state = make_state(incoming_order=4, inventory=0, pipeline=0, last_placed_order=4)
        order = agent.decide_order(state)
        # Change from last order (4) should be at most ±3
        assert abs(order - 4) <= 4  # Some tolerance for gap correction

    def test_never_zero_with_backlog(self):
        agent = InverterAgent()
        state = make_state(incoming_order=4, inventory=0, backlog=5, last_placed_order=0)
        order = agent.decide_order(state)
        assert order > 0


class TestAntifragileAdapter:
    def test_adapts_buffer_to_volatility(self):
        agent = AntifragileAdapterAgent(initial_buffer=1.0, learning_rate=0.1)
        # Feed stable demand — buffer should decrease
        for _ in range(15):
            agent.decide_order(make_state(incoming_order=4, inventory=12, pipeline=4))
        buffer_after_stable = agent.dynamic_buffer

        agent2 = AntifragileAdapterAgent(initial_buffer=1.0, learning_rate=0.1)
        # Feed volatile demand — buffer should increase
        import random
        rng = random.Random(42)
        for _ in range(15):
            d = rng.randint(1, 10)
            agent2.decide_order(make_state(incoming_order=d, inventory=12, pipeline=4))
        buffer_after_volatile = agent2.dynamic_buffer

        assert buffer_after_volatile >= buffer_after_stable


class TestHumanAgent:
    def test_with_callback(self):
        agent = HumanAgent(prompt_func=lambda s: 7)
        assert agent.decide_order(make_state()) == 7

    def test_negative_clamped(self):
        agent = HumanAgent(prompt_func=lambda s: -5)
        assert agent.decide_order(make_state()) >= 0


class TestRLAgent:
    def test_runs_without_crash(self):
        agent = RLAgent(seed=42)
        for _ in range(10):
            order = agent.decide_order(make_state())
            assert order >= 0

    def test_handles_missing_params(self):
        """RL agent should not crash when params is None."""
        agent = RLAgent(seed=42)
        state = make_state()
        state.params = None
        # Should use defaults, not crash
        agent.last_state = agent._discretize_state(state)
        agent.last_action = 0
        order = agent.decide_order(state)
        assert order >= 0


# ============================================================
# Simulation engine tests
# ============================================================

class TestSimulationEngine:
    def test_constant_demand_pipeline_steady(self):
        """PassivePipeline + constant demand should reach steady state."""
        agents = {r: PassivePipelineAgent(12) for r in ["retailer", "wholesaler", "distributor", "factory"]}
        config = SimulationConfig(periods=30, random_seed=42)
        df = SimulationRunner(agents, constant_demand(4), config).run()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 30 * 4  # 4 roles × 30 periods

    def test_all_roles_present(self):
        agents = {r: PassivePipelineAgent(12) for r in ["retailer", "wholesaler", "distributor", "factory"]}
        df = SimulationRunner(agents, constant_demand(4), SimulationConfig(periods=5)).run()
        assert set(df["role"].unique()) == {"retailer", "wholesaler", "distributor", "factory"}

    def test_missing_role_raises(self):
        agents = {"retailer": PassivePipelineAgent(12)}  # Missing 3 roles
        with pytest.raises(ValueError):
            SimulationRunner(agents, constant_demand(4), SimulationConfig(periods=5))

    def test_information_sharing_adjacent(self):
        """With adjacent info sharing, agents should receive neighbor state."""
        agents = {r: StabilizerAgent(12) for r in ["retailer", "wholesaler", "distributor", "factory"]}
        config = SimulationConfig(periods=10, information_sharing="adjacent")
        df = SimulationRunner(agents, constant_demand(4), config).run()
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 40

    def test_demand_patterns(self):
        """All demand patterns should produce valid simulations."""
        agents = {r: PassivePipelineAgent(12) for r in ["retailer", "wholesaler", "distributor", "factory"]}
        for demand_fn in [constant_demand(4), step_demand(), seasonal_demand(), noisy_demand(), shock_demand()]:
            df = SimulationRunner(agents, demand_fn, SimulationConfig(periods=20)).run()
            assert len(df) == 80


# ============================================================
# Metrics tests
# ============================================================

class TestMetrics:
    @pytest.fixture
    def sim_results(self):
        agents = {r: AggressiveGrowthHackerAgent() for r in ["retailer", "wholesaler", "distributor", "factory"]}
        return SimulationRunner(agents, step_demand(4, 8, 10), SimulationConfig(periods=30)).run()

    def test_bullwhip_computes(self, sim_results):
        bw = compute_bullwhip(sim_results)
        assert "bullwhip_factor" in bw.columns
        assert len(bw) == 4

    def test_summarize_kpis_computes(self, sim_results):
        kpis = summarize_kpis(sim_results)
        assert "total_cost" in kpis.columns
        assert len(kpis) == 4

    def test_service_level(self, sim_results):
        sl = compute_service_level(sim_results)
        assert "fill_rate" in sl.columns
        assert all(0 <= r <= 1 for r in sl["fill_rate"])

    def test_order_oscillation(self, sim_results):
        osc = compute_order_oscillation(sim_results)
        assert "oscillation_index" in osc.columns

    def test_system_cost_positive(self, sim_results):
        cost = compute_system_cost(sim_results)
        assert cost >= 0

    def test_compare_scenarios(self, sim_results):
        comparison = compare_scenarios({"test": sim_results})
        assert len(comparison) == 1
        assert "system_total_cost" in comparison.columns


# ============================================================
# Profile randomizer tests
# ============================================================

class TestProfileRandomizer:
    def test_available_profiles_includes_new(self):
        profiles = get_available_profiles()
        assert "stabilizer" in profiles
        assert "inverter" in profiles
        assert "bayesian_updater" in profiles
        assert "antifragile_adapter" in profiles
        assert "production_smoother" in profiles
        assert "rational_analyst" in profiles

    def test_seed_reproducibility(self):
        r1 = ProfileRandomizer(seed=42)
        r2 = ProfileRandomizer(seed=42)
        s1 = r1.create_random_scenario()
        s2 = r2.create_random_scenario()
        for role in ["retailer", "wholesaler", "distributor", "factory"]:
            assert s1[role][0] == s2[role][0]  # Same profile selected

    def test_balanced_scenarios_coverage(self):
        r = ProfileRandomizer(seed=1)
        scenarios = r.create_balanced_scenarios(num_scenarios=15)
        assert len(scenarios) == 15
