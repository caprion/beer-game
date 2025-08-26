
from __future__ import annotations

import numpy as np

from ..interfaces import AgentProtocol, RoleState


class RLAgent(AgentProtocol):
    """
    A reinforcement learning agent that learns to play the beer game.
    """

    def __init__(
        self,
        learning_rate: float = 0.1,
        discount_factor: float = 0.9,
        exploration_rate: float = 0.1,
        seed: int = 42,
    ) -> None:
        """
        Args:
            learning_rate: The learning rate for the Q-learning algorithm.
            discount_factor: The discount factor for future rewards.
            exploration_rate: The exploration rate for the epsilon-greedy policy.
            seed: The random seed for reproducibility.
        """
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.exploration_rate = exploration_rate
        self.rng = np.random.default_rng(seed)

        # Discretize the state space
        self.inventory_bins = np.linspace(0, 50, 10)
        self.backlog_bins = np.linspace(0, 50, 10)
        self.incoming_order_bins = np.linspace(0, 20, 5)

        # Discretize the action space
        self.actions = np.arange(0, 21, 5)

        # Initialize the Q-table
        self.q_table = np.zeros(
            (
                len(self.inventory_bins) + 1,
                len(self.backlog_bins) + 1,
                len(self.incoming_order_bins) + 1,
                len(self.actions),
            )
        )

        self.last_state = None
        self.last_action = None

    def _discretize_state(self, state: RoleState) -> tuple[int, int, int]:
        """Discretize the continuous state into a discrete state."""
        inventory_bin = np.digitize(state.inventory_on_hand, self.inventory_bins)
        backlog_bin = np.digitize(state.backlog, self.backlog_bins)
        incoming_order_bin = np.digitize(state.incoming_order, self.incoming_order_bins)
        return inventory_bin, backlog_bin, incoming_order_bin

    def decide_order(self, state: RoleState) -> int:
        """Return non-negative integer order quantity based on current state."""
        discretized_state = self._discretize_state(state)

        # Epsilon-greedy policy
        if self.rng.random() < self.exploration_rate:
            action_index = self.rng.integers(len(self.actions))
        else:
            action_index = np.argmax(self.q_table[discretized_state])

        # Get the action
        action = self.actions[action_index]

        # Update the Q-table
        if self.last_state is not None:
            reward = - (state.params['holding_cost'] * state.inventory_on_hand + state.params['backlog_cost'] * state.backlog)
            old_q_value = self.q_table[self.last_state][self.last_action]
            new_q_value = old_q_value + self.learning_rate * (
                reward
                + self.discount_factor * np.max(self.q_table[discretized_state])
                - old_q_value
            )
            self.q_table[self.last_state][self.last_action] = new_q_value

        # Save the last state and action
        self.last_state = discretized_state
        self.last_action = action_index

        return action
