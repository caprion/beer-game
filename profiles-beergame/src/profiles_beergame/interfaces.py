from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, Optional, Dict


@dataclass
class NeighborState:
    """Partial view of an adjacent supply chain partner's state.

    Used in information-sharing experiments: when visibility is enabled,
    an agent can see inventory and backlog of its upstream/downstream neighbor.
    """
    role: str
    inventory_on_hand: int
    backlog: int
    last_placed_order: int


@dataclass
class RoleState:
    period_index: int
    role: str  # 'retailer' | 'wholesaler' | 'distributor' | 'factory'
    incoming_order: int
    received_shipment: int
    inventory_on_hand: int
    backlog: int
    pipeline_on_order: int
    last_placed_order: int
    params: Optional[Dict[str, float]] = None
    # Information-sharing fields (None when visibility is off)
    upstream_state: Optional[NeighborState] = None
    downstream_state: Optional[NeighborState] = None


class AgentProtocol(Protocol):
    def decide_order(self, state: RoleState) -> int:
        """Return non-negative integer order quantity based on current state."""
        ...


