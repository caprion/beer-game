from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class InverterAgent(AgentProtocol):
    """
    The Inverter — applies Munger's Inversion principle at every step.

    Instead of asking "what is the best order?", it asks "what order
    would be worst?" and then picks the opposite.

    Worst-case heuristic: the order that maximizes expected cost variance.
    - Ordering zero when there's a backlog → maximizes backlog cost growth
    - Ordering a huge amount when inventory is high → maximizes holding cost
    - Any order that creates a large *change* from recent average → maximizes
      upstream disruption

    The Inverter avoids all three and picks the "least harmful" order.

    Mental-model lens:
      - Inversion: Core principle — avoid what guarantees failure.
      - Via Negativa: Subtracts harmful behaviors rather than adding clever ones.
      - Ergodicity: Designed to avoid ruin, not maximize average.
    """

    def __init__(
        self,
        target_inventory: int = 12,
        max_change_rate: int = 3,
    ) -> None:
        """
        Args:
            target_inventory: Desired inventory level.
            max_change_rate: Maximum allowed change from last order per period.
                Prevents the shock orders that cause bullwhip.
        """
        self.target_inventory = target_inventory
        self.max_change_rate = max_change_rate

    def decide_order(self, state: RoleState) -> int:
        # What would be worst?
        # 1. Ordering zero when backlog > 0 → avoid
        # 2. Ordering >> demand when inventory is high → avoid
        # 3. Large jump from last order → avoid

        # Ideal: order that moves inventory toward target, smoothly
        inventory_position = (
            state.inventory_on_hand
            + state.pipeline_on_order
            - state.backlog
        )
        gap = self.target_inventory - inventory_position

        # Base order = current demand + fraction of gap
        ideal = state.incoming_order + gap * 0.5

        # Rate-limit: don't jump too far from last order
        last = state.last_placed_order
        clamped = max(last - self.max_change_rate, min(last + self.max_change_rate, ideal))

        # Final guard: never zero unless we genuinely have excess
        if clamped <= 0 and state.backlog > 0:
            clamped = max(1, state.incoming_order)

        return max(0, int(clamped))
