from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class RationalAnalystAgent(AgentProtocol):
    """
    Rational By-the-Book Analyst — follows textbook inventory rules but
    systematically ignores pipeline orders, causing double-ordering.

    Mindset: Bases orders on last week's sales plus the gap between current
    and target inventory.  Sounds rational, but ignoring in-transit stock
    means the same demand gets ordered twice: once to replenish and once
    because the pipeline shipment "isn't counted."

    This is the Croson & Donohue (2006) archetype: "rational intentions,
    irrational omission."

    Mental-model lens:
      - Occam: Medium complexity, but the critical variable (pipeline) is
        *missing*, not extra.
      - Inversion: Guarantees double-ordering → guaranteed bullwhip.
      - Map ≠ Territory: Treats visible inventory as total position.
    """

    def __init__(
        self,
        target_inventory: int = 12,
        smoothing: float = 0.0,
    ) -> None:
        """
        Args:
            target_inventory: Desired on-hand inventory level.
            smoothing: Exponential smoothing factor for demand (0 = use raw).
        """
        self.target_inventory = target_inventory
        self.smoothing = smoothing
        self.smoothed_demand: float | None = None

    def decide_order(self, state: RoleState) -> int:
        demand = state.incoming_order

        if self.smoothing > 0 and self.smoothed_demand is not None:
            self.smoothed_demand = (
                self.smoothing * self.smoothed_demand
                + (1 - self.smoothing) * demand
            )
        else:
            self.smoothed_demand = float(demand)

        # Classic textbook formula *without* subtracting pipeline_on_order
        # This is the deliberate flaw: pretend pipeline doesn't exist
        gap = self.target_inventory - state.inventory_on_hand
        order = int(self.smoothed_demand + max(0, gap))
        return max(0, order)
