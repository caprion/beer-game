from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Callable, Optional, Any

from ..interfaces import AgentProtocol, RoleState, NeighborState


@dataclass
class SimulationConfig:
    periods: int = 52
    order_lead_time: int = 1
    shipment_lead_time: int = 2
    initial_inventory: int = 12
    initial_pipeline: int = 4
    holding_cost: float = 0.5
    backlog_cost: float = 1.0
    random_seed: Optional[int] = 42
    # Information sharing: 'none', 'adjacent', 'full'
    # none     = classic beer game (each agent sees only own state)
    # adjacent = each agent sees upstream + downstream neighbor state
    # full     = each agent sees all roles' states
    information_sharing: str = "none"


def constant_demand(value: int) -> Callable[[int], int]:
    def _f(t: int) -> int:
        return value
    return _f


class SimulationRunner:
    def __init__(
        self,
        agents_by_role: Dict[str, AgentProtocol],
        demand_fn: Callable[[int], int],
        config: SimulationConfig,
    ) -> None:
        self.agents = agents_by_role
        self.demand_fn = demand_fn
        self.cfg = config

        self.roles: List[str] = ["retailer", "wholesaler", "distributor", "factory"]
        for role in self.roles:
            if role not in self.agents:
                raise ValueError(f"Missing agent for role {role}")

        # State containers per role
        self.inventory: Dict[str, int] = {r: self.cfg.initial_inventory for r in self.roles}
        self.backlog: Dict[str, int] = {r: 0 for r in self.roles}
        self.pipeline: Dict[str, List[int]] = {r: [self.cfg.initial_pipeline] * self.cfg.order_lead_time for r in self.roles}
        self.incoming_order: Dict[str, int] = {r: 0 for r in self.roles}
        self.received_shipment: Dict[str, int] = {r: 0 for r in self.roles}
        self.last_order: Dict[str, int] = {r: 0 for r in self.roles}

        self.upstream_of: Dict[str, Optional[str]] = {
            "retailer": "wholesaler",
            "wholesaler": "distributor",
            "distributor": "factory",
            "factory": None,
        }

        self.downstream_of: Dict[str, Optional[str]] = {
            "retailer": None,
            "wholesaler": "retailer",
            "distributor": "wholesaler",
            "factory": "distributor",
        }

        # Shipments in transit between roles per lead time
        self.shipment_queues: Dict[str, List[int]] = {
            r: [0] * self.cfg.shipment_lead_time for r in self.roles
        }

        self.log_rows: List[Dict] = []

    def _build_neighbor_state(self, role: str) -> NeighborState:
        """Build a partial state snapshot of a given role for its neighbors."""
        return NeighborState(
            role=role,
            inventory_on_hand=self.inventory[role],
            backlog=self.backlog[role],
            last_placed_order=self.last_order[role],
        )

    def _build_state(self, role: str, t: int) -> RoleState:
        upstream_state = None
        downstream_state = None

        if self.cfg.information_sharing in ("adjacent", "full"):
            up = self.upstream_of[role]
            down = self.downstream_of[role]
            if up is not None:
                upstream_state = self._build_neighbor_state(up)
            if down is not None:
                downstream_state = self._build_neighbor_state(down)

        return RoleState(
            period_index=t,
            role=role,
            incoming_order=self.incoming_order[role],
            received_shipment=self.received_shipment[role],
            inventory_on_hand=self.inventory[role],
            backlog=self.backlog[role],
            pipeline_on_order=sum(self.pipeline[role]) if self.pipeline[role] else 0,
            last_placed_order=self.last_order[role],
            params={'holding_cost': self.cfg.holding_cost, 'backlog_cost': self.cfg.backlog_cost},
            upstream_state=upstream_state,
            downstream_state=downstream_state,
        )

    def _record(self, t: int, role: str, placed_order: int, cost_h: float, cost_b: float) -> None:
        self.log_rows.append(
            {
                "t": t,
                "role": role,
                "incoming_order": self.incoming_order[role],
                "placed_order": placed_order,
                "received_shipment": self.received_shipment[role],
                "inventory": self.inventory[role],
                "backlog": self.backlog[role],
                "pipeline": sum(self.pipeline[role]) if self.pipeline[role] else 0,
                "cost_holding": cost_h,
                "cost_backlog": cost_b,
            }
        )

    def run(self) -> Any:
        for t in range(self.cfg.periods):
            # 1) Demand at retailer
            self.incoming_order["retailer"] = self.demand_fn(t)
            # Others receive orders from downstream placed last step after lead time
            # (Handled via pipeline/order queues)

            # 2) Receive shipments (pop queues)
            for role in self.roles:
                queue = self.shipment_queues[role]
                received = queue.pop(0) if queue else 0
                self.received_shipment[role] = received
                queue.append(0)

            # 3) Update inventory/backlog based on received shipment and incoming order
            for role in self.roles:
                self.inventory[role] += self.received_shipment[role]
                demand = self.incoming_order[role] + self.backlog[role]
                shipped = min(self.inventory[role], demand)
                self.inventory[role] -= shipped
                self.backlog[role] = max(0, demand - shipped)

                # Ship what we shipped to downstream's shipment queue (arrives after lead time)
                downstream = self.downstream_of[role]
                if downstream is not None:
                    self.shipment_queues[downstream][-1] += shipped

            # 4) Agents decide orders
            new_orders: Dict[str, int] = {}
            for role in self.roles:
                state = self._build_state(role, t)
                qty = max(0, int(self.agents[role].decide_order(state)))
                new_orders[role] = qty
                self.last_order[role] = qty

            # 5) Push orders upstream (become upstream's incoming order after order lead time)
            for role in self.roles:
                upstream = self.upstream_of[role]
                if upstream is not None:
                    # push into role's own order pipeline
                    if self.pipeline[role]:
                        self.pipeline[role].pop(0)
                    self.pipeline[role].append(new_orders[role])
                    # when order lead time elapses, upstream receives incoming order
                    self.incoming_order[upstream] = self.pipeline[role][0]

            # 6) Factory production fulfillment: factory ships up to inventory
            # (already covered by shipment mechanics; factory incoming order set from distributor)

            # 7) Costs and logging
            for role in self.roles:
                cost_h = self.cfg.holding_cost * max(0, self.inventory[role])
                cost_b = self.cfg.backlog_cost * self.backlog[role]
                self._record(t, role, new_orders[role], cost_h, cost_b)

        try:
            import pandas as pd  # type: ignore
            return pd.DataFrame(self.log_rows)
        except Exception:
            return list(self.log_rows)


