from __future__ import annotations

import random
from typing import Dict, List, Tuple, Type, Any, Optional

from ..interfaces import AgentProtocol
from .random_baseline import RandomBaselineAgent
from .passive_pipeline import PassivePipelineAgent
from .aggressive_growth_hacker import AggressiveGrowthHackerAgent
from .conservative_custodian import ConservativeCustodianAgent
from .myopic_firefighter import MyopicFirefighterAgent
from .signal_chaser import SignalChaserAgent
from .human_agent import HumanAgent
from .rational_analyst import RationalAnalystAgent
from .stabilizer import StabilizerAgent
from .production_smoother import ProductionSmootherAgent
from .bayesian_updater import BayesianUpdaterAgent
from .inverter import InverterAgent
from .antifragile_adapter import AntifragileAdapterAgent


class ProfileRandomizer:
    """
    Utility class for creating randomized agent configurations and running experiments
    with different behavioral profile combinations.
    """
    
    # Define available profiles with their classes and parameter ranges
    PROFILE_CONFIGS = {
        "random_baseline": {
            "class": RandomBaselineAgent,
            "params": {
                "low": (0, 3),
                "high": (6, 12),
                "seed": (1, 1000)
            }
        },
        "passive_pipeline": {
            "class": PassivePipelineAgent,
            "params": {
                "target_inventory": (8, 16)
            }
        },
        "aggressive_growth_hacker": {
            "class": AggressiveGrowthHackerAgent,
            "params": {
                "amplification_factor": (1.2, 2.5),
                "safety_buffer": (1, 8),
                "panic_threshold": (1, 5)
            }
        },
        "conservative_custodian": {
            "class": ConservativeCustodianAgent,
            "params": {
                "conservation_factor": (0.6, 0.9),
                "max_inventory_target": (5, 12),
                "panic_backlog_threshold": (3, 8)
            }
        },
        "myopic_firefighter": {
            "class": MyopicFirefighterAgent,
            "params": {
                "panic_inventory_threshold": (2, 6),
                "panic_backlog_threshold": (1, 4),
                "overstock_threshold": (12, 20),
                "emotional_volatility": (0.1, 0.5),
                "seed": (1, 1000)
            }
        },
        "signal_chaser": {
            "class": SignalChaserAgent,
            "params": {
                "trend_sensitivity": (1.2, 3.0),
                "momentum_window": (2, 5),
                "extrapolation_factor": (1.3, 2.5),
                "min_trend_threshold": (1, 3)
            }
        },
        "rational_analyst": {
            "class": RationalAnalystAgent,
            "params": {
                "target_inventory": (8, 16),
                "smoothing": (0.0, 0.5),
            }
        },
        "stabilizer": {
            "class": StabilizerAgent,
            "params": {
                "target_inventory": (8, 16),
                "smoothing_alpha": (0.1, 0.5),
                "max_correction_per_period": (2, 6),
            }
        },
        "production_smoother": {
            "class": ProductionSmootherAgent,
            "params": {
                "window_size": (3, 8),
                "min_production": (1, 4),
                "max_production": (10, 20),
            }
        },
        "bayesian_updater": {
            "class": BayesianUpdaterAgent,
            "params": {
                "target_inventory": (8, 16),
                "prior_demand": (3.0, 6.0),
                "prior_strength": (3, 10),
            }
        },
        "inverter": {
            "class": InverterAgent,
            "params": {
                "target_inventory": (8, 16),
                "max_change_rate": (2, 5),
            }
        },
        "antifragile_adapter": {
            "class": AntifragileAdapterAgent,
            "params": {
                "target_inventory": (8, 16),
                "initial_buffer": (0.5, 3.0),
                "learning_rate": (0.05, 0.2),
                "max_buffer": (4.0, 8.0),
            }
        },
    }
    
    # Role-specific tendencies (weights for profile selection)
    ROLE_TENDENCIES = {
        "retailer": {
            "signal_chaser": 0.20,
            "aggressive_growth_hacker": 0.15,
            "myopic_firefighter": 0.12,
            "conservative_custodian": 0.08,
            "passive_pipeline": 0.08,
            "rational_analyst": 0.10,
            "stabilizer": 0.08,
            "bayesian_updater": 0.07,
            "inverter": 0.05,
            "antifragile_adapter": 0.04,
            "random_baseline": 0.03,
        },
        "wholesaler": {
            "passive_pipeline": 0.25,
            "conservative_custodian": 0.12,
            "signal_chaser": 0.10,
            "aggressive_growth_hacker": 0.08,
            "myopic_firefighter": 0.07,
            "rational_analyst": 0.10,
            "stabilizer": 0.10,
            "bayesian_updater": 0.07,
            "inverter": 0.05,
            "antifragile_adapter": 0.03,
            "random_baseline": 0.03,
        },
        "distributor": {
            "passive_pipeline": 0.22,
            "conservative_custodian": 0.15,
            "signal_chaser": 0.08,
            "aggressive_growth_hacker": 0.07,
            "myopic_firefighter": 0.06,
            "rational_analyst": 0.10,
            "stabilizer": 0.12,
            "bayesian_updater": 0.08,
            "inverter": 0.05,
            "antifragile_adapter": 0.04,
            "random_baseline": 0.03,
        },
        "factory": {
            "conservative_custodian": 0.15,
            "passive_pipeline": 0.12,
            "aggressive_growth_hacker": 0.10,
            "production_smoother": 0.18,
            "signal_chaser": 0.05,
            "myopic_firefighter": 0.05,
            "rational_analyst": 0.08,
            "stabilizer": 0.10,
            "bayesian_updater": 0.06,
            "inverter": 0.04,
            "antifragile_adapter": 0.04,
            "random_baseline": 0.03,
        },
    }
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize the randomizer with an optional seed for reproducibility."""
        self.rng = random.Random(seed)
    
    def _generate_random_params(self, profile_name: str) -> Dict[str, Any]:
        """Generate random parameters for a given profile within its valid ranges."""
        config = self.PROFILE_CONFIGS[profile_name]
        params = {}
        
        for param_name, param_range in config["params"].items():
            if isinstance(param_range[0], int):
                params[param_name] = self.rng.randint(param_range[0], param_range[1])
            else:
                params[param_name] = self.rng.uniform(param_range[0], param_range[1])
        
        return params
    
    def create_random_agent(self, profile_name: str) -> AgentProtocol:
        """Create a random instance of the specified profile."""
        if profile_name not in self.PROFILE_CONFIGS:
            raise ValueError(f"Unknown profile: {profile_name}. Available: {list(self.PROFILE_CONFIGS.keys())}")
        
        config = self.PROFILE_CONFIGS[profile_name]
        params = self._generate_random_params(profile_name)
        
        return config["class"](**params)
    
    def create_role_appropriate_agent(self, role: str) -> Tuple[str, AgentProtocol]:
        """Create an agent with a profile that's appropriate for the given role."""
        if role not in self.ROLE_TENDENCIES:
            raise ValueError(f"Unknown role: {role}. Available: {list(self.ROLE_TENDENCIES.keys())}")
        
        # Weighted random selection based on role tendencies
        profiles = list(self.ROLE_TENDENCIES[role].keys())
        weights = list(self.ROLE_TENDENCIES[role].values())
        
        selected_profile = self.rng.choices(profiles, weights=weights)[0]
        agent = self.create_random_agent(selected_profile)
        
        return selected_profile, agent
    
    def create_random_scenario(self, allow_human: bool = False) -> Dict[str, Tuple[str, AgentProtocol]]:
        """
        Create a complete random scenario with all four roles assigned.
        
        Args:
            allow_human: If True, may assign human agents to roles
            
        Returns:
            Dictionary mapping role -> (profile_name, agent_instance)
        """
        scenario = {}
        roles = ["retailer", "wholesaler", "distributor", "factory"]
        
        for role in roles:
            if allow_human and self.rng.random() < 0.1:  # 10% chance for human agent
                scenario[role] = ("human", HumanAgent())
            else:
                profile_name, agent = self.create_role_appropriate_agent(role)
                scenario[role] = (profile_name, agent)
        
        return scenario
    
    def create_agents_dict(self, scenario: Dict[str, Tuple[str, AgentProtocol]]) -> Dict[str, AgentProtocol]:
        """Extract just the agents from a scenario for use in SimulationRunner."""
        return {role: agent for role, (profile_name, agent) in scenario.items()}
    
    def create_balanced_scenarios(self, num_scenarios: int = 10) -> List[Dict[str, Tuple[str, AgentProtocol]]]:
        """
        Create multiple scenarios ensuring good coverage of different profile combinations.
        
        Args:
            num_scenarios: Number of scenarios to generate
            
        Returns:
            List of scenario dictionaries
        """
        scenarios = []
        profile_names = list(self.PROFILE_CONFIGS.keys())
        
        # Ensure each profile appears at least once
        for i in range(num_scenarios):
            if i < len(profile_names):
                # Force one specific profile for coverage
                forced_profile = profile_names[i]
                forced_role = self.rng.choice(["retailer", "wholesaler", "distributor", "factory"])
                
                scenario = self.create_random_scenario()
                # Override one role with the forced profile
                scenario[forced_role] = (forced_profile, self.create_random_agent(forced_profile))
            else:
                scenario = self.create_random_scenario()
            
            scenarios.append(scenario)
        
        return scenarios
    
    def describe_scenario(self, scenario: Dict[str, Tuple[str, AgentProtocol]]) -> str:
        """Create a human-readable description of a scenario."""
        description = "Scenario Configuration:\n"
        for role, (profile_name, agent) in scenario.items():
            description += f"  {role.capitalize()}: {profile_name.replace('_', ' ').title()}\n"
            
            # Add parameter details for non-human agents
            if profile_name != "human":
                if hasattr(agent, '__dict__'):
                    params = {k: v for k, v in agent.__dict__.items() 
                             if not k.startswith('_') and not callable(v)}
                    if params:
                        param_str = ", ".join([f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}" 
                                             for k, v in params.items() if k not in ['rng', 'demand_history', 'order_history']])
                        description += f"    Parameters: {param_str}\n"
        
        return description


