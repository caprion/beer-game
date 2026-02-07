from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class InfoAwareAgent(AgentProtocol):
    """
    Information-Aware Agent — designed specifically to demonstrate the
    value of information symmetry in the supply chain.

    When neighbor information is available (adjacent/full sharing mode),
    this agent incorporates upstream and downstream signals into its
    ordering decision.  When information is NOT available, it falls back
    to a standard order-up-to policy (equivalent to PassivePipeline).

    This agent is the experimental control for testing the hypothesis:
    "Information sharing reduces bullwhip effect."

    Information-sharing behaviors:
      - Sees downstream backlog → pre-emptively orders more
      - Sees downstream excess inventory → reduces order (demand will drop)
      - Sees upstream backlog → moderates order to avoid piling pressure
      - Sees upstream excess → can order normally (supply is safe)

    Mental-model lens:
      - Information Symmetry: Core principle — decisions improve with
        more accurate view of system state.
      - Map ≠ Territory: Expands the "map" toward the real "territory."
      - Second-Order Thinking: Uses neighbor state to think one step ahead.
      - Skin in the Game: Acts as if upstream/downstream costs matter.
    """

    def __init__(
        self,
        target_inventory: int = 12,
        smoothing_alpha: float = 0.3,
        info_weight: float = 0.5,
    ) -> None:
        """
        Args:
            target_inventory: Desired on-hand inventory level.
            smoothing_alpha: Exponential smoothing factor for demand.
            info_weight: How strongly to weight neighbor information
                (0.0 = ignore neighbors, 1.0 = fully weight neighbors).
        """
        self.target_inventory = target_inventory
        self.smoothing_alpha = smoothing_alpha
        self.info_weight = info_weight
        self.smoothed_demand: float | None = None

    def decide_order(self, state: RoleState) -> int:
        demand = state.incoming_order

        # Smooth demand
        if self.smoothed_demand is None:
            self.smoothed_demand = float(demand)
        else:
            self.smoothed_demand = (
                self.smoothing_alpha * demand
                + (1 - self.smoothing_alpha) * self.smoothed_demand
            )

        # Inventory position (accounts for pipeline — avoids double-ordering)
        inventory_position = (
            state.inventory_on_hand
            + state.pipeline_on_order
            - state.backlog
        )

        gap = self.target_inventory - inventory_position
        base_order = self.smoothed_demand + max(-3, min(3, gap))

        # ---------- Information-Sharing Intelligence ----------
        adjustment = 0.0

        if state.downstream_state is not None:
            down = state.downstream_state
            # If downstream has heavy backlog, demand will stay high → prepare
            if down.backlog > 3:
                adjustment += min(3, down.backlog * 0.3)
            # If downstream has excess stock, demand will drop → pull back
            if down.inventory_on_hand > self.target_inventory * 1.5:
                adjustment -= min(3, (down.inventory_on_hand - self.target_inventory) * 0.2)
            # Use downstream's last order as a leading indicator
            if down.last_placed_order > demand * 1.3:
                adjustment += 1  # Downstream is ramping up
            elif down.last_placed_order < demand * 0.7:
                adjustment -= 1  # Downstream is winding down

        if state.upstream_state is not None:
            up = state.upstream_state
            # If upstream has a backlog, moderate — they can't fulfill big orders anyway
            if up.backlog > 2:
                adjustment -= min(2, up.backlog * 0.2)
            # If upstream is flush, we can order freely
            if up.inventory_on_hand > self.target_inventory * 2:
                adjustment += 0.5  # Safe to stock up slightly

        order = int(base_order + adjustment * self.info_weight)
        return max(0, order)
