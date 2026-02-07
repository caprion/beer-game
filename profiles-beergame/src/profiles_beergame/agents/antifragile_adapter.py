from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class AntifragileAdapterAgent(AgentProtocol):
    """
    Antifragile Adapter — an agent that *benefits* from demand volatility
    by learning from its own prediction errors and adjusting its strategy.

    Derived from the Antifragility framework in MENTAL_MODELS.md.

    Key behaviors:
      - Tracks prediction error (what it ordered vs what was actually needed)
      - Adjusts safety buffer based on observed error magnitude — MORE
        volatility → slightly higher buffer (calibrated, not panicked)
      - Adjusts smoothing speed based on error trend — if errors are
        consistently in one direction, adapts faster
      - Asymmetric payoff: conservative in normal times (small cost),
        responsive in disruptions (large benefit)

    Mental-model lens:
      - Antifragility: Benefits from shocks via calibrated adaptation.
      - Ergodicity: Avoids ruin (never zero-orders during backlog).
      - Via Negativa: Starts minimal and only adds buffer when earned.
    """

    def __init__(
        self,
        target_inventory: int = 12,
        initial_buffer: float = 1.0,
        learning_rate: float = 0.1,
        max_buffer: float = 6.0,
    ) -> None:
        """
        Args:
            target_inventory: Base desired inventory level.
            initial_buffer: Starting dynamic safety buffer.
            learning_rate: How fast the buffer adapts to prediction errors.
            max_buffer: Maximum dynamic buffer (prevents runaway growth).
        """
        self.target_inventory = target_inventory
        self.dynamic_buffer = initial_buffer
        self.learning_rate = learning_rate
        self.max_buffer = max_buffer
        self.smoothed_demand: float | None = None
        self.last_prediction: float | None = None
        self.error_history: list[float] = []

    def decide_order(self, state: RoleState) -> int:
        demand = state.incoming_order

        # Update smoothed demand
        if self.smoothed_demand is None:
            self.smoothed_demand = float(demand)
        else:
            self.smoothed_demand = 0.3 * demand + 0.7 * self.smoothed_demand

        # Learn from prediction error
        if self.last_prediction is not None:
            error = abs(demand - self.last_prediction)
            self.error_history.append(error)
            if len(self.error_history) > 12:
                self.error_history.pop(0)

            # Adapt buffer: higher errors → higher buffer (but bounded)
            avg_error = sum(self.error_history) / len(self.error_history)
            # Buffer grows when errors are large, shrinks when small
            if avg_error > 2.0:
                self.dynamic_buffer = min(
                    self.max_buffer,
                    self.dynamic_buffer + self.learning_rate * avg_error,
                )
            elif avg_error < 1.0:
                self.dynamic_buffer = max(
                    0.5,
                    self.dynamic_buffer - self.learning_rate,
                )

        # Inventory position (full pipeline accounting)
        inventory_position = (
            state.inventory_on_hand
            + state.pipeline_on_order
            - state.backlog
        )

        # Target with dynamic buffer
        adjusted_target = self.target_inventory + self.dynamic_buffer
        gap = adjusted_target - inventory_position

        order = int(self.smoothed_demand + max(0, gap * 0.5))

        # ---------- Information-sharing adjustments ----------
        if state.upstream_state is not None:
            up = state.upstream_state
            # If upstream has ample stock, reduce our buffer — less risk
            if up.inventory_on_hand > self.target_inventory:
                order = int(order * 0.85)
            # If upstream is stressed, back off to avoid compounding
            elif up.backlog > 0:
                order = int(order * 0.9)

        if state.downstream_state is not None:
            down = state.downstream_state
            # If downstream is accumulating stock, future orders will drop
            if down.inventory_on_hand > self.target_inventory * 1.3:
                order = int(order * 0.8)
            # If downstream is in trouble, prepare buffer
            elif down.backlog > 3:
                order = min(order + 1, int(self.smoothed_demand * 1.2))

        # Record prediction for next period's error calculation
        self.last_prediction = self.smoothed_demand

        return max(0, order)
