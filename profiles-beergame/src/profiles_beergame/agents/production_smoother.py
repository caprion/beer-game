from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class ProductionSmootherAgent(AgentProtocol):
    """
    Production Smoother — factory-specific profile that prioritizes steady
    production over chasing demand spikes.

    From PROFILES.md: "Ignores sudden order surges and maintains a
    consistent pace, leading to inventory excesses or shortages."

    This agent uses a rolling average of incoming orders and clamps
    production within a min/max band to avoid costly start-stop cycles.

    Mental-model lens:
      - Occam: Simple — moving average + clamp. Two parameters.
      - Inversion: Avoids the factory's biggest failure (matching erratic
        orders 1:1), but creates a different risk (ignoring real changes).
      - Lindy: Production smoothing has 50+ years of manufacturing evidence.
      - Antifragility: Robust but not antifragile — doesn't learn.
    """

    def __init__(
        self,
        window_size: int = 5,
        min_production: int = 2,
        max_production: int = 15,
    ) -> None:
        """
        Args:
            window_size: Number of periods for rolling average of demand.
            min_production: Floor on production quantity (avoid zero).
            max_production: Ceiling on production (capacity constraint).
        """
        self.window_size = window_size
        self.min_production = min_production
        self.max_production = max_production
        self.order_history: list[int] = []

    def decide_order(self, state: RoleState) -> int:
        self.order_history.append(state.incoming_order)
        if len(self.order_history) > self.window_size:
            self.order_history.pop(0)

        avg_demand = sum(self.order_history) / len(self.order_history)

        # Small backlog correction (gradual, not panic)
        backlog_adj = min(2, state.backlog // 3) if state.backlog > 0 else 0

        production = int(avg_demand + backlog_adj)
        return max(self.min_production, min(self.max_production, production))
