from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class SignalChaserAgent(AgentProtocol):
    """
    Signal Chaser profile: Extrapolates recent demand trends aggressively (momentum following).
    
    Mindset: Treats every change in sales as a significant trend, aiming to capitalize quickly.
    Strategy: Overreacts to random fluctuations, causing substantial demand amplification upstream.
    Impact: Strongly initiates the bullwhip effect by misinterpreting natural sales variation.
    """
    
    def __init__(
        self,
        trend_sensitivity: float = 2.0,
        momentum_window: int = 3,
        extrapolation_factor: float = 1.8,
        min_trend_threshold: int = 1
    ) -> None:
        """
        Args:
            trend_sensitivity: How strongly to react to detected trends
            momentum_window: Number of periods to analyze for trends
            extrapolation_factor: How far to extrapolate trends into the future
            min_trend_threshold: Minimum change to consider a trend
        """
        self.trend_sensitivity = trend_sensitivity
        self.momentum_window = momentum_window
        self.extrapolation_factor = extrapolation_factor
        self.min_trend_threshold = min_trend_threshold
        self.demand_history = []
    
    def decide_order(self, state: RoleState) -> int:
        current_demand = state.incoming_order
        self.demand_history.append(current_demand)
        
        # Keep only the window we need for trend analysis
        if len(self.demand_history) > self.momentum_window + 2:
            self.demand_history.pop(0)
        
        # Need at least 2 periods to detect trends
        if len(self.demand_history) < 2:
            return current_demand
        
        # Detect trend over momentum window
        if len(self.demand_history) >= self.momentum_window:
            recent_values = self.demand_history[-self.momentum_window:]
            older_values = self.demand_history[-self.momentum_window-1:-1]
            
            recent_avg = sum(recent_values) / len(recent_values)
            older_avg = sum(older_values) / len(older_values) if older_values else recent_avg
            
            trend = recent_avg - older_avg
        else:
            # Simple trend for shorter history
            trend = self.demand_history[-1] - self.demand_history[-2]
        
        # Only react to significant trends
        if abs(trend) < self.min_trend_threshold:
            trend = 0
        
        # Extrapolate the trend aggressively
        if trend > 0:
            # Upward trend - chase it aggressively
            projected_demand = current_demand + (trend * self.extrapolation_factor * self.trend_sensitivity)
            
            # Add extra buffer for "not missing the boom"
            boom_buffer = max(2, int(trend * 2))
            order = projected_demand + boom_buffer
            
        elif trend < 0:
            # Downward trend - but still somewhat chase it (fear of continued decline)
            projected_demand = current_demand + (trend * self.extrapolation_factor * 0.7)  # Less aggressive on downtrends
            order = max(current_demand * 0.5, projected_demand)  # Don't go below 50% of current demand
            
        else:
            # No clear trend - but still look for patterns in noise
            if len(self.demand_history) >= 3:
                # Look for acceleration/deceleration
                recent_change = self.demand_history[-1] - self.demand_history[-2]
                previous_change = self.demand_history[-2] - self.demand_history[-3]
                acceleration = recent_change - previous_change
                
                if abs(acceleration) > 0:
                    # Interpret acceleration as a signal
                    order = current_demand + (acceleration * self.trend_sensitivity * 0.5)
                else:
                    order = current_demand
            else:
                order = current_demand
        
        # Signal chasers are optimistic - rarely order less than current demand
        order = max(current_demand, order)
        
        return int(max(0, order))
