
import pytest
import pandas as pd
from profiles_beergame.engine.simulation import SimulationRunner
from profiles_beergame.engine.simulation import SimulationConfig, constant_demand
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.agents.conservative_custodian import ConservativeCustodianAgent
from profiles_beergame.agents.myopic_firefighter import MyopicFirefighterAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent


def test_simulation_run():
    agents = {
        'retailer': AggressiveGrowthHackerAgent(),
        'wholesaler': AggressiveGrowthHackerAgent(),
        'distributor': AggressiveGrowthHackerAgent(),
        'factory': AggressiveGrowthHackerAgent(),
    }

    config = SimulationConfig(periods=20)
    demand_fn = constant_demand(4)
    game = SimulationRunner(agents_by_role=agents, demand_fn=demand_fn, config=config)

    results = game.run()

    assert isinstance(results, pd.DataFrame)
    assert not results.empty

    print("Results dataframe:")
    print(results.head())
    print(results.columns)

    # Try to reproduce the pivot
    try:
        pivoted = results.pivot(index='t', columns='role', values=['inventory', 'backlog'])
        print("Pivoted dataframe:")
        print(pivoted.head())
        print(pivoted.columns)
    except KeyError as e:
        print(f"KeyError: {e}")

