from __future__ import annotations

from typing import Callable, Optional

from ..interfaces import AgentProtocol, RoleState


class HumanAgent(AgentProtocol):
    def __init__(self, prompt_func: Optional[Callable[[RoleState], int]] = None) -> None:
        self.prompt_func = prompt_func

    def decide_order(self, state: RoleState) -> int:
        if self.prompt_func is not None:
            return int(max(0, self.prompt_func(state)))
        try:
            value = int(input(f"Week {state.period_index} [{state.role}] enter order: "))
            return max(0, value)
        except Exception:
            return 0