# Convenience functions for common use cases
def create_random_agents(seed: Optional[int] = None) -> Dict[str, AgentProtocol]:
    """Quick function to create a random set of agents for all roles."""
    randomizer = ProfileRandomizer(seed)
    scenario = randomizer.create_random_scenario()
    return randomizer.create_agents_dict(scenario)


def create_mixed_scenario(
    retailer_profile: Optional[str] = None,
    wholesaler_profile: Optional[str] = None,
    distributor_profile: Optional[str] = None,
    factory_profile: Optional[str] = None,
    seed: Optional[int] = None
) -> Dict[str, AgentProtocol]:
    """
    Create agents with specific profiles for some roles and random for others.
    
    Args:
        *_profile: Specific profile name for each role (None for random)
        seed: Random seed for reproducibility
    """
    randomizer = ProfileRandomizer(seed)
    agents = {}
    
    profiles = {
        "retailer": retailer_profile,
        "wholesaler": wholesaler_profile,
        "distributor": distributor_profile,
        "factory": factory_profile
    }
    
    for role, profile in profiles.items():
        if profile is not None:
            agents[role] = randomizer.create_random_agent(profile)
        else:
            _, agent = randomizer.create_role_appropriate_agent(role)
            agents[role] = agent
    
    return agents


def get_available_profiles() -> List[str]:
    """Get list of all available profile names."""
    return list(ProfileRandomizer.PROFILE_CONFIGS.keys())
