from __future__ import annotations

import random
from ..interfaces import AgentProtocol, RoleState


class MyopicFirefighterAgent(AgentProtocol):
    """
    Myopic Firefighter profile: Reactive, emotional decision-making with inconsistent approach.
    
    Mindset: Feels beset by unreliable partners and unpredictable demand and acts reactively.
    Strategy: Swings between zero orders and large, sudden orders based on immediate needs.
    Impact: Introduces volatility and unpredictability, making demand patterns impossible to trace upstream.
    """
    
    def __init__(
        self,
        panic_inventory_threshold: int = 3,
        panic_backlog_threshold: int = 2,
        overstock_threshold: int = 15,
        emotional_volatility: float = 0.3,
        seed: int = 42
    ) -> None:
        """
        Args:
            panic_inventory_threshold: Inventory level that triggers panic
            panic_backlog_threshold: Backlog level that triggers panic
            overstock_threshold: Inventory level that triggers zero orders
            emotional_volatility: Random factor for emotional swings (0-1)
            seed: Random seed for reproducibility
        """
        self.panic_inventory_threshold = panic_inventory_threshold
        self.panic_backlog_threshold = panic_backlog_threshold
        self.overstock_threshold = overstock_threshold
        self.emotional_volatility = emotional_volatility
        self.rng = random.Random(seed)
        self.last_crisis = None  # Track what kind of crisis we're in
        self.crisis_duration = 0
    
    def decide_order(self, state: RoleState) -> int:
        current_demand = state.incoming_order
        
        # Determine current crisis state
        inventory_crisis = (state.inventory_on_hand <= self.panic_inventory_threshold)
        backlog_crisis = (state.backlog >= self.panic_backlog_threshold)
        overstock_crisis = (state.inventory_on_hand >= self.overstock_threshold)
        
        # Track crisis duration for emotional state
        current_crisis = None
        if inventory_crisis or backlog_crisis:
            current_crisis = "shortage"
        elif overstock_crisis:
            current_crisis = "overstock"
        
        if current_crisis == self.last_crisis:
            self.crisis_duration += 1
        else:
            self.crisis_duration = 1
            self.last_crisis = current_crisis
        
        # Emotional volatility factor (more volatile during longer crises)
        emotion_factor = 1.0 + self.emotional_volatility * self.rng.uniform(-1, 1)
        if self.crisis_duration > 3:
            emotion_factor *= 1.5  # More emotional during prolonged crisis
        
        # Reactive decision making based on immediate pain
        if backlog_crisis:
            # PANIC! Order way too much to clear backlog
            panic_order = (state.backlog * 3 + current_demand * 2) * emotion_factor
            return int(max(0, panic_order))
        
        elif inventory_crisis:
            # Shortage panic - order aggressively
            shortage_order = current_demand * 2.5 * emotion_factor
            return int(max(0, shortage_order))
        
        elif overstock_crisis:
            # Too much inventory - swing to zero orders
            # But sometimes emotional volatility makes us order anyway
            if self.rng.random() < 0.2:  # 20% chance to still order despite overstock
                erratic_order = current_demand * emotion_factor
                return int(max(0, erratic_order))
            else:
                return 0  # Zero order due to overstock
        
        else:
            # No immediate crisis, but still erratic
            base_order = current_demand
            
            # Random emotional swings
            if self.rng.random() < 0.3:  # 30% chance of emotional swing
                swing_factor = self.rng.uniform(0.3, 2.0)
                base_order *= swing_factor
            
            # Apply general emotional volatility
            base_order *= emotion_factor
            
            return int(max(0, base_order))
