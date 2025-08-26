#!/usr/bin/env python3
"""
Simple example demonstrating profile randomization in the Beer Game simulation.
Run this script to see different behavioral profiles in action.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'profiles-beergame', 'src'))

from profiles_beergame import (
    ProfileRandomizer, SimulationRunner, SimulationConfig, 
    constant_demand, compute_bullwhip, create_mixed_scenario
)


def main():
    print("🍺 Beer Game Profile Randomization Demo")
    print("=" * 50)
    
    # Create a random scenario
    print("\n1. Creating a random scenario...")
    randomizer = ProfileRandomizer(seed=42)
    scenario = randomizer.create_random_scenario()
    
    print("Random Agent Assignment:")
    print(randomizer.describe_scenario(scenario))
    
    # Run the simulation
    print("\n2. Running simulation...")
    agents = randomizer.create_agents_dict(scenario)
    config = SimulationConfig(periods=30, random_seed=42)
    runner = SimulationRunner(agents, constant_demand(4), config)
    results = runner.run()
    
    # Analyze results
    print(f"✅ Simulation completed! Generated {len(results)} data points")
    
    bullwhip = compute_bullwhip(results)
    print("\n3. Bullwhip Analysis:")
    for _, row in bullwhip.iterrows():
        print(f"   {row['role'].capitalize()}: {row['bullwhip_factor']:.3f}")
    
    # Compare with a controlled scenario
    print("\n4. Comparing with aggressive vs conservative scenario...")
    aggressive_agents = create_mixed_scenario(
        retailer_profile="aggressive_growth_hacker",
        wholesaler_profile="conservative_custodian",
        distributor_profile="conservative_custodian", 
        factory_profile="passive_pipeline",
        seed=123
    )
    
    runner2 = SimulationRunner(aggressive_agents, constant_demand(4), config)
    results2 = runner2.run()
    bullwhip2 = compute_bullwhip(results2)
    
    print("\nAggressive Retailer + Conservative Upstream:")
    for _, row in bullwhip2.iterrows():
        print(f"   {row['role'].capitalize()}: {row['bullwhip_factor']:.3f}")
    
    # Summary
    print("\n5. Summary:")
    total_bullwhip_random = bullwhip['bullwhip_factor'].sum()
    total_bullwhip_mixed = bullwhip2['bullwhip_factor'].sum()
    
    print(f"   Random scenario total bullwhip: {total_bullwhip_random:.3f}")
    print(f"   Mixed scenario total bullwhip:  {total_bullwhip_mixed:.3f}")
    
    if total_bullwhip_mixed > total_bullwhip_random:
        print("   → Mixed aggressive/conservative created more bullwhip!")
    else:
        print("   → Random scenario created more bullwhip!")
    
    print("\n🎯 Try running this script multiple times with different seeds!")
    print("   Edit the seed parameter in ProfileRandomizer(seed=42) to explore different combinations.")


if __name__ == "__main__":
    main()
