from __future__ import annotations

from ..interfaces import AgentProtocol, RoleState


class BayesianUpdaterAgent(AgentProtocol):
    """
    Bayesian Updater — maintains a probabilistic demand estimate and
    updates beliefs proportionally to evidence strength.

    Derived from the Circle of Competence + Map ≠ Territory frameworks
    in MENTAL_MODELS.md.

    Key behaviors:
      - Higher confidence → smaller adjustments to new data
      - Lower confidence → more responsive to observations
      - Never panics: corrections are confidence-weighted
      - Accounts for pipeline (inventory position)

    Uses a simple online Bayesian update: the "prior" is the running
    mean/variance of demand, and each new observation shifts the
    estimate proportional to 1/(n+1).
    """

    def __init__(
        self,
        target_inventory: int = 12,
        prior_demand: float = 4.0,
        prior_strength: int = 5,
    ) -> None:
        """
        Args:
            target_inventory: Desired inventory level.
            prior_demand: Initial belief about average demand.
            prior_strength: How many "pseudo-observations" the prior is
                worth.  Higher = slower to change beliefs.
        """
        self.target_inventory = target_inventory
        self.demand_mean = prior_demand
        self.demand_var = 1.0
        self.n = prior_strength  # pseudo-count for prior strength

    def decide_order(self, state: RoleState) -> int:
        obs = state.incoming_order
        self.n += 1

        # Online Bayesian update of demand mean and variance
        old_mean = self.demand_mean
        self.demand_mean += (obs - self.demand_mean) / self.n
        self.demand_var += (obs - old_mean) * (obs - self.demand_mean) - self.demand_var / self.n

        # Inventory position (includes pipeline, unlike Rational Analyst)
        inventory_position = (
            state.inventory_on_hand
            + state.pipeline_on_order
            - state.backlog
        )

        gap = self.target_inventory - inventory_position

        # Confidence-weighted correction: high confidence → smaller step
        confidence = min(1.0, self.n / 20.0)
        correction = gap * (1 - confidence * 0.5)

        order = int(self.demand_mean + correction)
        return max(0, order)
