import streamlit as st
import pandas as pd
import numpy as np
from profiles_beergame.engine.simulation import SimulationRunner as BeerGame
from profiles_beergame.engine.simulation import SimulationConfig, constant_demand
from profiles_beergame.agents.aggressive_growth_hacker import AggressiveGrowthHackerAgent
from profiles_beergame.agents.conservative_custodian import ConservativeCustodianAgent
from profiles_beergame.agents.myopic_firefighter import MyopicFirefighterAgent
from profiles_beergame.agents.passive_pipeline import PassivePipelineAgent
from profiles_beergame.agents.random_baseline import RandomBaselineAgent
from profiles_beergame.agents.signal_chaser import SignalChaserAgent
from profiles_beergame.agents.profile_randomizer import get_available_profiles

st.title('Beer Game Simulation')

# Add a sidebar for simulation parameters
st.sidebar.title('Simulation Parameters')
num_periods = st.sidebar.slider('Number of periods', 5, 50, 20)

# Create a form for agent selection
st.sidebar.header('Select Agents')

agent_classes = {
    'aggressive_growth_hacker': AggressiveGrowthHackerAgent,
    'conservative_custodian': ConservativeCustodianAgent,
    'myopic_firefighter': MyopicFirefighterAgent,
    'passive_pipeline': PassivePipelineAgent,
    'random_baseline': RandomBaselineAgent,
    'signal_chaser': SignalChaserAgent,
}

available_profiles = get_available_profiles()

retailer_agent_profile = st.sidebar.selectbox('Retailer', available_profiles)
wholesaler_agent_profile = st.sidebar.selectbox('Wholesaler', available_profiles)
distributor_agent_profile = st.sidebar.selectbox('Distributor', available_profiles)
factory_agent_profile = st.sidebar.selectbox('Factory', available_profiles)

# Add a section for customizing agent parameters
st.sidebar.header('Customize Agent Parameters')

agent_params = {}

for role, profile in [
    ('retailer', retailer_agent_profile),
    ('wholesaler', wholesaler_agent_profile),
    ('distributor', distributor_agent_profile),
    ('factory', factory_agent_profile),
]:
    with st.sidebar.expander(f'{role.capitalize()} ({profile})'):
        if profile == 'aggressive_growth_hacker':
            amplification_factor = st.slider('Amplification Factor', 1.0, 3.0, 1.5, key=f'{role}_af')
            safety_buffer = st.slider('Safety Buffer', 0, 10, 3, key=f'{role}_sb')
            panic_threshold = st.slider('Panic Threshold', 0, 10, 2, key=f'{role}_pt')
            agent_params[role] = {
                'amplification_factor': amplification_factor,
                'safety_buffer': safety_buffer,
                'panic_threshold': panic_threshold,
            }
        elif profile == 'conservative_custodian':
            conservation_factor = st.slider('Conservation Factor', 0.5, 1.0, 0.8, key=f'{role}_cf')
            max_inventory_target = st.slider('Max Inventory Target', 5, 20, 8, key=f'{role}_mit')
            panic_backlog_threshold = st.slider('Panic Backlog Threshold', 3, 10, 5, key=f'{role}_pbt')
            agent_params[role] = {
                'conservation_factor': conservation_factor,
                'max_inventory_target': max_inventory_target,
                'panic_backlog_threshold': panic_backlog_threshold,
            }
        elif profile == 'myopic_firefighter':
            panic_inventory_threshold = st.slider('Panic Inventory Threshold', 1, 10, 3, key=f'{role}_pit')
            panic_backlog_threshold = st.slider('Panic Backlog Threshold', 1, 10, 2, key=f'{role}_pbt2')
            overstock_threshold = st.slider('Overstock Threshold', 10, 30, 15, key=f'{role}_ot')
            emotional_volatility = st.slider('Emotional Volatility', 0.0, 1.0, 0.3, key=f'{role}_ev')
            seed = st.number_input('Seed', value=42, key=f'{role}_seed')
            agent_params[role] = {
                'panic_inventory_threshold': panic_inventory_threshold,
                'panic_backlog_threshold': panic_backlog_threshold,
                'overstock_threshold': overstock_threshold,
                'emotional_volatility': emotional_volatility,
                'seed': seed,
            }
        elif profile == 'passive_pipeline':
            target_inventory = st.slider('Target Inventory', 5, 20, 12, key=f'{role}_ti')
            agent_params[role] = {'target_inventory': target_inventory}
        elif profile == 'random_baseline':
            low = st.slider('Low', 0, 5, 0, key=f'{role}_low')
            high = st.slider('High', 6, 20, 10, key=f'{role}_high')
            seed = st.number_input('Seed', value=42, key=f'{role}_seed2')
            agent_params[role] = {'low': low, 'high': high, 'seed': seed}
        elif profile == 'signal_chaser':
            trend_sensitivity = st.slider('Trend Sensitivity', 1.0, 4.0, 2.0, key=f'{role}_ts')
            momentum_window = st.slider('Momentum Window', 2, 6, 3, key=f'{role}_mw')
            extrapolation_factor = st.slider('Extrapolation Factor', 1.0, 3.0, 1.8, key=f'{role}_ef')
            min_trend_threshold = st.slider('Min Trend Threshold', 0, 5, 1, key=f'{role}_mtt')
            agent_params[role] = {
                'trend_sensitivity': trend_sensitivity,
                'momentum_window': momentum_window,
                'extrapolation_factor': extrapolation_factor,
                'min_trend_threshold': min_trend_threshold,
            }

# Create a button to run the simulation
if st.sidebar.button('Run Simulation'):
    # Create the agents
    agents = {}
    for role, profile in [
        ('retailer', retailer_agent_profile),
        ('wholesaler', wholesaler_agent_profile),
        ('distributor', distributor_agent_profile),
        ('factory', factory_agent_profile),
    ]:
        agent_class = agent_classes[profile]
        params = agent_params.get(role, {})
        agents[role] = agent_class(**params)

    # Create the beer game
    config = SimulationConfig(periods=num_periods)
    demand_fn = constant_demand(4)
    game = BeerGame(agents_by_role=agents, demand_fn=demand_fn, config=config)

    # Run the simulation
    results = game.run()

    # Display the results
    st.header('Results')
    st.dataframe(results)

    # Display a chart of the results
    st.header('Inventory/Backlog')
    pivoted_inventory = results.pivot(index='t', columns='role', values=['inventory', 'backlog'])
    pivoted_inventory.columns = ['_'.join(str(s) for s in col) for col in pivoted_inventory.columns.values]
    st.line_chart(pivoted_inventory)

    st.header('Order History')
    pivoted_orders = results.pivot(index='t', columns='role', values='placed_order')
    st.line_chart(pivoted_orders)