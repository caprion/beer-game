from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class PassivePipelineAgent(AgentProtocol):
    def __init__(self, target_inventory: int = 12) -> None:
        self.target_inventory = target_inventory

    def decide_order(self, state: RoleState) -> int:
        desired = max(0, self.target_inventory + state.incoming_order + state.backlog - (state.inventory_on_hand + state.pipeline_on_order))
        return int(desired)


