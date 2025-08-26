from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class ConservativeCustodianAgent(AgentProtocol):
    """
    Conservative Custodian profile: Extremely risk-averse, prioritizes minimal inventory.
    
    Mindset: Keep inventory as low as possible, even tolerating minor backlogs.
    Strategy: Consistently orders less than received, dismissing demand spikes as anomalies.
    Impact: Initially dampens demand spikes but eventually places large "panic orders" when shortages occur.
    """
    
    def __init__(
        self,
        conservation_factor: float = 0.8,
        max_inventory_target: int = 8,
        panic_backlog_threshold: int = 5
    ) -> None:
        """
        Args:
            conservation_factor: Fraction of demand to order (< 1.0 for conservative approach)
            max_inventory_target: Maximum desired inventory level
            panic_backlog_threshold: Backlog level that triggers panic ordering
        """
        self.conservation_factor = conservation_factor
        self.max_inventory_target = max_inventory_target
        self.panic_backlog_threshold = panic_backlog_threshold
        self.demand_history = []
        self.spike_count = 0
    
    def decide_order(self, state: RoleState) -> int:
        current_demand = state.incoming_order
        self.demand_history.append(current_demand)
        
        # Keep only recent history
        if len(self.demand_history) > 8:
            self.demand_history.pop(0)
        
        # Calculate average demand to identify spikes
        if len(self.demand_history) >= 3:
            recent_avg = sum(self.demand_history[-3:]) / 3
            overall_avg = sum(self.demand_history) / len(self.demand_history)
            
            # Detect if current demand is a spike
            is_spike = current_demand > overall_avg * 1.3
            if is_spike:
                self.spike_count += 1
            else:
                self.spike_count = max(0, self.spike_count - 1)
        else:
            recent_avg = current_demand
            is_spike = False
        
        # Conservative base order (reduce demand by conservation factor)
        base_order = int(current_demand * self.conservation_factor)
        
        # If we have excess inventory, order even less
        if state.inventory_on_hand > self.max_inventory_target:
            reduction = min(base_order, state.inventory_on_hand - self.max_inventory_target)
            base_order = max(0, base_order - reduction)
        
        # Panic ordering if backlog gets too high
        if state.backlog >= self.panic_backlog_threshold:
            # Large panic order to clear backlog
            panic_order = state.backlog * 2 + current_demand
            return int(panic_order)
        
        # Dismiss demand spikes as anomalies (order based on average instead)
        if is_spike and self.spike_count <= 2:
            if len(self.demand_history) >= 3:
                base_order = int(recent_avg * self.conservation_factor)
        
        return max(0, int(base_order))
