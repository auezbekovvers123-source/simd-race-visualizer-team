"""
Race animation timeline model — Person 2.

No Tkinter: pure math for scalar vs SIMD logical progress per frame.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

OperationKey = str  # "add" | "mul" | "dot"


def ceil_div(a: int, b: int) -> int:
    """Return ceil(a / b) for positive integers."""
    return (a + b - 1) // b


def logical_scalar_cycles(n: int, op: OperationKey) -> int:
    """Scalar logical cycle budget (dot counts mul+add per element)."""
    if op == "dot":
        return n * 2
    return n


def logical_simd_cycles(n: int, width: int, op: OperationKey) -> int:
    """SIMD logical cycles: chunks of width plus a small dot-reduction term."""
    chunks = ceil_div(n, width)
    if op == "dot":
        return chunks + max(0, int(math.ceil(math.log2(width))))
    return chunks


@dataclass(frozen=True)
class RaceFrameState:
    """Logical progress snapshot for one animation frame."""

    scalar_elems: int
    simd_elems: int
    scalar_cycles: int
    simd_cycles: int


class RaceAnimation:
    """
    Compressed timeline: scalar finishes in ``anim_frames``; SIMD finishes sooner.

    SIMD progress uses a smaller logical cycle budget (``logical_simd_cycles``).
    """

    def __init__(self, anim_frames: int = 140) -> None:
        self.anim_frames = max(1, int(anim_frames))

    def progress(self, frame: int, n: int, width: int, op: OperationKey) -> RaceFrameState:
        """Return progress for 0-based frame index."""
        F = self.anim_frames
        sf = min(1.0, frame / F)
        scalar_elems = min(n, int(math.floor(n * sf + 1e-9)))

        sc = logical_scalar_cycles(n, op)
        vc = max(1, logical_simd_cycles(n, width, op))
        simd_f = min(1.0, sf / (vc / sc))
        simd_elems = min(n, int(math.floor(n * simd_f + 1e-9)))

        scalar_cycles = min(sc, int(math.floor(sc * sf + 1e-9)))
        simd_cycles = min(vc, int(math.ceil(vc * simd_f + 1e-9)))

        return RaceFrameState(scalar_elems, simd_elems, scalar_cycles, simd_cycles)

    def cycles_saved(self, state: RaceFrameState) -> int:
        """Teaching metric: scalar_cycles - simd_cycles on the model timeline."""
        return max(0, state.scalar_cycles - state.simd_cycles)
