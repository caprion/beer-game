from __future__ import annotations

import random

from ..interfaces import AgentProtocol, RoleState


class RandomBaselineAgent(AgentProtocol):
    def __init__(self, low: int = 0, high: int = 10, seed: int = 42) -> None:
        self.low = low
        self.high = high
        self._rng = random.Random(seed)

    def decide_order(self, state: RoleState) -> int:
        return self._rng.randint(self.low, self.high)


