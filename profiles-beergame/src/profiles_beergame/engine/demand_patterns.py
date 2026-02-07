"""Configurable demand pattern generators for simulation experiments."""

from __future__ import annotations

import math
import random
from typing import Callable


def step_demand(
    initial: int = 4, final: int = 8, step_period: int = 20
) -> Callable[[int], int]:
    """Demand jumps from *initial* to *final* at *step_period*."""
    def _f(t: int) -> int:
        return final if t >= step_period else initial
    return _f


def seasonal_demand(
    base: int = 4, amplitude: int = 2, period: int = 12
) -> Callable[[int], int]:
    """Sinusoidal demand: base ± amplitude with given period."""
    def _f(t: int) -> int:
        return max(0, int(base + amplitude * math.sin(2 * math.pi * t / period)))
    return _f


def noisy_demand(
    base: int = 4, noise: int = 2, seed: int = 42
) -> Callable[[int], int]:
    """Constant base demand + uniform random noise in [-noise, +noise]."""
    rng = random.Random(seed)
    def _f(t: int) -> int:
        return max(0, base + rng.randint(-noise, noise))
    return _f


def shock_demand(
    base: int = 4,
    shock_period: int = 10,
    shock_duration: int = 3,
    shock_magnitude: int = 12,
) -> Callable[[int], int]:
    """Normal demand with a one-time spike (supply disruption scenario)."""
    def _f(t: int) -> int:
        if shock_period <= t < shock_period + shock_duration:
            return shock_magnitude
        return base
    return _f
