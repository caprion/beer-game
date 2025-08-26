"""Beer Game Behavioral Profiles Simulation Toolkit"""

from .agents.random_baseline import RandomBaselineAgent
from .agents.passive_pipeline import PassivePipelineAgent
from .agents.human_agent import HumanAgent
from .agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from .agents.conservative_custodian import ConservativeCustodianAgent
from .agents.myopic_firefighter import MyopicFirefighterAgent
from .agents.signal_chaser import SignalChaserAgent
from .agents.profile_randomizer import ProfileRandomizer, create_random_agents, create_mixed_scenario, get_available_profiles

from .engine.simulation import SimulationRunner, SimulationConfig, constant_demand
from .metrics.analytics import compute_bullwhip, summarize_kpis
from .plots.plotting import plot_time_series

__all__ = [
    # Agents
    "RandomBaselineAgent",
    "PassivePipelineAgent", 
    "HumanAgent",
    "AggressiveGrowthHackerAgent",
    "ConservativeCustodianAgent",
    "MyopicFirefighterAgent",
    "SignalChaserAgent",
    
    # Randomization
    "ProfileRandomizer",
    "create_random_agents",
    "create_mixed_scenario", 
    "get_available_profiles",
    
    # Simulation
    "SimulationRunner",
    "SimulationConfig",
    "constant_demand",
    
    # Analytics
    "compute_bullwhip",
    "summarize_kpis",
    "plot_time_series",
]


