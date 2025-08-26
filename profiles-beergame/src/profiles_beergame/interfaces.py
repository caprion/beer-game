from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, Optional, Dict


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


class AgentProtocol(Protocol):
    def decide_order(self, state: RoleState) -> int:
        """Return non-negative integer order quantity based on current state."""
        ...


