from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class AggressiveGrowthHackerAgent(AgentProtocol):
    """
    Aggressive Growth-Hacker profile: Over-orders to avoid stockouts at all costs.
    
    Mindset: Avoid stock-outs at all costs. Overstocking is manageable; running out is catastrophic.
    Strategy: Responds to any demand increase by ordering even more than needed, creating a large safety buffer.
    Impact: Strongly amplifies the bullwhip effect by turning small demand fluctuations into major upstream order surges.
    """
    
    def __init__(
        self, 
        amplification_factor: float = 1.5, 
        safety_buffer: int = 3,
        panic_threshold: int = 2
    ) -> None:
        """
        Args:
            amplification_factor: How much to amplify demand increases (>1.0)
            safety_buffer: Additional units to order as safety stock
            panic_threshold: Inventory level that triggers panic ordering
        """
        self.amplification_factor = amplification_factor
        self.safety_buffer = safety_buffer
        self.panic_threshold = panic_threshold
        self.last_demand = 4  # Track demand changes
    
    def decide_order(self, state: RoleState) -> int:
        current_demand = state.incoming_order
        
        # Calculate demand change and amplify increases
        demand_change = current_demand - self.last_demand
        if demand_change > 0:
            # Amplify demand increases aggressively
            adjusted_demand = current_demand + int(demand_change * self.amplification_factor)
        else:
            # Don't reduce orders as much for demand decreases
            adjusted_demand = current_demand + max(0, int(demand_change * 0.5))
        
        # Add safety buffer
        base_order = adjusted_demand + self.safety_buffer
        
        # Panic ordering if inventory is too low
        total_available = state.inventory_on_hand + state.pipeline_on_order
        if total_available <= self.panic_threshold or state.backlog > 0:
            panic_bonus = max(3, state.backlog * 2)
            base_order += panic_bonus
        
        # Never order less than current demand
        order = max(current_demand, base_order)
        
        self.last_demand = current_demand
        return int(order)
