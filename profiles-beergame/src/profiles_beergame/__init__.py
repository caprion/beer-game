"""Beer Game Behavioral Profiles Simulation Toolkit"""

from .agents.random_baseline import RandomBaselineAgent
from .agents.passive_pipeline import PassivePipelineAgent
from .agents.human_agent import HumanAgent
from .agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from .agents.conservative_custodian import ConservativeCustodianAgent
from .agents.myopic_firefighter import MyopicFirefighterAgent
from .agents.signal_chaser import SignalChaserAgent
from .agents.rational_analyst import RationalAnalystAgent
from .agents.stabilizer import StabilizerAgent
from .agents.production_smoother import ProductionSmootherAgent
from .agents.bayesian_updater import BayesianUpdaterAgent
from .agents.inverter import InverterAgent
from .agents.antifragile_adapter import AntifragileAdapterAgent
from .agents.profile_randomizer import ProfileRandomizer, create_random_agents, create_mixed_scenario, get_available_profiles

from .engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from .engine.demand_patterns import (
    step_demand, seasonal_demand, noisy_demand, shock_demand,
)
from .metrics.analytics import compute_bullwhip, summarize_kpis
from .plots.plotting import plot_time_series, plot_bullwhip, plot_costs, plot_order_comparison

__all__ = [
    # Agents — original
    "RandomBaselineAgent",
    "PassivePipelineAgent", 
    "HumanAgent",
    "AggressiveGrowthHackerAgent",
    "ConservativeCustodianAgent",
    "MyopicFirefighterAgent",
    "SignalChaserAgent",
    # Agents — new (from PROFILES.md and mental models)
    "RationalAnalystAgent",
    "StabilizerAgent",
    "ProductionSmootherAgent",
    "BayesianUpdaterAgent",
    "InverterAgent",
    "AntifragileAdapterAgent",
    
    # Randomization
    "ProfileRandomizer",
    "create_random_agents",
    "create_mixed_scenario", 
    "get_available_profiles",
    
    # Simulation
    "SimulationRunner",
    "SimulationConfig",
    "constant_demand",
    "step_demand",
    "seasonal_demand",
    "noisy_demand",
    "shock_demand",
    
    # Analytics
    "compute_bullwhip",
    "summarize_kpis",
    "plot_time_series",
    "plot_bullwhip",
    "plot_costs",
    "plot_order_comparison",
]


