from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class StabilizerAgent(AgentProtocol):
    """
    Stabilizer / System Thinker — attempts to dampen the bullwhip effect
    by using exponential smoothing, accounting for pipeline, and
    rate-limiting corrections.

    From PROFILES.md: "Tries to find a stable ordering pattern.  Might
    intentionally place smaller, more consistent orders even when direct
    inputs suggest a large spike, aiming to smooth demand for the
    upstream partner."

    Mental-model lens:
      - Occam: Minimal moving parts — smoothed demand + inventory position.
      - Inversion: Specifically avoids every failure mode identified in
        MENTAL_MODELS.md (no panic, no amplification, no noise chasing).
      - Second-order: Considers impact of own orders on upstream partner.
      - Feedback loops: Designed for gain < 1.0 → convergence.
      - Antifragility: Adapts smoothing to observed variance.
    """

    def __init__(
        self,
        target_inventory: int = 12,
        smoothing_alpha: float = 0.3,
        max_correction_per_period: int = 4,
        adapt_smoothing: bool = True,
    ) -> None:
        """
        Args:
            target_inventory: Long-run desired on-hand inventory.
            smoothing_alpha: Exponential smoothing weight for demand
                (lower = smoother, less reactive).
            max_correction_per_period: Maximum adjustment toward target
                per period — prevents panic jumps.
            adapt_smoothing: If True, widens smoothing when demand
                variance increases (antifragile behavior).
        """
        self.target_inventory = target_inventory
        self.smoothing_alpha = smoothing_alpha
        self.max_correction = max_correction_per_period
        self.adapt_smoothing = adapt_smoothing
        self.smoothed_demand: float | None = None
        self.demand_history: list[int] = []

    def _current_alpha(self) -> float:
        """Optionally adapt smoothing factor based on recent variance."""
        if not self.adapt_smoothing or len(self.demand_history) < 4:
            return self.smoothing_alpha
        recent = self.demand_history[-8:]
        mean = sum(recent) / len(recent)
        variance = sum((x - mean) ** 2 for x in recent) / len(recent)
        # Higher variance → lower alpha (more smoothing)
        if variance > 4:
            return max(0.1, self.smoothing_alpha * 0.6)
        return self.smoothing_alpha

    def decide_order(self, state: RoleState) -> int:
        demand = state.incoming_order
        self.demand_history.append(demand)
        if len(self.demand_history) > 16:
            self.demand_history.pop(0)

        alpha = self._current_alpha()
        if self.smoothed_demand is None:
            self.smoothed_demand = float(demand)
        else:
            self.smoothed_demand = alpha * demand + (1 - alpha) * self.smoothed_demand

        # Inventory position: on-hand + pipeline - backlog
        inventory_position = (
            state.inventory_on_hand
            + state.pipeline_on_order
            - state.backlog
        )

        gap = self.target_inventory - inventory_position

        # Rate-limit the correction to avoid shock orders
        clamped_correction = max(-self.max_correction, min(self.max_correction, gap))

        order = int(self.smoothed_demand + clamped_correction)

        # ---------- Information-sharing adjustments ----------
        # When we can see neighbors, we can make smarter decisions.
        if state.upstream_state is not None:
            up = state.upstream_state
            # If upstream is well-stocked (plenty to ship us), ease off
            if up.inventory_on_hand > self.target_inventory * 1.5:
                order = int(order * 0.75)
            # If upstream is struggling (low stock / has backlog), moderate
            # our order to avoid piling more pressure on them
            elif up.backlog > 0 or up.inventory_on_hand < 3:
                order = int(order * 0.85)

        if state.downstream_state is not None:
            down = state.downstream_state
            # If downstream has excess inventory, they'll order less soon —
            # pre-emptively reduce to avoid future glut
            if down.inventory_on_hand > self.target_inventory * 1.5:
                order = int(order * 0.8)
            # If downstream has a heavy backlog, we should prepare to ship
            # more — slight upward adjustment (but still rate-limited)
            elif down.backlog > self.target_inventory * 0.5:
                order = min(order + 2, int(self.smoothed_demand * 1.3))

        return max(0, order)
